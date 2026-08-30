"""Match rows of an ESA run-timings sheet to their YouTube VODs.

Title search alone is a guess. The timings sheet also carries StartTimestamp
and EndTimestamp, whose difference is the length of the whole slot ESA streamed
- and that is exactly what ends up on YouTube as the VOD. So a candidate whose
duration equals the slot to within a couple of seconds is not a fuzzy match at
all; it is a near-certain one, confirmed by a number the search never saw.
"""
from __future__ import annotations

import csv
import difflib
import json
import re
import urllib.request

from . import video

HORARO_JSON = "https://horaro.net/esa/{}.json"
# horaro refuses a request with no User-Agent.
UA = "esavods-vod-timer/0.1 (+https://github.com/TheShrug/esavods)"

MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-")


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def players(cell: str) -> list[str]:
    try:
        d = json.loads(cell or "{}")
    except (ValueError, TypeError):
        return []
    return [k for k in d.keys() if k]


def _plain(text: str) -> str:
    return MD_LINK.sub(lambda m: m.group(1), text or "").strip()


def hms(seconds: int) -> str:
    return f"{seconds // 3600}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"


def horaro_rows(slug: str) -> list[dict]:
    """Load a published ESA schedule as rows shaped like the timings sheet.

    This is the path that matters for the backfill: for the six missing years
    ESA never published run timings, so the schedule is all there is. It gives
    the estimate but no slot length, which costs us the strongest match check -
    see match().
    """
    req = urllib.request.Request(HORARO_JSON.format(slug), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as fh:
        payload = json.load(fh)

    sched = payload["schedule"]
    cols = [c.lower() for c in sched["columns"]]
    rows = []
    for idx, item in enumerate(sched["items"]):
        cells = dict(zip(cols, item.get("data") or []))
        game = _plain(cells.get("game", ""))
        if not game:
            continue
        players = [_plain(p) for p in (cells.get("player(s)") or "").split(",")]
        rows.append({
            "UUID": cells.get("id") or f"{slug}-{idx}",
            "GameName": game,
            "CategoryName": cells.get("category") or "",
            "PlayerNamesTwitch": json.dumps({p: p for p in players if p}),
            "Estimate": hms(int(item.get("length_t") or 0)),
            "Actual Time": "",
            "_slot": None,
            "_scheduled": item.get("scheduled") or "",
            "_layout": cells.get("layout") or "",
            # kept verbatim: the importer wants players as pipe-separated
            # markdown, which is the shape horaro already stores them in.
            "_players_md": (cells.get("player(s)") or "").replace(", ", "|"),
            "_platform": cells.get("platform") or "",
        })
    return rows


def timed_rows(path: str) -> list[dict]:
    with open(path, encoding="utf8") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        if not UUID_RE.match((r.get("UUID") or "").strip()):
            continue
        try:
            slot = int(r["EndTimestamp"]) - int(r["StartTimestamp"])
        except (KeyError, ValueError, TypeError):
            continue
        if slot <= 0:
            continue
        r["_slot"] = slot
        out.append(r)
    return out


def match(row: dict, tag: str, limit: int = 6) -> dict:
    game = row.get("GameName") or ""
    who = players(row.get("PlayerNamesTwitch", ""))
    slot = row.get("_slot")
    query = " ".join([game] + who[:2] + ["#" + tag])

    try:
        hits = video.search(query, limit)
    except Exception as exc:
        return {"video_id": "", "how": "search-failed", "note": str(exc)[:120]}

    scored = []
    for h in hits:
        title = h.get("title") or ""
        tagged = tag.lower() in norm(title).replace(" ", "")
        head = norm(title.split(" [")[0])
        gscore = difflib.SequenceMatcher(None, norm(game), head).ratio()
        dur = h.get("duration") or 0
        delta = abs(dur - slot) if (dur and slot) else None
        ntitle = norm(title)
        runner_hit = any(norm(w) and norm(w) in ntitle for w in who)
        scored.append({
            "video_id": h["video_id"], "title": title, "duration": dur,
            "tagged": tagged, "gscore": round(gscore, 3), "delta": delta,
            "runner": runner_hit,
        })

    # Slot-length agreement outranks everything; the tag outranks title fuzz.
    def rank(c):
        exact = c["delta"] is not None and c["delta"] <= 5
        return (exact, c["tagged"], c["runner"], c["gscore"],
                -(c["delta"] if c["delta"] is not None else 1e9))

    scored.sort(key=rank, reverse=True)
    best = scored[0] if scored else None
    if not best or not best["video_id"]:
        return {"video_id": "", "how": "no-hits", "note": query}

    if best["delta"] is not None and best["delta"] <= 5 and best["tagged"]:
        how = "slot-exact"
    elif best["delta"] is not None and best["delta"] <= 5:
        how = "slot-only"
    elif best["tagged"] and best["runner"] and best["gscore"] >= 0.75:
        # No slot length to check against, so the confirmation is three-way
        # agreement instead: the event hashtag, the game, and the runner.
        how = f"tag-game-runner({best['gscore']})"
    elif best["tagged"] and best["gscore"] >= 0.85:
        how = f"tag-game({best['gscore']})"
    else:
        how = f"weak({best['gscore']})"

    return {
        "video_id": best["video_id"], "how": how, "title": best["title"],
        "vod_duration": best["duration"], "slot": row["_slot"],
        "delta": best["delta"], "note": "",
    }
