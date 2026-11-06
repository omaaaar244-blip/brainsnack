"""Myth-buster list Short (2026-11-06): dark navy, each myth shown, stamped MYTH, then the truth. Generated beat.
usage: python3 renderers/myth.py puzzles/NNNN.json videos/NNNN.mp4
json: {"type":"myth","hook":"5 \"FACTS\" THAT ARE FALSE","sub":"#3 fooled everyone",
       "items":[["🐟","Goldfish have a 3-second memory","They can remember things for months"],...],
       "myth_s":1.4,"truth_s":2.5,"outro":"Which one fooled you? Comment the number"}
"""
import json, math, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import W, H, FPS, font, ease, pop, wrap, load_emojis, paste, Audio, encode

P = json.load(open(sys.argv[1])); OUT = sys.argv[2]
BG = (14, 20, 38); WHITE = (240, 242, 248); RED = (240, 58, 70); GREEN = (60, 210, 120); DIM = (120, 128, 150)
ITEMS = P["items"]; MS, TS = P.get("myth_s", 1.4), P.get("truth_s", 2.5); SEG = MS + TS
EM = load_emojis([i[0] for i in ITEMS])
T0 = 1.3; T_OUT = T0 + SEG * len(ITEMS); TOTAL = T_OUT + 2.4
hook_f = font(96, "black")
hook_ls = wrap(P["hook"], hook_f, 960)

def stamp(txt, col, ang, scale):
    f = font(110, "black"); tw = int(f.getlength(txt)) + 80
    s = Image.new("RGBA", (tw, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(s)
    d.rounded_rectangle((6, 6, tw - 6, 184), 24, outline=col, width=12)
    d.text((tw / 2, 95), txt, font=f, fill=col, anchor="mm")
    s = s.resize((max(2, int(tw * scale)), max(2, int(190 * scale)))); return s.rotate(ang, expand=True, resample=Image.BICUBIC)

def frame(i):
    t = i / FPS
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im, "RGBA")
    # faint grid backdrop
    for x in range(0, W, 90): d.line((x, 0, x, H), fill=(255, 255, 255, 8), width=2)
    for y in range(0, H, 90): d.line((0, y, W, y), fill=(255, 255, 255, 8), width=2)
    if t < T0:
        k = ease(t / 0.3)
        for n, l in enumerate(hook_ls):
            d.text((W / 2, 820 + n * 115 - (len(hook_ls) - 1) * 57 + (1 - k) * 40), l, font=hook_f, fill=WHITE + (int(255 * k),), anchor="mm")
        if P.get("sub"): d.text((W / 2, 1120), P["sub"], font=font(54), fill=RED, anchor="mm")
        return im
    # small persistent header
    d.text((W / 2, 200), P.get("header", "MYTH OR TRUTH?"), font=font(54, "black"), fill=DIM, anchor="mm")
    if t >= T_OUT:
        k = ease((t - T_OUT) / 0.3)
        for n, l in enumerate(wrap(P.get("outro", "Follow for more"), font(80, "black"), 920)):
            d.text((W / 2, 880 + n * 105), l, font=font(80, "black"), fill=WHITE + (int(255 * k),), anchor="mm")
        return im
    j = int((t - T0) // SEG); tl = t - T0 - j * SEG; e, myth, truth = ITEMS[j]
    d.text((W / 2, 380), f"#{j + 1}", font=font(90, "black"), fill=WHITE, anchor="mm")  # item number
    k = ease(tl / 0.3)
    paste(im, EM[e], W / 2, 700 + 8 * math.sin(t * 3), 300 * (0.7 + 0.3 * k), k)
    mf = font(70); mls = wrap(f"“{myth}”", mf, 920)
    my0 = 1020
    for n, l in enumerate(mls):
        y = my0 + n * 92
        d.text((W / 2, y), l, font=mf, fill=(WHITE if tl < MS else DIM) + (int(255 * k),), anchor="mm")
        if tl >= MS - 0.5:  # strike-through grows
            sk = ease((tl - (MS - 0.5)) / 0.3); lw = mf.getlength(l)
            d.line((W / 2 - lw / 2, y + 4, W / 2 - lw / 2 + lw * sk, y + 4), fill=RED, width=8)
    if tl >= MS - 0.5:
        st = stamp("MYTH", RED, 10, pop((tl - (MS - 0.5)) / 0.25) * 0.8)
        im.paste(st, (int(W / 2 + 300 - st.width / 2), int(620 - st.height / 2)), st)
    if tl >= MS:
        kk = ease((tl - MS) / 0.3); ty = my0 + len(mls) * 92 + 90
        d.text((W / 2, ty + (1 - kk) * 30), "TRUTH", font=font(56, "black"), fill=GREEN + (int(255 * kk),), anchor="mm")
        tf = font(72, "black"); tls = wrap(truth, tf, 940)
        for n, l in enumerate(tls):
            d.text((W / 2, ty + 100 + n * 94 + (1 - kk) * 30), l, font=tf, fill=WHITE + (int(255 * kk),), anchor="mm")
    # progress pips
    for n in range(len(ITEMS)):
        x = W / 2 + (n - (len(ITEMS) - 1) / 2) * 56
        d.rounded_rectangle((x - 20, 1735, x + 20, 1747), 6, fill=(GREEN if n < j else WHITE if n == j else (50, 58, 80)))
    return im

# ---------------- beat: minor-key pulse, 100 bpm, stamp thuds ----------------
A = Audio(TOTAL); bt = 0.6
bass = [110.0, 110.0, 87.3, 98.0]
for b in range(int(TOTAL / bt) + 1):
    t0 = b * bt
    A.add(t0, Audio.tone(55, .35, 9), .45)                                  # kick-ish
    A.add(t0, Audio.tone(bass[(b // 4) % 4], .5, 5, (1, .3)), .18)
    A.add(t0 + bt / 2, Audio.noise(.04, 90), .05)                          # hat
A.add(0, Audio.tone(220, 1.0, 3, (1, .5, .3)), .25)
for j in range(len(ITEMS)):
    s = T0 + j * SEG
    A.add(s + MS - 0.5, Audio.noise(.15, 25), .35); A.add(s + MS - 0.5, Audio.tone(70, .3, 10), .5)   # stamp
    A.add(s + MS, Audio.tone(880, .5, 6), .18); A.add(s + MS + .08, Audio.tone(1318.5, .6, 6), .15)  # truth ding
encode(OUT, frame, TOTAL, A)
