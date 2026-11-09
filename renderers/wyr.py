"""'Would you rather' Short (2026-11-09): split screen red/blue cards, emoji, OR badge, countdown bar, ticks.
No fake vote percentages; the viewer answers in the comments (e.g. "ABBAB").
usage: python3 renderers/wyr.py puzzles/NNNN.json videos/NNNN.mp4
json: {"type":"wyr","hook":"...","rounds":[["option A","🅰emoji","option B","emoji"],...],"secs":3.2,"end":"..."}
"""
import json, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import W, H, FPS, font, ease, pop, wrap, load_emojis, paste, Audio, encode

P = json.load(open(sys.argv[1])); OUT = sys.argv[2]
R, SECS = P["rounds"], P.get("secs", 3.2)
EM = load_emojis([r[1] for r in R] + [r[3] for r in R])
RED, BLUE, WHITE = (232, 64, 76), (44, 110, 235), (250, 250, 252)
T0 = 0.15; TOTAL = T0 + SECS * len(R) + 3.0
TOPY, MID, BOT = 250, 1085, 1920

def card(im, d, y0, y1, color, letter, txt, emo, k):
    d.rectangle((0, y0, W, y1), fill=color)
    cy = (y0 + y1) / 2
    paste(im, EM[emo], W / 2, cy - 150, 230 * pop(k))
    f = font(66, "black"); lines = wrap(txt, f, 900); y = cy + 40 + (0 if len(lines) == 1 else -30)
    for ln in lines:
        d.text((W / 2, y), ln, font=f, fill=WHITE, anchor="mm"); y += 80
    d.text((60, y0 + 50), letter, font=font(70, "black"), fill=(255, 255, 255, 150), anchor="lt")

def frame(i):
    t = i / FPS
    im = Image.new("RGB", (W, H), (14, 14, 18)); d = ImageDraw.Draw(im, "RGBA")
    d.text((W / 2, 130), P["hook"], font=font(64, "black"), fill=WHITE, anchor="mm")
    r = min(len(R) - 1, max(0, int((t - T0) // SECS)))
    lt = t - T0 - r * SECS
    if t >= T0 + SECS * len(R):
        lt = SECS
    k = ease(lt / 0.35) if t >= T0 else 0
    a_txt, a_em, b_txt, b_em = R[r]
    sl = int((1 - k) * W)
    card(im, d, TOPY, MID - 10, RED, "A", a_txt, a_em, k)
    card(im, d, MID + 10, BOT - 150, BLUE, "B", b_txt, b_em, k)
    if sl > 0: d.rectangle((W - sl, TOPY, W, BOT - 150), fill=(14, 14, 18))
    rr = 85 * pop(k); d.ellipse((W / 2 - rr, MID - rr, W / 2 + rr, MID + rr), fill=(20, 20, 24), outline=WHITE, width=6)
    if rr > 30: d.text((W / 2, MID), "OR", font=font(int(54 * rr / 85), "black"), fill=WHITE, anchor="mm")
    # countdown bar + round counter
    p = 1 - min(1, max(0, lt / SECS)) if t >= T0 else 1
    d.rectangle((0, BOT - 150, W, BOT), fill=(14, 14, 18))
    d.rounded_rectangle((80, BOT - 100, 80 + 920 * p, BOT - 70), 15, fill=(255, 210, 70))
    d.text((W / 2, BOT - 125), f"{r + 1} / {len(R)}  ·  remember your letter", font=font(34, "bold"), fill=(170, 170, 180), anchor="mm")
    if t >= T0 + SECS * len(R):
        q = ease((t - T0 - SECS * len(R)) / 0.4)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, int(225 * q))); im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
        y = 820
        for ln in wrap(P["end"], font(72, "black"), 900):
            d.text((W / 2, y), ln, font=font(72, "black"), fill=WHITE, anchor="mm"); y += 92
        d.text((W / 2, y + 70), "e.g.  A B B A B", font=font(60, "black"), fill=(255, 210, 70), anchor="mm")
    return im

au = Audio(TOTAL)
for n in range(len(R)):
    t = T0 + n * SECS
    au.add(t, Audio.noise(0.25, 18), .12); au.add(t + .05, Audio.tone(660, .3, 10, (1, .3)), .25)
    for s in range(1, int(SECS) + 1): au.add(t + s - 0.15, Audio.tone(1200, .05, 60), .18)
te = T0 + SECS * len(R)
for j, f in enumerate((523, 659, 784, 1047)): au.add(te + j * .09, Audio.tone(f, .6, 5, (1, .3)), .22)
encode(OUT, frame, TOTAL, au)
