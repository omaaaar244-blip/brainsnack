"""Calendar-facts renderer (2026-11-13): drawn month calendars, circled dates, a small bar chart, a big word.
usage: python3 renderers/calfacts.py puzzles/NNNN.json videos/NNNN.mp4
json: {"type":"calendar","scenes":[{"kind":"month"|"months"|"startsun"|"bars"|"word"|"end", "t":4, "title":"...",
        "sub":"...", "months":[[2026,11]], "circle":13, "bars":{"Mon":685,...}, "word":"..."}]}
All dates are computed with Python's calendar, never typed in. Ticking clock + minor stings synthesised here.
"""
import calendar, json, os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import W, H, FPS, font, ease, pop, wrap, Audio, encode, clamp

P = json.load(open(sys.argv[1])); OUT = sys.argv[2]
SC = P["scenes"]; starts = np.cumsum([0] + [s["t"] for s in SC]); TOTAL = float(starts[-1])
BG = (16, 16, 20); CARD = (30, 30, 36); WHITE = (244, 244, 244); GREY = (140, 140, 150); RED = (232, 52, 52)
DAYS = ["S", "M", "T", "W", "T", "F", "S"]

def text_c(d, y, s, f, col):
    for ln in wrap(s, f, W - 140):
        d.text((W / 2, y), ln, font=f, fill=col, anchor="mt"); y += f.size * 1.18
    return y

def month(d, x, y, w, yr, mo, lt, circle=None, hl_sun1=False):
    """draw a month grid at (x,y) width w; returns bottom y. circles `circle` after lt>0.6"""
    cw = w / 7; ch = cw * 0.82; bottom = y + cw * 1.12 + ch * 6
    d.rounded_rectangle((x, y, x + w, bottom), 28, fill=CARD)
    d.text((x + w / 2, y + cw * 0.12), f"{calendar.month_name[mo].upper()} {yr}", font=font(cw * 0.36, "black"), fill=WHITE, anchor="mt")
    hy = y + cw * 0.62
    for i, n in enumerate(DAYS):
        d.text((x + cw * (i + .5), hy), n, font=font(cw * 0.26), fill=RED if i == 5 else GREY, anchor="mt")
    cal = calendar.Calendar(firstweekday=6).monthdayscalendar(yr, mo)
    gy = hy + cw * 0.5
    for r, wk in enumerate(cal):
        for c, dd in enumerate(wk):
            if not dd: continue
            cx, cy = x + cw * (c + .5), gy + ch * (r + .5)
            if hl_sun1 and dd == 1:
                k = ease((lt - 0.3) / 0.5); rr = cw * 0.4
                if k > 0: d.rounded_rectangle((cx - rr, cy - rr, cx + rr, cy + rr), 14, fill=(60, 60, 200))
            if circle == dd:
                k = ease((lt - 0.6) / 0.6); rr = cw * 0.42 * (0.3 + 0.7 * pop((lt - 0.6) / 0.6))
                if k > 0: d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=RED)
            d.text((cx, cy), str(dd), font=font(cw * 0.32), fill=WHITE, anchor="mm")
    return bottom

def frame(i):
    t = i / FPS; j = int(np.searchsorted(starts, t, side="right") - 1); j = min(j, len(SC) - 1)
    s = SC[j]; lt = t - starts[j]; k = s["kind"]
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    a = ease(lt / 0.35)
    tcol = tuple(int(BG[n] + (WHITE[n] - BG[n]) * a) for n in range(3))
    y = 170
    if s.get("title"): y = text_c(d, y, s["title"], font(84, "black"), tcol) + 20
    if s.get("sub"): y = text_c(d, y, s["sub"], font(52), tuple(int(BG[n] + (GREY[n] - BG[n]) * a) for n in range(3))) + 30
    if k == "month":
        yr, mo = s["months"][0]; month(d, 90, max(y, 520), W - 180, yr, mo, lt, s.get("circle"))
    elif k == "startsun":
        yr, mo = s["months"][0]; month(d, 90, max(y, 560), W - 180, yr, mo, lt, s.get("circle"), hl_sun1=True)
    elif k == "months":
        ms = s["months"]; w = 520; gap = 24; yy = max(y, 420); xs = [(W - w) / 2] * len(ms)
        for n, (yr, mo) in enumerate(ms):
            ml = lt - n * 0.7
            if ml < 0: continue
            off = (1 - ease(ml / 0.4)) * 200
            yy = month(d, xs[n] + off, yy, w, yr, mo, ml + 0.2, s.get("circle")) + gap
    elif k == "bars":
        b = s["bars"]; vals = list(b.values()); lo = min(vals) - 4; hi = max(vals); top = max(y, 560) + 40
        bw = (W - 200) / len(b)
        for n, (name, v) in enumerate(b.items()):
            g = ease((lt - 0.2 - n * 0.1) / 0.8); hpx = (v - lo) / (hi - lo) * 760 * g
            x0 = 100 + n * bw + 14; x1 = x0 + bw - 28; base = top + 860
            col = RED if v == hi else (80, 80, 92)
            d.rectangle((x0, base - hpx, x1, base), fill=col)
            d.text(((x0 + x1) / 2, base + 24), name, font=font(40), fill=WHITE if v == hi else GREY, anchor="mt")
            if g > 0.9: d.text(((x0 + x1) / 2, base - hpx - 14), str(v), font=font(34), fill=WHITE, anchor="mb")
        d.text((W / 2, top + 1000), s.get("note", ""), font=font(36), fill=GREY, anchor="mt")
    elif k == "word":
        f = font(72, "black"); g = ease((lt - 0.5) / 0.5)
        col = tuple(int(BG[n] + (RED[n] - BG[n]) * g) for n in range(3))
        yy = 860
        for part in s["word"].split("|"):
            d.text((W / 2, yy), part, font=f, fill=col, anchor="mt"); yy += 96
        if s.get("foot") and lt > 1.4: text_c(d, yy + 80, s["foot"], font(46), GREY)
    elif k == "end":
        yr, mo = s["months"][0]; month(d, 190, max(y, 560), W - 380, yr, mo, lt, s.get("circle"))
        if s.get("foot") and lt > 1.0: text_c(d, 1560, s["foot"], font(54, "black"), WHITE)
    # progress bar
    d.rectangle((0, H - 14, W * t / TOTAL, H), fill=RED)
    return im

au = Audio(TOTAL)
for n in range(int(TOTAL * 2)):  # clock ticks twice a second, tick-tock
    au.add(n * 0.5, Audio.tone(2200 if n % 2 == 0 else 1700, 0.05, decay=90), 0.10)
for st in starts[:-1]:  # low minor sting at each scene start
    for f in (110.0, 130.81, 164.81):
        au.add(float(st) + 0.55, Audio.tone(f, 2.2, decay=1.6, harm=(1, .4, .2)), 0.12)
encode(OUT, frame, TOTAL, au)
