#!/usr/bin/env python3
"""Draw the news-image-20261118 entry: one 1024x1024 infographic of the world
news of Wednesday 18 November 2026. Deterministic: no randomness, no
timestamps, no network. All text and graphics are drawn with PIL from the
verified facts in RESEARCH.md. Run: python3 gen_image.py [out.png]"""

import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 232)      # warm off-white
CARD = (255, 255, 255)
INK = (22, 22, 26)
NAVY = (27, 42, 74)
RED = (180, 35, 24)
GRAY = (96, 96, 100)
LIGHT_LINE = (216, 210, 192)

F = {
    "serif_b": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "sans_b": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
}


def font(kind, size):
    return ImageFont.truetype(F[kind], size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_headline(draw, text, sizes, max_w):
    """Largest serif-bold size from `sizes` that fits max_w."""
    for size in sizes:
        fnt = font("serif_b", size)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt
    return font("serif_b", sizes[-1])


def fit_summary(draw, text, sizes, max_w, max_lines=2):
    """Largest sans size from `sizes` whose wrap fits in max_lines lines."""
    for size in sizes:
        fnt = font("sans", size)
        if len(wrap(draw, text, fnt, max_w)) <= max_lines:
            return fnt
    return font("sans", sizes[-1])


def draw_tracked(draw, xy, text, fnt, fill, tracking=3):
    """Draw text with extra letter spacing (for kickers)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def rounded(draw, box, radius, **kw):
    draw.rounded_rectangle(box, radius=radius, **kw)


# ---------------------------------------------------------------- stories
LEAD = {
    "kicker": "MIDDLE EAST · GULF — LEAD STORY",
    "headline": "GULF FLARES AGAIN",
    "summary": (
        "Bahrain gave the all-clear after fresh threat alerts, Kuwait's "
        "defences intercepted drones overnight, and US jets hit a missile "
        "site on Iran's Qeshm Island."
    ),
    "source": "REUTERS · AL JAZEERA",
    "color": RED,
}

CARDS = [
    {
        "kicker": "DIPLOMACY",
        "headline": "APEC OPENS IN SHENZHEN",
        "summary": "Xi keynotes as leaders gather in Shenzhen; Trump and Putin arrive "
                   "ahead of Thursday's first three-way summit.",
        "source": "AJU PRESS · CDS WORLD",
        "color": (30, 58, 95),
        "icon": "summit",
    },
    {
        "kicker": "BUSINESS",
        "headline": "NVIDIA'S RECORD QUARTER",
        "summary": "Record $115.8bn quarter, up 103%; the board will not reinstate "
                   "founder Jensen Huang as CEO.",
        "source": "REUTERS · COINTELEGRAPH",
        "color": (22, 101, 52),
        "icon": "chart",
    },
    {
        "kicker": "UNITED STATES",
        "headline": "27 YEARS FOR TRUMP PLOT",
        "summary": "Asif Merchant, an Iranian operative, got 330 months for a plot to "
                   "kill Trump and other US officials.",
        "source": "REUTERS · US JUSTICE DEPT",
        "color": (51, 65, 85),
        "icon": "scales",
    },
    {
        "kicker": "FINANCE",
        "headline": "DEUTSCHE BANK FILES LEAK",
        "summary": "Leaked files show the bank kept Russian oligarch clients despite "
                   "warnings; shares fell 6%.",
        "source": "REUTERS · FINANCIAL TIMES",
        "color": (180, 83, 9),
        "icon": "bank",
    },
    {
        "kicker": "RUSSIA",
        "headline": "MILITARY PLANE CRASHES",
        "summary": "An An-12 transport crashed in Siberia, killing all on board; the "
                   "toll is disputed.",
        "source": "CNN · REUTERS",
        "color": (71, 85, 105),
        "icon": "plane",
    },
    {
        "kicker": "UKRAINE · WAR",
        "headline": "WORST YEAR FOR CIVILIANS",
        "summary": "UN: 372 civilians killed in October; 2026's toll already tops all "
                   "of 2025.",
        "source": "UN NEWS · OHCHR",
        "color": (109, 40, 217),
        "icon": "candle",
    },
]


# ---------------------------------------------------------------- icons
def draw_icon(draw, kind, box, color):
    """Draw a simple white geometric glyph on a coloured rounded square."""
    x0, y0, x1, y1 = box
    rounded(draw, box, 10, fill=color)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    w = (255, 255, 255)
    if kind == "summit":
        for dx, dy in ((-16, 4), (0, -8), (16, 4)):
            draw.ellipse([cx + dx - 7, cy + dy - 7, cx + dx + 7, cy + dy + 7],
                         fill=w)
        draw.line([(cx - 16, cy + 4), (cx, cy - 8)], fill=w, width=2)
        draw.line([(cx, cy - 8), (cx + 16, cy + 4)], fill=w, width=2)
    elif kind == "chart":
        for i, h in enumerate((10, 18, 26)):
            bx = cx - 18 + i * 13
            draw.rectangle([bx, cy + 14 - h, bx + 8, cy + 14], fill=w)
        draw.line([(cx - 20, cy - 16), (cx + 20, cy - 16)], fill=w, width=2)
        draw.polygon([(cx + 14, cy - 20), (cx + 22, cy - 16), (cx + 14, cy - 12)],
                     fill=w)
    elif kind == "scales":
        draw.line([(cx, cy - 16), (cx, cy + 16)], fill=w, width=2)
        draw.line([(cx - 16, cy - 12), (cx + 16, cy - 12)], fill=w, width=2)
        for dx in (-16, 16):
            draw.line([(cx + dx, cy - 12), (cx + dx - 7, cy + 2)], fill=w, width=2)
            draw.line([(cx + dx, cy - 12), (cx + dx + 7, cy + 2)], fill=w, width=2)
            draw.arc([cx + dx - 7, cy - 2, cx + dx + 7, cy + 8], 0, 180,
                     fill=w, width=2)
        draw.rectangle([cx - 8, cy + 14, cx + 8, cy + 18], fill=w)
    elif kind == "bank":
        draw.polygon([(cx - 20, cy - 12), (cx, cy - 20), (cx + 20, cy - 12)],
                     fill=w)
        for dx in (-16, -5, 6, 17):
            draw.rectangle([cx + dx - 3, cy - 8, cx + dx + 3, cy + 12], fill=w)
        draw.rectangle([cx - 22, cy + 12, cx + 22, cy + 17], fill=w)
    elif kind == "plane":
        draw.polygon([(cx - 18, cy + 12), (cx + 2, cy - 14), (cx + 8, cy - 14),
                      (cx + 18, cy - 2), (cx + 6, cy + 2), (cx + 2, cy + 10)],
                     fill=w)
        draw.polygon([(cx - 12, cy + 14), (cx - 2, cy + 6), (cx + 4, cy + 14)],
                     fill=w)
        for dx, dy in ((-20, -16), (-12, -20), (-24, -8)):
            draw.ellipse([cx + dx - 2, cy + dy - 2, cx + dx + 2, cy + dy + 2],
                         fill=(220, 220, 220))
    elif kind == "candle":
        draw.rectangle([cx - 6, cy - 2, cx + 6, cy + 18], fill=w)
        draw.ellipse([cx - 6, cy - 14, cx + 6, cy - 2], fill=(245, 197, 66))
        draw.ellipse([cx - 3, cy - 10, cx + 3, cy - 4], fill=(229, 87, 46))


def draw_gulf_panel(draw, box):
    """Geometric illustration: a radar station watching drones over the Gulf
    at night."""
    x0, y0, x1, y1 = box
    night = (13, 27, 62)
    sea = (23, 68, 104)
    draw.rectangle(box, fill=night)
    # stars
    for sx, sy in ((30, 18), (90, 34), (150, 14), (210, 30), (260, 16),
                   (60, 60), (180, 52), (240, 58), (120, 70)):
        draw.ellipse([x0 + sx - 2, y0 + sy - 2, x0 + sx + 2, y0 + sy + 2],
                     fill=(255, 255, 255))
    # moon
    draw.ellipse([x1 - 58, y0 + 12, x1 - 24, y0 + 46], fill=(240, 230, 190))
    draw.ellipse([x1 - 52, y0 + 18, x1 - 30, y0 + 40], fill=night)
    # sea
    draw.rectangle([x0, y0 + 168, x1, y1], fill=sea)
    for wx in range(x0 + 10, x1 - 10, 36):
        draw.arc([wx, y0 + 178, wx + 24, y0 + 190], 180, 360,
                 fill=(255, 255, 255), width=2)
        draw.arc([wx + 10, y0 + 206, wx + 32, y0 + 218], 180, 360,
                 fill=(255, 255, 255), width=2)
    # radar tower on the shore
    tx = x0 + 70
    draw.rectangle([tx - 4, y0 + 92, tx + 4, y0 + 168], fill=(200, 200, 200))
    draw.polygon([(tx - 14, y0 + 92), (tx + 14, y0 + 92), (tx, y0 + 74)],
                 fill=(200, 200, 200))
    # radar sweep arcs
    for r in (26, 44, 62):
        draw.arc([tx - r, y0 + 92 - r, tx + r, y0 + 92 + r], 270, 360,
                 fill=(120, 200, 120), width=2)
    # drones as small crosses with red dots
    for dx, dy in ((190, 60), (230, 96), (160, 110)):
        draw.line([(dx - 8, dy), (dx + 8, dy)], fill=(255, 255, 255), width=2)
        draw.line([(dx, dy - 8), (dx, dy + 8)], fill=(255, 255, 255), width=2)
        draw.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=(229, 87, 46))
    # interceptor burst
    bx, by = x0 + 250, y0 + 130
    pts = []
    for i in range(12):
        ang = math.pi * i / 6
        r = 16 if i % 2 == 0 else 7
        pts.append((bx + r * math.cos(ang), by + r * math.sin(ang)))
    draw.polygon(pts, fill=(245, 166, 38))
    draw.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=(255, 236, 180))
    # caption
    draw.text((x0 + 10, y1 - 24), "THE GULF, OVERNIGHT", font=font("sans_b", 12),
              fill=(255, 255, 255))


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 28  # margin
    CW = W - 2 * M  # 968

    # ---- masthead
    y = 26
    draw_tracked(d, (M, y), "WORLD NEWS  ·  ONE DAY IN ONE IMAGE",
                 font("sans_b", 15), RED, tracking=3)
    y += 30
    date_text = "WEDNESDAY, 18 NOVEMBER 2026"
    date_fnt = font("serif_b", 54)
    for _size in (54, 52, 50, 48, 46, 44):
        date_fnt = font("serif_b", _size)
        if d.textlength(date_text, font=date_fnt) <= CW:
            break
    d.text((M, y), date_text, font=date_fnt, fill=NAVY)
    y += 74
    d.text((M, y), "Seven stories that defined the day — verified against independent reporting.",
           font=font("sans", 17), fill=GRAY)
    y += 30
    d.line([(M, y), (W - M, y)], fill=INK, width=3)
    d.line([(M, y + 6), (W - M, y + 6)], fill=INK, width=1)

    # ---- lead story
    ly = 168
    lh = 240
    d.text((M, ly), LEAD["kicker"], font=font("sans_b", 14), fill=RED)
    lhf = fit_headline(d, LEAD["headline"], [46, 44, 42], 596)
    d.text((M, ly + 24), LEAD["headline"], font=lhf, fill=INK)
    sum_lines = wrap(d, LEAD["summary"], font("sans", 19), 596)
    sy = ly + 84
    for ln in sum_lines:
        d.text((M, sy), ln, font=font("sans", 19), fill=INK)
        sy += 25
    d.text((M, ly + lh - 24), LEAD["source"], font=font("sans_b", 13), fill=GRAY)
    draw_gulf_panel(d, (648, ly, W - M, ly + lh))

    # ---- divider
    dy = ly + lh + 14
    d.line([(M, dy), (W - M, dy)], fill=LIGHT_LINE, width=2)

    # ---- grid of six cards
    gy = dy + 16
    card_w, card_h, gap = 476, 152, 16
    for i, c in enumerate(CARDS):
        row, col = divmod(i, 2)
        x = M + col * (card_w + gap)
        yy = gy + row * (card_h + gap)
        rounded(d, (x, yy, x + card_w, yy + card_h), 8, fill=CARD,
                outline=LIGHT_LINE, width=1)
        d.rectangle([x + 8, yy, x + card_w - 8, yy + 5], fill=c["color"])
        draw_icon(d, c["icon"], (x + 14, yy + 16, x + 70, yy + 72), c["color"])
        d.text((x + 82, yy + 16), c["kicker"], font=font("sans_b", 12),
               fill=c["color"])
        hf = fit_headline(d, c["headline"], [22, 21, 20, 19, 18], card_w - 96)
        d.text((x + 82, yy + 34), c["headline"], font=hf, fill=INK)
        sf = fit_summary(d, c["summary"], [15, 14, 13], card_w - 28)
        s_lines = wrap(d, c["summary"], sf, card_w - 28)
        syy = yy + 82
        for ln in s_lines[:3]:
            d.text((x + 14, syy), ln, font=sf, fill=INK)
            syy += 19
        d.text((x + 14, yy + card_h - 20), c["source"],
               font=font("sans_b", 11), fill=GRAY)

    # ---- footer
    fy = gy + 3 * card_h + 2 * gap + 14
    d.line([(M, fy), (W - M, fy)], fill=INK, width=2)
    f1 = ("Sources: Reuters · Al Jazeera · Aju Press · Cointelegraph · CNN · "
          "Financial Times · UN News · US Justice Department")
    f2 = ("Every fact checked against at least two independent reports. "
          "News of Wednesday, 18 November 2026.")
    d.text((M, fy + 10), f1, font=font("sans", 13), fill=INK)
    d.text((M, fy + 30), f2, font=font("sans", 13), fill=GRAY)
    return img


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    im = build()
    im.save(out, optimize=True)
    print(f"saved {out}: {im.size} {os.path.getsize(out)} bytes")
