#!/usr/bin/env python3
"""
THE WORLD IN ONE DAY -- Thursday 19 November 2026 (v2).

Draws a classic broadsheet front page as a 1024x1024 PNG with Pillow:
a masthead, one large hero scene, 15 illustrated story cards and a set of
numbered one-line briefs, plus markets, weather and a date-check box.
Every story was date-verified to Thursday 19 November 2026.

Deterministic: no randomness anywhere; two runs are byte-identical.
Output: entry.png inside MAKEFUN_OUTPUT_DIR (default /output).
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants

W, H = 1024, 1024
MARGIN = 22
CW = W - 2 * MARGIN  # content width = 980

PAPER = (247, 242, 227)
CARD_BG = (255, 253, 246)
INK = (26, 23, 18)
FAINT = (96, 87, 66)
RULE = (122, 109, 82)
RED = (163, 22, 33)
GOLD = (176, 141, 62)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


# ---------------------------------------------------------------- text utils

_probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def text_w(text, fnt):
    return _probe.textlength(text, font=fnt)


def fit_line(text, fnt, maxw):
    """Truncate text with an ellipsis so it fits maxw."""
    if text_w(text, fnt) <= maxw:
        return text
    ell = "…"
    while text and text_w(text + ell, fnt) > maxw:
        text = text[:-1]
    return text.rstrip() + ell


def wrap(text, fnt, maxw, max_lines):
    """Greedy word wrap into at most max_lines lines (last one ellipsised)."""
    words = text.split()
    lines = []
    cur = ""
    idx = 0
    while idx < len(words):
        word = words[idx]
        trial = word if not cur else cur + " " + word
        if text_w(trial, fnt) <= maxw:
            cur = trial
            idx += 1
        else:
            lines.append(cur)
            cur = ""
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if idx < len(words) and lines:
        lines[-1] = fit_line(lines[-1].rstrip(".") + "…", fnt, maxw)
    return lines


def centered(d, cx, y, text, fnt, fill=INK):
    d.text((cx - text_w(text, fnt) / 2, y), text, font=fnt, fill=fill)


# ---------------------------------------------------------------- scene kit

def sky_bands(d, w, h, top, bottom, bands=7):
    for i in range(bands):
        t = i / max(1, bands - 1)
        col = tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3))
        y0 = int(h * i / bands)
        y1 = int(h * (i + 1) / bands)
        d.rectangle([0, y0, w, y1], fill=col)


def sun(d, cx, cy, r, col=(250, 205, 90)):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)


def person(d, cx, cy, s, col=(30, 30, 34)):
    """Tiny figure: head + shoulders. cy is the shoulder line."""
    d.ellipse([cx - s * 0.32, cy - s * 0.95, cx + s * 0.32, cy - s * 0.31], fill=col)
    d.pieslice([cx - s * 0.62, cy - s * 0.35, cx + s * 0.62, cy + s * 0.85],
               start=180, end=360, fill=col)


def scene_hero(w, h):
    im = Image.new("RGB", (w, h), (28, 44, 78))
    d = ImageDraw.Draw(im)
    sky_bands(d, w, h, (26, 42, 78), (238, 138, 74))
    sun(d, int(w * 0.80), int(h * 0.34), 15)
    # Shenzhen skyline silhouette
    towers = [(0.02, 0.52, 0.10, 0.30), (0.12, 0.40, 0.07, 0.42),
              (0.21, 0.58, 0.09, 0.24), (0.66, 0.46, 0.08, 0.36),
              (0.76, 0.56, 0.10, 0.26), (0.88, 0.42, 0.09, 0.40)]
    for fx, fy, fw, fh in towers:
        d.rectangle([w * fx, h * fy, w * (fx + fw), h * (fy + fh)], fill=(18, 24, 40))
        for k in range(3):
            d.point((w * (fx + fw * (0.3 + 0.2 * k)), h * (fy + fh * 0.4)),
                    fill=(250, 220, 130))
    d.rectangle([0, h * 0.80, w, h], fill=(16, 20, 32))
    # three flags on poles behind the table
    pole_x = [int(w * 0.36), int(w * 0.50), int(w * 0.64)]
    for px in pole_x:
        d.line([px, h * 0.16, px, h * 0.78], fill=(210, 210, 215), width=2)
    fw_, fh_ = int(w * 0.115), int(h * 0.30)
    y0 = int(h * 0.16)
    # United States: stripes + blue canton
    x0 = pole_x[0]
    for i in range(7):
        col = (178, 34, 52) if i % 2 == 0 else (240, 240, 240)
        d.rectangle([x0, y0 + fh_ * i / 7, x0 + fw_, y0 + fh_ * (i + 1) / 7], fill=col)
    d.rectangle([x0, y0, x0 + fw_ * 0.45, y0 + fh_ * 0.54], fill=(60, 59, 110))
    for r in range(3):
        for c in range(4):
            d.point((x0 + 4 + c * 5, y0 + 4 + r * 5), fill=(255, 255, 255))
    # China: red field, gold stars
    x0 = pole_x[1]
    d.rectangle([x0, y0, x0 + fw_, y0 + fh_], fill=(222, 41, 16))
    d.polygon([(x0 + 8, y0 + 10), (x0 + 12, y0 + 20), (x0 + 2, y0 + 20)],
              fill=(255, 222, 0))
    for dx, dy in [(20, 5), (24, 12), (24, 20), (20, 27)]:
        d.ellipse([x0 + dx, y0 + dy, x0 + dx + 3, y0 + dy + 3], fill=(255, 222, 0))
    # Russia: white / blue / red
    x0 = pole_x[2]
    for i, col in enumerate([(245, 245, 245), (0, 57, 166), (213, 43, 30)]):
        d.rectangle([x0, y0 + fh_ * i / 3, x0 + fw_, y0 + fh_ * (i + 1) / 3], fill=col)
    # summit table + three leaders
    ty = int(h * 0.80)
    d.rectangle([w * 0.24, ty, w * 0.76, ty + h * 0.13], fill=(96, 62, 34))
    d.rectangle([w * 0.24, ty, w * 0.76, ty + 3], fill=(150, 108, 58))
    for fx in (0.36, 0.50, 0.64):
        person(d, int(w * fx), int(h * 0.80), int(h * 0.34), col=(12, 12, 16))
    return im


def scene_icj(w, h):
    im = Image.new("RGB", (w, h), (196, 208, 220))
    d = ImageDraw.Draw(im)
    d.rectangle([0, h * 0.78, w, h], fill=(150, 148, 138))
    cx = w // 2
    d.polygon([(cx - w * 0.34, h * 0.30), (cx + w * 0.34, h * 0.30), (cx, h * 0.10)],
              fill=(232, 228, 216))
    d.rectangle([cx - w * 0.34, h * 0.30, cx + w * 0.34, h * 0.36], fill=(210, 205, 192))
    for i in range(5):
        x = cx - w * 0.28 + i * w * 0.14
        d.rectangle([x, h * 0.36, x + w * 0.055, h * 0.74], fill=(238, 235, 226))
    d.rectangle([cx - w * 0.36, h * 0.74, cx + w * 0.36, h * 0.80], fill=(206, 201, 188))
    # scales of justice in front
    sx, sy = cx, int(h * 0.50)
    d.line([sx, sy - 16, sx, sy + 20], fill=(70, 60, 30), width=2)
    d.line([sx - 20, sy - 12, sx + 20, sy - 12], fill=(70, 60, 30), width=2)
    for ex in (sx - 20, sx + 20):
        d.line([ex, sy - 12, ex - 6, sy + 2], fill=(70, 60, 30), width=1)
        d.line([ex, sy - 12, ex + 6, sy + 2], fill=(70, 60, 30), width=1)
        d.arc([ex - 8, sy, ex + 8, sy + 12], start=0, end=180, fill=(70, 60, 30),
              width=2)
    d.rectangle([sx - 12, sy + 20, sx + 12, sy + 24], fill=(70, 60, 30))
    return im


def scene_ipo(w, h):
    im = Image.new("RGB", (w, h), (14, 26, 44))
    d = ImageDraw.Draw(im)
    for i in range(4):
        y = h * (0.2 + 0.2 * i)
        d.line([6, y, w - 6, y], fill=(38, 58, 88), width=1)
    pts = [(8, h * 0.80), (w * 0.25, h * 0.70), (w * 0.42, h * 0.74),
           (w * 0.60, h * 0.48), (w * 0.78, h * 0.36), (w - 10, h * 0.16)]
    d.line(pts, fill=(64, 220, 130), width=3)
    for px, py in pts:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(180, 255, 210))
    d.polygon([(w - 12, h * 0.16), (w - 24, h * 0.15), (w - 14, h * 0.27)],
              fill=(64, 220, 130))
    d.text((10, 8), "ANT", font=font(SANS_B, 17), fill=(240, 244, 250))
    d.text((52, 10), "+34%", font=font(SANS_B, 15), fill=(64, 220, 130))
    return im


def scene_pif(w, h):
    im = Image.new("RGB", (w, h), (70, 52, 66))
    d = ImageDraw.Draw(im)
    sky_bands(d, w, h, (58, 44, 70), (196, 110, 84))
    d.rectangle([0, h * 0.82, w, h], fill=(30, 24, 30))
    for fx, fh in [(0.04, 0.34), (0.16, 0.24), (0.80, 0.30), (0.90, 0.20)]:
        d.rectangle([w * fx, h * (0.82 - fh), w * (fx + 0.09), h * 0.82],
                    fill=(24, 20, 28))
    # the tower
    tx0, tx1 = w * 0.42, w * 0.58
    d.polygon([(tx0, h * 0.82), (tx0 + 4, h * 0.10), (tx1 - 4, h * 0.10),
               (tx1, h * 0.82)], fill=(36, 34, 44))
    for r in range(6):
        for c in range(3):
            if (r * 3 + c) % 3 != 0:
                d.rectangle([tx0 + 6 + c * 8, h * (0.18 + 0.1 * r),
                             tx0 + 10 + c * 8, h * (0.22 + 0.1 * r)],
                            fill=(250, 214, 130))
    # damage smoke
    for dx, dy, r in [(0.50, 0.16, 10), (0.55, 0.11, 13), (0.61, 0.07, 16)]:
        d.ellipse([w * dx - r, h * dy - r * 0.6, w * dx + r, h * dy + r * 0.6],
                  fill=(120, 112, 116))
    # missile trail
    d.arc([w * 0.58, -h * 0.30, w * 1.15, h * 0.42], start=95, end=175,
          fill=(255, 120, 80), width=2)
    return im


def scene_gaza(w, h):
    im = Image.new("RGB", (w, h), (168, 158, 142))
    d = ImageDraw.Draw(im)
    sky_bands(d, w, h, (150, 142, 128), (196, 186, 168))
    d.rectangle([0, h * 0.80, w, h], fill=(122, 108, 88))
    # broken buildings
    for fx, fh, fw in [(0.03, 0.44, 0.13), (0.80, 0.50, 0.15), (0.66, 0.30, 0.10)]:
        d.rectangle([w * fx, h * (0.80 - fh), w * (fx + fw), h * 0.80],
                    fill=(104, 96, 84))
        d.polygon([(w * fx, h * (0.80 - fh)), (w * (fx + fw * 0.5), h * (0.86 - fh)),
                   (w * (fx + fw), h * (0.80 - fh))], fill=(168, 158, 142))
    # tank
    ty = h * 0.66
    d.rectangle([w * 0.30, ty, w * 0.66, ty + h * 0.13], fill=(74, 74, 58))
    d.rectangle([w * 0.40, ty - h * 0.09, w * 0.58, ty], fill=(82, 82, 64))
    d.line([w * 0.58, ty - h * 0.05, w * 0.80, ty - h * 0.08], fill=(60, 60, 48),
           width=4)
    d.rectangle([w * 0.28, ty + h * 0.13, w * 0.68, ty + h * 0.20], fill=(56, 56, 44))
    for i in range(6):
        cx = w * (0.32 + 0.058 * i)
        d.ellipse([cx - 4, ty + h * 0.145, cx + 4, ty + h * 0.185], fill=(40, 40, 32))
    # smoke
    for dx, dy, r in [(0.86, 0.22, 9), (0.90, 0.15, 12)]:
        d.ellipse([w * dx - r, h * dy - r * 0.6, w * dx + r, h * dy + r * 0.6],
                  fill=(128, 122, 112))
    return im


def scene_bridge(w, h):
    im = Image.new("RGB", (w, h), (150, 190, 214))
    d = ImageDraw.Draw(im)
    d.rectangle([0, h * 0.62, w, h], fill=(52, 104, 156))
    for i in range(5):
        y = h * (0.70 + 0.06 * i)
        d.line([w * (0.05 + 0.07 * (i % 2)), y, w * (0.30 + 0.07 * (i % 2)), y],
               fill=(120, 180, 220), width=2)
    dy = h * 0.52
    d.rectangle([0, dy, w, dy + 5], fill=(70, 70, 76))
    for fx in (0.30, 0.66):
        d.rectangle([w * fx, h * 0.22, w * fx + 5, dy], fill=(70, 70, 76))
        d.line([w * fx + 2, h * 0.22, 4, dy], fill=(90, 90, 96), width=1)
        d.line([w * fx + 2, h * 0.22, w - 4, dy], fill=(90, 90, 96), width=1)
    # train
    for i in range(4):
        d.rectangle([w * (0.08 + 0.07 * i), dy - 9, w * (0.135 + 0.07 * i), dy - 1],
                    fill=(178, 34, 52))
    # explosion at mid-span
    cx, cy = int(w * 0.52), int(dy - 4)
    for ang in range(0, 360, 30):
        r1 = 4
        r2 = 13 + (4 if ang % 90 == 0 else 0)
        d.line([cx + r1 * math.cos(math.radians(ang)),
                cy + r1 * math.sin(math.radians(ang)),
                cx + r2 * math.cos(math.radians(ang)),
                cy + r2 * math.sin(math.radians(ang))],
               fill=(255, 150, 40), width=2)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 200, 70))
    d.ellipse([cx - 8, cy - 26, cx + 10, cy - 12], fill=(140, 134, 128))
    return im


def scene_vangogh(w, h):
    im = Image.new("RGB", (w, h), (16, 22, 54))
    d = ImageDraw.Draw(im)
    # swirling night sky
    for cx, cy, r in [(0.24, 0.30, 15), (0.55, 0.20, 11), (0.78, 0.38, 13)]:
        for rr in (r, int(r * 0.62)):
            d.arc([w * cx - rr, h * cy - rr, w * cx + rr, h * cy + rr],
                  start=20, end=320, fill=(90, 130, 200), width=2)
        sun(d, int(w * cx), int(h * cy), 4, col=(250, 224, 130))
    d.polygon([(0, h), (w * 0.30, h * 0.55), (w * 0.42, h)], fill=(10, 14, 34))
    d.rectangle([0, h * 0.86, w, h], fill=(24, 34, 44))
    for i in range(4):
        d.rectangle([w * (0.55 + 0.09 * i), h * 0.78, w * (0.58 + 0.09 * i), h * 0.86],
                    fill=(250, 214, 130))
    # gold frame + price tag
    d.rectangle([2, 2, w - 3, h - 3], outline=GOLD, width=4)
    tag = "SOLD $190M"
    f = font(SANS_B, 12)
    tw = text_w(tag, f)
    d.rectangle([w - tw - 16, h - 24, w - 6, h - 6], fill=(245, 240, 228))
    d.text((w - tw - 11, h - 21), tag, font=f, fill=RED)
    return im


def scene_gta(w, h):
    im = Image.new("RGB", (w, h), (240, 120, 90))
    d = ImageDraw.Draw(im)
    sky_bands(d, w, h, (120, 60, 140), (250, 150, 80))
    sun(d, int(w * 0.68), int(h * 0.52), 16, col=(255, 220, 130))
    d.rectangle([0, h * 0.78, w, h], fill=(30, 22, 40))
    # palms
    for fx, s in [(0.14, 1.0), (0.86, 0.8)]:
        bx, by = w * fx, h * 0.82
        d.line([bx, by, bx + 6 * s, by - h * 0.52 * s], fill=(20, 16, 26), width=3)
        tx, ty = bx + 6 * s, by - h * 0.52 * s
        for a in (-50, -20, 10, 40, 70):
            ex = tx + 20 * s * math.cos(math.radians(a + 180))
            ey = ty + 12 * s * math.sin(math.radians(a)) + 6
            d.line([tx, ty, ex, ey + 8], fill=(20, 16, 26), width=2)
    # sports car silhouette
    cy = h * 0.80
    d.polygon([(w * 0.30, cy), (w * 0.38, cy - h * 0.13), (w * 0.55, cy - h * 0.15),
               (w * 0.66, cy - h * 0.06), (w * 0.70, cy)], fill=(16, 12, 22))
    d.rectangle([w * 0.28, cy, w * 0.72, cy + h * 0.07], fill=(16, 12, 22))
    for fx in (0.36, 0.62):
        d.ellipse([w * fx - 7, cy + h * 0.03, w * fx + 7, cy + h * 0.03 + 14],
                  fill=(8, 6, 12), outline=(200, 200, 210), width=1)
    return im


def scene_cop(w, h):
    im = Image.new("RGB", (w, h), (178, 216, 200))
    d = ImageDraw.Draw(im)
    cx, cy, r = int(w * 0.42), int(h * 0.52), int(h * 0.34)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 130, 190))
    d.pieslice([cx - r, cy - r, cx + r, cy + r], start=300, end=60, fill=(96, 170, 96))
    d.pieslice([cx - r, cy - r, cx + r, cy + r], start=140, end=230,
               fill=(96, 170, 96))
    d.pieslice([cx - r, cy - r, cx + r, cy + r], start=80, end=120,
               fill=(110, 180, 100))
    # thermometer
    tx = int(w * 0.78)
    d.rectangle([tx - 3, h * 0.16, tx + 3, h * 0.66], outline=(90, 90, 90), width=2)
    d.rectangle([tx - 2, h * 0.30, tx + 2, h * 0.66], fill=RED)
    d.ellipse([tx - 8, h * 0.62, tx + 8, h * 0.62 + 16], fill=RED)
    # leaf
    d.pieslice([w * 0.60, h * 0.58, w * 0.78, h * 0.92], start=270, end=60,
               fill=(60, 150, 70))
    return im


def scene_boat(w, h):
    im = Image.new("RGB", (w, h), (150, 196, 224))
    d = ImageDraw.Draw(im)
    sun(d, int(w * 0.82), int(h * 0.24), 12)
    d.rectangle([0, h * 0.52, w, h], fill=(46, 102, 156))
    for row in range(3):
        y = h * (0.60 + 0.13 * row)
        pts = [(x, y + 3 * math.sin(x / 9.0 + row * 2)) for x in range(0, w, 6)]
        d.line(pts, fill=(130, 190, 230), width=2)
    # overloaded boat
    by = h * 0.52
    d.polygon([(w * 0.24, by), (w * 0.76, by), (w * 0.68, by + h * 0.16),
               (w * 0.32, by + h * 0.16)], fill=(120, 72, 40))
    for i in range(6):
        person(d, int(w * (0.32 + 0.07 * i)), int(by - 2), int(h * 0.20),
               col=(40, 34, 30))
    return im


def scene_prague(w, h):
    im = Image.new("RGB", (w, h), (186, 198, 214))
    d = ImageDraw.Draw(im)
    # spires
    for fx, fh in [(0.10, 0.52), (0.20, 0.40), (0.82, 0.46)]:
        x = w * fx
        d.rectangle([x, h * (0.72 - fh), x + w * 0.07, h * 0.72], fill=(70, 74, 86))
        d.polygon([(x - 2, h * (0.72 - fh)), (x + w * 0.035, h * (0.72 - fh) - 14),
                   (x + w * 0.07 + 2, h * (0.72 - fh))], fill=(50, 54, 66))
    d.rectangle([0, h * 0.72, w, h], fill=(120, 116, 108))
    # crowd with signs
    for row in range(2):
        for i in range(8):
            cx = int(w * (0.08 + 0.105 * i)) + (row * 7) % 11
            cy = int(h * (0.84 + 0.10 * row))
            d.ellipse([cx - 4, cy - 9, cx + 4, cy - 1], fill=(40, 38, 40))
            d.rectangle([cx - 5, cy - 1, cx + 5, cy + 6],
                        fill=(90 + (i % 3) * 40, 60, 70))
            if (i + row) % 3 == 0:
                d.line([cx + 6, cy - 2, cx + 6, cy - 18], fill=(60, 50, 40), width=1)
                d.rectangle([cx - 2, cy - 26, cx + 14, cy - 17], fill=(245, 242, 230),
                            outline=(120, 60, 60))
    return im


def scene_chatbot(w, h):
    im = Image.new("RGB", (w, h), (30, 34, 48))
    d = ImageDraw.Draw(im)
    # circuit traces
    for fx, fy in [(0.08, 0.2), (0.9, 0.3), (0.12, 0.8), (0.88, 0.78)]:
        d.ellipse([w * fx - 2, h * fy - 2, w * fx + 2, h * fy + 2],
                  fill=(90, 200, 220))
        d.line([w * fx, h * fy, w * 0.5, h * fy], fill=(60, 110, 130), width=1)
    # monitor
    mx0, my0, mx1, my1 = w * 0.24, h * 0.14, w * 0.76, h * 0.74
    d.rectangle([mx0, my0, mx1, my1], fill=(16, 20, 30), outline=(150, 160, 175),
                width=2)
    d.rectangle([w * 0.46, my1, w * 0.54, my1 + h * 0.10], fill=(150, 160, 175))
    d.rectangle([w * 0.36, my1 + h * 0.10, w * 0.64, my1 + h * 0.13],
                fill=(150, 160, 175))
    # chat bubbles
    d.rounded_rectangle([mx0 + 8, my0 + 8, mx0 + w * 0.30, my0 + h * 0.20], radius=4,
                        fill=(52, 120, 180))
    d.rounded_rectangle([mx1 - w * 0.30, my0 + h * 0.26, mx1 - 8, my0 + h * 0.38],
                        radius=4, fill=(222, 41, 16))
    for i in range(3):
        d.ellipse([mx0 + 12 + i * 8, my0 + h * 0.44, mx0 + 16 + i * 8,
                   my0 + h * 0.44 + 4], fill=(200, 210, 220))
    return im


def scene_gravity(w, h):
    im = Image.new("RGB", (w, h), (214, 206, 188))
    d = ImageDraw.Draw(im)
    # brick wall in the middle
    wx0, wx1 = w * 0.42, w * 0.58
    d.rectangle([wx0, h * 0.10, wx1, h * 0.90], fill=(168, 96, 74))
    for r in range(6):
        y = h * (0.10 + 0.133 * r)
        d.line([wx0, y, wx1, y], fill=(120, 66, 50), width=1)
        off = (r % 2) * w * 0.04
        d.line([wx0 + off + w * 0.04, y, wx0 + off + w * 0.04, y + h * 0.133],
               fill=(120, 66, 50), width=1)
    # wave arcs on both sides (passing through)
    for cx, flip in [(w * 0.20, 1), (w * 0.80, -1)]:
        for r in (8, 15, 22):
            box = [cx - r, h * 0.5 - r, cx + r, h * 0.5 + r]
            if flip == 1:
                d.arc(box, start=300, end=60, fill=(50, 90, 160), width=2)
            else:
                d.arc(box, start=120, end=240, fill=(50, 90, 160), width=2)
    person(d, int(w * 0.16), int(h * 0.86), int(h * 0.26), col=(52, 52, 58))
    person(d, int(w * 0.84), int(h * 0.86), int(h * 0.26), col=(52, 52, 58))
    return im


def scene_crabs(w, h):
    im = Image.new("RGB", (w, h), (240, 220, 170))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, h * 0.30], fill=(70, 140, 180))
    for i in range(3):
        y = h * (0.08 + 0.08 * i)
        pts = [(x, y + 2 * math.sin(x / 8.0 + i)) for x in range(0, w, 6)]
        d.line(pts, fill=(170, 220, 240), width=2)

    def crab(cx, cy, s):
        d.ellipse([cx - s, cy - s * 0.55, cx + s, cy + s * 0.55], fill=(206, 44, 32))
        for side in (-1, 1):
            for k in range(3):
                d.line([cx + side * s * 0.7, cy + (k - 1) * 2,
                        cx + side * s * 1.5, cy + (k - 1) * 4 + 3],
                       fill=(178, 36, 26), width=1)
            d.arc([cx + side * s * 1.1 - 4, cy - s * 0.9, cx + side * s * 1.1 + 4,
                   cy - s * 0.1], start=200, end=340, fill=(178, 36, 26), width=2)
        d.ellipse([cx - 3, cy - s * 0.5, cx - 1, cy - s * 0.5 + 2], fill=(30, 20, 20))
        d.ellipse([cx + 1, cy - s * 0.5, cx + 3, cy - s * 0.5 + 2], fill=(30, 20, 20))

    for fx, fy, s in [(0.16, 0.55, 9), (0.34, 0.72, 11), (0.52, 0.50, 8),
                      (0.64, 0.78, 12), (0.82, 0.58, 9), (0.26, 0.86, 8),
                      (0.74, 0.38, 7), (0.46, 0.90, 9)]:
        crab(int(w * fx), int(h * fy), s)
    return im


def scene_tanker(w, h):
    im = Image.new("RGB", (w, h), (164, 196, 216))
    d = ImageDraw.Draw(im)
    d.rectangle([0, h * 0.60, w, h], fill=(52, 104, 152))
    for row in range(2):
        y = h * (0.70 + 0.14 * row)
        pts = [(x, y + 3 * math.sin(x / 9.0 + row)) for x in range(0, w, 6)]
        d.line(pts, fill=(140, 195, 230), width=2)
    # hull + deck tanks
    hy = h * 0.56
    d.polygon([(w * 0.08, hy), (w * 0.92, hy), (w * 0.84, hy + h * 0.14),
               (w * 0.16, hy + h * 0.14)], fill=(40, 40, 46))
    d.rectangle([w * 0.08, hy + h * 0.05, w * 0.92, hy + h * 0.075], fill=(178, 34, 52))
    for i in range(3):
        d.rectangle([w * (0.20 + 0.18 * i), hy - h * 0.10, w * (0.34 + 0.18 * i), hy],
                    fill=(196, 200, 204), outline=(120, 124, 128))
    d.rectangle([w * 0.80, hy - h * 0.22, w * 0.88, hy], fill=(90, 94, 100))
    for dx, dy, r in [(0.84, 0.16, 8), (0.88, 0.10, 11)]:
        d.ellipse([w * dx - r, h * dy - r * 0.6, w * dx + r, h * dy + r * 0.6],
                  fill=(130, 128, 126))
    return im


def scene_han(w, h):
    im = Image.new("RGB", (w, h), (206, 214, 224))
    d = ImageDraw.Draw(im)
    d.rectangle([0, h * 0.80, w, h], fill=(156, 154, 144))
    cx = w // 2
    d.polygon([(cx - w * 0.32, h * 0.32), (cx + w * 0.32, h * 0.32), (cx, h * 0.13)],
              fill=(236, 232, 220))
    d.rectangle([cx - w * 0.32, h * 0.32, cx + w * 0.32, h * 0.38], fill=(214, 209, 196))
    for i in range(4):
        x = cx - w * 0.24 + i * w * 0.155
        d.rectangle([x, h * 0.38, x + w * 0.05, h * 0.76], fill=(240, 237, 228))
    d.rectangle([cx - w * 0.34, h * 0.76, cx + w * 0.34, h * 0.82], fill=(210, 205, 192))
    # taegeuk disc on the pediment
    r = 9
    d.ellipse([cx - r, h * 0.185 - r, cx + r, h * 0.185 + r], fill=(205, 46, 58))
    d.pieslice([cx - r, h * 0.185 - r, cx + r, h * 0.185 + r], start=90, end=270,
               fill=(0, 71, 160))
    # gavel
    gx, gy = int(w * 0.72), int(h * 0.60)
    d.line([gx - 10, gy + 10, gx + 8, gy - 8], fill=(120, 82, 40), width=3)
    d.rectangle([gx + 2, gy - 16, gx + 16, gy - 6], fill=(140, 98, 48))
    d.rectangle([gx - 12, gy + 14, gx + 12, gy + 18], fill=(120, 82, 40))
    return im


# ---------------------------------------------------------------- story data

HERO = {
    "kicker": "THE TOP STORY — SHENZHEN, CHINA · APEC SUMMIT",
    "headline": "Trump, Xi and Putin hold first trilateral summit in Shenzhen",
    "summary": "The three presidents met for 90 minutes at APEC and issued a joint "
               "“peace declaration” on nuclear risk, UN reform and energy — "
               "with Ukraine and Europe not in the room.",
    "caption": "DRAWN: the Shenzhen skyline, three flags, one table — the day's "
               "defining image.",
}

# (headline, summary, scene function) -- stories 2..16
CARDS = [
    ("World Court: Myanmar guilty of genocide",
     "First state-genocide verdict ever; reparations ordered.", scene_icj),
    ("Anthropic's record $81.3bn IPO debut",
     "Priced at $83, opened $111.50 — up 34% on a jittery day.", scene_ipo),
    ("Houthi strike damages Riyadh PIF Tower",
     "Missile hits the Saudi fund's HQ as the Iran war widens.", scene_pif),
    ("Israeli tanks enter central Gaza",
     "Hospital strike kills six, incl. a surgeon, near Nuseirat.", scene_gaza),
    ("Ukraine hits Crimean Bridge again",
     "Third strike in a week halts rail on the Kerch link.", scene_bridge),
    ("Van Gogh sells for record $190m",
     "Nazi-era provenance fails to dent a historic price.", scene_vangogh),
    ("GTA VI debuts to acclaim",
     "Rockstar's epic arrives after a 13-year wait since GTA V.", scene_gta),
    ("COP31 endgame: fossil split",
     "Phaseout wording, finance and 2035 target unresolved.", scene_cop),
    ("Boat sinks off Senegal; dozens missing",
     "About 100 people aboard; search and rescue under way.", scene_boat),
    ("Prague rallies for free media",
     "Hundreds of thousands protest a proposed media law.", scene_prague),
    ("N. Korea unveils AI chatbot",
     "“Fountain of Wisdom” shown at a Pyongyang IT show.", scene_chatbot),
    ("A message sent through a wall",
     "Physicists signal through brick — using gravity itself.", scene_gravity),
    ("Red crabs begin great march",
     "Millions cross Christmas Island toward the sea.", scene_crabs),
    ("LPG tanker sinks off Bulgaria",
     "Gas Husky downed by a projectile in the Black Sea.", scene_tanker),
    ("Seoul court clears ex-PM Han",
     "Martial-law conviction overturned by Supreme Court.", scene_han),
]

# (section tag for the first brief of a group, one-line text) -- stories 17..48
BRIEFS = [
    ("AMERICAS", "US targets $16bn EPA grants"),
    (None, "FDA sets up biologics safety council"),
    (None, "Kushner firm quietly bought defence shares"),
    (None, "El Salvador sends 2,500 troops to Haiti mission"),
    ("EUROPE", "Denmark–Greenland–US Arctic deal"),
    (None, "Estonia to shut Russia border posts in Dec"),
    (None, "General strike disrupts Spanish ports"),
    (None, "AI-run cyberattack hit EU in Oct, official says"),
    ("ASIA-PACIFIC", "Xi pitches deeper APEC ties"),
    (None, "Japan PM Takaichi holds talks with Putin"),
    (None, "Seoul's Lee renews call for Pyongyang talks"),
    (None, "Indonesia passes asset-forfeiture law"),
    (None, "One dead in Indonesian refinery blast"),
    ("MIDDLE EAST", "3 tankers ablaze in Hormuz"),
    (None, "Palestinian kids: third of child violations"),
    ("AFRICA", "Kenya picks US minerals consortium"),
    (None, "Nigeria Senate seeks justice for 37 miners"),
    (None, "RSF commander defects to Sudan's army"),
    (None, "Ebola response in DR Congo hit by insecurity"),
    ("ECONOMY", "UniCredit wins Berlin backing"),
    (None, "Walmart lifts outlook for third time"),
    (None, "Traders price in a December Fed hike"),
    (None, "Nvidia fades after earnings"),
    ("SCIENCE", "Data-centre CO2 may jump 70%"),
    (None, "Pregnancy brain changes may key MS cure"),
    ("CLIMATE", "Indonesia fire emissions spike"),
    (None, "Fiji declares El Niño drought disaster"),
    ("SPORT", "Chelsea edge PSG 1–0 in Women's CL"),
    (None, "France, Qatar win at U-17 World Cup"),
    (None, "Portugal top group in five-goal thriller"),
    ("CULTURE", "Actor Stacy Keach dies at 85"),
    (None, "Ramsay unveils Hollywood Walk of Fame star"),
]

DATE_CHECKS = [
    "Hegseth US–Venezuela pact — Wed 18 Nov",
    "Sanon guilty in Moïse plot — 18 Nov",
    "Google Gemini 4 “Neon” launch — 18 Nov",
    "Anthropic IPO priced $83 — 18 Nov",
    "Trump “dirty bomb” remark — 18 Nov",
    "Cyclone Akvan landfall — due Fri 20 Nov",
]

MARKET_LINES = [
    "THU CLOSES: Nikkei 59,444.21 +0.71% · Kospi 5,137.89 +1.39% · Hang Seng 22,841.62 "
    "−1.95% · ASX 8,730.4 −1.04% · STOXX −0.88% · FTSE −0.93% · DAX −1.06% · CAC −0.81%",
    "US WED CLOSE (REPORTED THU): S&P 7,323.63 −0.23% · Dow 50,198.17 −1.11% · Nasdaq "
    "24,429.88 +0.42% · EUR/USD 1.0967 · BTC $63,478.72 −2.18% · BRENT (THU) ~$93.50",
]

WEATHER_LINE = ("WEATHER — Cyclone Akvan nears India: 72,000 evacuated, landfall Fri "
                "20 Nov · Utah: 18in+ early snow · Fiji drought disaster · Indonesia's "
                "worst fire season in years")

N_STORIES = 1 + len(CARDS) + len(BRIEFS)
N_SCENES = 1 + len(CARDS)


# ---------------------------------------------------------------- page build

def draw_masthead(d):
    d.line([MARGIN, 10, W - MARGIN, 10], fill=INK, width=2)
    d.line([MARGIN, 13, W - MARGIN, 13], fill=INK, width=1)
    centered(d, W // 2, 17, "THE WORLD IN ONE DAY", font(SERIF_B, 46))
    centered(d, W // 2, 67, "THURSDAY 19 NOVEMBER 2026", font(SANS_B, 31), fill=RED)
    strap = "%d STORIES · 5 CONTINENTS · ONE FRONT PAGE" % N_STORIES
    centered(d, W // 2, 103, strap, font(SANS_B, 13), fill=FAINT)
    centered(d, W // 2, 119, fit_line(WEATHER_LINE, font(SANS, 11), CW),
             font(SANS, 11), fill=FAINT)
    d.line([MARGIN, 135, W - MARGIN, 135], fill=INK, width=3)


def draw_hero(d, page):
    y = 141
    scene = scene_hero(500, 140)
    page.paste(scene, (MARGIN, y))
    d.rectangle([MARGIN, y, MARGIN + 500, y + 140], outline=RULE, width=1)
    d.text((MARGIN, y + 143), fit_line(HERO["caption"], font(SANS, 11), 500),
           font=font(SANS, 11), fill=FAINT)
    x = MARGIN + 516
    tw = W - MARGIN - x
    d.rectangle([x, y + 2, x + 26, y + 28], fill=RED)
    d.text((x + 8, y + 7), "1", font=font(SANS_B, 15), fill=(255, 255, 255))
    d.text((x + 34, y + 8), HERO["kicker"], font=font(SANS_B, 12), fill=RED)
    hy = y + 32
    for line in wrap(HERO["headline"], font(SERIF_B, 26), tw, 3):
        d.text((x, hy), line, font=font(SERIF_B, 26), fill=INK)
        hy += 28
    sy = y + 120
    for line in wrap(HERO["summary"], font(SANS, 14), tw, 3):
        d.text((x, sy), line, font=font(SANS, 14), fill=INK)
        sy += 17


def draw_cards(d, page):
    y0 = 313
    cols = 5
    gap_x, gap_y = 8, 6
    card_w = (CW - (cols - 1) * gap_x) // cols  # 189
    card_h = 152
    scene_w, scene_h = card_w - 16, 90
    num = 2
    for idx, (headline, summary, scene_fn) in enumerate(CARDS):
        r, c = divmod(idx, cols)
        x = MARGIN + c * (card_w + gap_x)
        y = y0 + r * (card_h + gap_y)
        d.rectangle([x, y, x + card_w, y + card_h], fill=CARD_BG, outline=RULE,
                    width=1)
        scene = scene_fn(scene_w, scene_h)
        page.paste(scene, (x + 8, y + 5))
        label = str(num)
        chip_w = 8 + text_w(label, font(SANS_B, 11))
        d.rectangle([x + 8, y + 5, x + 8 + chip_w, y + 22], fill=RED)
        d.text((x + 12, y + 7), label, font=font(SANS_B, 11), fill=(255, 255, 255))
        ty = y + 99
        for line in wrap(headline, font(SERIF_B, 13), card_w - 14, 2):
            d.text((x + 7, ty), line, font=font(SERIF_B, 13), fill=INK)
            ty += 14
        sy = y + 128
        for line in wrap(summary, font(SANS, 11), card_w - 14, 2):
            d.text((x + 7, sy), line, font=font(SANS, 11), fill=FAINT)
            sy += 12
        num += 1


def draw_briefs(d):
    y = 784
    d.text((MARGIN, y), "IN BRIEF — THE REST OF THURSDAY", font=font(SANS_B, 12),
           fill=INK)
    d.line([MARGIN, y + 16, W - MARGIN, y + 16], fill=RULE, width=1)
    y += 22
    cols_x = [MARGIN, MARGIN + 331, MARGIN + 662]
    col_w = 318
    groups = [BRIEFS[:11], BRIEFS[11:22], BRIEFS[22:]]
    num = 2 + len(CARDS)  # hero = 1, cards = 2..16, first brief = 17
    f_num = font(SANS_B, 12)
    f_txt = font(SANS, 12)
    f_tag = font(SANS_B, 12)
    for ci, group in enumerate(groups):
        x = cols_x[ci]
        cy = y
        for tag, text in group:
            label = "%d." % num
            d.text((x, cy), label, font=f_num, fill=RED)
            tx = x + text_w(label, f_num) + 5
            if tag:
                d.text((tx, cy), tag + " — ", font=f_tag, fill=INK)
                tx += text_w(tag + " — ", f_tag)
            d.text((tx, cy), fit_line(text, f_txt, x + col_w - tx), font=f_txt,
                   fill=INK)
            cy += 13
            num += 1


def draw_datecheck(d):
    y = 952
    d.rectangle([MARGIN, y, W - MARGIN, y + 36], fill=(250, 236, 224), outline=RED,
                width=1)
    d.text((MARGIN + 8, y + 2), "DATE CHECK — NOT 19 NOVEMBER NEWS:",
           font=font(SANS_B, 10), fill=RED)
    f_i = font(SANS, 10)
    cols_x = [MARGIN + 8, MARGIN + 338, MARGIN + 668]
    for i, item in enumerate(DATE_CHECKS):
        cx = cols_x[i % 3]
        cy = y + 14 + (i // 3) * 11
        d.text((cx, cy), fit_line(item, f_i, MARGIN + CW - cx - 4), font=f_i,
               fill=INK)


def draw_bottom_strip(d):
    y = 991
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=2)
    f = font(SANS, 10)
    yy = y + 4
    for line in MARKET_LINES:
        centered(d, W // 2, yy, fit_line(line, f, CW), f, fill=INK)
        yy += 11
    stats = ("%d STORIES · 10 SECTIONS · %d DRAWN SCENES · EVERY STORY DATE-VERIFIED "
             "TO THURSDAY 19 NOVEMBER 2026" % (N_STORIES, N_SCENES))
    centered(d, W // 2, yy, fit_line(stats, font(SANS_B, 10), CW), font(SANS_B, 10),
             fill=RED)


def main():
    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)
    draw_masthead(d)
    draw_hero(d, page)
    draw_cards(d, page)
    draw_briefs(d)
    draw_datecheck(d)
    draw_bottom_strip(d)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    page.save(os.path.join(out_dir, "entry.png"), format="PNG")


if __name__ == "__main__":
    main()
