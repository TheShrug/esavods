"""Locate every HH:MM:SS on the review strips and sample its colour.

The Summer 2025 doc records that this overlay renders the timer orange while
running and green once stopped, and warns that a fast path must confirm the
clock has stopped. Colour is the only per-frame way to do that -- ticking
needs two frames of a clock that is still moving, which is exactly what the
end of a VOD does not have. So: is the colour separable, and does it sit
where the recorded crops say it does?
"""
import sys, json
sys.path.insert(0, "/app")
from pathlib import Path
from PIL import Image
from vodtimer import ocr


def swatch(img, box):
    """Mean RGB of the brightest tenth of the box -- the glyphs, not the plate."""
    c = img.convert("RGB").crop((box.x, box.y, box.x + box.w, box.y + box.h))
    px = list(c.getdata())
    if not px:
        return None
    px.sort(key=lambda p: p[0] + p[1] + p[2], reverse=True)
    top = px[: max(1, len(px) // 10)]
    n = len(top)
    return tuple(sum(p[i] for p in top) // n for i in range(3))


def label(rgb):
    r, g, b = rgb
    if r > 180 and g > 120 and b < 110 and r - b > 90:
        return "orange"
    if g > 130 and g - r > 40 and g - b > 40:
        return "green"
    if max(rgb) - min(rgb) < 45:
        return "white"
    return "other"


rows = []
for p in sorted(Path("/out/frames").glob("*.png")):
    with Image.open(p) as im:
        w, h = im.size
        hits = []
        for text, spans in ocr._lines_with_boxes(im):
            for m in ocr.TIMER_RE.finditer(text):
                boxes = [b for (a, z, b) in spans if a < m.end() and z > m.start()]
                if not boxes:
                    continue
                box = ocr._union(boxes)
                rgb = swatch(im, box)
                hits.append({"text": m.group(0), "box": box.as_tuple(),
                             "rgb": rgb, "colour": label(rgb)})
        rows.append({"frame": p.name, "size": [w, h], "hits": hits})

for r in rows:
    print("%-14s %-9s %s" % (r["frame"], "%dx%d" % tuple(r["size"]),
          "  ".join("%s@%s %s%s" % (h["text"], h["box"], h["colour"], h["rgb"])
                    for h in r["hits"]) or "(nothing timer-shaped)"))

Path("/spike/strips.json").write_text(json.dumps(rows, indent=1))
