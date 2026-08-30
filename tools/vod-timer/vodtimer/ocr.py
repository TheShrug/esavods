"""Find the run timer in a frame, then read it.

The crop rectangle is *derived from the footage*, not hardcoded per layout.
ESA has run many nodecg-speedcontrol layouts over six years (16x9-1p, 16x9-2p,
4x3-1p, GBA layouts, ...) and each puts the timer somewhere different, so a
lookup table would be a maintenance liability that silently mis-crops the day a
new layout shows up. Instead we OCR a handful of whole frames, ask where a
HH:MM:SS-shaped string keeps appearing in the same place, and lock that box.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import pytesseract
from PIL import Image, ImageOps

# The on-screen clock. Hours are 0-9 in practice but allow two digits; the
# fractional part is optional because some layouts show tenths and some don't.
TIMER_RE = re.compile(r"(?<![\d:])(\d{1,2}):([0-5]\d):([0-5]\d)(?:[.,](\d{1,3}))?(?![\d:])")

# Digits and separators only. Stops tesseract "helpfully" reading 0 as O.
WHITELIST = "0123456789:."


@dataclass
class Box:
    x: int
    y: int
    w: int
    h: int

    def pad(self, px: int, py: int, bounds: tuple[int, int]) -> "Box":
        W, H = bounds
        x = max(0, self.x - px)
        y = max(0, self.y - py)
        return Box(x, y, min(W - x, self.w + 2 * px), min(H - y, self.h + 2 * py))

    def as_tuple(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.w, self.h)

    def crop_box(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.x + self.w, self.y + self.h)


def to_seconds(text: str) -> float | None:
    m = TIMER_RE.search(text)
    if not m:
        return None
    h, mi, s, frac = m.group(1), m.group(2), m.group(3), m.group(4)
    total = int(h) * 3600 + int(mi) * 60 + int(s)
    if frac:
        total += int(frac) / (10 ** len(frac))
    return float(total)


def fmt(seconds: float) -> str:
    s = int(round(seconds))
    return f"{s // 3600}:{(s % 3600) // 60:02d}:{s % 60:02d}"


# --------------------------------------------------------------------------
# calibration
# --------------------------------------------------------------------------

def _lines_with_boxes(img: Image.Image, scale: int = 2):
    """Whole-frame sparse OCR, regrouped into lines with per-word char spans."""
    big = img.convert("L").resize((img.width * scale, img.height * scale), Image.LANCZOS)
    data = pytesseract.image_to_data(
        big, config="--psm 11", output_type=pytesseract.Output.DICT
    )
    lines = defaultdict(list)
    for i, word in enumerate(data["text"]):
        word = (word or "").strip()
        if not word:
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        lines[key].append((
            word,
            Box(data["left"][i] // scale, data["top"][i] // scale,
                data["width"][i] // scale, data["height"][i] // scale),
        ))

    out = []
    for words in lines.values():
        text, spans = "", []
        for word, box in words:
            spans.append((len(text), len(text) + len(word), box))
            text += word
        out.append((text, spans))
    return out


def _median(boxes: list[Box]) -> Box:
    """Typical box for a cluster. A union would swallow the neighbouring line
    on any frame where tesseract merged two rows; the median ignores those."""
    def mid(vals):
        vals = sorted(vals)
        return vals[len(vals) // 2]
    return Box(mid([b.x for b in boxes]), mid([b.y for b in boxes]),
               mid([b.w for b in boxes]), mid([b.h for b in boxes]))


def _union(boxes: list[Box]) -> Box:
    x0 = min(b.x for b in boxes)
    y0 = min(b.y for b in boxes)
    x1 = max(b.x + b.w for b in boxes)
    y1 = max(b.y + b.h for b in boxes)
    return Box(x0, y0, x1 - x0, y1 - y0)


def _candidates(frames, positions, max_frames, grid):
    stride = max(1, len(frames) // max_frames)
    picks = list(zip(frames, positions))[::stride][:max_frames]

    clusters: dict[tuple[int, int], dict] = {}
    for path, pos in picks:
        with Image.open(path) as img:
            for text, spans in _lines_with_boxes(img):
                for m in TIMER_RE.finditer(text):
                    hit = [b for (a, z, b) in spans if a < m.end() and z > m.start()]
                    if not hit:
                        continue
                    box = _union(hit)
                    key = ((box.x + box.w // 2) // grid, (box.y + box.h // 2) // grid)
                    c = clusters.setdefault(key, {"boxes": [], "series": []})
                    c["boxes"].append(box)
                    c["series"].append((pos, to_seconds(m.group(0))))
    return clusters, len(picks)


def _running_score(series: list[tuple[float, float]]) -> int:
    """How many consecutive samples advance by exactly the wall time between them.

    Only a live clock does that. The estimate, the runner's PB and any other
    HH:MM:SS on the layout sit still, which is why they score zero here even
    though they OCR far more cleanly than the thing we actually want.
    """
    ordered = sorted(series)
    good = 0
    for (p0, v0), (p1, v1) in zip(ordered, ordered[1:]):
        if v0 is None or v1 is None:
            continue
        if abs((v1 - v0) - (p1 - p0)) <= 2.0:
            good += 1
    return good


def calibrate(frames: list[Path], positions: list[float], max_frames: int = 12,
              grid: int = 24) -> tuple["Box | None", dict]:
    """Locate the run timer, distinguishing it from the layout's other clocks."""
    info: dict = {"sampled": 0, "candidates": [], "running": False}
    if not frames:
        return None, info

    clusters, sampled = _candidates(frames, positions, max_frames, grid)
    info["sampled"] = sampled
    if not clusters:
        return None, info

    scored = []
    for key, c in clusters.items():
        values = [v for _, v in c["series"] if v is not None]
        scored.append({
            "box": _median(c["boxes"]),
            "hits": len(c["series"]),
            "running": _running_score(c["series"]),
            "constant": len(set(values)) <= 1,
            "sample": fmt(values[-1]) if values else None,
        })

    # A live clock first; only if nothing on screen is ticking do we fall back
    # to whatever was merely seen most often.
    scored.sort(key=lambda c: (c["running"], c["hits"]), reverse=True)
    info["candidates"] = [
        {"box": c["box"].as_tuple(), "hits": c["hits"],
         "running": c["running"], "sample": c["sample"]}
        for c in scored
    ]
    best = scored[0]
    info["running"] = best["running"] >= 2
    info["agreed"] = best["hits"]
    return best["box"], info


# --------------------------------------------------------------------------
# reading
# --------------------------------------------------------------------------

def _variants(crop: Image.Image, scale: int = 4):
    g = crop.convert("L")
    g = g.resize((g.width * scale, g.height * scale), Image.LANCZOS)
    g = ImageOps.autocontrast(g)
    yield g
    yield ImageOps.invert(g)
    yield g.point(lambda p: 255 if p > 150 else 0)
    yield ImageOps.invert(g).point(lambda p: 255 if p > 150 else 0)


def read_box(path: Path, box: Box, debug_dir: Path | None = None,
             quorum: int = 2) -> float | None:
    """Read one frame's timer.

    Twelve OCR passes per frame is the thorough answer and far too slow for a
    whole marathon, so the variants are ordered easiest-first and we stop as
    soon as `quorum` of them independently produce the same value. A clean
    frozen timer settles in two passes; only the awkward frames pay full price.
    """
    with Image.open(path) as img:
        crop = img.crop(box.crop_box())
        crop.load()

    votes: Counter = Counter()
    for i, variant in enumerate(_variants(crop)):
        if debug_dir and i == 0:
            debug_dir.mkdir(parents=True, exist_ok=True)
            variant.save(debug_dir / f"{path.stem}.crop.png")
        for psm in (7, 13, 6):
            try:
                text = pytesseract.image_to_string(
                    variant,
                    config=f"--psm {psm} -c tessedit_char_whitelist={WHITELIST}",
                )
            except pytesseract.TesseractError:
                continue
            secs = to_seconds(text.replace(" ", ""))
            if secs is None:
                continue
            votes[secs] += 1
            if votes[secs] >= quorum:
                return secs
    if not votes:
        return None
    return votes.most_common(1)[0][0]
