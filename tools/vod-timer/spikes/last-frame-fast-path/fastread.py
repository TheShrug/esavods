"""A last-frame fast path: pinned crop, no calibration, plus a colour gate.

Three departures from the slow pipeline:

  * The crop is a *fraction of the frame*, not a pixel rectangle. Every
    single-player crop the Summer 2025 batch recorded lands on the same
    fraction once you account for the download height varying, so a rectangle
    in pixels would have been three different rectangles for no reason.

  * There is no calibration, because calibration needs a ticking clock and the
    end of a VOD does not have one. That is obstacle 1 in #69.

  * The clock's *colour* is read alongside its digits. This overlay renders the
    timer orange while running and green once stopped, and the estimate in
    white. Colour is the only stopped-signal available from a single frozen
    frame -- ticking needs two frames of a clock that is still moving.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, "/app")

from PIL import Image

from vodtimer import ocr, video

# x, y, w, h as fractions of the frame. Derived in spike/crops_norm.py from the
# 41 single-player crops the batch recorded, which span x 0.516-0.532 and
# y 0.759-0.803 with a bottom edge at 0.922. Padded outwards from that, and
# stopped short of 0.93 vertically because the donation bar starts just below.
REGION = (0.505, 0.745, 0.260, 0.180)

# Glyph colours, measured off the review strips in spike/strip_scan.py.
# Orange and green are 130 apart in RGB space; the gate is nowhere near tight.
COLOURS = {
    "running": (243, 189, 56),
    "stopped": (107, 186, 137),
    "static": (243, 243, 243),     # the estimate, and a clock reset to 0:00:00
}
COLOUR_TOL = 60
MIN_GLYPH_PX = 120                 # below this the region holds no big digits


def region_box(size: tuple[int, int]) -> ocr.Box:
    W, H = size
    fx, fy, fw, fh = REGION
    return ocr.Box(int(W * fx), int(H * fy), int(W * fw), int(H * fh))


def classify_colour(img: Image.Image, box: ocr.Box) -> tuple[str, dict]:
    crop = img.convert("RGB").crop(box.crop_box())
    counts = {k: 0 for k in COLOURS}
    for r, g, b in crop.getdata():
        for name, (cr, cg, cb) in COLOURS.items():
            if abs(r - cr) < COLOUR_TOL and abs(g - cg) < COLOUR_TOL and abs(b - cb) < COLOUR_TOL:
                counts[name] += 1
                break
    best = max(counts, key=counts.get)
    if counts[best] < MIN_GLYPH_PX:
        return "none", counts
    return best, counts


def read_frames(frames: list[Path]) -> list[dict]:
    out = []
    for f in frames:
        with Image.open(f) as img:
            box = region_box(img.size)
            colour, counts = classify_colour(img, box)
        out.append({
            "frame": f.name,
            "box": box.as_tuple(),
            "value": ocr.read_box(f, box),
            "colour": colour,
            "counts": counts,
        })
    return out


def verdict(reads: list[dict], estimate: float | None, duration: int | None = None) -> dict:
    """One answer from a handful of frozen frames, and how much to trust it.

    Deliberately strict. A frozen overlay gives the *same pixels* to every
    frame, so agreement between frames is not independent evidence the way the
    slow path's ramp is -- it only proves tesseract is deterministic, which we
    already knew. The checks that carry weight here are the ones that do not
    come from the digits: the colour, and the estimate.
    """
    values = [r["value"] for r in reads if r["value"] is not None]
    colours = [r["colour"] for r in reads]
    res = {
        "value": None, "time": None, "verdict": "reject", "why": [],
        "frames": len(reads), "read": len(values),
        "colours": {c: colours.count(c) for c in set(colours)},
    }
    if not values:
        res["why"].append("nothing timer-shaped in the pinned region")
        return res

    top = max(set(values), key=values.count)
    res["value"], res["time"] = top, ocr.fmt(top)
    res["agree"] = values.count(top)

    if values.count(top) < len(values):
        res["why"].append("frames disagree (%s)" % sorted(set(values)))

    stopped = colours.count("stopped")
    if stopped == 0:
        res["why"].append("the clock is not green in any frame: it never stopped on camera")
        return res
    if stopped < len(reads):
        res["why"].append("the clock is green in only %d of %d frames" % (stopped, len(reads)))

    if estimate and abs(top - estimate) < 1.0:
        res["why"].append("reads exactly the estimate (#65)")
        return res
    if duration and top > duration + 1:
        res["why"].append("longer than the video itself")
        return res
    if top < 60:
        res["why"].append("under a minute")
        return res

    res["verdict"] = "accept" if values.count(top) == len(values) == len(reads) else "check"
    return res
