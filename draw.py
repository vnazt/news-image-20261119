# THE WORLD IN ONE DAY - front page for Thursday 19 November 2026.
# Fresh drawing program (v3): fewer stories, much bigger illustrations.
# Writes entry.png beside this file and to $MAKEFUN_OUTPUT_DIR if set.
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")

SANS = "DejaVuSans.ttf"
SANSB = "DejaVuSans-Bold.ttf"
SERIFB = "DejaVuSerif-Bold.ttf"

_font_cache = {}


def F(name, size):
    key = (name, size)
    if key not in _font_cache:
        # Raises OSError if the bundled font file is missing - by design,
        # the wrapper then falls back to the bundled verified image.
        _font_cache[key] = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    return _font_cache[key]


PAPER = (247, 241, 227)
CARD_BG = (255, 253, 246)
INK = (26, 23, 18)
RED = (179, 32, 44)
MUTED = (107, 98, 82)
GOLD = (217, 164, 65)
DARK = (30, 24, 20)

W = 1024
M = 36
CW = W - 2 * M  # 952 content width

_probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def tw(s, f):
    return _probe.textlength(s, font=f)


def fit_size(text, name, max_w, start, floor=9):
    size = start
    while size > floor and tw(text, F(name, size)) > max_w:
        size -= 1
    return F(name, size)


def wrap(text, f, max_w):
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if tw(trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def fit_lines(text, f, max_w, max_lines):
    """Wrap text into at most max_lines lines, ellipsising the tail."""
    lines = wrap(text, f, max_w)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    last = lines[-1]
    while last and tw(last + " …", f) > max_w:
        last = last[:-1]
    lines[-1] = last.rstrip() + " …"
    return lines


def fit_one(text, f, max_w):
    if tw(text, f) <= max_w:
        return text
    t = text
    while t and tw(t + "…", f) > max_w:
        t = t[:-1]
    return t.rstrip() + "…"


def fit_lines_shrink(text, name, max_w, max_lines, start, floor):
    """Largest font in start..floor whose wrap fits max_lines. Never ellipsises."""
    for size in range(start, floor - 1, -1):
        f = F(name, size)
        lines = wrap(text, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
    f = F(name, floor)
    return f, wrap(text, f, max_w)[:max_lines]


def fit_one_shrink(text, name, max_w, start, floor):
    """Largest font in start..floor that fits text on one line. Never ellipsises."""
    for size in range(start, floor - 1, -1):
        f = F(name, size)
        if tw(text, f) <= max_w:
            return f, text
    return F(name, floor), text


def vgrad(w, h, stops):
    """Vertical gradient image. stops = [(pos0to1, (r,g,b)), ...]"""
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        p = y / max(1, h - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= p <= p1:
                t = 0 if p1 == p0 else (p - p0) / (p1 - p0)
                c = tuple(int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3))
                break
        else:
            c = stops[-1][1]
        d.line([(0, y), (w, y)], fill=c)
    return img


def centered(d, cx, y, text, f, fill):
    d.text((cx - tw(text, f) / 2, y), text, font=f, fill=fill)


# ---------------------------------------------------------------- scenes

def hero_scene(w, h):
    """Shenzhen trilateral summit at sunset."""
    img = vgrad(w, h, [(0.0, (43, 24, 66)), (0.45, (128, 44, 74)),
                        (0.75, (214, 96, 52)), (1.0, (246, 168, 60))])
    d = ImageDraw.Draw(img)
    # sun disc low over the skyline
    sx, sy, sr = int(w * 0.72), int(h * 0.66), int(h * 0.30)
    d.ellipse([sx - sr - 10, sy - sr - 10, sx + sr + 10, sy + sr + 10], fill=(250, 190, 90))
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 217, 122))
    # skyline silhouettes
    sil = (30, 17, 44)
    base = h
    buildings = [(0, 46), (52, 70), (112, 40), (168, 84), (232, 54), (292, 66),
                 (352, 44), (560, 58), (622, 88), (688, 48), (748, 72),
                 (812, 52), (868, 78), (922, 44)]
    for bx, bh in buildings:
        d.rectangle([bx, base - bh, bx + 46, base], fill=sil)
    # the tall tower (Ping An style) with a spire
    tx = 452
    d.rectangle([tx, base - 128, tx + 52, base], fill=sil)
    d.polygon([(tx + 8, base - 128), (tx + 44, base - 128), (tx + 26, base - 146)], fill=sil)
    # lit windows on a few buildings
    for wx, wy in [(70, base - 52), (90, base - 34), (250, base - 40), (640, base - 66),
                   (660, base - 44), (830, base - 56), (466, base - 96), (466, base - 62)]:
        d.rectangle([wx, wy, wx + 5, wy + 7], fill=(255, 214, 120))
    # three flag poles with national flags
    pole = (240, 235, 225)
    for i, fx in enumerate((170, 476, 782)):
        fy = 26
        d.line([(fx, fy), (fx, 118)], fill=pole, width=3)
        d.ellipse([fx - 3, fy - 3, fx + 3, fy + 3], fill=GOLD)
        fw, fh = 46, 28
        if i == 0:      # United States: stripes + blue canton
            for s in range(6):
                col = (178, 34, 52) if s % 2 == 0 else (245, 245, 245)
                d.rectangle([fx + 2, fy + 2 + s * (fh // 6), fx + 2 + fw, fy + 2 + (s + 1) * (fh // 6)], fill=col)
            d.rectangle([fx + 2, fy + 2, fx + 2 + fw // 2, fy + 2 + fh // 2], fill=(40, 50, 120))
        elif i == 1:    # China: red field, yellow stars
            d.rectangle([fx + 2, fy + 2, fx + 2 + fw, fy + 2 + fh], fill=(206, 32, 40))
            d.ellipse([fx + 7, fy + 6, fx + 13, fy + 12], fill=(255, 222, 60))
            for dx, dy in [(16, 4), (18, 9), (16, 14)]:
                d.ellipse([fx + dx, fy + dy, fx + dx + 3, fy + dy + 3], fill=(255, 222, 60))
        else:           # Russia: white / blue / red
            d.rectangle([fx + 2, fy + 2, fx + 2 + fw, fy + 2 + fh // 3], fill=(245, 245, 245))
            d.rectangle([fx + 2, fy + 2 + fh // 3, fx + 2 + fw, fy + 2 + 2 * fh // 3], fill=(38, 74, 160))
            d.rectangle([fx + 2, fy + 2 + 2 * fh // 3, fx + 2 + fw, fy + 2 + fh], fill=(206, 32, 40))
    # foreground: long signing table with three seated silhouettes, one
    # centred under each flag; gold rim light so they read against both
    # the bright sunset and the dark skyline
    fig = (16, 9, 22)
    rim = (255, 205, 110)
    ty = h - 30
    for fx in (170, 476, 782):
        head = [fx - 11, ty - 36, fx + 11, ty - 14]
        d.ellipse(head, fill=fig)
        d.ellipse(head, outline=rim)
        pts = [(fx - 21, ty + 2), (fx + 21, ty + 2), (fx + 12, ty - 16),
               (fx - 12, ty - 16)]
        d.polygon(pts, fill=fig)
        d.line(pts + [pts[0]], fill=rim, width=2)
    d.rectangle([60, ty, w - 60, ty + 16], fill=fig)                # table block
    d.line([(60, ty), (w - 60, ty)], fill=rim, width=2)             # table top edge
    d.rectangle([0, ty + 16, w, h], fill=fig)                       # foreground ground
    for fx in (170, 476, 782):
        d.rectangle([fx - 10, ty + 4, fx + 10, ty + 8], fill=(245, 238, 220))  # papers
    return img


def scene_icj(w, h):
    img = Image.new("RGB", (w, h), (206, 220, 230))
    d = ImageDraw.Draw(img)
    stone = (244, 241, 230)
    dark = (70, 66, 60)
    d.rectangle([0, h - 6, w, h], fill=(150, 148, 138))
    cx = w // 2
    d.polygon([(cx - 62, 14), (cx + 62, 14), (cx, 2)], fill=(150, 74, 58))
    d.rectangle([cx - 62, 15, cx + 62, 19], fill=stone)
    for i in range(5):
        x = cx - 52 + i * 26
        d.rectangle([x, 20, x + 9, h - 12], fill=stone, outline=dark)
    d.rectangle([cx - 66, h - 12, cx + 66, h - 7], fill=stone, outline=dark)
    d.rectangle([cx - 70, h - 6, cx + 70, h - 2], fill=stone)
    return img


def scene_ipo(w, h):
    img = Image.new("RGB", (w, h), (14, 20, 24))
    d = ImageDraw.Draw(img)
    for gx in range(14, w, 26):
        d.line([(gx, 2), (gx, h - 2)], fill=(32, 48, 44))
    for gy in range(8, h, 14):
        d.line([(2, gy), (w - 2, gy)], fill=(32, 48, 44))
    pts = [(8, h - 8), (52, h - 14), (88, h - 11), (122, h - 24),
           (156, h - 21), (188, h - 38), (w - 8, h - 46)]
    d.line(pts, fill=(53, 199, 89), width=3)
    for px, py in pts:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(140, 240, 160))
    ax, ay = pts[-1]
    d.polygon([(ax, ay), (ax - 11, ay + 1), (ax - 4, ay + 9)], fill=(53, 199, 89))
    d.text((8, 3), "ANT +34%", font=F(SANSB, 11), fill=(140, 240, 160))
    return img


def scene_riyadh(w, h):
    img = vgrad(w, h, [(0.0, (46, 32, 66)), (0.7, (150, 70, 60)), (1.0, (214, 110, 60))])
    d = ImageDraw.Draw(img)
    tx = w // 2 - 11
    d.rectangle([tx, 4, tx + 22, h], fill=(34, 26, 44))
    d.polygon([(tx, 4), (tx + 22, 4), (tx + 11, -4)], fill=(34, 26, 44))
    for wy in range(10, h - 4, 9):
        for wx in (tx + 4, tx + 12):
            d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 214, 120))
    # smoke plume drifting from the crown
    for i, (ox, oy, r) in enumerate([(16, 2, 7), (30, 0, 9), (48, 1, 11), (68, 3, 12)]):
        d.ellipse([tx + 22 + ox - r, oy + 2, tx + 22 + ox + r, oy + 2 + r], fill=(120, 112, 118))
    d.rectangle([0, h - 5, w, h], fill=(24, 18, 32))
    return img


def scene_gaza(w, h):
    img = Image.new("RGB", (w, h), (228, 219, 196))
    d = ImageDraw.Draw(img)
    # hospital block with red cross
    d.rectangle([16, 8, 96, h - 10], fill=(250, 250, 246), outline=(120, 112, 96))
    d.rectangle([48, 13, 64, 29], fill=(196, 40, 48))
    d.rectangle([53, 8, 59, 34], fill=(250, 250, 246))
    d.rectangle([50, 16, 62, 22], fill=(196, 40, 48))
    for wy in (36, 44):
        for wx in (24, 40, 68, 84):
            d.rectangle([wx, wy, wx + 6, wy + 5], fill=(150, 160, 165))
    # tank silhouette in the foreground
    tk = (52, 48, 44)
    d.polygon([(118, h - 12), (196, h - 12), (186, h - 24), (128, h - 24)], fill=tk)
    d.rectangle([146, h - 32, 172, h - 24], fill=tk)
    d.line([(172, h - 29), (212, h - 33)], fill=tk, width=4)
    for wx in range(126, 192, 12):
        d.ellipse([wx, h - 12, wx + 8, h - 4], fill=(30, 28, 26))
    d.rectangle([0, h - 3, w, h], fill=(168, 156, 130))
    return img


def scene_bridge(w, h):
    img = vgrad(w, h, [(0.0, (146, 190, 214)), (0.55, (110, 164, 198)), (1.0, (58, 116, 158))])
    d = ImageDraw.Draw(img)
    deck = h - 20
    d.rectangle([0, deck, w, deck + 4], fill=(52, 56, 62))
    for px in (34, w // 2, w - 40):
        d.rectangle([px - 3, deck - 20, px + 3, deck + 12], fill=(52, 56, 62))
    d.arc([10, deck - 30, w - 10, deck + 16], start=180, end=360, fill=(52, 56, 62), width=2)
    for wx in range(8, w, 22):
        d.line([(wx, deck + 9), (wx + 10, deck + 12)], fill=(210, 232, 242), width=1)
    # explosion flash on the deck
    cx, cy = w // 2 + 28, deck - 8
    pts = []
    import math
    for i in range(16):
        ang = math.pi * i / 8
        r = 13 if i % 2 == 0 else 5
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d.polygon(pts, fill=(255, 196, 60), outline=(230, 120, 30))
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 240, 190))
    return img


def scene_cyclone(w, h):
    img = Image.new("RGB", (w, h), (38, 96, 108))
    d = ImageDraw.Draw(img)
    # coastline
    d.polygon([(0, h), (0, h - 14), (52, h - 20), (96, h - 8), (128, h), ], fill=(214, 188, 138))
    d.rectangle([0, h - 3, w, h], fill=(24, 70, 84))
    # spiral storm
    cx, cy = w - 58, h // 2 - 2
    for r, a0 in [(26, 20), (19, 150), (12, 300)]:
        d.arc([cx - r, cy - r, cx + r, cy + r], start=a0, end=a0 + 250,
              fill=(235, 244, 240), width=4)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(235, 244, 240))
    # rain streaks
    for rx in range(12, w - 90, 16):
        for ry in (8, 26):
            d.line([(rx, ry), (rx - 4, ry + 8)], fill=(170, 214, 220), width=2)
    return img


def scene_utah(w, h):
    img = Image.new("RGB", (w, h), (168, 188, 208))
    d = ImageDraw.Draw(img)
    peaks = [(6, 118, 26), (74, 168, 12), (140, 128, 30)]
    for x0, x1, top in peaks:
        mid = (x0 + x1) // 2
        d.polygon([(x0, h), (mid, top), (x1, h)], fill=(110, 122, 140))
        d.polygon([(mid - 13, top + 13), (mid, top), (mid + 13, top + 13),
                   (mid + 5, top + 19), (mid, top + 14), (mid - 5, top + 19)], fill=(250, 252, 255))
    d.rectangle([0, h - 6, w, h], fill=(244, 248, 252))
    # deterministic snowfall
    for i in range(38):
        sx = (i * 53 + 17) % w
        sy = (i * 29 + 7) % (h - 8)
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
    return img


def scene_sport(w, h):
    img = Image.new("RGB", (w, h), (10, 26, 18))
    d = ImageDraw.Draw(img)
    # light cones (drawn first, pale)
    for fx in (36, w - 36):
        d.polygon([(fx, 8), (fx - 26, h - 12), (fx + 26, h - 12)], fill=(38, 62, 44))
    # pitch
    d.rectangle([0, h - 13, w, h], fill=(34, 120, 62))
    d.line([(w // 2, h - 13), (w // 2, h)], fill=(220, 240, 220), width=1)
    d.ellipse([w // 2 - 9, h - 11, w // 2 + 9, h - 3], outline=(220, 240, 220))
    # floodlight pylons
    for fx in (36, w - 36):
        d.line([(fx, h - 12), (fx, 6)], fill=(200, 205, 200), width=2)
        for lx in (-8, 0, 8):
            d.ellipse([fx + lx - 2, 3, fx + lx + 2, 7], fill=(255, 250, 200))
    # ball
    d.ellipse([w // 2 - 26, h - 22, w // 2 - 16, h - 12], fill=(250, 250, 250))
    return img


CARDS = [
    (scene_icj, "WORLD COURT: MYANMAR GENOCIDE VERDICT", "Historic first ruling, 9-6"),
    (scene_ipo, "ANTHROPIC IPO OPENS +34% ON DEBUT", "Record $81.3bn Nasdaq listing"),
    (scene_riyadh, "HOUTHI ATTACK DAMAGES PIF TOWER", "Hits Saudi wealth fund HQ"),
    (scene_gaza, "TANKS ENTER GAZA; HOSPITAL HIT", "Nasser Hospital strike kills 6"),
    (scene_bridge, "UKRAINE HITS CRIMEAN BRIDGE AGAIN", "Third strike in a week"),
    (scene_cyclone, "CYCLONE AKVAN: 72,000 EVACUATED", "Severe storm nears landfall"),
    (scene_utah, "UTAH SNOWSTORM DROPS 18 INCHES", "Mountain towns dig out"),
    (scene_sport, "CHELSEA BEAT PSG 1-0 IN EUROPE", "Buurman's 87' winner seals it"),
]

BRIEFS = [
    "Trump asks top court to scrap EPA climate grants",
    "El Salvador sends 2,500 troops to Haiti mission",
    "Denmark, Greenland, US sign Arctic security deal",
    "Huge Prague rally defends media independence",
    "Japan's Takaichi holds direct talks with Putin",
    "Seoul top court clears ex-PM Han in martial-law case",
    "Indonesia lets state seize graft assets, no trial",
    "Three tankers reported ablaze in Strait of Hormuz",
    "Arab League condemns attacks on Gaza hospitals",
    "Dozens missing as migrant boat sinks off Senegal",
    "RSF commander defects to Sudan's army in civil war",
    "Walmart raises outlook for third time this year",
    "UniCredit wins backing for Commerzbank takeover",
    "Physicists send a message through a wall by gravity",
    "Data-centre emissions may jump 70% by 2030 - IEA",
    "Van Gogh with Nazi-era past sells for record $190m",
]

TRAPS = [
    "Hegseth US-Venezuela pact - 18 Nov",
    "Sanon convicted over Moise plot - 18 Nov",
    "Anthropic IPO priced at $83 - 18 Nov",
    "Gemini 4 'Neon' launch - 18 Nov",
]

HERO_HEAD = "TRUMP, XI AND PUTIN SIGN PEACE DECLARATION AT SHENZHEN SUMMIT"
HERO_DEK = ("The three rivals met face-to-face for 90 minutes at APEC - a first in "
            "modern diplomacy - pledging talks on nuclear risks, UN reform and "
            "stable energy flows. No deal on Ukraine; Kyiv was not in the room.")

MKT_1 = "NIKKEI 59,444.21 +0.71% \u00b7 HANG SENG 22,841.62 -1.95% \u00b7 STOXX 600 -0.88%"
MKT_2 = "BRENT ~$93.50 +~1.3% \u00b7 EUR/USD 1.0967 -0.24% \u00b7 BITCOIN $63,478.72 -2.18%"


def build_page():
    img = Image.new("RGB", (W, W), PAPER)
    d = ImageDraw.Draw(img)
    cx = W // 2

    # ---- masthead
    f_title = fit_size("THE WORLD IN ONE DAY", SERIFB, CW, 64)
    centered(d, cx, 12, "THE WORLD IN ONE DAY", f_title, INK)
    d.rectangle([M, 82, W - M, 87], fill=RED)
    d.rectangle([M, 90, W - M, 91], fill=INK)
    f_date = fit_size("THURSDAY 19 NOVEMBER 2026", SANSB, CW, 40)
    centered(d, cx, 96, "THURSDAY 19 NOVEMBER 2026", f_date, RED)
    d.rectangle([M, 142, W - M, 143], fill=INK)
    centered(d, cx, 148, "76 stories verified for this date \u00b7 One front page",
             F(SANS, 15), MUTED)
    d.rectangle([M, 170, W - M, 171], fill=INK)

    # ---- hero
    img.paste(hero_scene(CW, 158), (M, 178))
    d.rectangle([M, 178, W - M - 1, 178 + 158 - 1], outline=INK, width=2)
    f_hh, hh_lines = fit_lines_shrink(HERO_HEAD, SANSB, CW, 2, 31, 24)
    y = 344
    for ln in hh_lines:
        centered(d, cx, y, ln, f_hh, INK)
        y += 34
    f_dek, dek_lines = fit_lines_shrink(HERO_DEK, SANS, CW, 2, 17, 13)
    y = 416
    for ln in dek_lines:
        centered(d, cx, y, ln, f_dek, (58, 52, 44))
        y += 19
    d.rectangle([M, 458, W - M, 460], fill=RED)

    # ---- cards, 2 rows of 4
    card_w, card_h, gap = 230, 104, 10
    top = 470
    for idx, (scene_fn, head, dek) in enumerate(CARDS):
        r, c = divmod(idx, 4)
        x = M + c * (card_w + gap)
        yy = top + r * (card_h + 6)
        d.rectangle([x, yy, x + card_w - 1, yy + card_h - 1], fill=CARD_BG, outline=INK, width=1)
        img.paste(scene_fn(card_w - 12, 42), (x + 6, yy + 5))
        f_ch, ch_lines = fit_lines_shrink(head, SANSB, card_w - 14, 2, 15, 11)
        ly = yy + 52
        for ln in ch_lines:
            d.text((x + 7, ly), ln, font=f_ch, fill=INK)
            ly += 16
        f_cd, dek_txt = fit_one_shrink(dek, SANS, card_w - 14, 12, 9)
        d.text((x + 7, yy + 88), dek_txt, font=f_cd, fill=MUTED)

    # ---- briefs, two columns of 8
    by = 696
    d.text((M, by), "THE DAY IN BRIEF", font=F(SANSB, 19), fill=INK)
    d.rectangle([M, by + 24, W - M, by + 25], fill=INK)
    f_bn = F(SANSB, 15)
    col_w = 470
    for i, b in enumerate(BRIEFS):
        col, row = divmod(i, 8)
        x = M + col * (col_w + 12)
        yy = by + 33 + row * 18
        num = "%d." % (i + 1)
        d.text((x, yy), num, font=f_bn, fill=RED)
        f_br, b_txt = fit_one_shrink(b, SANS, col_w - 34, 15, 12)
        d.text((x + tw(num, f_bn) + 6, yy), b_txt, font=f_br, fill=INK)

    # ---- date check box
    dy = 880
    d.rectangle([M, dy, W - M, dy + 44], outline=INK, width=1)
    d.text((M + 12, dy + 6), "DATE CHECK", font=F(SANSB, 13), fill=RED)
    d.text((M + 12, dy + 24), "NOT 19 NOV:", font=F(SANSB, 12), fill=INK)
    f_tr = F(SANS, 12)
    for i, t in enumerate(TRAPS):
        col, row = divmod(i, 2)
        x = M + 150 + col * 400
        yy = dy + 7 + row * 18
        d.text((x, yy), fit_one(t, f_tr, 392), font=f_tr, fill=(58, 52, 44))

    # ---- footer line
    foot = ("All stories happened or were first reported on Thursday 19 November 2026 "
            "\u00b7 Drawn by program \u00b7 Page 1 of 1")
    centered(d, cx, 934, foot, fit_size(foot, SANS, CW, 10), MUTED)

    # ---- markets band (last element; band bottom 1006, paper margin 18)
    my = 952
    d.rectangle([M, my, W - M, my + 54], fill=DARK)
    centered(d, cx, my + 5, "MARKETS \u00b7 AS REPORTED 19 NOV", F(SANSB, 10), GOLD)
    f_mk = fit_size(MKT_1, SANSB, CW - 30, 15)
    centered(d, cx, my + 20, MKT_1, f_mk, PAPER)
    centered(d, cx, my + 37, MKT_2, f_mk, PAPER)
    return img


def main():
    img = build_page()
    targets = []
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        targets.append(os.path.join(out_dir, "entry.png"))
    targets.append(os.path.join(HERE, "entry.png"))
    saved = False
    for path in targets:
        try:
            img.save(path, "PNG")
            saved = True
        except OSError:
            pass
    if not saved:
        raise OSError("draw.py: no writable output path for entry.png")


main()
