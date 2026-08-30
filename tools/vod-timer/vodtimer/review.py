"""Turn a batch result into a short list for a person, and fold their answers back.

The tool is only useful if the runs it cannot vouch for are cheap to check by
hand. That means a numbered list, one line of context each, and a link that
lands the reader at the moment the clock is already frozen - not at the top of
a two-hour video.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

# Worst first: a reject is a refusal to answer, a medium is a coin flip.
SEVERITY = {"none": 0, "reject": 1, "low": 2, "medium": 3, "high": 4}

# If we never recorded where the clock froze, land a few minutes from the end.
# Outros in this data run 2-6 minutes, so this is nearly always inside one.
DEFAULT_LOOKBACK = 240


def _int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def jump_second(row: dict) -> int:
    at = _int(row.get("check_at"), 0)
    if at > 0:
        return max(0, at - 15)
    duration = _int(row.get("duration"), 0)
    return max(0, duration - DEFAULT_LOOKBACK)


def flagged(rows: list[dict], trust: set[str]) -> list[dict]:
    out = [r for r in rows if (r.get("confidence") or "none") not in trust]
    out.sort(key=lambda r: (SEVERITY.get(r.get("confidence") or "none", 0),
                            r.get("game") or ""))
    return out


def describe(row: dict) -> str:
    read = row.get("final_time") or "nothing"
    note = re.sub(r"\s+", " ", row.get("notes") or "").strip()
    if len(note) > 110:
        note = note[:107] + "..."
    return f"read {read} - {row.get('confidence')}: {note}" if note else f"read {read}"


def render(rows: list[dict], extra: dict[str, dict], event: str = "") -> tuple[str, list[dict]]:
    lines = []
    header = f"{len(rows)} run(s) need a human"
    if event:
        header += f" - {event}"
    lines.append(header)
    lines.append("")
    lines.append("Open each link (it starts near the end, where the timer is "
                 "already stopped), read the final time, and reply with the "
                 "number and the time, one per line, e.g. `3 1:12:04`. "
                 "Reply `skip` for any you cannot read.")
    lines.append("")

    index = []
    for n, r in enumerate(rows, 1):
        vid = r.get("video_id", "")
        meta = extra.get(vid, {})
        who = meta.get("runner") or ""
        cat = meta.get("category") or ""
        title = " - ".join(x for x in [r.get("game") or meta.get("game", ""), cat] if x)
        if who:
            title += f" ({who})"
        t = jump_second(r)
        lines.append(f"{n:>2}. {title}")
        lines.append(f"    {describe(r)}")
        lines.append(f"    https://youtu.be/{vid}?t={t}")
        lines.append("")
        index.append({"n": n, "video_id": vid, "game": r.get("game", ""),
                      "was_read": r.get("final_time", ""),
                      "confidence": r.get("confidence", "")})
    return "\n".join(lines), index


ANSWER_RE = re.compile(r"^\s*(\d+)\s*[.):]?\s+(.+?)\s*$")


def parse_answers(text: str) -> dict[int, str]:
    """Accept '3 1:12:04', '3. 1:12:04', '3) 1:12:04', '3: skip'."""
    out: dict[int, str] = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        m = ANSWER_RE.match(line)
        if not m:
            continue
        out[int(m.group(1))] = m.group(2).strip()
    return out
