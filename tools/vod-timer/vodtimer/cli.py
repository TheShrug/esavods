from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from importlib.resources import files
from pathlib import Path

from collections import Counter

from . import __version__, resolve, review as review_mod, video
from .ocr import fmt
from .pipeline import analyse, parse_duration

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"
COLOUR = {"high": GREEN, "medium": YELLOW, "low": YELLOW, "reject": RED, "none": RED}

# yt-dlp's wording for "this IP is rate-limited", in the forms it actually
# emits. Matched on "not a bot" rather than the whole sentence because the
# real message contains a curly apostrophe in "you're".
BOT_WALL = re.compile(r"not a bot|sign in to confirm|HTTP Error 429|too many requests",
                      re.I)
# Exit code for "stopped early, nothing wrong with the input" - distinct from
# 1, which means the batch finished and some runs were unreadable.
EX_BLOCKED = 75


def _bot_walled(r: dict) -> bool:
    return bool(BOT_WALL.search(r.get("error") or ""))


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

    # `crop` is the rectangle calibration settled on, in 480p-frame pixels.
    # Recorded because it is the only positional evidence a read produces, and
    # ESA moves the timer per layout - `16x9-1p` and `4x3-7p` cannot put it in
    # the same place. Collected across an event it says where each layout keeps
    # its clock, which is what a --crop fast path would need. Without this the
    # information is computed for every run and then thrown away.
    #
    # `frames_read`/`frames_total` are here because a short read is otherwise
    # invisible outside the container logs: the two truncated Summer 2022
    # clips read 11/11 and 14/14 frames where 50 were expected, and their rows
    # carried a final_time, a confidence and notes that all looked ordinary.
    # `_report` has always printed the pair; the CSV is what survives the run.
    fields = ["video_id", "game", "actual", "final_time", "final_seconds",
              "confidence", "frames_read", "frames_total", "duration",
              "estimate", "check_at", "crop", "notes"]

    # Results are written and flushed per run, not collected and dumped at the
    # end. A whole-marathon batch takes hours; a crash three hours in must not
    # throw away three hours of answers, and --resume reads this same file back.
    done: set[str] = set()
    kept: list[dict] = []
    if args.out and args.resume and Path(args.out).exists():
        with open(args.out, encoding="utf8") as fh:
            previous = [r for r in csv.DictReader(fh) if r.get("video_id")]

        # Done means "produced a time", not "has a row". A failure is recorded
        # as a row too, so keying resume on the video_id alone makes a failure
        # indistinguishable from a success and permanently unretryable: when
        # YouTube's bot wall blocked 53 runs of ESA Winter 2026, every later
        # --resume skipped exactly the runs that still needed reading.
        kept = [r for r in previous if (r.get("final_time") or "").strip()]
        done = {r["video_id"] for r in kept}
        retry = len(previous) - len(kept)
        print(f"resuming: {len(done)} already done"
              + (f", {retry} failed and will be re-read" if retry else ""))

    sink = writer = None
    if args.out:
        # Rewritten from `kept`, never appended to. The failed rows have to come
        # out of the file, or re-reading one leaves two rows for the same video
        # and whichever the merge sees last wins.
        sink = open(args.out, "w", newline="", encoding="utf8")
        writer = csv.DictWriter(sink, fieldnames=fields, extrasaction="ignore",
                                restval="")
        writer.writeheader()
        for previous_row in kept:
            writer.writerow(previous_row)
        sink.flush()

    shard_i, shard_n = 0, 1
    if args.shard:
        shard_i, shard_n = (int(x) for x in args.shard.split("/"))
        rows = [r for k, r in enumerate(rows) if k % shard_n == shard_i]
        print(f"shard {shard_i}/{shard_n}: {len(rows)} of this event's runs")

    results = []
    # Consecutive bot-wall failures. Once YouTube starts refusing this IP it
    # refuses every subsequent request, and the batch's own error handling is
    # what hides that: each failure is caught, recorded and stepped over, so a
    # run that has stopped reading anything looks exactly like a run in
    # progress. ESA Summer 2025 spent about half of a two-hour batch failing
    # this way, and those ~92 doomed requests are themselves more load on an
    # IP that is already being throttled - so continuing does not merely waste
    # the wall time, it plausibly lengthens the block.
    consecutive_wall = 0
    blocked = False
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
                "confidence": r.get("confidence"),
                "frames_read": r.get("frames_read", ""),
                "frames_total": r.get("frames_total", ""),
                "duration": r.get("duration", ""),
                "estimate": r.get("estimate", ""),
                "check_at": r.get("plateau_starts_at") or "",
                "crop": ",".join(str(v) for v in r["crop"]) if r.get("crop") else "",
                "notes": "; ".join(r.get("reasons", [])) or r.get("error", ""),
            })
            sink.flush()
        if args.discard_clips:
            video.forget_clips(vid)

        # Reset on anything that is not the wall, a non-wall error included: a
        # clip that downloaded and then failed in ffmpeg is proof YouTube is
        # still answering us, which is exactly what the counter is asking.
        if _bot_walled(r):
            consecutive_wall += 1
            if args.bot_wall_limit and consecutive_wall >= args.bot_wall_limit:
                blocked = True
                break
        else:
            consecutive_wall = 0

    if sink is not None:
        sink.close()
        print(f"wrote {args.out}")
    ok = sum(1 for r in results if r.get("confidence") in ("high", "medium"))
    print(f"{ok}/{len(results)} usable")
    if blocked:
        print(f"\n{RED}stopped: {consecutive_wall} consecutive runs refused "
              f"by YouTube's bot wall.{RESET}", file=sys.stderr)
        print("  Nothing is lost - only runs that produced a time were written,"
              "\n  so --resume re-reads everything this batch did not finish."
              "\n  Wait for the block to lift, or mount cookies and pass"
              "\n  --ytdlp-arg --cookies --ytdlp-arg /cookies.txt",
              file=sys.stderr)
        return EX_BLOCKED
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
              "video_id", "how", "slot", "vod_duration", "delta", "title",
              "scheduled", "platform", "players_md", "note"]
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
                "scheduled": row.get("_scheduled", ""),
                "platform": row.get("_platform", ""),
                "players_md": row.get("_players_md", ""),
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


def cmd_seed(args) -> int:
    """Prime the metadata cache from resolve's own search results.

    Run between `resolve` and `batch`. Every row `resolve` matched already
    carries the title and duration YouTube handed back, so re-asking for them
    is a request spent on something already known - one per run, against a bot
    wall counted in requests. ESA Summer 2023 spent about 200 that way.
    """
    seeded = present = skipped = 0
    for row in _read_csv(args.resolved):
        vid = (row.get("video_id") or "").strip()
        try:
            dur = int(float(row.get("vod_duration") or 0))
        except (TypeError, ValueError):
            dur = 0
        if not vid or not dur:
            skipped += 1
            continue
        if video.seed(vid, row.get("title") or "", dur):
            seeded += 1
        else:
            present += 1
    print(f"seeded {seeded}"
          + (f", {present} already cached" if present else "")
          + (f", {skipped} with no id or duration" if skipped else ""))
    print(f"that is {seeded} yt-dlp request(s) the batch will not have to make")
    return 0


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


def cmd_export(args) -> int:
    """Write the app importer's CSV: Scheduled;Game;Players;...;Time;Event;Youtube.

    The importer splits Time on ':' and expects three parts, treats Players as
    pipe-separated markdown, and reads the YouTube id straight out of the last
    column. Everything here exists to hand it exactly that.
    """
    rows = _read_csv(args.results)
    meta = {r["video_id"]: r for r in _read_csv(args.resolved) if r.get("video_id")}

    written = skipped = impossible = 0
    with open(args.out, "w", newline="", encoding="utf8") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["Scheduled", "Game", "Players", "Platform", "Category",
                    "Categories", "Twitch", "Time", "Event", "Youtube"])
        for r in rows:
            time = (r.get("final_time") or "").strip()
            if not time or time.count(":") != 2:
                skipped += 1
                continue

            # An OCR read longer than the video it came from is not a doubtful
            # time, it is a wrong one - a 19:35:00 run out of a 37-minute video
            # is worse on the site than the run being absent. Left out on the
            # same principle as a run with no time at all; the review list still
            # carries it for a human to supply.
            #
            # Never applied to a human answer. ESA splits a long run across
            # several VODs and the timer carries the cumulative total, so Part
            # 5/6 of the Skies of Arcadia 100% legitimately reads 20:30:31
            # inside a four-hour video. A person read that off the screen; this
            # check exists to catch the tool's own digit misreads, and it has no
            # business overruling the human it was written to defer to.
            if (r.get("source") or "ocr") == "ocr":
                try:
                    secs = float(r.get("final_seconds") or 0)
                    dur = float(r.get("duration") or 0)
                except (TypeError, ValueError):
                    secs = dur = 0.0
                if dur and secs > dur:
                    impossible += 1
                    continue

            vid = r.get("video_id", "")
            m = meta.get(vid, {})
            w.writerow([
                m.get("scheduled", ""),
                r.get("game") or m.get("game", ""),
                m.get("players_md", ""),
                m.get("platform", ""),
                m.get("category", ""),
                "",
                "",
                time,
                args.event_name,
                vid,
            ])
            written += 1

    print(f"wrote {args.out}: {written} runs"
          + (f", {skipped} with no time" if skipped else "")
          + (f", {impossible} longer than their own video" if impossible else ""))
    if skipped or impossible:
        print("those are left out entirely rather than imported as a wrong time")
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
    p.add_argument("--bot-wall-limit", type=int, default=5, metavar="N",
                   help="give up after N consecutive runs refused by YouTube's "
                        "bot wall (default: 5; 0 disables). Exits %d." % 75)
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

    p = sub.add_parser("seed", help="prime the metadata cache from a resolve --out CSV")
    p.add_argument("resolved", help="the resolve --out CSV")
    p.set_defaults(func=cmd_seed)

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

    p = sub.add_parser("export", help="write a CSV the app's runCsv:import can read")
    p.add_argument("results", help="final.csv from apply, or results.csv from batch")
    p.add_argument("--resolved", required=True, help="the resolve --out CSV")
    p.add_argument("--event-name", required=True,
                   help='exact event name for the app, e.g. "ESA 2026 Summer (One)"')
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_export)

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
