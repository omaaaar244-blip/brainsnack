"""Group-chat text story Short (2026-11-08): dark messenger UI, typing dots, bubbles pop in, generated blips.
usage: python3 renderers/chat.py puzzles/NNNN.json videos/NNNN.mp4
json: {"type":"chat","group":"the squad","group_emoji":"🍕","pov":"POV: ...",
       "people":{"Sam":[255,140,90],...},           # "Me" is always the right-hand blue bubble
       "msgs":[["Me","ok dinner saturday?","🍝"],["Sam","yesss"],["--","SATURDAY · 5:42 PM"],...],
       "gap":1.25,"end":"Tag the friend who..."}
A msg is [who, text] or [who, text, emoji]; who "--" draws a centred time divider.
"""
import json, math, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import W, H, FPS, font, ease, pop, wrap, load_emojis, paste, Audio, encode

P = json.load(open(sys.argv[1])); OUT = sys.argv[2]
BG = (12, 12, 16); BAR = (24, 24, 30); ME = (47, 124, 246); THEM = (38, 38, 44); WHITE = (245, 245, 250); GREY = (150, 150, 160)
MSGS, GAP = P["msgs"], P.get("gap", 1.25)
EM = load_emojis([P["group_emoji"]] + [m[2] for m in MSGS if len(m) > 2])
TF, NF, SF = font(54, "bold"), font(34, "bold"), font(32, "bold")
TOP, BOTTOM, MAXW = 560, 1720, 640
T0 = 0.7  # first message right after the POV hook appears

# layout + timing
items, y, t = [], TOP, T0
for m in MSGS:
    who, txt = m[0], m[1]; emo = m[2] if len(m) > 2 else None
    if who == "--":
        items.append(dict(kind="div", txt=txt, y=y, h=90, t=t + 0.3)); y += 110; t += GAP * 1.2; continue
    lines = wrap(txt, TF, MAXW); tw = max(TF.getlength(l) for l in lines)
    bw = tw + 64 + (82 if emo else 0); bh = 40 + 70 * len(lines)
    name_h = 0 if who == "Me" else 44
    typing = 0.0 if who == "Me" else 0.55
    items.append(dict(kind="msg", who=who, lines=lines, emo=emo, bw=bw, bh=bh, y=y + name_h, name_y=y, t=t + typing, ty=t))
    y += name_h + bh + 26; t += GAP + (0.25 * (len(lines) - 1))
T_END = t + 1.6; TOTAL = T_END + 2.6

def scroll_at(t):
    """content offset so the newest visible item sits above BOTTOM"""
    off = 0.0
    for it in items:
        if t >= it.get("ty", it["t"]):
            bottom = it["y"] + it["h" if it["kind"] == "div" else "bh"] + (60 if it["kind"] == "msg" and t < it["t"] else 0)
            need = bottom - BOTTOM
            if need > off:
                k = ease((t - it.get("ty", it["t"])) / 0.35); off = off + (need - off) * k
    return off

def header(im, d):
    d.rectangle((0, 0, W, 300), fill=BAR)
    d.text((70, 200), "‹", font=font(90, "bold"), fill=ME, anchor="lm")
    d.ellipse((150, 145, 260, 255), fill=(60, 60, 72)); paste(im, EM[P["group_emoji"]], 205, 200, 70)
    d.text((290, 178), P["group"], font=font(50, "black"), fill=WHITE, anchor="lm")
    d.text((290, 232), ", ".join(["you"] + list(P["people"])), font=SF, fill=GREY, anchor="lm")
    d.line((0, 300, W, 300), fill=(40, 40, 48), width=2)

def frame(i):
    t = i / FPS
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im, "RGBA")
    off = scroll_at(t)
    for it in items:
        if it["kind"] == "div":
            if t < it["t"]: continue
            k = ease((t - it["t"]) / 0.3); yy = it["y"] - off + 45
            if yy < 535: continue
            tw = SF.getlength(it["txt"]) + 60
            d.rounded_rectangle((W / 2 - tw / 2, yy - 30, W / 2 + tw / 2, yy + 30), 30, fill=(40, 40, 48, int(255 * k)))
            d.text((W / 2, yy), it["txt"], font=SF, fill=GREY + (int(255 * k),), anchor="mm"); continue
        me = it["who"] == "Me"; col = ME if me else THEM
        if t < it["ty"]: continue
        x0 = W - 50 - it["bw"] if me else 50
        if not me:
            ny = it["name_y"] - off
            if ny > 520: d.text((x0 + 20, ny + 18), it["who"], font=NF, fill=tuple(P["people"][it["who"]]), anchor="lm")
        yy = it["y"] - off
        if t < it["t"]:  # typing dots
            if yy > 520:
                d.rounded_rectangle((x0, yy, x0 + 170, yy + 100), 50, fill=col)
                for n in range(3):
                    a = 0.5 + 0.5 * math.sin(t * 9 - n * 0.9)
                    d.ellipse((x0 + 40 + n * 38 - 12, yy + 38, x0 + 40 + n * 38 + 12, yy + 62), fill=(200, 200, 210, int(110 + 145 * a)))
            continue
        k = pop((t - it["t"]) / 0.3)
        if yy + it["bh"] < 300: continue
        bw, bh = it["bw"] * (0.6 + 0.4 * k), it["bh"] * (0.6 + 0.4 * k)
        bx = W - 50 - bw if me else x0
        bub = Image.new("RGBA", (int(bw) + 2, int(bh) + 2), (0, 0, 0, 0)); bd = ImageDraw.Draw(bub)
        bd.rounded_rectangle((0, 0, bw, bh), 44, fill=col)
        if k > 0.85:
            for n, l in enumerate(it["lines"]):
                bd.text((32, 20 + 70 * n + 35), l, font=TF, fill=WHITE, anchor="lm")
            if it["emo"]: paste(bub, EM[it["emo"]], bw - 32 - 34, bh / 2, 68)
        im.paste(bub, (int(bx), int(yy)), bub)
    # cover anything scrolled under the header, then the header and the POV caption
    d.rectangle((0, 0, W, 300), fill=BAR); d.rectangle((0, 300, W, 535), fill=BG); header(im, d)
    k = ease(t / 0.4); pf = font(56, "black"); pl = wrap(P["pov"], pf, 940)
    ch = 40 + 70 * len(pl)
    d.rounded_rectangle((50, 320, W - 50, 320 + ch), 30, fill=(255, 214, 64, int(240 * k)))
    for n, l in enumerate(pl): d.text((W / 2, 320 + 20 + 35 + 70 * n), l, font=pf, fill=(20, 20, 20, int(255 * k)), anchor="mm")
    # input bar
    d.rectangle((0, 1760, W, H), fill=BAR)
    d.rounded_rectangle((50, 1790, W - 160, 1880), 45, fill=(40, 40, 48))
    d.text((90, 1835), "Message", font=SF, fill=GREY, anchor="lm")
    d.ellipse((W - 140, 1790, W - 50, 1880), fill=ME); d.text((W - 95, 1833), "↑", font=font(50, "black"), fill=WHITE, anchor="mm")
    if t > T_END:
        k = ease((t - T_END) / 0.4)
        d.rectangle((0, 0, W, H), fill=(0, 0, 0, int(215 * k)))
        ef = font(80, "black"); el = wrap(P["end"], ef, 820); ch = 80 + 100 * len(el); cy = 960 + (1 - k) * 40
        d.rounded_rectangle((90, cy - ch / 2, W - 90, cy + ch / 2), 50, fill=(255, 214, 64, int(255 * k)))
        for n, l in enumerate(el):
            d.text((W / 2, cy - (len(el) - 1) * 50 + n * 100), l, font=ef, fill=(20, 20, 20, int(255 * k)), anchor="mm")
    return im

au = Audio(TOTAL)
for it in items:
    if it["kind"] == "div": au.add(it["t"], Audio.tone(330, .5, 5, (1, .3)), .18); continue
    if it["who"] == "Me": au.add(it["t"], Audio.tone(1320, .18, 22, (1, .2)), .30); au.add(it["t"] + .04, Audio.tone(1760, .16, 22), .18)
    else: au.add(it["t"], Audio.tone(880, .22, 18, (1, .25)), .30); au.add(it["t"] + .06, Audio.tone(660, .2, 18), .18)
au.add(T_END, Audio.tone(523, 1.2, 3, (1, .4, .2)), .25); au.add(T_END + .15, Audio.tone(659, 1.2, 3, (1, .4)), .2); au.add(T_END + .3, Audio.tone(784, 1.4, 3, (1, .4)), .2)
encode(OUT, frame, TOTAL, au)
