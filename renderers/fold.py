"""Paper-folding doubling Short (2026-11-10): a 0.1 mm sheet folded 42 times, thickness computed live (0.1 mm * 2^n),
sky -> space background, milestone stops with Twemoji, generated rising tones.
usage: python3 renderers/fold.py puzzles/NNNN.json videos/NNNN.mp4
json: {"type":"fold","mm":0.1,"folds":42,"hook":"...","milestones":[[n,"emoji","label"],...],"end":[...]}
"""
import json, os, sys, random
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import W, H, FPS, font, ease, pop, wrap, Audio, encode, load_emojis, paste

P = json.load(open(sys.argv[1])); OUT = sys.argv[2]
MM, N = P.get("mm", 0.1), P.get("folds", 42)
MS = {m[0]: (m[1], m[2]) for m in P["milestones"]}
EM = load_emojis([m[1] for m in P["milestones"]] + ["📄"], 300)
T0, STEP, HOLD = 2.2, 0.26, 1.15
times = []; t = T0
for n in range(1, N + 1):
    times.append(t); t += STEP + (HOLD if n in MS and n != N else 0)
T_END = times[-1] + 2.4
TOTAL = T_END + 4.6

def fmt(mm):
    if mm < 10: return f"{mm:.1f} mm"
    if mm < 1000: return f"{mm/10:.1f} cm"
    if mm < 1e6: return f"{mm/1000:,.1f} m"
    return f"{mm/1e6:,.1f} km" if mm < 1e8 else f"{mm/1e6:,.0f} km"

def lerp(a, b, k): return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))
SKY = [(0, (150, 205, 245)), (14, (90, 150, 220)), (24, (40, 70, 150)), (30, (10, 14, 40)), (42, (3, 3, 10))]
def bg(nf):
    for (a, ca), (b, cb) in zip(SKY, SKY[1:]):
        if nf <= b: return lerp(ca, cb, (nf - a) / (b - a))
    return SKY[-1][1]
STARS = [(random.Random(s).randint(0, W), random.Random(s + 999).randint(0, H), random.Random(s + 7).choice([2, 3, 4])) for s in range(140)]

def folds_at(t):
    n = sum(1 for x in times if x <= t); prog = 0.0
    if n < N:
        nxt = times[n]; prog = ease((t - (nxt - STEP)) / STEP) if t > nxt - STEP else 0
    return n, n + prog

def frame(i):
    t = i / FPS; n, nf = folds_at(t)
    top, bot = bg(nf), lerp(bg(nf), (0, 0, 0), .35)
    im = Image.new("RGB", (W, H), top); d = ImageDraw.Draw(im)
    for y in range(0, H, 8): d.rectangle((0, y, W, y + 8), fill=lerp(top, bot, y / H))
    if nf > 26:
        a = min(1, (nf - 26) / 6)
        for x, y, r in STARS: d.ellipse((x, y, x + r, y + r), fill=lerp(top, (255, 255, 255), a * .9))
    dark = nf > 18; fg = (255, 255, 255) if dark else (15, 25, 45); sub = (200, 210, 230) if dark else (40, 60, 95)
    y = 190
    for ln in wrap(P["hook"], font(66, "black"), 960):
        d.text((W / 2, y), ln, font=font(66, "black"), fill=fg, anchor="mm"); y += 82
    if t < T0: d.text((W / 2, y + 30), P.get("sub", ""), font=font(40, "bold"), fill=sub, anchor="mm")
    # paper card with a folding flap
    cx, cy, pw, ph = W / 2, 760, 300, 380
    flap = 0
    if n < N and t > times[n] - STEP and t >= T0 - STEP: flap = ease((t - (times[n] - STEP)) / STEP)
    d.rectangle((cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2), fill=(250, 250, 245), outline=(180, 180, 175), width=3)
    if flap > 0:
        fw = pw / 2 * (1 - 2 * flap); x0 = cx + min(0, fw); x1 = cx + max(0, fw)
        d.rectangle((x0, cy - ph / 2, x1, cy + ph / 2), fill=(225, 225, 218) if flap < .5 else (235, 235, 228), outline=(170, 170, 165), width=3)
    lay = min(n, 5)
    for k in range(1, 2 ** lay):
        yy = cy - ph / 2 + ph * k / 2 ** lay; d.line((cx - pw / 2 + 12, yy, cx + pw / 2 - 12, yy), fill=(215, 215, 210), width=1)
    # counters
    d.text((W / 2, 1050), f"FOLD {n}", font=font(60, "black"), fill=sub, anchor="mm")
    d.text((W / 2, 1160), fmt(MM * 2 ** n), font=font(120, "black"), fill=fg, anchor="mm")
    d.text((W / 2, 1255), f"{2 ** n:,} layer" + ("s" if n else ""), font=font(40, "bold"), fill=sub, anchor="mm")
    # milestone
    last = max([m for m in MS if m <= n], default=None)
    if last is not None and n == last:
        tm = times[last - 1]; k = pop((t - tm) / 0.35)
        e, lab = MS[last]; paste(im, EM[e], W / 2, 1460, 230 * k); d = ImageDraw.Draw(im)
        for j, ln in enumerate(wrap(lab, font(50, "bold"), 940)):
            d.text((W / 2, 1640 + j * 62), ln, font=font(50, "bold"), fill=fg, anchor="mm")
    if t > T_END:
        k = ease((t - T_END) / 0.4)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, int(225 * k))); im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
        y = 640
        for j, para in enumerate(P["end"]):
            f = font(68 if j == 0 else 48, "black" if j == 0 else "bold")
            for ln in wrap(para, f, 940):
                d.text((W / 2, y), ln, font=f, fill=(255, 255, 255) if j < 2 else (190, 200, 220), anchor="mm"); y += f.size * 1.25
            y += 40
    return im

au = Audio(TOTAL)
for n, tm in enumerate(times, 1):
    au.add(tm - 0.05, Audio.noise(0.12, 45), .05)
    au.add(tm, Audio.tone(196 * 2 ** (n / 14), 0.18, 18, (1, .3, .1)), .2)
    if n in MS: au.add(tm, Audio.tone(392 * 2 ** (n / 28), 1.0, 3.5, (1, .5, .2)), .22)
au.add(T_END, Audio.tone(523, 1.8, 2, (1, .4, .2)), .25); au.add(T_END, Audio.tone(659, 1.8, 2), .18); au.add(T_END, Audio.tone(784, 1.8, 2), .15)
print("final", fmt(MM * 2 ** N))
encode(OUT, frame, TOTAL, au)
