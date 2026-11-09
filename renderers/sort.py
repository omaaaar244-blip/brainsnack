"""Satisfying sorting race Short (2026-11-09): two panels sort the SAME shuffled bars at the same comparison rate,
bubble sort vs quick sort, with generated tones (pitch = bar height). Counts shown are computed, not invented.
usage: python3 renderers/sort.py puzzles/NNNN.json videos/NNNN.mp4
json: {"type":"sort","n":36,"seed":7,"rate":36,"hook":"...","end":"..."}
"""
import json, os, sys, random, colorsys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import W, H, FPS, font, ease, wrap, Audio, encode

P = json.load(open(sys.argv[1])); OUT = sys.argv[2]
N, RATE = P.get("n", 36), P.get("rate", 36)
arr0 = list(range(1, N + 1)); random.Random(P.get("seed", 7)).shuffle(arr0)

def bubble(a):
    a = a[:]; tr = []
    for i in range(len(a)):
        sw = False
        for j in range(len(a) - 1 - i):
            if a[j] > a[j + 1]: a[j], a[j + 1] = a[j + 1], a[j]; sw = True
            tr.append((a[:], (j, j + 1)))
        if not sw: break
    return tr

def quick(a):
    a = a[:]; tr = []
    def part(lo, hi):
        p = a[hi]; i = lo
        for j in range(lo, hi):
            if a[j] < p: a[i], a[j] = a[j], a[i]; i += 1
            tr.append((a[:], (j, hi)))
        a[i], a[hi] = a[hi], a[i]
        if tr: tr[-1] = (a[:], tr[-1][1])  # show the pivot landing in place
        return i
    def qs(lo, hi):
        if lo < hi: m = part(lo, hi); qs(lo, m - 1); qs(m + 1, hi)
    qs(0, len(a) - 1); return tr

TR = {"BUBBLE SORT": bubble(arr0), "QUICK SORT": quick(arr0)}
for tr in TR.values(): assert tr[-1][0] == sorted(arr0)
P["end"] = P["end"].replace("COUNTQ", str(len(TR["QUICK SORT"]))).replace("COUNTB", str(len(TR["BUBBLE SORT"])))
T0 = 1.6                                   # hook first, then both start together
LONG = max(len(t) for t in TR.values())
T_DONE = T0 + LONG / RATE
TOTAL = T_DONE + 1.2 + 3.2
WHITE, GREY = (245, 245, 250), (140, 140, 150)
PANELS = [("BUBBLE SORT", 470), ("QUICK SORT", 1180)]   # (name, panel top y)
PH = 560; X0, X1 = 70, W - 70; BW = (X1 - X0) / N

def col(v):
    r, g, b = colorsys.hsv_to_rgb(0.62 - 0.62 * (v - 1) / (N - 1), 0.75, 1.0); return (int(r * 255), int(g * 255), int(b * 255))

def state(name, t):
    tr = TR[name]; k = int((t - T0) * RATE)
    if k < 0: return arr0, (), False, 0
    if k >= len(tr): return tr[-1][0], (), True, len(tr)
    return tr[k][0], tr[k][1], False, k + 1

def frame(i):
    t = i / FPS
    im = Image.new("RGB", (W, H), (8, 8, 12)); d = ImageDraw.Draw(im)
    y = 150
    for ln in wrap(P["hook"], font(70, "black"), 940):
        d.text((W / 2, y), ln, font=font(70, "black"), fill=WHITE, anchor="mm"); y += 86
    for name, top in PANELS:
        a, hi, done, cmp = state(name, t)
        d.text((X0, top - 30), name, font=font(46, "black"), fill=WHITE, anchor="ls")
        d.text((X1, top - 30), f"{cmp} comparisons", font=font(38, "bold"), fill=(120, 230, 140) if done else GREY, anchor="rs")
        base = top + PH
        sweep = int(N * ease((t - (T0 + len(TR[name]) / RATE)) / 0.7)) if done else 0
        for idx, v in enumerate(a):
            x = X0 + idx * BW; h = PH * v / N
            c = (255, 255, 255) if idx in hi else ((90, 235, 120) if idx < sweep else col(v))
            d.rectangle((x + 2, base - h, x + BW - 2, base), fill=c)
        if done and t > T0 + len(TR[name]) / RATE + 0.7:
            d.text((W / 2, base + 50), "DONE", font=font(44, "black"), fill=(90, 235, 120), anchor="mm")
    if t > T_DONE + 1.2:
        k = ease((t - T_DONE - 1.2) / 0.4)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, int(235 * k))); im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
        y = 760
        for ln in wrap(P["end"], font(64, "black"), 900):
            d.text((W / 2, y), ln, font=font(64, "black"), fill=WHITE, anchor="mm"); y += 84
        d.text((W / 2, y + 60), "Which one would you watch again?", font=font(42, "bold"), fill=GREY, anchor="mm")
    return im

au = Audio(TOTAL)
for n, (name, tr) in enumerate(TR.items()):
    for k, (a, hi) in enumerate(tr):
        v = a[hi[0]]; f = 220 * 2 ** (2.2 * v / N)
        au.add(T0 + k / RATE, Audio.tone(f * (1 if n == 0 else 1.5), 0.07, decay=40, harm=(1, .3) if n == 0 else (1, 0, .2)), .16)
    tend = T0 + len(tr) / RATE
    for s in range(N):
        au.add(tend + 0.7 * s / N, Audio.tone(220 * 2 ** (2.2 * (s + 1) / N), 0.09, decay=35), .14)
au.add(T_DONE + 1.2, Audio.tone(523, 1.2, 3, (1, .4, .2)), .3); au.add(T_DONE + 1.2, Audio.tone(784, 1.2, 3), .2)
P["_counts"] = {k: len(v) for k, v in TR.items()}; print(P["_counts"])
encode(OUT, frame, TOTAL, au)
