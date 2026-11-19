#!/usr/bin/env python3
"""
THE WORLD IN ONE DAY - a drawn broadsheet front page for one day's news:
Thursday 19 November 2026 (make.fun competition news-image-20261119).

The program draws the whole page with Pillow (stdlib + Pillow only, no
network) and writes it to entry.png in $MAKEFUN_OUTPUT_DIR (default /output).
The render is deterministic: fixed layout, fixed seeds, no clocks, no
unordered iteration - two runs write byte-identical bytes.

All 76 stories on the page were happened-or-first-reported on Thursday
19 November 2026; the DATE CHECK box near the footer names the day's famous
near-miss stories with their real dates (18 / 20 Nov) instead.
"""

import os
import random

from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

W = H = 1024
MARGIN = 16
CW = W - 2 * MARGIN  # content width = 992

PAPER = (248, 244, 233)
INK = (18, 18, 18)
SOFT = (44, 42, 38)
GREY = (104, 100, 92)
RED = (178, 10, 30)
DARKRED = (128, 8, 22)
BLACK = (12, 12, 12)
GREEN = (8, 118, 48)
GOLD = (186, 132, 26)
NAVY = (22, 44, 84)
SKYLT = (203, 216, 233)

FD = "/usr/share/fonts/truetype/dejavu/"
SERIF = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans-Bold.ttf"
SANSR = "DejaVuSans.ttf"
ITAL = "DejaVuSans-Oblique.ttf"

_font_cache = {}


def F(name, size):
    key = (name, int(size))
    if key not in _font_cache:
        try:
            _font_cache[key] = ImageFont.truetype(FD + name, int(size))
        except OSError:
            # DejaVuSans-Oblique is absent on some systems; fall back to
            # the regular DejaVu Sans face (still the DejaVu family).
            _font_cache[key] = ImageFont.truetype(FD + SANSR, int(size))
    return _font_cache[key]


def tw(d, s, f):
    return d.textlength(s, font=f)


def fit_text(d, s, name, size, maxw, minsize=7):
    """Shrink font (then ellipsize) until s fits maxw. Deterministic."""
    sz = int(size)
    while sz > minsize:
        f = F(name, sz)
        if tw(d, s, f) <= maxw:
            return f, s
        sz -= 1
    f = F(name, minsize)
    if tw(d, s, f) <= maxw:
        return f, s
    while s and tw(d, s + "...", f) > maxw:
        s = s[:-1]
    return f, s.rstrip() + "..."


def wrap(d, s, f, maxw):
    """Greedy word wrap; returns list of lines that each fit maxw."""
    lines = []
    cur = ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if tw(d, trial, f) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def center(d, cx, y, s, f, fill):
    d.text((cx - tw(d, s, f) / 2.0, y), s, font=f, fill=fill)


# --------------------------------------------------------------------------
# Content - every story happened or was first reported on Thu 19 Nov 2026
# --------------------------------------------------------------------------

HERO_KICKER = "SHENZHEN \u00b7 APEC SUMMIT \u00b7 THE DAY'S TOP STORY"
HERO_HEADLINE = "TRUMP, XI AND PUTIN HOLD FIRST TRILATERAL SUMMIT"
HERO_DECK = ("JOINT 'PEACE DECLARATION' PLEDGES TALKS ON NUCLEAR RISK, "
             "UN REFORM AND STABLE ENERGY FLOWS")
HERO_SUMMARY = ("The US, Chinese and Russian presidents met face-to-face for "
                "90 minutes in Shenzhen - a first in modern diplomacy. No "
                "settlement on Ukraine or Iran was announced, and Kyiv and "
                "its European allies were not in the room.")
HERO_SOURCE = "Reported by AP and Reuters, 19 Nov 2026 \u00b7 see also stories 13, 22 and 3"

# (number, scene key, headline, summary)
CARDS = [
    (2, "icj", "WORLD COURT: MYANMAR COMMITTED GENOCIDE",
     "9-6 ruling on the 2017 Rohingya campaign - the first genocide finding "
     "in the ICJ's 80 years. Reparations ordered."),
    (47, "ipo", "ANTHROPIC'S $81.3BN IPO IS HISTORY'S BIGGEST DEBUT",
     "ANT opens at $111.50, up 34% on the $83 price, eclipsing SpaceX's "
     "record raise."),
    (32, "riyadh", "HOUTHI ATTACK DAMAGES RIYADH'S PIF TOWER",
     "Missile strike hits the Saudi wealth fund's HQ - the capital's "
     "tallest tower - as the Iran war widens."),
    (33, "gaza", "ISRAELI TANKS PUSH INTO CENTRAL GAZA",
     "Armour crosses the ceasefire line near Nuseirat; Hamas cries "
     "violation; IDF cites a tunnel operation."),
    (3, "crimea", "UKRAINE HITS CRIMEAN BRIDGE, THIRD TIME IN A WEEK",
     "Rail traffic halted on the Kerch Bridge as European allies meet in "
     "Berlin on Ukraine's defence."),
    (70, "vangogh", "VAN GOGH WITH NAZI-ERA PAST SELLS FOR $190M",
     "At $190.4m it is the most expensive Van Gogh ever auctioned, "
     "despite a complex provenance."),
    (59, "cop31", "COP31 TALKS ENTER FINAL STAGE",
     "Fossil-fuel language still unresolved - 'transition away' vs a "
     "full phaseout - and finance split."),
    (15, "prague", "HUGE PRAGUE PROTEST DEFENDS FREE MEDIA",
     "Hundreds of thousands rally in the Czech capital against a "
     "proposed media law."),
    (24, "han", "SEOUL COURT CLEARS EX-PM HAN OVER MARTIAL LAW",
     "Supreme Court overturns Han Duck-soo's conviction for aiding "
     "Yoon's Dec 2024 martial-law decree."),
    (43, "senegal", "DOZENS MISSING AS MIGRANT BOAT SINKS OFF SENEGAL",
     "Vessel carrying about 100 people goes down off the coast; "
     "search and rescue under way."),
    (48, "unicredit", "UNICREDIT WINS BERLIN BACKING FOR COMMERZBANK",
     "Germany agrees governance terms for the \u20ac41bn deal; "
     "UniCredit shares rose 2.26%."),
    (71, "gta", "GTA VI FINALLY DEBUTS - TO ACCLAIM",
     "Rockstar's sequel launches after a 13-year wait since GTA V - "
     "and the critics are thrilled."),
]

# Briefs, grouped into the four printed columns (section header, [(num, text)])
BRIEF_COLUMNS = [
    [("AMERICAS", [
        (4, "Trump asks Supreme Court to scrap EPA climate grants"),
        (5, "Trump: US will 'see what happens' on Iran after Jan 1"),
        (6, "FDA sets up council to review vaccine, gene-therapy safety"),
        (7, "Tech outages pile up as AI raises the stakes"),
        (8, "Kushner firm quietly bought defence-contractor shares"),
        (9, "Utah county certifies midterms at 57.7% turnout"),
        (10, "El Salvador sends some 2,500 troops to Haiti"),
        (11, "Christmas Island's red crabs begin annual migration"),
    ]),
     ("EUROPE", [
        (12, "Denmark, Greenland & US strike Arctic security deal"),
        (13, "European allies gather in Berlin on Ukraine's defence"),
        (14, "Estonia to close Russia border crossings from Dec"),
        (16, "General strike disrupts Spanish ports, factories"),
        (17, "EU governments greenlight Indonesia trade pact"),
        (18, "UK launches latest renewables auction"),
        (19, "EU halts probe into XXXLutz furniture takeover"),
        (20, "AI-run cyberattack targeted the EU in October"),
        (21, "LPG tanker sinks off Bulgaria after projectile hit"),
    ])],
    [("ASIA-PACIFIC", [
        (22, "Xi pitches deeper regional integration at APEC"),
        (23, "Japan's Takaichi holds talks with Putin"),
        (25, "Seoul's Lee renews call for talks with Pyongyang"),
        (26, "North Korea shows off its first AI chatbot"),
        (27, "Trump: Nvidia's Huang came up 'briefly' with Xi"),
        (28, "Indonesia passes asset-forfeiture law"),
        (29, "One worker killed in Indonesian refinery blast"),
        (30, "Bangladesh shutdown as Yunus family home torched"),
        (31, "Japan car industry agrees common parts standards"),
    ]),
     ("MIDDLE EAST", [
        (34, "Strike on Gaza's Nasser Hospital kills six"),
        (35, "Three tankers reported ablaze in Strait of Hormuz"),
        (36, "Saudi coalition intercepts ballistic missile"),
        (37, "Arab League condemns attacks on Gaza hospitals"),
        (38, "Lebanon charges five Hezbollah members"),
        (39, "Palestinian children a third of child violations"),
    ])],
    [("AFRICA", [
        (40, "Kenya picks US consortium for minerals project"),
        (41, "Nigerian Senate seeks justice over 37 dead miners"),
        (42, "Tinubu widens 2027 campaign tour to 19 states"),
        (44, "RSF commander defects to Sudanese army"),
        (45, "Ebola response in DR Congo hampered by insecurity"),
        (46, "ICC presses Libya on war-crimes cooperation"),
    ]),
     ("ECONOMY", [
        (49, "Walmart raises outlook for third time this year"),
        (50, "Traders all but certain of a December Fed hike"),
        (51, "Nvidia fades after earnings as Huang fallout grows"),
        (52, "Australian jobless hits 4.9%, highest since 2021"),
        (53, "Rio Tinto puts $250m into Panguna legacy fund"),
    ]),
     ("SCIENCE & TECH", [
        (54, "48 pepper genomes map the chilli's origins"),
        (55, "Physicists send a message through a wall, by gravity"),
        (56, "Data-centre emissions could jump 70% by 2030: IEA"),
        (57, "Brain changes in pregnancy may hold key to MS cure"),
        (58, "Record 589m children now live in conflict zones"),
    ])],
    [("CLIMATE & WEATHER", [
        (60, "Indonesia's fire emissions third-highest on record"),
        (61, "Fiji declares disaster state over El Ni\u00f1o drought"),
        (62, "Vanuatu demands climate-summit reform"),
        (63, "Australia's dirtiest data-centre plans rival coal"),
    ]),
     ("SPORT", [
        (64, "Chelsea edge PSG 1-0 in Women's Champions League"),
        (65, "City, Madrid and Juventus also win in Europe"),
        (66, "France and Qatar win at U-17 World Cup"),
        (67, "Portugal edge Wales in five-goal thriller"),
        (68, "Svay Rieng rout Port FC 4-1 in ASEAN Shopee Cup"),
        (69, "India's hockey team opens NZ tour with a win"),
    ]),
     ("CULTURE", [
        (72, "Actor Stacy Keach dies at 85"),
        (73, "Gordon Ramsay gets his Hollywood star"),
        (74, "Ocean Photographer of the Year opens in Sydney"),
        (75, "Global English proficiency falls for 5th year"),
        (76, "AFF named AFC's best regional association again"),
    ])],
]

# (name, level, move, up?) - levels/moves exactly as reported on 19 Nov 2026
MARKETS = [
    ("NIKKEI 225", "59,444.21", "+0.71%", True),
    ("HANG SENG", "22,841.62", "-1.95%", False),
    ("STOXX 600", "level n/a", "-0.88%", False),
    ("BRENT CRUDE", "~$93.50", "+~1.3%", True),
    ("EUR/USD", "1.0967", "-0.24%", False),
    ("BITCOIN", "$63,478.72", "-2.18%", False),
]

WEATHER_LINE = ("CYCLONE AKVAN NEARS INDIA - 72,000 EVACUATED \u00b7 UTAH "
                "MOUNTAINS BURIED UNDER 18IN OF EARLY SNOW \u00b7 FIJI IN "
                "EL NI\u00d1O DROUGHT DISASTER \u00b7 INDONESIA'S WORST "
                "FIRE SEASON IN YEARS")

DATECHECK_1 = ("DATE CHECK - EVERY STORY ABOVE HAPPENED OR WAS FIRST "
               "REPORTED ON THURSDAY 19 NOVEMBER 2026.")
DATECHECK_2 = ("NOT THIS DAY: Hegseth announces US-Venezuela pact in "
               "Caracas - Wed 18 Nov \u00b7 Sanon convicted in Miami over "
               "Mo\u00efse assassination - 18 Nov \u00b7 Google releases "
               "Gemini 4 'Neon' - 18 Nov \u00b7 Anthropic prices its IPO "
               "at $83 - 18 Nov (trading began 19 Nov) \u00b7 Cyclone Akvan "
               "landfall in India - Fri 20 Nov (expected) \u00b7 Judge "
               "extends order blocking Trump's 'triumphal arch' - 18 Nov")

FOOTER = ("76 STORIES \u00b7 6 CONTINENTS \u00b7 SOURCES: AP \u00b7 REUTERS "
          "\u00b7 BBC \u00b7 UN NEWS \u00b7 NYT \u00b7 JUST SECURITY + 20 "
          "MORE OUTLETS \u00b7 DRAWN BY A PYTHON PROGRAM \u00b7 NO "
          "PHOTOGRAPHS")

# --------------------------------------------------------------------------
# Dot-grid world map (simplified continent polygons, lon/lat)
# --------------------------------------------------------------------------

EURASIA = [(-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (0, 49),
           (2, 51), (5, 53), (8, 55), (8, 57), (12, 56), (18, 56),
           (21, 59), (24, 59), (30, 60), (28, 66), (32, 70), (45, 68),
           (60, 69), (75, 72), (90, 75), (105, 77), (120, 73), (135, 72),
           (150, 70), (162, 70), (178, 66), (178, 62), (162, 60),
           (158, 52), (150, 45), (142, 42), (140, 38), (135, 35),
           (129, 33), (126, 38), (122, 38), (121, 31), (120, 26),
           (114, 22), (108, 18), (108, 12), (106, 9), (103, 5),
           (100, 8), (98, 14), (94, 17), (92, 16), (89, 22), (86, 20),
           (80, 13), (77, 8), (72, 20), (66, 25), (61, 25), (57, 26),
           (54, 26), (52, 29), (50, 29), (48, 28), (50, 25), (55, 24),
           (59, 22), (55, 17), (52, 15), (45, 12), (43, 12), (40, 15),
           (38, 20), (35, 28), (36, 36), (30, 36), (27, 37), (26, 38),
           (23, 36), (19, 40), (15, 38), (16, 40), (12, 42), (10, 44),
           (7, 44), (3, 43), (0, 39), (-2, 37)]
NAMERICA = [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80),
            (-85, 70), (-80, 73), (-75, 62), (-65, 60), (-55, 52),
            (-60, 46), (-70, 44), (-74, 40), (-76, 35), (-80, 32),
            (-80, 26), (-84, 30), (-89, 29), (-94, 29), (-97, 26),
            (-97, 22), (-94, 18), (-90, 14), (-83, 9), (-79, 9),
            (-83, 15), (-87, 13), (-92, 15), (-97, 16), (-102, 18),
            (-105, 20), (-110, 23), (-114, 28), (-117, 33), (-122, 37),
            (-124, 46), (-130, 55), (-150, 60), (-162, 58)]
SAMERICA = [(-79, 9), (-72, 12), (-64, 10), (-55, 6), (-50, 0), (-44, -3),
            (-35, -8), (-39, -13), (-40, -20), (-48, -26), (-52, -33),
            (-57, -38), (-62, -41), (-65, -45), (-67, -50), (-68, -54),
            (-71, -54), (-73, -46), (-73, -37), (-71, -30), (-70, -20),
            (-75, -15), (-79, -8), (-81, -4), (-80, 1), (-77, 4)]
AFRICA = [(-17, 15), (-10, 29), (-6, 35), (0, 36), (10, 37), (11, 34),
          (20, 32), (30, 31), (32, 31), (35, 28), (38, 22), (40, 15),
          (43, 12), (48, 11), (51, 12), (44, 0), (40, -6), (40, -15),
          (36, -22), (33, -26), (28, -33), (20, -35), (17, -32),
          (15, -27), (13, -18), (12, -10), (9, -1), (9, 4), (4, 6),
          (-3, 5), (-8, 4), (-13, 8), (-17, 12)]
UK = [(-5, 50), (-3, 53), (-5, 55), (-3, 57), (-2, 58), (-4, 58),
      (-6, 56), (-8, 54), (-6, 52)]
JAPAN = [(130, 31), (133, 34), (137, 35), (140, 36), (141, 40),
         (142, 44), (144, 44), (142, 42), (140, 38), (138, 35),
         (135, 34), (131, 33)]
GREENLAND = [(-45, 60), (-40, 64), (-32, 68), (-22, 70), (-20, 76),
             (-30, 80), (-45, 78), (-55, 72), (-58, 66), (-53, 61)]
ICELAND = [(-22, 64), (-15, 64), (-14, 66), (-20, 66)]
AUSTRALIA = [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (145, -38), (147, -38), (150, -37), (153, -30), (153, -25),
             (151, -24), (146, -19), (142, -15), (142, -11), (137, -12),
             (136, -15), (135, -12), (132, -11), (130, -12), (126, -14),
             (122, -17), (118, -20)]
NZ = [(167, -45), (170, -43), (172, -41), (174, -39), (176, -38),
      (174, -37), (172, -40), (169, -43), (167, -46)]
MADAGASCAR = [(43, -16), (47, -15), (50, -18), (47, -22), (45, -25),
              (44, -22), (43, -18)]
SUMATRA = [(95, 5), (100, 2), (104, -2), (106, -6), (102, -4), (97, 2)]
BORNEO = [(109, 1), (113, 4), (117, 6), (119, 2), (117, -2), (113, -3),
          (110, -1)]
JAVA = [(105, -6), (110, -7), (114, -8), (114, -9), (106, -8)]
NEWGUINEA = [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9),
             (147, -9), (141, -8), (136, -4), (132, -3)]
PHILIPPINES = [(120, 18), (122, 16), (121, 13), (123, 10), (122, 7),
               (120, 9), (119, 12), (120, 15)]

LAND = [EURASIA, NAMERICA, SAMERICA, AFRICA, UK, JAPAN, GREENLAND,
        ICELAND, AUSTRALIA, NZ, MADAGASCAR, SUMATRA, BORNEO, JAVA,
        NEWGUINEA, PHILIPPINES]

# (lon, lat, label, label dx, label dy)
HOTSPOTS = [
    (114.1, 22.5, "SHENZHEN", 5, -3),
    (4.3, 52.1, "HAGUE", -34, -9),
    (46.7, 24.6, "RIYADH", 5, -2),
    (34.3, 31.5, "GAZA", -26, 3),
    (34.0, 44.9, "CRIMEA", 5, -9),
    (-74.0, 40.7, "NEW YORK", 5, -3),
    (127.0, 37.5, "SEOUL", 5, -8),
    (-17.4, 14.7, "DAKAR", -30, -3),
    (151.2, -33.9, "SYDNEY", -8, 5),
]


def in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)) and \
           (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


# --------------------------------------------------------------------------
# Scenes (each returns an RGB image of the requested size)
# --------------------------------------------------------------------------

def canvas(w, h, bg):
    im = Image.new("RGB", (w, h), bg)
    return im, ImageDraw.Draw(im)


def scene_hero(w, h):
    rng = random.Random(20261119)
    im, d = canvas(w, h, (250, 176, 102))
    # sunset bands
    for i, col in enumerate([(252, 190, 110), (250, 176, 102),
                             (244, 156, 104), (236, 138, 110)]):
        d.rectangle([0, i * 16, w, i * 16 + 16], fill=col)
    d.ellipse([w * 0.82 - 20, 8, w * 0.82 + 20, 48], fill=(252, 205, 118))
    d.ellipse([w * 0.82 - 13, 15, w * 0.82 + 13, 41], fill=(255, 228, 156))
    # Shenzhen skyline silhouette
    base = 108
    x = -4
    while x < w:
        bw = rng.randint(13, 30)
        bh = rng.randint(20, 56)
        d.rectangle([x, base - bh, x + bw, base], fill=(86, 62, 96))
        for _ in range(rng.randint(1, 4)):
            wx = x + rng.randint(2, max(3, bw - 5))
            wy = base - bh + rng.randint(3, max(4, bh - 8))
            d.rectangle([wx, wy, wx + 2, wy + 3], fill=(255, 216, 130))
        x += bw + rng.randint(2, 6)
    d.rectangle([0, base, w, base + 4], fill=(70, 50, 80))
    # flags behind the figures
    centres = [w * 0.24, w * 0.50, w * 0.76]
    for i, cx in enumerate(centres):
        px = int(cx - 30)
        d.line([px, 30, px, 106], fill=(40, 32, 40), width=2)
        fx, fy, fw, fh = px, 28, 42, 26
        if i == 0:  # United States
            for s in range(7):
                col = (178, 34, 52) if s % 2 == 0 else (244, 240, 235)
                d.rectangle([fx, fy + s * fh / 7, fx + fw,
                             fy + (s + 1) * fh / 7], fill=col)
            d.rectangle([fx, fy, fx + 18, fy + 14], fill=(40, 52, 110))
            for r in range(3):
                for c in range(4):
                    d.ellipse([fx + 2 + c * 4, fy + 2 + r * 4,
                               fx + 4 + c * 4, fy + 4 + r * 4],
                              fill=(255, 255, 255))
        elif i == 1:  # China
            d.rectangle([fx, fy, fx + fw, fy + fh], fill=(206, 32, 40))
            d.ellipse([fx + 5, fy + 4, fx + 12, fy + 11], fill=(252, 214, 40))
            for (sx, sy) in [(15, 3), (17, 8), (17, 13), (14, 17)]:
                d.ellipse([fx + sx, fy + sy, fx + sx + 3, fy + sy + 3],
                          fill=(252, 214, 40))
        else:  # Russia
            d.rectangle([fx, fy, fx + fw, fy + fh / 3], fill=(244, 244, 244))
            d.rectangle([fx, fy + fh / 3, fx + fw, fy + 2 * fh / 3],
                        fill=(36, 66, 160))
            d.rectangle([fx, fy + 2 * fh / 3, fx + fw, fy + fh],
                        fill=(206, 32, 40))
    # three seated figures
    suits = [(30, 42, 74), (24, 24, 30), (48, 48, 54)]
    ties = [(178, 10, 30), (178, 10, 30), (36, 66, 160)]
    skins = [(233, 192, 158), (240, 206, 170), (236, 196, 164)]
    hairs = [(196, 178, 150), (28, 26, 26), (168, 168, 168)]
    for i, cx in enumerate(centres):
        cx = int(cx)
        d.polygon([(cx - 21, 134), (cx + 21, 134), (cx + 14, 104),
                   (cx - 14, 104)], fill=suits[i])
        d.polygon([(cx - 5, 104), (cx + 5, 104), (cx, 118)],
                  fill=(245, 245, 245))
        d.polygon([(cx - 2, 106), (cx + 2, 106), (cx + 3, 122),
                   (cx - 3, 122)], fill=ties[i])
        d.ellipse([cx - 13, 76, cx + 13, 102], fill=skins[i])
        d.pieslice([cx - 13, 72, cx + 13, 96], 180, 360, fill=hairs[i])
    # summit table
    d.polygon([(30, 128), (w - 30, 128), (w - 12, 142), (12, 142)],
              fill=(146, 102, 66))
    d.rectangle([12, 142, w - 12, 158], fill=(110, 74, 46))
    for cx in centres:
        cx = int(cx)
        d.rectangle([cx - 12, 131, cx + 12, 136], fill=(240, 236, 226))
    # caption strip
    d.rectangle([0, h - 15, w, h], fill=(16, 14, 20))
    f = F(SANS, 9)
    d.text((8, h - 12), "SHENZHEN, CHINA - THE THREE PRESIDENTS AT THE "
                        "APEC SUMMIT TABLE", font=f, fill=(250, 246, 236))
    return im


def scene_icj(w, h):
    im, d = canvas(w, h, SKYLT)
    d.rectangle([0, h - 6, w, h], fill=(110, 108, 104))
    cx = w // 2
    d.polygon([(cx - 56, 15), (cx + 56, 15), (cx, 3)], fill=(244, 242, 236))
    d.rectangle([cx - 56, 15, cx + 56, 19], fill=(244, 242, 236))
    for i in range(5):
        x = cx - 44 + i * 22
        d.rectangle([x, 20, x + 7, 36], fill=(250, 248, 242))
    d.rectangle([cx - 58, 36, cx + 58, 40], fill=(238, 236, 228))
    d.ellipse([cx - 4, 7, cx + 4, 15], fill=RED)
    return im


def scene_ipo(w, h):
    im, d = canvas(w, h, (13, 22, 34))
    for gx in range(0, w, 28):
        d.line([gx, 0, gx, h], fill=(34, 52, 72))
    for gy in range(0, h, 14):
        d.line([0, gy, w, gy], fill=(34, 52, 72))
    pts = [(6, 35), (44, 31), (80, 34), (116, 25), (152, 27), (188, 15),
           (224, 8)]
    d.line(pts, fill=(64, 214, 130), width=3)
    d.polygon([(224, 8), (214, 6), (218, 15)], fill=(64, 214, 130))
    f = F(SANS, 13)
    d.text((104, 3), "ANT +34%", font=f, fill=(64, 214, 130))
    return im


def scene_riyadh(w, h):
    im, d = canvas(w, h, (243, 178, 112))
    d.rectangle([0, 26, w, h], fill=(238, 156, 108))
    d.ellipse([w - 42, 4, w - 18, 28], fill=(255, 226, 150))
    # PIF-style tower with a jagged crack and smoke
    d.polygon([(104, 42), (108, 4), (126, 2), (132, 42)], fill=(52, 48, 62))
    d.line([(126, 4), (120, 14), (128, 20), (121, 30)], fill=(240, 230, 210),
           width=2)
    for (sx, sy, sr) in [(136, 4, 5), (144, 2, 7), (152, 4, 5)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(168, 164, 160))
    for bx in (30, 60, 168, 198):
        d.rectangle([bx, 24, bx + 16, 42], fill=(96, 74, 84))
    d.rectangle([0, 41, w, h], fill=(120, 84, 74))
    return im


def scene_gaza(w, h):
    im, d = canvas(w, h, (219, 203, 172))
    d.rectangle([14, 14, 52, 40], fill=(150, 142, 128))
    d.polygon([(14, 14), (30, 6), (52, 14)], fill=(150, 142, 128))
    d.rectangle([186, 10, 222, 40], fill=(158, 148, 132))
    d.polygon([(186, 10), (204, 2), (222, 10)], fill=(158, 148, 132))
    # tank
    d.polygon([(58, 29), (178, 29), (188, 38), (48, 38)], fill=(72, 76, 64))
    d.rectangle([98, 21, 142, 30], fill=(72, 76, 64))
    d.line([142, 24, 200, 19], fill=(52, 56, 46), width=3)
    for i in range(5):
        cx = 66 + i * 26
        d.ellipse([cx - 5, 33, cx + 5, 43], fill=(40, 42, 36))
    d.ellipse([30, 30, 66, 40], fill=(206, 192, 164))
    d.rectangle([0, 40, w, h], fill=(168, 150, 118))
    return im


def scene_crimea(w, h):
    im, d = canvas(w, h, (198, 220, 238))
    d.rectangle([0, 27, w, h], fill=(84, 128, 178))
    for wx in range(6, w, 26):
        d.arc([wx, 32, wx + 14, 39], 180, 360, fill=(210, 230, 246))
    # bridge deck with a broken, tilted span
    d.line([4, 20, 128, 20], fill=(52, 56, 62), width=3)
    d.polygon([(140, 22), (196, 30), (194, 34), (140, 26)], fill=(52, 56, 62))
    d.line([196, 30, 232, 24], fill=(52, 56, 62), width=3)
    for px in (30, 84, 214):
        d.rectangle([px, 20, px + 4, 34], fill=(70, 74, 80))
    d.arc([10, 8, 120, 30], 180, 330, fill=(90, 96, 104))
    for (sx, sy, sr) in [(140, 8, 5), (150, 5, 7), (160, 8, 5)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(150, 150, 150))
    return im


def scene_vangogh(w, h):
    im, d = canvas(w, h, (22, 30, 82))
    for (cx, cy, r) in [(44, 14, 7), (96, 9, 5), (150, 16, 8), (204, 10, 5)]:
        for rr in range(r, 1, -3):
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                      outline=(238, 206, 92))
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(255, 226, 130))
    d.arc([16, 20, 90, 44], 200, 340, fill=(150, 180, 230), width=2)
    d.arc([120, 24, 210, 46], 190, 330, fill=(150, 180, 230), width=2)
    d.polygon([(0, h), (0, 34), (60, 28), (120, 36), (180, 30), (w, 38),
               (w, h)], fill=(14, 20, 38))
    return im


def scene_cop31(w, h):
    im, d = canvas(w, h, (208, 230, 238))
    cx, cy, r = 66, 21, 17
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 130, 200))
    d.ellipse([cx - 11, cy - 10, cx - 2, cy - 2], fill=(76, 168, 92))
    d.ellipse([cx + 2, cy + 2, cx + 12, cy + 11], fill=(76, 168, 92))
    d.ellipse([cx - 4, cy + 8, cx + 4, cy + 14], fill=(76, 168, 92))
    # thermometer
    tx = 168
    d.rectangle([tx, 5, tx + 7, 32], outline=(90, 90, 90), width=2)
    d.rectangle([tx + 2, 14, tx + 5, 32], fill=RED)
    d.ellipse([tx - 3, 28, tx + 10, 41], fill=RED)
    # rising heat arcs
    for i, rr in enumerate((8, 13, 18)):
        d.arc([196 - rr, 22 - rr, 196 + rr, 22 + rr], 300, 60,
              fill=(230, 120, 60), width=2)
    d.ellipse([192, 18, 200, 26], fill=(250, 176, 60))
    return im


def scene_prague(w, h):
    im, d = canvas(w, h, (228, 221, 205))
    # banners
    for (bx, col) in [(36, (250, 248, 242)), (104, RED), (172, (250, 248, 242))]:
        d.line([bx + 16, 16, bx + 16, 30], fill=(90, 80, 70), width=2)
        d.rectangle([bx, 3, bx + 34, 15], fill=col)
    # crowd
    tones = [(233, 192, 158), (196, 150, 110), (150, 108, 76),
             (240, 206, 170)]
    rng = random.Random(19)
    for row, yy in enumerate((26, 35)):
        for i in range(11):
            cx = 14 + i * 21 + (7 if row else 0)
            tone = tones[rng.randint(0, 3)]
            d.ellipse([cx - 5, yy - 5, cx + 5, yy + 5], fill=tone)
            d.arc([cx - 7, yy + 2, cx + 7, yy + 12], 0, 180,
                  fill=(70, 70, 84), width=3)
    return im


def scene_han(w, h):
    im, d = canvas(w, h, (233, 229, 215))
    cx = 104
    d.line([cx, 7, cx, 34], fill=(90, 70, 30), width=3)
    d.line([cx - 34, 10, cx + 34, 10], fill=(90, 70, 30), width=3)
    d.rectangle([cx - 16, 34, cx + 16, 38], fill=(90, 70, 30))
    for px in (cx - 34, cx + 34):
        d.line([px, 10, px - 8, 22], fill=(90, 70, 30), width=1)
        d.line([px, 10, px + 8, 22], fill=(90, 70, 30), width=1)
        d.arc([px - 10, 18, px + 10, 30], 0, 180, fill=GOLD, width=3)
    d.ellipse([cx - 4, 4, cx + 4, 12], fill=GOLD)
    # gavel
    d.line([176, 34, 204, 12], fill=(120, 80, 44), width=4)
    d.line([196, 8, 212, 20], fill=(90, 60, 30), width=7)
    return im


def scene_senegal(w, h):
    im, d = canvas(w, h, (168, 208, 232))
    d.ellipse([8, 3, 26, 21], fill=(255, 226, 140))
    d.rectangle([0, 26, w, h], fill=(66, 124, 176))
    for wx in range(4, w, 24):
        d.arc([wx, 30, wx + 16, 38], 180, 360, fill=(214, 234, 248))
    d.polygon([(70, 25), (168, 25), (152, 36), (86, 36)], fill=(122, 82, 50))
    d.line([118, 25, 118, 10], fill=(90, 64, 40), width=2)
    d.polygon([(118, 10), (132, 16), (118, 18)], fill=RED)
    for hx in (88, 106, 128, 146):
        d.ellipse([hx - 4, 17, hx + 4, 25], fill=(150, 108, 76))
    return im


def scene_unicredit(w, h):
    im, d = canvas(w, h, (206, 220, 236))
    cx = w // 2
    d.polygon([(cx - 52, 14), (cx + 52, 14), (cx, 3)], fill=(246, 244, 238))
    for i in range(4):
        x = cx - 40 + i * 24
        d.rectangle([x, 15, x + 7, 34], fill=(250, 248, 242))
    d.rectangle([cx - 54, 34, cx + 54, 39], fill=(240, 238, 230))
    f = F(SERIF, 15)
    d.text((cx - tw(d, "\u20ac", f) / 2, 2), "\u20ac", font=f, fill=GOLD)
    d.polygon([(196, 30), (204, 18), (212, 30)], fill=GREEN)
    d.rectangle([201, 30, 207, 38], fill=GREEN)
    return im


def scene_gta(w, h):
    bands = [(255, 94, 160), (255, 120, 128), (255, 158, 96),
             (255, 196, 104), (255, 220, 130)]
    im, d = canvas(w, h, bands[0])
    bh = h / len(bands)
    for i, col in enumerate(bands):
        d.rectangle([0, i * bh, w, (i + 1) * bh + 1], fill=col)
    d.ellipse([w / 2 - 13, h - 30, w / 2 + 13, h - 4], fill=(255, 240, 190))
    # palm silhouettes
    for (px, flip) in [(30, 1), (w - 34, -1)]:
        d.line([px, h, px + 4 * flip, 14], fill=(30, 24, 34), width=3)
        for a in range(5):
            ex = px + 4 * flip + (a - 2) * 8
            ey = 12 + abs(a - 2) * 3
            d.arc([min(px, ex) - 2, 4, max(px, ex) + 10, 22], 180, 360,
                  fill=(30, 24, 34), width=2)
    f = F(SERIF, 21)
    s = "VI"
    d.text((w / 2 - tw(d, s, f) / 2 + 1, 7), s, font=f, fill=DARKRED)
    d.text((w / 2 - tw(d, s, f) / 2, 6), s, font=f, fill=(255, 250, 244))
    return im


SCENES = {
    "icj": scene_icj, "ipo": scene_ipo, "riyadh": scene_riyadh,
    "gaza": scene_gaza, "crimea": scene_crimea, "vangogh": scene_vangogh,
    "cop31": scene_cop31, "prague": scene_prague, "han": scene_han,
    "senegal": scene_senegal, "unicredit": scene_unicredit,
    "gta": scene_gta,
}


def badge(d, x, y, num, size=17):
    d.rectangle([x, y, x + size, y + size], fill=RED)
    f = F(SANS, 10 if num < 10 else 9)
    s = str(num)
    d.text((x + (size - tw(d, s, f)) / 2, y + size / 2 - 6), s,
           font=f, fill=(255, 252, 246))


# --------------------------------------------------------------------------
# Page assembly
# --------------------------------------------------------------------------

def draw_masthead(d):
    d.line([MARGIN, 10, W - MARGIN, 10], fill=INK, width=1)
    f = F(SANSR, 9)
    d.text((MARGIN, 26), "GLOBAL EDITION", font=f, fill=SOFT)
    r = "EST. 2026 \u00b7 VOL. I \u00b7 No. 19"
    d.text((W - MARGIN - tw(d, r, f), 26), r, font=f, fill=SOFT)
    f = F(SERIF, 41)
    center(d, W / 2, 12, "THE WORLD IN ONE DAY", f, INK)
    d.rectangle([MARGIN, 58, W - MARGIN, 61], fill=RED)
    # date bar
    d.rectangle([MARGIN, 65, W - MARGIN, 97], fill=BLACK)
    f = F(SANS, 23)
    center(d, W / 2, 69, "THURSDAY 19 NOVEMBER 2026", f, (252, 250, 244))
    f = F(SANS, 10)
    d.text((MARGIN + 10, 76), "76 STORIES", font=f, fill=(250, 214, 120))
    r = "6 CONTINENTS \u00b7 ONE DAY"
    d.text((W - MARGIN - 10 - tw(d, r, f), 76), r, font=f,
           fill=(250, 214, 120))
    f = F(ITAL, 11)
    center(d, W / 2, 101,
           "Every story on this page happened, or was first reported, on "
           "this one day", f, SOFT)


def draw_hero(img, d):
    y = 118
    scene = scene_hero(446, 172)
    img.paste(scene, (MARGIN, y))
    d.rectangle([MARGIN, y, MARGIN + 446, y + 172], outline=INK, width=1)
    x = MARGIN + 462
    w = W - MARGIN - x
    badge(d, x, y + 1, 1, 19)
    f = F(SANS, 12)
    d.text((x + 26, y + 3), HERO_KICKER, font=f, fill=RED)
    f = F(SERIF, 25)
    lines = wrap(d, HERO_HEADLINE, f, w)
    yy = y + 24
    for ln in lines:
        d.text((x, yy), ln, font=f, fill=INK)
        yy += 29
    d.line([x, yy + 1, x + w, yy + 1], fill=RED, width=2)
    yy += 6
    f = F(SANS, 11)
    for ln in wrap(d, HERO_DECK, f, w):
        d.text((x, yy), ln, font=f, fill=DARKRED)
        yy += 14
    yy += 2
    f = F(SANSR, 12)
    for ln in wrap(d, HERO_SUMMARY, f, w):
        d.text((x, yy), ln, font=f, fill=SOFT)
        yy += 15
    yy += 3
    f = F(ITAL, 9)
    d.text((x, yy), HERO_SOURCE, font=f, fill=GREY)


def draw_cards(img, d):
    y0 = 296
    ch, gap = 106, 6
    cw = (CW - 3 * gap) // 4
    for idx, (num, key, head, summ) in enumerate(CARDS):
        row, col = divmod(idx, 4)
        x = MARGIN + col * (cw + gap)
        y = y0 + row * (ch + gap)
        d.rectangle([x, y, x + cw, y + ch], outline=INK, width=1)
        scene = SCENES[key](cw - 6, 43)
        img.paste(scene, (x + 3, y + 3))
        badge(d, x + 5, y + 5, num, 16)
        tx = x + 7
        maxw = cw - 14
        yy = y + 50
        f = F(SANS, 11)
        lines = wrap(d, head, f, maxw)[:2]
        if len(lines) == 2 and tw(d, head, f) > maxw * 2:
            f, head2 = fit_text(d, head, SANS, 11, maxw * 2 - 4, 9)
            lines = wrap(d, head2, f, maxw)[:2]
        for ln in lines:
            d.text((tx, yy), ln, font=f, fill=INK)
            yy += 12
        yy += 1
        f = F(SANSR, 9)
        slines = wrap(d, summ, f, maxw)
        if len(slines) > 2:
            f2, s2 = fit_text(d, summ, SANSR, 9, maxw * 2 - 4, 8)
            slines = wrap(d, s2, f2, maxw)[:2]
            f = f2
        for ln in slines[:2]:
            d.text((tx, yy), ln, font=f, fill=SOFT)
            yy += 10.5


def draw_band(d):
    y = 632
    f = F(SANS, 10)
    d.text((MARGIN, y), "THE DAY ON THE MAP", font=f, fill=RED)
    d.text((512, y), "MARKETS - THURSDAY 19 NOV CLOSES & MOVES", font=f,
           fill=RED)
    d.line([MARGIN, y + 13, W - MARGIN, y + 13], fill=INK, width=1)
    # dot-grid map
    cols, rows = 76, 14
    x0, y0 = MARGIN + 2, y + 16
    pitch = 5.4
    land_col = (92, 98, 84)
    for r in range(rows):
        lat = 78 - (r + 0.5) * (138.0 / rows)
        for c in range(cols):
            lon = -180 + (c + 0.5) * (360.0 / cols)
            if any(in_poly(lon, lat, p) for p in LAND):
                cx = x0 + c * pitch
                cy = y0 + r * pitch
                d.ellipse([cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5],
                          fill=land_col)
    f = F(SANS, 7)
    for (lon, lat, label, dx, dy) in HOTSPOTS:
        cx = x0 + (lon + 180) / 360.0 * cols * pitch
        cy = y0 + (78 - lat) / 138.0 * rows * pitch
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)
        d.ellipse([cx - 1.2, cy - 1.2, cx + 1.2, cy + 1.2],
                  fill=(255, 250, 240))
        d.text((cx + dx, cy + dy), label, font=f, fill=DARKRED,
               stroke_width=2, stroke_fill=PAPER)
    # markets grid: 2 columns x 3 rows
    mx = 512
    mw = (W - MARGIN - mx - 12) // 2
    fN = F(SANS, 10)
    fV = F(SANSR, 10)
    for i, (name, level, move, up) in enumerate(MARKETS):
        r, c = divmod(i, 2)
        x = mx + c * (mw + 12)
        yy = y + 22 + r * 24
        d.text((x, yy), name, font=fN, fill=INK)
        nx = x + tw(d, name, fN) + 6
        d.text((nx, yy), level, font=fV, fill=SOFT)
        mxv = nx + tw(d, level, fV) + 6
        d.text((mxv, yy), move, font=fN, fill=GREEN if up else RED)
    f = F(SANSR, 8)
    d.text((mx, y + 22 + 3 * 24 - 2),
           "Levels as reported on 19 Nov 2026; STOXX 600 published as a "
           "move only.", font=f, fill=GREY)


def draw_weather(d):
    y = 726
    f = F(SANS, 10)
    d.text((MARGIN, y), "WEATHER", font=f, fill=RED)
    x = MARGIN + tw(d, "WEATHER", f) + 8
    f2, s = fit_text(d, WEATHER_LINE, SANSR, 10, W - MARGIN - x, 8)
    d.text((x, y), s, font=f2, fill=INK)
    d.line([MARGIN, y + 14, W - MARGIN, y + 14], fill=INK, width=1)


def draw_briefs(d):
    y0 = 745
    gap = 10
    cw = (CW - 3 * gap) // 4
    fH = F(SANS, 10)
    for ci, column in enumerate(BRIEF_COLUMNS):
        x = MARGIN + ci * (cw + gap)
        y = y0
        for (header, items) in column:
            d.text((x, y), header, font=fH, fill=RED)
            d.line([x, y + 11, x + cw, y + 11], fill=RED, width=1)
            y += 14
            for (num, text) in items:
                ns = str(num)
                fN = F(SANS, 9)
                nw = tw(d, ns, fN)
                fT, t = fit_text(d, text, SANSR, 9, cw - nw - 5, 7)
                d.text((x, y), ns, font=fN, fill=RED)
                d.text((x + nw + 4, y), t, font=fT, fill=INK)
                y += 9.9
            y += 3


def draw_datecheck(d):
    y = 958
    d.rectangle([MARGIN, y, W - MARGIN, y + 34], outline=INK, width=1)
    f = F(SANS, 9)
    d.text((MARGIN + 8, y + 4), DATECHECK_1, font=f, fill=INK)
    f = F(SANSR, 8)
    lines = wrap(d, DATECHECK_2, f, CW - 16)
    yy = y + 16
    for ln in lines[:2]:
        d.text((MARGIN + 8, yy), ln, font=f, fill=SOFT)
        yy += 9


def draw_footer(d):
    y = 994
    d.rectangle([MARGIN, y, W - MARGIN, y + 22], fill=BLACK)
    f, s = fit_text(d, FOOTER, SANS, 9, CW - 20, 8)
    center(d, W / 2, y + 6, s, f, (250, 248, 240))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_hero(img, d)
    d = ImageDraw.Draw(img)
    draw_cards(img, d)
    d = ImageDraw.Draw(img)
    draw_band(d)
    draw_weather(d)
    draw_briefs(d)
    draw_datecheck(d)
    draw_footer(d)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    img.save(os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
