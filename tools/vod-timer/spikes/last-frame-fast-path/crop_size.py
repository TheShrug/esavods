"""Crop *size* as a fraction of the frame -- the signal issue #71 wants.

#71 says a global size threshold cannot work because "genuinely different
layouts produce 279x83, 244x57, 164x50, 161x49, 143x44 and 116x64". Two of
those are not different layouts at all: 279x83 is the standard box at 720p
(confirmed by extra-720.csv, which lists exactly the two runs re-read at that
height) and 143x44 is the standard box at 360p. Once each box is divided by
its own frame width the spread collapses, and the one known-bad crop sits
clear of every good one with no layout key involved.
"""
W = {360: 640.0, 480: 854.0, 720: 1280.0}

# (label, crop w, crop h, assumed frame height, why that height)
CASES = [
    ("1p standard",              188, 57, 480, "the batch ran --height 480"),
    ("1p standard",              189, 57, 480, "same, +-1px calibration jitter"),
    ("1p, Dare to Dream",        279, 83, 720, "extra-720.csv: one of two runs re-read at 720p"),
    ("1p, We Love Katamari",     143, 44, 360, "480p would put it at x=0.39; 360p puts it in the cluster"),
    ("1p, Final Fantasy IX",     143, 44, 360, "same rectangle as We Love Katamari"),
    ("4x3-2p, Ghoul School",     164, 50, 480, "reconstructed from strip r2 -- see below"),
    ("4x3-2p, Where's Waldo",    161, 49, 480, "same layout"),
    ("no layout, Boardland",     244, 57, 480, ""),
    ("no layout, Closing Speech",116, 64, 480, "not a speedrun; kept for range"),
    ("BAD: FFIX Part 3",          58, 16, 480, "landed on EST. 24:00:00 -- the #71 case"),
    ("BAD: FFIX Part 3",          58, 16, 720, "same box if that manual read was 720p"),
]

print("%-28s %-9s %-7s  %-8s %s" % ("case", "crop", "frame", "w/frame", "why that height"))
for label, w, h, hgt, why in CASES:
    print("%-28s %-9s %5dp   %.3f    %s" % (label, "%dx%d" % (w, h), hgt, w / W[hgt], why))

good = [w / W[hgt] for label, w, h, hgt, _ in CASES if not label.startswith("BAD")]
bad = [w / W[hgt] for label, w, h, hgt, _ in CASES if label.startswith("BAD")]
print()
print("every crop that produced a correct read:  %.3f - %.3f of frame width" % (min(good), max(good)))
print("the one crop known to be wrong:           %.3f - %.3f" % (min(bad), max(bad)))
print("gap between them:                         %.3f  (a factor of %.1f)"
      % (min(good) - max(bad), min(good) / max(bad)))

# Reconstructing Ghoul School's frame height from the review strip, which is a
# 720p grab: the recorded crop is the glyph union padded by (w//12+5, h//5+3),
# so undoing the padding has to land back on the strip's own box.
gx, gw = 140, 197                      # glyph union on strip r2, at 720p
for hgt in (360, 480, 720):
    s = W[hgt] / 1280.0
    w0 = gw * s
    pad = int(w0) // 12 + 5
    print("\nGhoul School at %dp: glyph w %.0f, pad %d -> recorded x %.0f w %.0f (actual 77, 164)"
          % (hgt, w0, pad, gx * s - pad, w0 + 2 * pad))
