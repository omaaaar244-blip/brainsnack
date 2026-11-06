"""Recipe card Short (2026-11-06): warm cream card, ingredients then one step at a time, generated marimba.
usage: python3 renderers/recipe.py puzzles/NNNN.json videos/NNNN.mp4
json: {"type":"recipe","tag":"NO YEAST · 10 MIN","title":"2-Ingredient Flatbread","hero":"🫓",
       "hook":"2 ingredients. No yeast.","ingredients":[["🌾","1 cup","self-rising flour"],...],
       "steps":[["🥣","Mix into a soft dough"],...],"beat":2.7,"end":"Save this for tonight"}
A step text starting with "TIP:" is drawn as a tip card.
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import W, H, FPS, font, ease, pop, wrap, load_emojis, paste, Audio, encode

P = json.load(open(sys.argv[1])); OUT = sys.argv[2]
BG = (250, 242, 228); INK = (44, 32, 26); ACC = (222, 84, 48); SOFT = (238, 224, 202); CARD = (255, 251, 244); GREEN = (70, 140, 80)
ING, STEPS, BEAT = P["ingredients"], P["steps"], P.get("beat", 2.7)
EM = load_emojis([P["hero"]] + [i[0] for i in ING] + [s[0] for s in STEPS])
T_HOOK = 1.8; T_ING = T_HOOK; T_STEPS = T_ING + 1.0 + 1.1 * len(ING); T_END = T_STEPS + BEAT * len(STEPS); TOTAL = T_END + 2.6

title_f = font(108, "round7")
while title_f.getlength(P["title"]) > 980: title_f = font(title_f.size - 4, "round7")

def header(d, t):
    k = ease(t / 0.3)
    tf = font(40, "black"); tw = tf.getlength(P["tag"]) + 60
    d.rounded_rectangle((W / 2 - tw / 2, 150, W / 2 + tw / 2, 214), 32, fill=ACC)
    d.text((W / 2, 182), P["tag"], font=tf, fill=(255, 255, 255), anchor="mm")
    d.text((W / 2, 300 + (1 - k) * 30), P["title"], font=title_f, fill=INK, anchor="mm")

def progress(d, t):
    n = len(STEPS); x0, x1, y = 120, W - 120, 1770
    d.rounded_rectangle((x0, y - 8, x1, y + 8), 8, fill=SOFT)
    if t >= T_STEPS:
        f = min(1.0, (t - T_STEPS) / (BEAT * n))
        d.rounded_rectangle((x0, y - 8, x0 + (x1 - x0) * f, y + 8), 8, fill=ACC)

def frame(i):
    t = i / FPS
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im, "RGBA")
    # subtle checkered tablecloth strip at the bottom
    for x in range(0, W, 60):
        for r in range(3):
            if (x // 60 + r) % 2 == 0: d.rectangle((x, 1830 + r * 30, x + 60, 1860 + r * 30), fill=(232, 120, 96, 90))
    header(d, t)
    if t < T_HOOK:
        k = pop(t / 0.5); paste(im, EM[P["hero"]], W / 2, 900 + 10 * math.sin(t * 3), 560 * k)
        d.text((W / 2, 1360), P["hook"], font=font(78, "round7"), fill=ACC, anchor="mm")
    elif t < T_STEPS:
        d.text((W / 2, 520), "YOU NEED", font=font(48, "black"), fill=ACC, anchor="mm")
        for n, (e, qty, name) in enumerate(ING):
            k = ease((t - T_ING - 0.2 - n * 1.1) / 0.35)
            if k <= 0: continue
            y = 760 + n * 330; x = (1 - k) * 200
            d.rounded_rectangle((90 + x, y - 135, W - 90 + x, y + 135), 40, fill=CARD + (int(255 * k),), outline=SOFT, width=4)
            paste(im, EM[e], 250 + x, y, 190, k)
            d.text((390 + x, y - 40), qty, font=font(72, "round7"), fill=ACC + (int(255 * k),), anchor="lm")
            d.text((390 + x, y + 40), name, font=font(54, "round"), fill=INK + (int(255 * k),), anchor="lm")
            if n < len(ING) - 1 and t > T_ING + 0.2 + (n + 1) * 1.1:
                d.text((W / 2, y + 165), "+", font=font(90, "round7"), fill=INK, anchor="mm")
    elif t < T_END:
        j = int((t - T_STEPS) // BEAT); tl = t - T_STEPS - j * BEAT
        e, txt = STEPS[j]; tip = txt.startswith("TIP:")
        k = ease(tl / 0.35)
        if tip:
            d.rounded_rectangle((90, 560, W - 90, 1560), 50, fill=(255, 236, 170), outline=(240, 200, 90), width=6)
            d.text((W / 2, 650), "TIP", font=font(56, "black"), fill=(170, 110, 0), anchor="mm")
            txt = txt[4:].strip()
        else:
            d.text((W / 2, 560), f"STEP {sum(1 for s in STEPS[:j + 1] if not s[1].startswith('TIP:'))}",
                   font=font(52, "black"), fill=ACC, anchor="mm")
        paste(im, EM[e], W / 2, 900 + (1 - k) * 60 + 8 * math.sin(t * 3), 420 * pop(tl / 0.45), k)
        lf = font(70, "round7"); ls = wrap(txt, lf, 860)
        for n, l in enumerate(ls):
            d.text((W / 2, 1260 + n * 92 - (len(ls) - 1) * 20), l, font=lf, fill=INK + (int(255 * k),), anchor="mm")
    else:
        tl = t - T_END
        paste(im, EM[P["hero"]], W / 2, 880, 560 * pop(tl / 0.5))
        d.text((W / 2, 1300), "Done.", font=font(110, "round7"), fill=ACC, anchor="mm")
        if tl > 0.6:
            k = ease((tl - 0.6) / 0.3)
            for n, l in enumerate(wrap(P.get("end", "Save this for later"), font(60, "round"), 900)):
                d.text((W / 2, 1450 + n * 80), l, font=font(60, "round"), fill=INK + (int(255 * k),), anchor="mm")
    progress(d, t)
    return im

# ---------------- music: light marimba groove in C major, 112 bpm ----------------
A = Audio(TOTAL); bt = 60 / 112
chords = [[261.6, 329.6, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7]]
mar = lambda f, dur=.35: Audio.tone(f, dur, 9, (1.0, 0.0, 0.0, 0.25))
n_beats = int(TOTAL / bt) + 1
for b in range(n_beats):
    ch = chords[(b // 4) % 4]; t0 = b * bt
    A.add(t0, Audio.tone(ch[0] / 2, .5, 5), .22)                       # bass
    A.add(t0 + bt / 2, mar(ch[(b % 3)] * 2), .12)                        # off-beat marimba
    if b % 2 == 0: A.add(t0, mar(ch[2] * 2), .10)
    A.add(t0 + bt / 2, Audio.noise(.05, 80), .03)                        # shaker
A.add(0.0, Audio.tone(1046.5, .6, 5), .25)
for j in range(len(STEPS)): A.add(T_STEPS + j * BEAT, mar(784.0, .4), .25)
for j, f in enumerate([523.3, 659.3, 784.0, 1046.5]): A.add(T_END + j * .09, mar(f, .8), .25)
encode(OUT, frame, TOTAL, A)
