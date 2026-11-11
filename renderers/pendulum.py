"""Pendulum-wave Short (2026-11-11): 15 pendulums seen from above, pendulum i swings (n0+i) times per cycle,
so they drift into snakes, split into two opposite rows at half-cycle and line up again at the end of the cycle. Real physics:
period T/(n0+i), length g*(period/2pi)^2 (printed). Generated tone each time a bob reaches its right side.
usage: python3 renderers/pendulum.py puzzles/NNNN.json videos/NNNN.mp4
json: {"type":"pendulum","n":15,"n0":16,"cycle":20,"hook":"...","end":"...","cta":"..."}
"""
import json, math, os, sys, colorsys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import W, H, FPS, font, ease, wrap, Audio, encode

P = json.load(open(sys.argv[1])); OUT = sys.argv[2]
N, N0, T = P.get("n", 15), P.get("n0", 16), P.get("cycle", 20.0)
LEAD = 0.0; TAIL = 3.2; TOTAL = T + TAIL
freqs = [(N0 + i) / T for i in range(N)]
lengths = [9.81 * (1 / f / (2 * math.pi)) ** 2 for f in freqs]
print("lengths cm:", ", ".join(f"{l*100:.1f}" for l in lengths))
BG = (12, 14, 24); INK = (240, 240, 248); DIM = (120, 126, 150)
CX, A = W / 2, 370; Y0, Y1 = 560, 1460
rows = [Y0 + (Y1 - Y0) * i / (N - 1) for i in range(N)]
cols = [tuple(int(c * 255) for c in colorsys.hsv_to_rgb(0.02 + 0.75 * i / (N - 1), 0.72, 1.0)) for i in range(N)]
PENTA = [0, 2, 4, 7, 9]
notes = [220 * 2 ** ((12 * (i // 5) + PENTA[i % 5]) / 12) for i in range(N)]

def caption(t):
    marks = [(0.0, 3.2, P["hook"]), (3.6, 7.2, "Each one swings 1 extra time per cycle"),
             (T / 2 - 0.8, T / 2 + 1.2, "Halfway: 2 rows, perfectly opposite"), (T - 2.2, T - 0.4, "Wait for it...")]
    for a, b, s in marks:
        if a <= t < b: return s, min(1, (t - a) / .25, (b - t) / .25)
    return None, 0

def x_of(i, t): return CX + A * math.cos(2 * math.pi * freqs[i] * t)

def frame(k):
    t = k / FPS; ts = t if t <= T else T + (t - T) * 0.06  # slow-mo after the realign
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im, "RGBA")
    # frame rails and centre line
    d.rounded_rectangle((CX - A - 60, Y0 - 70, CX + A + 60, Y1 + 70), 40, outline=(40, 44, 66), width=4)
    d.line((CX, Y0 - 50, CX, Y1 + 50), fill=(50, 56, 84), width=3)
    tf = font(46, "black"); d.text((W / 2, 230), "PENDULUM WAVE", font=tf, fill=DIM, anchor="mm")
    # cycle timer bar
    f = min(1, ts / T); d.rounded_rectangle((180, 300, W - 180, 314), 7, fill=(36, 40, 60))
    d.rounded_rectangle((180, 300, 180 + (W - 360) * f, 314), 7, fill=(255, 200, 80))
    d.text((W / 2, 360), f"{min(ts, T):4.1f} s", font=font(40, "bold"), fill=DIM, anchor="mm")
    # trails + strings (seen from above: string from centre pivot line) + bobs
    for i in range(N):
        y = rows[i]
        for j in range(6, 0, -1):
            tx = x_of(i, ts - j * 0.03); a = int(70 * (1 - j / 7))
            d.ellipse((tx - 20, y - 20, tx + 20, y + 20), fill=cols[i] + (a,))
        x = x_of(i, ts)
        d.line((CX, y, x, y), fill=cols[i] + (90,), width=4)
        d.ellipse((x - 34, y - 34, x + 34, y + 34), fill=cols[i] + (60,))
        d.ellipse((x - 25, y - 25, x + 25, y + 25), fill=cols[i])
        d.ellipse((x - 12, y - 16, x - 2, y - 6), fill=(255, 255, 255, 140))
    s, a = caption(t)
    if s:
        cf = font(64, "black"); ls = wrap(s, cf, 940)
        for n, l in enumerate(ls):
            d.text((W / 2, 1600 + n * 78), l, font=cf, fill=INK + (int(255 * a),), anchor="mm")
    if t >= T - 0.1:
        e = ease((t - T + 0.1) / 0.4)
        d.text((W / 2, 470), "All back in line.", font=font(70, "black"), fill=(255, 200, 80, int(255 * e)), anchor="mm")
        if t >= T + 0.8:
            e2 = ease((t - T - 0.8) / 0.4); ef = font(50, "bold")
            for n, l in enumerate(wrap(P["end"], ef, 960)):
                d.text((W / 2, 1600 + n * 64), l, font=ef, fill=INK + (int(255 * e2),), anchor="mm")
            for n, l in enumerate(wrap(P["cta"], ef, 960)):
                d.text((W / 2, 1760 + n * 64), l, font=ef, fill=(255, 200, 80, int(255 * e2)), anchor="mm")
    return im

au = Audio(TOTAL)
for i in range(N):
    m = 1
    while m / freqs[i] < T + 0.05:
        au.add(m / freqs[i], Audio.tone(notes[i], 0.5, decay=9, harm=(1, .3, .1)), 0.07); m += 1
au.add(0.0, sum(Audio.tone(n, 1.2, decay=4) for n in notes), 0.04)
au.add(T, sum(Audio.tone(n, 2.5, decay=2) for n in notes), 0.05)
encode(OUT, frame, TOTAL, au)
