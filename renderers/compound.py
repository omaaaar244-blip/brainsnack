"""Motivational compounding Short (2026-11-10): 1.01^d vs 0.99^d drawn day by day for a year (values computed),
kinetic text and a generated soft piano progression.
usage: python3 renderers/compound.py puzzles/NNNN.json videos/NNNN.mp4
json: {"type":"compound","rate":0.01,"days":365,"hook":"...","lines":["...", ...]}
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import W, H, FPS, font, ease, pop, wrap, Audio, encode

P = json.load(open(sys.argv[1])); OUT = sys.argv[2]
R, D = P.get("rate", .01), P.get("days", 365)
UP = lambda d: (1 + R) ** d
DN = lambda d: (1 - R) ** d
T0, TG = 2.4, 9.0                 # chart grows from T0 to T0+TG
T_REV = T0 + TG + .3
T_TXT = T_REV + 3.0
LINES = P["lines"]; LGAP = 1.9
TOTAL = T_TXT + LGAP * len(LINES) + 2.2
BG, WHITE, GREY = (14, 12, 18), (250, 246, 238), (150, 145, 160)
GOLD, RED = (255, 196, 70), (235, 90, 90)
CX0, CX1, CY0, CY1 = 120, W - 90, 560, 1260
YMAX = UP(D) * 1.08

def pt(d, v): return CX0 + (CX1 - CX0) * d / D, CY1 - (CY1 - CY0) * v / YMAX

def frame(i):
    t = i / FPS
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    y = 210
    for ln in wrap(P["hook"], font(72, "black"), 960):
        d.text((W / 2, y), ln, font=font(72, "black"), fill=WHITE, anchor="mm"); y += 90
    if t < T_TXT + .3:
        a = 1 - ease((t - T_TXT) / .3)
        col = lambda c: tuple(int(BG[k] + (c[k] - BG[k]) * a) for k in range(3))
        day = int(D * ease((t - T0) / TG) if t > T0 else 0)
        # axes
        d.line((CX0, CY0 - 20, CX0, CY1), fill=col((70, 66, 80)), width=3); d.line((CX0, CY1, CX1, CY1), fill=col((70, 66, 80)), width=3)
        for g in (1, 10, 20, 30):
            gy = pt(0, g)[1]; d.line((CX0, gy, CX1, gy), fill=col((34, 32, 42)), width=1)
            d.text((CX0 - 18, gy), f"{g}x", font=font(30, "bold"), fill=col(GREY), anchor="rm")
        d.text((CX1, CY1 + 40), f"day {day}", font=font(44, "black"), fill=col(WHITE), anchor="rm")
        d.text((CX0, CY1 + 40), "day 0", font=font(32, "bold"), fill=col(GREY), anchor="lm")
        if day > 0:
            for f, c, w in ((DN, RED, 7), (UP, GOLD, 9)):
                pts = [pt(k, f(k)) for k in range(0, day + 1, 2)] + [pt(day, f(day))]
                d.line(pts, fill=col(c), width=w, joint="curve")
                x, yy = pts[-1]; d.ellipse((x - 12, yy - 12, x + 12, yy + 12), fill=col(c))
        # live values
        d.text((W / 2 - 230, 1430), "+1% a day", font=font(42, "bold"), fill=col(GOLD), anchor="mm")
        d.text((W / 2 + 230, 1430), "-1% a day", font=font(42, "bold"), fill=col(RED), anchor="mm")
        d.text((W / 2 - 230, 1520), f"{UP(day):.2f}x", font=font(88, "black"), fill=col(GOLD), anchor="mm")
        d.text((W / 2 + 230, 1520), f"{DN(day):.2f}x", font=font(88, "black"), fill=col(RED), anchor="mm")
        if t > T_REV:
            k = pop((t - T_REV) / .4)
            f = font(int(64 * k) + 1, "black")
            d.text((W / 2, 1680), f"1.01^365 = {UP(D):.1f}   0.99^365 = {DN(D):.2f}", font=font(int(46 * k) + 1, "black"), fill=col(WHITE), anchor="mm")
    else:
        y = 700
        for j, ln in enumerate(LINES):
            tj = T_TXT + .3 + j * LGAP
            if t < tj: break
            a = ease((t - tj) / .45); f = font(70 if j < len(LINES) - 1 else 60, "black")
            c = [GOLD, RED, WHITE, GREY][min(j, 3)]
            for sub in wrap(ln, f, 940):
                d.text((W / 2, y + 40 * (1 - a)), sub, font=f, fill=tuple(int(BG[k] + (c[k] - BG[k]) * a) for k in range(3)), anchor="mm"); y += f.size * 1.25
            y += 60
    return im

# generated soft piano: Am F C G, arpeggiated
au = Audio(TOTAL)
CH = [(220, 261.6, 329.6), (174.6, 220, 261.6), (130.8 * 2, 329.6, 392), (196, 246.9, 293.7)]
bar = 2.0; t = 0.0; k = 0
while t < TOTAL - .5:
    ch = CH[k % 4]
    au.add(t, Audio.tone(ch[0] / 2, 2.4, 1.6, (1, .35, .1)), .22)
    for j, n in enumerate(ch + (ch[1] * 2,)):
        au.add(t + j * bar / 4, Audio.tone(n, 1.4, 2.6, (1, .25, .08)), .13)
    t += bar; k += 1
au.add(T_REV, Audio.tone(659, 1.6, 2, (1, .4)), .18)
print(f"up {UP(D):.4f} down {DN(D):.4f}")
encode(OUT, frame, TOTAL, au)
