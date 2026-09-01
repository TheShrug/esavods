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

# From ESA Summer 2025 on, the schedule links each run to its own VOD from
# the Game cell. That is ESA naming the video themselves, so it beats any
# title search we could run against it - see match().
YT_LINK = re.compile(r"youtu(?:\.be/|be\.com/watch\?v=)([\w-]{11})")

# ESA titles a per-run VOD "Game [Category] by Runner - #tag". The bracketed
# part is the only thing separating two runs of the same game in one event -
# and with the runner out of the search query (see match()) it does that job
# alone, so it is worth reading out of the titles that break the convention
# too. "Mega Man 2 Relay Race (any%) - #ESASummer24" has no bracket at all.
TITLE_CATEGORY = re.compile(r"\[([^\]]+)\]")
TITLE_PARENS = re.compile(r"\(([^)]+)\)\s*$")
# The trailing "- #ESASummer24" is in every title and in none of the fields we
# compare it against, so it is pure noise in both game and category scoring.
TITLE_TAG = re.compile(r"[\s\-–—|]*#\S+\s*$")

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
    """The name a cell is carrying, without its markdown links.

    The first link is the thing the cell names; any later one is a second
    stream for the same run, which ESA links from the same cell. Keeping every
    link text turned `[...Beta Quest](twitch) + [Stream 2](twitch)` into the
    game name "The Legend of Zelda Ocarina of Time Beta Quest + Stream 2",
    which no VOD title carries and which therefore matched nothing.
    """
    m = MD_LINK.search(text or "")
    return (m.group(1) if m else (text or "")).strip()


def title_fields(title: str) -> tuple[str, str]:
    """Split a VOD title into the part naming the game and the category.

    ESA's own convention is "Game [Category] by Runner - #tag", but it is a
    convention and not a rule: some titles put the category in parentheses,
    and some carry no runner. Reading the bracket only, off a title still
    holding its hashtag, scored those titles as having no category at all.
    """
    text = TITLE_TAG.sub("", title or "").strip()
    found = TITLE_CATEGORY.search(text) or TITLE_PARENS.search(text)
    if not found:
        return text, ""
    return text[:found.start()].strip(), found.group(1).strip()


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
    return schedule_rows(payload, slug)


def schedule_rows(payload: dict, slug: str) -> list[dict]:
    """The parsing half of horaro_rows, off an already-fetched schedule."""
    sched = payload["schedule"]
    cols = [c.lower() for c in sched["columns"]]
    rows = []
    for idx, item in enumerate(sched["items"]):
        cells = dict(zip(cols, item.get("data") or []))
        raw_game = cells.get("game", "")
        game = _plain(raw_game)
        if not game:
            continue
        linked = YT_LINK.search(raw_game or "")
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
            "_vod": linked.group(1) if linked else "",
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


def search_query(row: dict, tag: str) -> str:
    """The one query a run gets. The runner is deliberately not in it.

    YouTube's search is conjunctive enough that a single token nothing matches
    returns zero results rather than worse ones, and horaro's Player(s) cell
    does not have to agree with the VOD title about a runner's name - ESA
    Summer 2024's schedule holds Oengus display names against Twitch handles
    in the titles (`Syn`/`synn1_`, `prisi`/`prisiii3`). Six such disagreements
    cost that event 14 of its 124 runs outright, each one reported as a video
    that does not exist. So the runner ranks candidates in rank() instead,
    where being wrong costs a place rather than the whole run.
    """
    return " ".join([row.get("GameName") or "", "#" + tag])


def gscore(game: str, head: str) -> float:
    """How well the game part of a VOD title matches the schedule's game name.

    Character similarity alone reads "Mega Man 5" as a better match for
    `Mega Man 2` than "Mega Man 2 Relay Race" is, because extra words cost
    more than a wrong digit does - and that is how Mega Man 5's video won the
    Mega Man 2 row on ESA Summer 2024. Counting whole words instead, weighted
    towards recall, does not make that mistake: a title carrying every word of
    the game name is that game even when it carries more besides, while one
    missing a word is a different game however close the spelling. Precision
    is still in it, because that is what keeps `Portal` off "Portal 2".
    """
    # Sets, not lists: "Yogho! Yogho!" is one word said twice, and counting it
    # twice halves the recall of a title that carries it.
    want, got = set(norm(game).split()), set(norm(head).split())
    shared = len(want & got)
    if not shared:
        # No word in common to count, so fall back to character similarity
        # rather than call it zero - two spellings of one name can share none.
        return difflib.SequenceMatcher(None, norm(game), norm(head)).ratio()
    recall, precision = shared / len(want), shared / len(got)
    return 5 * recall * precision / (4 * precision + recall)


def score(row: dict, tag: str, hits: list[dict]) -> list[dict]:
    """Score search results against a schedule row. No network, no ordering."""
    game = row.get("GameName") or ""
    who = players(row.get("PlayerNamesTwitch", ""))
    slot = row.get("_slot")
    scored = []
    for h in hits:
        title = h.get("title") or ""
        tagged = tag.lower() in norm(title).replace(" ", "")
        head, tcat = title_fields(title)
        dur = h.get("duration") or 0
        delta = abs(dur - slot) if (dur and slot) else None
        ntitle = norm(title)
        scored.append({
            "video_id": h["video_id"], "title": title, "duration": dur,
            "tagged": tagged,
            "gscore": round(gscore(game, head), 3),
            "delta": delta,
            # The runner is a rank signal, not a filter: horaro and the VOD
            # title agreeing on a name confirms a match, disagreeing on one
            # says nothing.
            "runner": any(norm(w) and norm(w) in ntitle for w in who),
            # Without a timing sheet there is no slot length to tell two runs
            # of the same game apart, and the game name scores identically for
            # both. The category in the title is what distinguishes them.
            "cscore": round(difflib.SequenceMatcher(
                None, norm(row.get("CategoryName") or ""), norm(tcat)).ratio(), 3),
        })
    return scored


def rank(c: dict) -> tuple:
    """Slot length, then the tag, then the game, then who ran it.

    The runner used to sort above the game, which was safe only while the
    query had already thrown away every candidate whose title did not name
    them. Ranking a set chosen on game and tag alone, a runner's name in an
    unrelated title is a coincidence and not a confirmation: it put Street
    Boyz above Kingdom Hearts for the Kingdom Hearts row, and Baby Shark VR
    Dancing above Teenage Mutant Ninja Turtles for the Turtles row. Below the
    game it still does the job it is there for - telling two runs of one game
    apart - with the category behind it for when the two schedules disagree
    about a runner's name, which is the case that started all this.
    """
    exact = c["delta"] is not None and c["delta"] <= 5
    return (exact, c["tagged"], round(c["gscore"], 1), c["runner"],
            c["cscore"], c["gscore"],
            -(c["delta"] if c["delta"] is not None else 1e9))


def verdict(best: dict) -> str:
    if best["delta"] is not None and best["delta"] <= 5 and best["tagged"]:
        return "slot-exact"
    if best["delta"] is not None and best["delta"] <= 5:
        return "slot-only"
    if best["tagged"] and best["runner"] and best["gscore"] >= 0.75:
        # No slot length to check against, so the confirmation is three-way
        # agreement instead: the event hashtag, the game, and the runner.
        return f"tag-game-runner({best['gscore']})"
    if best["tagged"] and best["gscore"] >= 0.85:
        return f"tag-game({best['gscore']})"
    return f"weak({best['gscore']})"


def best_of(row: dict, tag: str, hits: list[dict]) -> dict | None:
    scored = score(row, tag, hits)
    scored.sort(key=rank, reverse=True)
    return scored[0] if scored else None


def match(row: dict, tag: str, limit: int = 6) -> dict:
    slot = row.get("_slot")
    query = search_query(row, tag)

    # ESA's own link, when the schedule carries one, is not a match at all -
    # it is the answer. Searching anyway would only give us a chance to
    # disagree with the organisers about which video is theirs. We still probe
    # it, because that is what tells us a link is dead rather than merely
    # wrong, and because a stale link is the one failure this path can have.
    linked = row.get("_vod")
    if linked:
        try:
            meta = video.probe(linked)
        except Exception as exc:
            return {"video_id": linked, "how": "horaro-link-dead",
                    "slot": slot, "note": str(exc)[:120]}
        return {"video_id": linked, "how": "horaro-link", "title": meta.title,
                "vod_duration": meta.duration, "slot": slot,
                "delta": abs(meta.duration - slot) if slot else None, "note": ""}

    try:
        hits = video.search(query, limit)
    except Exception as exc:
        return {"video_id": "", "how": "search-failed", "note": str(exc)[:120]}

    best = best_of(row, tag, hits)
    if not best or not best["video_id"]:
        return {"video_id": "", "how": "no-hits", "note": query}

    return {
        "video_id": best["video_id"], "how": verdict(best), "title": best["title"],
        "vod_duration": best["duration"], "slot": slot,
        "delta": best["delta"], "note": "",
    }
