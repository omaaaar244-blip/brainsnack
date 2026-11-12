"""Optical-illusion quiz renderer (2026-11-12): two classic illusions, a question + countdown, then a reveal
that removes the context and measures. Müller-Lyer (equal lines with arrow fins) and Ebbinghaus (equal circles
among big / small circles). Both are drawn here with PIL; the shapes really are identical in size.
usage: python3 renderers/illusion.py puzzles/NNNN.json videos/NNNN.mp4
json: {"type":"illusion","hook":"...","outro":"..."}
"""
import json, math, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import W, H, FPS, font, ease, clamp, wrap, Audio, encode

P = json.load(open(sys.argv[1])); OUT = sys.argv[2]
BG = (250, 248, 240); INK = (25, 25, 30); RED = (230, 57, 70); BLUE = (40, 110, 230); ORANGE = (245, 140, 20)
GREEN = (30, 170, 90); GREY = (120, 120, 130); LIGHT = (150, 160, 190)
Q, CD, REV, HOLD = 1.2, 3.0, 2.2, 1.6          # question in, countdown, reveal animation, hold
SEG = Q + CD + REV + HOLD
T2 = SEG                                      # second illusion start
TEND = 2 * SEG; TOTAL = TEND + 3.0

def text_c(d, y, s, size, fill, kind="black", a=1.0, maxw=960, lh=1.18):
    f = font(size, kind)
    for n, l in enumerate(wrap(s, f, maxw)):
        d.text((W / 2, y + n * size * lh), l, font=f, fill=fill + (int(255 * a),), anchor="mm")

def countdown(d, t):  # t since question start
    if Q <= t < Q + CD:
        n = 3 - int(t - Q); k = (t - Q) % 1
        d.text((W / 2, 1640), str(n), font=font(150, "black"), fill=INK + (int(255 * (1 - 0.6 * k)),), anchor="mm")

def muller(d, t):
    L = 560; x0 = (W - L) / 2; ys = (820, 1240); fin = 90
    fins_a = 1 - ease((t - Q - CD - 0.2) / 0.6)            # fins fade out at reveal
    slide = ease((t - Q - CD - 0.9) / 0.9)                  # lower line slides up next to the other
    col = (RED, BLUE)
    for j, y in enumerate(ys):
        yy = y if j == 0 else ys[1] - slide * (ys[1] - ys[0] - 80)
        d.line((x0, yy, x0 + L, yy), fill=col[j], width=16)
        if fins_a > 0:
            a = int(255 * fins_a); s = 1 if j == 0 else -1   # top: inward arrows (<->), bottom: outward (>-<)
            for xe, dx in ((x0, 1), (x0 + L, -1)):
                for dy in (-1, 1):
                    d.line((xe, yy, xe + s * dx * fin * 0.75, yy + dy * fin * 0.75), fill=INK + (a,), width=12)
        d.text((x0 - 120, yy), "AB"[j], font=font(70, "black"), fill=col[j] + (255,), anchor="mm")
    if t > Q + CD + 1.8:
        k = ease((t - Q - CD - 1.8) / 0.4)
        for xe in (x0, x0 + L):
            d.line((xe, 700, xe, 1100), fill=GREEN + (int(220 * k),), width=5)

def circles(d, cx, cy, big, a_ctx):
    r0 = 70
    if a_ctx > 0:
        a = int(255 * a_ctx)
        if big:
            for k in range(6):
                ang = k * math.pi / 3; R = 230; rr = 120
                x, y = cx + R * math.cos(ang), cy + R * math.sin(ang)
                d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=LIGHT + (a,))
        else:
            for k in range(8):
                ang = k * math.pi / 4; R = 120; rr = 30
                x, y = cx + R * math.cos(ang), cy + R * math.sin(ang)
                d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=LIGHT + (a,))
    d.ellipse((cx - r0, cy - r0, cx + r0, cy + r0), fill=ORANGE + (255,))

def ebbing(d, t):
    a_ctx = 1 - ease((t - Q - CD - 0.2) / 0.6)
    slide = ease((t - Q - CD - 0.9) / 0.9)
    ya, yb = 900, 1345
    yb2 = yb - slide * (yb - ya - 0)          # B slides up beside A
    xa, xb = W / 2 - slide * 110, W / 2 + slide * 110
    circles(d, xa, ya, True, a_ctx); circles(d, xb, yb2, False, a_ctx)
    d.text((xa, ya + (0 if slide < .5 else 115)), "A", font=font(56, "black"), fill=(255, 255, 255, 255) if slide < .5 else INK + (255,), anchor="mm")
    d.text((xb, yb2 + (0 if slide < .5 else 115)), "B", font=font(56, "black"), fill=(255, 255, 255, 255) if slide < .5 else INK + (255,), anchor="mm")
    if t > Q + CD + 1.8:
        k = ease((t - Q - CD - 1.8) / 0.4)
        for yy in (ya - 70, ya + 70):
            d.line((xa - 140, yy, xb + 140, yy), fill=GREEN + (int(220 * k),), width=5)

def frame(i):
    t = i / FPS
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im, "RGBA")
    d.text((W / 2, 110), P["hook"], font=font(54, "black"), fill=GREY + (255,), anchor="mm")
    if t < TEND:
        s = 0 if t < T2 else 1; tl = t - s * SEG
        qa = ease(tl / 0.3)
        q = ["Which line is longer?", "Which orange circle is bigger?"][s]
        nl = len(wrap(q, font(84, "black"), 960))
        text_c(d, 260, q, 84, INK, a=qa)
        text_c(d, 260 + nl * 100, "A or B?", 64, GREY, kind="bold", a=qa)
        (muller if s == 0 else ebbing)(d, tl)
        countdown(d, tl)
        if tl > Q + CD + 1.9:
            k = ease((tl - Q - CD - 1.9) / 0.35)
            text_c(d, 1600, "SAME SIZE.", 120, GREEN, a=k)
            text_c(d, 1730, "Your brain judged the surroundings.", 48, GREY, kind="bold", a=k)
    else:
        k = ease((t - TEND) / 0.4)
        text_c(d, 760, "Did both fool you?", 96, INK, a=k)
        text_c(d, 960, P["outro"], 64, RED, a=ease((t - TEND - 0.6) / 0.4))
    return im

au = Audio(TOTAL)
for s in (0, 1):
    b = s * SEG
    au.add(b + 0.05, Audio.tone(660, .25, 10), .25)
    for n in range(3): au.add(b + Q + n, Audio.tone(880, .12, 25, (1, .3)), .35)
    au.add(b + Q + CD + 0.2, Audio.noise(.4, 12), .08)
    for j, f in enumerate((523.3, 659.3, 784.0)): au.add(b + Q + CD + 1.9 + j * .07, Audio.tone(f, 1.0, 3.5, (1, .3)), .22)
for j, f in enumerate((392.0, 523.3, 659.3, 784.0)): au.add(TEND + j * .12, Audio.tone(f, 1.2, 3, (1, .3)), .2)
encode(OUT, frame, TOTAL, au)
