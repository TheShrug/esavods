from __future__ import annotations

import argparse
import csv
import json
import sys
from importlib.resources import files
from pathlib import Path

from collections import Counter

from . import __version__, resolve, review as review_mod, video
from .ocr import fmt
from .pipeline import analyse, parse_duration

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"
COLOUR = {"high": GREEN, "medium": YELLOW, "low": YELLOW, "reject": RED, "none": RED}


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--tail", type=int, default=780,
                   help="seconds of the end of the video to inspect (default: 780)")
    p.add_argument("--step", type=float, default=10.0,
                   help="seconds between sampled frames (default: 10)")
    p.add_argument("--height", type=int, default=720,
                   help="max video height to download (default: 720)")
    p.add_argument("--min-plateau", type=int, default=3,
                   help="frames that must agree before a value is a plateau (default: 3)")
    p.add_argument("--crop", metavar="X,Y,W,H",
                   help="skip calibration and read this rectangle")
    p.add_argument("--debug-crops", metavar="DIR",
                   help="write every timer crop here for eyeballing or a vision model")
    p.add_argument("--ytdlp-arg", action="append", default=[], dest="ytdlp_args",
                   help="pass an extra argument through to yt-dlp (repeatable)")


def _kwargs(args) -> dict:
    return {
        "tail": args.tail,
        "step": args.step,
        "height": args.height,
        "min_plateau": args.min_plateau,
        "crop": tuple(int(v) for v in args.crop.split(",")) if args.crop else None,
        "debug_dir": Path(args.debug_crops) if args.debug_crops else None,
        "ytdlp_args": args.ytdlp_args,
    }


def _report(r: dict) -> None:
    if r.get("error"):
        print(f"{RED}FAILED{RESET} {r['video_id']}: {r['error']}")
        return
    c = COLOUR.get(r["confidence"], "")
    print(f"{r['title']}")
    print(f"  final time   {c}{r['final_time']}{RESET}   ({r['confidence']} confidence)")
    print(f"  video length {r['duration_hms']}"
          + (f"   estimate {r['estimate']}" if r.get("estimate") else ""))
    print(f"  {DIM}crop {r['crop']}  "
          f"calibration {r['calibration'].get('agreed', 0)}/{r['calibration'].get('sampled', 0)}  "
          f"frames read {r['frames_read']}/{r['frames_total']}{RESET}")
    for reason in r["reasons"]:
        print(f"  {DIM}- {reason}{RESET}")


def cmd_read(args) -> int:
    r = analyse(args.video_id, estimate=args.estimate, verbose=not args.json, **_kwargs(args))
    if args.json:
        json.dump(r, sys.stdout, indent=2)
        print()
    else:
        _report(r)
    return 0 if r.get("confidence") in ("high", "medium") else 1


def cmd_batch(args) -> int:
    rows = list(csv.DictReader(
        line for line in Path(args.input).read_text(encoding="utf8").splitlines()
        if not line.startswith("#")
    ))

    fields = ["video_id", "game", "actual", "final_time", "final_seconds",
              "confidence", "duration", "estimate", "check_at", "notes"]

    # Results are written and flushed per run, not collected and dumped at the
    # end. A whole-marathon batch takes hours; a crash three hours in must not
    # throw away three hours of answers, and --resume reads this same file back.
    done: set[str] = set()
    if args.out and args.resume and Path(args.out).exists():
        with open(args.out, encoding="utf8") as fh:
            done = {r["video_id"] for r in csv.DictReader(fh) if r.get("video_id")}
        print(f"resuming: {len(done)} already done")

    sink = writer = None
    if args.out:
        appending = bool(done)
        sink = open(args.out, "a" if appending else "w", newline="", encoding="utf8")
        writer = csv.DictWriter(sink, fieldnames=fields)
        if not appending:
            writer.writeheader()
            sink.flush()

    shard_i, shard_n = 0, 1
    if args.shard:
        shard_i, shard_n = (int(x) for x in args.shard.split("/"))
        rows = [r for k, r in enumerate(rows) if k % shard_n == shard_i]
        print(f"shard {shard_i}/{shard_n}: {len(rows)} of this event's runs")

    results = []
    for i, row in enumerate(rows, 1):
        vid = row.get("video_id") or row.get("youtube_vod_id")
        if not vid or vid in done:
            continue
        print(f"[{i}/{len(rows)}] {vid} {row.get('game', '')}", flush=True)
        try:
            r = analyse(vid, estimate=row.get("estimate"), verbose=args.verbose,
                        **_kwargs(args))
        except Exception as exc:                      # keep the batch moving
            r = {"video_id": vid, "error": str(exc), "confidence": "none"}
        r["game"] = row.get("game", "")
        r["actual"] = row.get("actual", "")
        _report(r)
        results.append(r)

        if writer is not None:
            writer.writerow({
                "video_id": r.get("video_id"), "game": r.get("game", ""),
                "actual": r.get("actual", ""), "final_time": r.get("final_time", ""),
                "final_seconds": r.get("final_seconds", ""),
                "confidence": r.get("confidence"), "duration": r.get("duration", ""),
                "estimate": r.get("estimate", ""),
                "check_at": r.get("plateau_starts_at") or "",
                "notes": "; ".join(r.get("reasons", [])) or r.get("error", ""),
            })
            sink.flush()
        if args.discard_clips:
            video.forget_clips(vid)

    if sink is not None:
        sink.close()
        print(f"wrote {args.out}")
    ok = sum(1 for r in results if r.get("confidence") in ("high", "medium"))
    print(f"{ok}/{len(results)} usable")
    return 0 if ok == len(results) else 1


def cmd_search(args) -> int:
    for hit in video.search(" ".join(args.query), args.limit):
        length = fmt(hit["duration"]) if hit.get("duration") else "?"
        print(f"{hit['video_id']}  {length:>9}  {hit['title']}")
    return 0


def cmd_resolve(args) -> int:
    """Turn an ESA run-timings sheet into a CSV of video ids to read."""
    if args.horaro:
        rows = resolve.horaro_rows(args.horaro)
        source = "horaro.net/esa/" + args.horaro
    else:
        rows = resolve.timed_rows(args.input)
        source = args.input
    print(f"{len(rows)} runs from {source}")
    print("")
    fields = ["uuid", "game", "category", "runner", "estimate", "actual",
              "video_id", "how", "slot", "vod_duration", "delta", "title", "note"]
    counts: Counter = Counter()
    with open(args.out, "w", newline="", encoding="utf8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for i, row in enumerate(rows, 1):
            m = resolve.match(row, args.tag)
            counts[m["how"].split("(")[0]] += 1
            rec = {
                "uuid": row["UUID"], "game": row.get("GameName", ""),
                "category": row.get("CategoryName", ""),
                "runner": " & ".join(resolve.players(row.get("PlayerNamesTwitch", ""))),
                "estimate": row.get("Estimate", ""), "actual": row.get("Actual Time", ""),
                "video_id": m.get("video_id", ""), "how": m.get("how", ""),
                "slot": m.get("slot", ""), "vod_duration": m.get("vod_duration", ""),
                "delta": m.get("delta", ""), "title": m.get("title", ""),
                "note": m.get("note", ""),
            }
            w.writerow(rec)
            fh.flush()
            print(f"[{i}/{len(rows)}] {m.get('how',''):>14}  {row.get('GameName','')[:44]}")
    print(f"\nwrote {args.out}")
    for how, n in counts.most_common():
        print(f"  {how:>14}  {n}")
    return 0


def _read_csv(path: str) -> list[dict]:
    with open(path, encoding="utf8") as fh:
        return list(csv.DictReader(l for l in fh.read().splitlines()
                                   if not l.startswith("#")))


def cmd_review(args) -> int:
    """List the runs a person still has to check, worst first."""
    rows = _read_csv(args.results)
    extra = {}
    if args.resolved:
        extra = {r["video_id"]: r for r in _read_csv(args.resolved) if r.get("video_id")}

    trust = set(args.trust)
    picked = review_mod.flagged(rows, trust)
    text, index = review_mod.render(picked, extra, args.event or "")

    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf8")
        idx = Path(args.out).with_suffix("") .as_posix() + "-index.csv"
        with open(idx, "w", newline="", encoding="utf8") as fh:
            w = csv.DictWriter(fh, fieldnames=["n", "video_id", "game",
                                               "was_read", "confidence"])
            w.writeheader()
            w.writerows(index)
        print(f"wrote {args.out} and {idx}")
    print(f"{len(rows) - len(picked)}/{len(rows)} accepted without review")
    return 0


def cmd_apply(args) -> int:
    """Merge a person's answers back over the machine's, and say what changed."""
    rows = {r["video_id"]: r for r in _read_csv(args.results) if r.get("video_id")}
    index = {int(r["n"]): r for r in _read_csv(args.index)}
    answers = review_mod.parse_answers(Path(args.answers).read_text(encoding="utf8"))

    unknown = sorted(set(answers) - set(index))
    if unknown:
        print(f"warning: no such item(s) in the index: {unknown}")

    applied = skipped = 0
    for n, value in answers.items():
        entry = index.get(n)
        if not entry:
            continue
        row = rows.get(entry["video_id"])
        if row is None:
            continue
        if value.lower() in ("skip", "-", "?", "none", "unreadable"):
            row["confidence"] = "unresolved"
            row["source"] = "human-skip"
            skipped += 1
            continue
        row["final_time"] = value
        row["final_seconds"] = parse_duration(value)
        row["confidence"] = "human"
        row["source"] = "human"
        applied += 1

    for row in rows.values():
        row.setdefault("source", "ocr" if row.get("final_time") else "")

    fields = ["video_id", "game", "final_time", "final_seconds", "confidence",
              "source", "duration", "estimate", "check_at", "notes"]
    with open(args.out, "w", newline="", encoding="utf8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in rows.values():
            w.writerow(row)

    usable = sum(1 for r in rows.values()
                 if r.get("confidence") in ("high", "medium", "human"))
    print(f"applied {applied}, skipped {skipped}")
    print(f"{usable}/{len(rows)} runs now have a time")
    print(f"wrote {args.out}")
    return 0


def cmd_selftest(args) -> int:
    """Read ESA Summer 2022 VODs whose true times ESA themselves published."""
    text = files("vodtimer.fixtures").joinpath("esa-summer-2022.csv").read_text(encoding="utf8")
    cases = list(csv.DictReader(l for l in text.splitlines() if not l.startswith("#")))
    if args.only:
        cases = [c for c in cases if c["video_id"] in args.only]

    failures = 0
    print(f"{len(cases)} case(s), tolerance +/-{args.tolerance}s\n")
    for case in cases:
        truth = parse_duration(case["actual"])
        try:
            r = analyse(case["video_id"], estimate=case["estimate"],
                        verbose=True, **_kwargs(args))
        except Exception as exc:
            print(f"{RED}ERROR{RESET} {case['game']}: {exc}\n")
            failures += 1
            continue
        _report(r)
        got = r.get("final_seconds")
        if got is None:
            print(f"  {RED}FAIL{RESET} truth {case['actual']}, read nothing\n")
            failures += 1
            continue
        delta = got - truth
        if abs(delta) <= args.tolerance and r["confidence"] in ("high", "medium"):
            print(f"  {GREEN}PASS{RESET} truth {case['actual']}, off by {delta:+.0f}s\n")
        else:
            print(f"  {RED}FAIL{RESET} truth {case['actual']}, off by {delta:+.0f}s\n")
            failures += 1

    print(f"{len(cases) - failures}/{len(cases)} passed")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="vodtimer",
        description="Read the finished run time off the end of an ESA YouTube VOD.",
    )
    ap.add_argument("--version", action="version", version=f"vodtimer {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("read", help="read one video")
    p.add_argument("video_id")
    p.add_argument("--estimate", help="scheduled estimate, e.g. 00:45:00, for a sanity check")
    p.add_argument("--json", action="store_true")
    _common(p)
    p.set_defaults(func=cmd_read)

    p = sub.add_parser("batch", help="read a CSV of videos")
    p.add_argument("input", help="CSV with a video_id column, optionally estimate and game")
    p.add_argument("--out", help="write results here")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--resume", action="store_true",
                   help="skip video ids already present in --out")
    p.add_argument("--discard-clips", action="store_true",
                   help="delete each downloaded clip once read (saves disk on long runs)")
    p.add_argument("--shard", metavar="I/N",
                   help="process only every Nth row starting at I, for running "
                        "several containers at once (YouTube throttles per "
                        "connection, so this is how throughput is bought)")
    _common(p)
    p.set_defaults(func=cmd_batch)

    p = sub.add_parser("resolve", help="match an ESA run-timings sheet to YouTube VODs")
    p.add_argument("input", nargs="?",
                   help="a data/run-timings/*.csv from estimate-accuracy-model")
    p.add_argument("--horaro", metavar="SLUG",
                   help="instead, read the published schedule, e.g. 2021-winter")
    p.add_argument("--tag", required=True, help="event hashtag in VOD titles, e.g. ESASummer22")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_resolve)

    p = sub.add_parser("review", help="list the runs a person still has to check")
    p.add_argument("results", help="a batch --out CSV")
    p.add_argument("--resolved", help="the resolve --out CSV, for runner/category context")
    p.add_argument("--event", default="", help="event name, for the heading")
    p.add_argument("--trust", nargs="*", default=["high"],
                   help="confidence tiers accepted without review (default: high)")
    p.add_argument("--out", help="also write the list here, plus a -index.csv")
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("apply", help="merge human answers back into the results")
    p.add_argument("results", help="a batch --out CSV")
    p.add_argument("--index", required=True, help="the -index.csv review wrote")
    p.add_argument("--answers", required=True, help="file of 'N H:MM:SS' lines")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_apply)

    p = sub.add_parser("search", help="find a VOD by title via yt-dlp's ytsearch")
    p.add_argument("query", nargs="+")
    p.add_argument("--limit", type=int, default=5)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("selftest", help="check against ESA's own published run timings")
    p.add_argument("--tolerance", type=float, default=1.0, help="seconds (default: 1)")
    p.add_argument("--only", nargs="*", help="limit to these video ids")
    _common(p)
    p.set_defaults(func=cmd_selftest)

    args = ap.parse_args(argv)
    return args.func(args)
