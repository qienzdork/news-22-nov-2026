#!/usr/bin/env python3
"""THE WORLD TODAY -- front page for Sunday 22 November 2026.

Draws a one-page newspaper front page summing up the day's world news
with Pillow (procedural drawing only, no external assets) and writes a
deterministic 1024x1024 RGB PNG to /output/entry.png (or $OUTPUT_PATH).

Lead story, verified from live news on 22 Nov 2026:
  Bahrain says Iran struck a civilian industrial site late on Saturday,
  as two oil tankers were hit in the Strait of Hormuz. The IRGC claimed
  it hit two US bases; no injuries were reported.
Also: COP31 climate talks in overtime in Antalya; Mexico captures
'El Chapo Isidro'; a magnitude 6.8 quake shakes Peru; Alcaraz faces
Zverev in the ATP Finals decider.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (16, 16, 16)
GREY = (96, 92, 84)
RED = (176, 32, 32)
SEA_TOP = (52, 108, 142)
SEA_BOT = (24, 66, 96)
LAND = (216, 196, 158)
SMOKE = (150, 148, 142)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    """Load a DejaVu font; fall back to Pillow's default bitmap font."""
    try:
        return ImageFont.truetype(FONT_DIR + name, size)
    except OSError:
        return ImageFont.load_default()


F_MAST = font("DejaVuSerif-Bold.ttf", 66)
F_DATE = font("DejaVuSans-Bold.ttf", 20)
F_KICK = font("DejaVuSans-Bold.ttf", 22)
F_HEAD = font("DejaVuSerif-Bold.ttf", 38)
F_STAND = font("DejaVuSerif.ttf", 22)
F_COL_HEAD = font("DejaVuSerif-Bold.ttf", 24)
F_BODY = font("DejaVuSerif.ttf", 18)
F_CAP = font("DejaVuSerif.ttf", 17)
F_SPORT = font("DejaVuSans-Bold.ttf", 22)
F_FOOT = font("DejaVuSans.ttf", 16)
F_MAP = font("DejaVuSans-Bold.ttf", 20)
F_MAP_BIG = font("DejaVuSans-Bold.ttf", 26)


def wrap(d, text, f, max_w):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def rule(d, x0, x1, y, width=2, fill=INK):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def text_block(d, x, y, lines, f, fill=INK, leading=1.28):
    """Draw wrapped lines; returns the y just below the last line."""
    size = f.size
    for line in lines:
        d.text((x, y), line, font=f, fill=fill)
        y += int(size * leading)
    return y


def draw_tanker(d, x, y, scale=1.0):
    """A black oil tanker silhouette with a red waterline, facing right."""
    hw, hh = int(190 * scale), int(26 * scale)
    hull = [(x, y), (x + hw - 24, y), (x + hw, y + hh // 2),
            (x + hw - 24, y + hh), (x, y + hh)]
    d.polygon(hull, fill=(12, 12, 12))
    d.line([(x, y + hh - 4), (x + hw - 8, y + hh - 4)],
           fill=RED, width=3)
    d.rectangle([x + 18, y - 16, x + 66, y], fill=(230, 228, 222))
    d.rectangle([x + 74, y - 10, x + 96, y], fill=(230, 228, 222))
    d.rectangle([x + 130, y - 22, x + 150, y], fill=(176, 32, 32))
    for cx in range(x + 8, x + hw - 30, 26):
        d.rectangle([cx, y - 6, cx + 14, y], fill=(70, 70, 70))


def draw_smoke(d, x, y):
    """A rising smoke plume: stacked grey puffs, darkest at the base."""
    puffs = [(0, 0, 46, (110, 108, 104)), (-16, -30, 56, (128, 126, 122)),
             (14, -58, 62, (150, 148, 142)), (-8, -92, 52, (172, 170, 164)),
             (10, -122, 40, (196, 194, 188))]
    for dx, dy, r, col in puffs:
        d.ellipse([x + dx - r // 2, y + dy - r // 2,
                   x + dx + r // 2, y + dy + r // 2], fill=col)


def draw_strait(d, x0, y0, x1, y1):
    """The Strait of Hormuz: sea between Iran (top) and Oman (bottom),
    two tankers under smoke, the world's oil tap under attack.
    Geometry is relative to the panel height so it stays inside the sea."""
    land_h = 62
    sea_top = y0 + land_h
    sea_bot = y1 - land_h
    d.rectangle([x0, y0, x1, y1], fill=SEA_TOP)
    bands = 10
    for i in range(bands):
        t = i / (bands - 1)
        col = tuple(int(SEA_TOP[c] + (SEA_BOT[c] - SEA_TOP[c]) * t)
                    for c in range(3))
        yy = y0 + (y1 - y0) * i // bands
        d.rectangle([x0, yy, x1, y0 + (y1 - y0) * (i + 1) // bands],
                    fill=col)
    d.rectangle([x0, y0, x1, y0 + land_h], fill=LAND)
    d.rectangle([x0, y1 - land_h, x1, y1], fill=LAND)
    d.text((x0 + 22, y0 + 14), "IRAN", font=F_MAP_BIG, fill=(60, 52, 40))
    d.text((x0 + 22, y1 - 52), "OMAN", font=F_MAP_BIG, fill=(60, 52, 40))
    d.text((x1 - 330, sea_top + 10), "STRAIT OF HORMUZ", font=F_MAP_BIG,
           fill=(255, 255, 255))
    d.text((x1 - 330, sea_top + 42), "one-fifth of the world's oil",
           font=F_MAP, fill=(220, 228, 234))
    # Tanker one, mid-channel, smoking.
    draw_tanker(d, x0 + 120, sea_top + 88, 1.0)
    draw_smoke(d, x0 + 200, sea_top + 80)
    # Tanker two, further east, smoking (kept left of the strait label).
    draw_tanker(d, x0 + 470, sea_top + 104, 0.85)
    draw_smoke(d, x0 + 530, sea_top + 96)
    # Dashed shipping lane through the strait.
    for sx in range(x0 + 10, x1 - 10, 34):
        d.line([(sx, sea_bot - 14), (sx + 18, sea_bot - 14)],
               fill=(255, 255, 255), width=3)
    # Compass rose, right of the sea.
    cx, cy = x1 - 52, sea_top + 88
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26],
              outline=(255, 255, 255), width=2)
    d.polygon([(cx, cy - 20), (cx + 7, cy + 8), (cx - 7, cy + 8)],
              fill=(255, 255, 255))
    d.text((cx - 7, cy + 12), "N", font=F_MAP, fill=(255, 255, 255))


def draw_masthead(d):
    """Nameplate, dateline bar and the lead headline + standfirst."""
    d.text(((W - d.textlength("THE WORLD TODAY", font=F_MAST)) / 2, 22),
           "THE WORLD TODAY", font=F_MAST, fill=INK)
    rule(d, 36, 988, 104, width=3)
    rule(d, 36, 988, 110, width=1)
    d.text((36, 122), "SUNDAY 22 NOVEMBER 2026", font=F_DATE, fill=INK)
    right = "WORLD NEWS  •  EDITION 1  •  $2.00"
    d.text((988 - d.textlength(right, font=F_DATE), 122), right,
           font=F_DATE, fill=INK)
    rule(d, 36, 988, 152, width=1)
    d.text((36, 168), "GULF CRISIS", font=F_KICK, fill=RED)
    head = ("BAHRAIN SAYS IRAN STRUCK INDUSTRIAL SITE "
            "AS TANKERS HIT IN HORMUZ")
    y = text_block(d, 36, 196, wrap(d, head, F_HEAD, 952), F_HEAD)
    stand = ("Iran struck a civilian industrial site in Bahrain late on "
             "Saturday, Bahrain said, as two oil tankers were hit in the "
             "Strait of Hormuz. Tehran's Revolutionary Guards claimed they "
             "hit two US bases. No injuries were reported.")
    text_block(d, 36, y + 8, wrap(d, stand, F_STAND, 952), F_STAND)
    # Recompute the standfirst end so the panel below can sit under it.
    end_y = y + 8 + len(wrap(d, stand, F_STAND, 952)) * int(22 * 1.28)
    return end_y


COLUMNS = [
    ("CLIMATE — ANTALYA",
     "COP31 talks run into overtime with no deal in sight",
     "Nations remain split over fossil fuels and funding; the EU "
     "wants a good deal — or no deal."),
    ("MEXICO",
     "Mexico captures 'El Chapo Isidro' in army raid",
     "Fausto Isidro Meza Flores was seized at a remote hideout in "
     "the latest cartel arrest."),
    ("PERU",
     "Strong quake shakes Peru's central Andes",
     "A magnitude 6.8 tremor struck the Andean region and was felt "
     "in Lima."),
]


def draw_column(d, x, y, width, kicker, headline, body):
    """One secondary story: red kicker, bold headline, short body."""
    d.text((x, y), kicker, font=F_KICK, fill=RED)
    y += 30
    y = text_block(d, x, y, wrap(d, headline, F_COL_HEAD, width),
                   F_COL_HEAD)
    y = text_block(d, x, y + 6, wrap(d, body, F_BODY, width), F_BODY)
    return y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    y = draw_masthead(d)

    py0 = y + 14
    py1 = py0 + 260
    draw_strait(d, 36, py0, 988, py1)
    cap = ("Two tankers were hit in the Strait of Hormuz as Bahrain "
           "blamed Iran for the fire. (Illustration)")
    text_block(d, 36, py1 + 8, wrap(d, cap, F_CAP, 952), F_CAP)
    rule(d, 36, 988, py1 + 40, width=2)

    col_y = py1 + 56
    col_w = 304
    for i, (kicker, headline, body) in enumerate(COLUMNS):
        draw_column(d, 36 + i * (col_w + 20), col_y, col_w,
                    kicker, headline, body)
        if i < 2:
            x = 36 + (i + 1) * (col_w + 20) - 10
            d.line([(x, col_y), (x, col_y + 190)], fill=GREY, width=1)

    sport_y = col_y + 212
    rule(d, 36, 988, sport_y, width=1)
    d.text((36, sport_y + 10), "SPORT", font=F_SPORT, fill=RED)
    d.text((36 + 96, sport_y + 10),
           "Alcaraz to face Zverev in ATP Finals title decider",
           font=F_SPORT, fill=INK)

    out = os.environ.get("OUTPUT_PATH")
    if not out and os.environ.get("MAKEFUN_OUTPUT_DIR"):
        out = os.path.join(os.environ["MAKEFUN_OUTPUT_DIR"], "entry.png")
    if not out:
        out = "/output/entry.png"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    img.save(out, format="PNG")


if __name__ == "__main__":
    main()
