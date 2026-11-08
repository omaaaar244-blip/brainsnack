"""Autumn-leaf science explainer (2026-11-08): one big drawn leaf changes colour scene by scene, pigment chips,
falling-leaf particles, generated soft chords. All graphics drawn here (no emoji, no stock).
usage: python3 renderers/leaf.py puzzles/NNNN.json videos/NNNN.mp4
json: {"type":"leaf","hook":"...","hook_sub":"...","hook_t":2.8,
       "scenes":[{"t":3.6,"text":"...","color":[r,g,b],"chip":"CHLOROPHYLL","chip_color":[r,g,b],"fall":false},...],
       "end":"...","end_t":2.8}
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import W, H, FPS, SR, font, ease, pop, wrap, Audio, encode

P = json.load(open(sys.argv[1])); OUT = sys.argv[2]
SC = P["scenes"]; T_HOOK = P.get("hook_t", 2.8)
starts = [T_HOOK]
for s in SC: starts.append(starts[-1] + s["t"])
T_END = starts[-1]; TOTAL = T_END + P.get("end_t", 2.8)
CREAM = (255, 240, 220)
rng = np.random.default_rng(7)
parts = rng.uniform(0, 1, (46, 5))
PAL = [(214, 120, 40), (232, 176, 52), (190, 60, 40), (150, 90, 40)]

bg = Image.new("RGB", (W, H)); bd = ImageDraw.Draw(bg)
for y in range(H):
    k = y / H; bd.line((0, y, W, y), fill=(int(46 - 26 * k), int(26 - 14 * k), int(18 - 9 * k)))

def leaf_layer(col, size=900):
    L = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    cx, top, ln, wd = size / 2, 90, 600, 200
    left, right = [], []
    for n in range(61):
        s = n / 60; w = wd * math.sin(math.pi * s) ** 0.75 * (1 + 0.05 * math.sin(s * 60))
        y = top + ln * s; left.append((cx - w, y)); right.append((cx + w, y))
    d.polygon(left + right[::-1], fill=col)
    dark = tuple(int(c * 0.62) for c in col)
    d.line((cx, top + 20, cx, top + ln + 120), fill=dark, width=12)   # midrib + stem
    for n in range(1, 8):
        y = top + ln * n / 8.5; w = wd * math.sin(math.pi * (n / 8.5)) ** 0.75 * 0.82
        d.line((cx, y + 40, cx - w, y - 30), fill=dark, width=6); d.line((cx, y + 40, cx + w, y - 30), fill=dark, width=6)
    hi = tuple(int(c + (255 - c) * 0.18) for c in col)
    d.ellipse((cx - wd * .62, top + 150, cx - wd * .22, top + 330), fill=hi)
    return L

def lerp(a, b, k): return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))

def scene_at(t):
    for j in range(len(SC)):
        if t < starts[j + 1]: return j, t - starts[j]
    return len(SC) - 1, t - starts[len(SC) - 1]

def leaf_color(t):
    if t < T_HOOK: return tuple(SC[0]["color"])
    j, tl = scene_at(t); prev = SC[j - 1]["color"] if j else SC[0]["color"]
    return lerp(prev, SC[j]["color"], ease(tl / 1.4))

def frame(i):
    t = i / FPS
    im = bg.copy(); d = ImageDraw.Draw(im, "RGBA")
    for x, y, sp, ph, c in parts:   # background falling leaves
        yy = ((y * H + t * (60 + 90 * sp)) % (H + 80)) - 40; xx = x * W + 40 * math.sin(t * (0.8 + sp) + ph * 6)
        r = 10 + 14 * sp; a = math.sin(t * 2 + ph * 9) * r * 0.6
        d.ellipse((xx - r, yy - abs(a) - 4, xx + r, yy + abs(a) + 4), fill=PAL[int(c * 4)] + (int(70 + 70 * sp),))
    # big leaf
    col = leaf_color(t); fall = 0.0
    if t >= T_HOOK:
        j, tl = scene_at(t)
        if SC[j].get("fall"): fall = max(0.0, tl - 1.2)
    ang = 8 * math.sin(t * 1.3) + fall * 70
    L = leaf_layer(col).rotate(ang, resample=Image.BICUBIC)
    cx = W / 2 + fall * 120 * math.sin(fall * 2.2); cy = 820 + fall * fall * 260
    k = pop(t / 0.5)
    if k < 1: L = L.resize((int(900 * k) or 1, int(900 * k) or 1))
    if cy - 450 < H: im.paste(L, (int(cx - L.width / 2), int(cy - L.height / 2)), L)
    d = ImageDraw.Draw(im, "RGBA")
    if t < T_HOOK:
        hf = font(92, "round7"); hl = wrap(P["hook"], hf, 960)
        for n, l in enumerate(hl): d.text((W / 2, 230 + n * 104), l, font=hf, fill=CREAM, anchor="mm")
        if t > 1.1:
            kk = ease((t - 1.1) / 0.4); sf = font(78, "round7"); sl = wrap(P["hook_sub"], sf, 960)
            for n, l in enumerate(sl):
                d.text((W / 2, 1420 + n * 92 + (1 - kk) * 30), l, font=sf, fill=(255, 200, 70, int(255 * kk)), anchor="mm")
    elif t < T_END:
        j, tl = scene_at(t); s = SC[j]; kk = ease(tl / 0.4)
        if s.get("chip"):
            cf = font(50, "black"); cw = cf.getlength(s["chip"]) + 70; cc = tuple(s.get("chip_color", s["color"]))
            d.rounded_rectangle((W / 2 - cw / 2, 220, W / 2 + cw / 2, 300), 40, fill=cc + (int(255 * kk),))
            d.text((W / 2, 260), s["chip"], font=cf, fill=(255, 255, 255, int(255 * kk)), anchor="mm")
        tf = font(72, "round7"); tl_ = wrap(s["text"], tf, 940)
        y0 = 1430 - (len(tl_) - 1) * 44
        for n, l in enumerate(tl_):
            d.text((W / 2, y0 + n * 88 + (1 - kk) * 30), l, font=tf, fill=CREAM + (int(255 * kk),), anchor="mm")
        # progress dots
        for n in range(len(SC)):
            x = W / 2 + (n - (len(SC) - 1) / 2) * 44
            d.ellipse((x - 10, 1780 - 10, x + 10, 1780 + 10), fill=(255, 200, 70) if n <= j else (90, 60, 45))
    else:
        kk = ease((t - T_END) / 0.4); ef = font(86, "round7"); el = wrap(P["end"], ef, 900)
        for n, l in enumerate(el):
            d.text((W / 2, 900 + n * 104 - (len(el) - 1) * 52 + (1 - kk) * 40), l, font=ef, fill=(255, 200, 70, int(255 * kk)), anchor="mm")
    return im

# music: soft electric-piano chords Fmaj7 Em7 Dm7 Cmaj7, 2.4 s each, plus a slow pluck melody
au = Audio(TOTAL)
ep = lambda f, dur, v: Audio.tone(f, dur, 1.6, (1, .35, .12)) * v
chords = [[174.6, 220.0, 261.6, 329.6], [164.8, 196.0, 246.9, 293.7], [146.8, 174.6, 220.0, 261.6], [130.8, 164.8, 196.0, 246.9]]
mel = [523.3, 440.0, 493.9, 392.0, 440.0, 349.2, 392.0, 329.6]
bt, k = 0.0, 0
while bt < TOTAL:
    ch = chords[k % 4]
    au.add(bt, ep(ch[0] / 2, 3.0, .20), 1)
    for n, f in enumerate(ch): au.add(bt + .04 * n, ep(f, 2.6, .07), 1)
    au.add(bt + 1.2, Audio.tone(mel[(2 * k) % 8], 1.0, 4, (1, .2)), .09)
    au.add(bt + 1.8, Audio.tone(mel[(2 * k + 1) % 8], 1.0, 4, (1, .2)), .07)
    bt += 2.4; k += 1
for s0 in starts[:-1]: au.add(s0, Audio.noise(.25, 25), .05)
encode(OUT, frame, TOTAL, au)
