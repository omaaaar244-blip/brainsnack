"""Brain Snack short renderer.
usage: python3 render_short.py puzzle.json out.mp4

Puzzle types (all share: number, hook, answer, explain?, seconds?):
  emoji_guess : {"type":"emoji_guess","hook":"GUESS THE MOVIE","emojis":["🚢","🧊","💔"],"answer":"Titanic"}
  odd_one_out : {"type":"odd_one_out","hook":"FIND THE ODD ONE","base":"🐱","odd":"🐯","cols":6,"rows":8,"pos":[3,5]}
  riddle      : {"type":"riddle","hook":"RIDDLE TIME","question":"What has keys\\nbut can't open locks?","answer":"A piano"}
  scramble    : {"type":"scramble","hook":"UNSCRAMBLE THE WORD","letters":"NAABNA","answer":"BANANA","hint":"A yellow fruit"}
"""
import json, math, os, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(sys.argv[1])); OUT = sys.argv[2]
TYPE = P["type"]
W, H, FPS = 1080, 1920, 30
INK = (36, 18, 63); BG = (42, 22, 80); CARD = (59, 36, 112); YEL = (255, 200, 61)
PINK = (255, 143, 179); WHITE = (246, 240, 255); GREEN = (90, 220, 160)
F7 = os.path.join(D, "assets/fredoka700.ttf"); F6 = os.path.join(D, "assets/fredoka600.ttf")
_fc = {}
def font(s, b=True):
    k = (int(s), b)
    if k not in _fc: _fc[k] = ImageFont.truetype(F7 if b else F6, int(s))
    return _fc[k]
MS = 360
mascot = Image.open(os.path.join(D, "assets/brain_transparent.png")).convert("RGBA").resize((MS, MS), Image.LANCZOS)

def ease_out_back(t):
    t = max(0, min(1, t)); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def clamp(t): return max(0.0, min(1.0, t))

# ---------- emoji rasterising (Twemoji, CC-BY 4.0) ----------
EMO_DIR = os.path.join(D, "assets/twemoji")
def emoji_file(e):
    cps = [f"{ord(c):x}" for c in e]
    for cand in ("-".join(cps), "-".join(c for c in cps if c != "fe0f")):
        p = os.path.join(EMO_DIR, cand + ".svg")
        if os.path.exists(p): return p
    raise SystemExit(f"no twemoji for {e!r} ({'-'.join(cps)})")
def load_emojis(chars, px=320):
    from playwright.sync_api import sync_playwright
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": px, "height": px})
        for e in dict.fromkeys(chars):
            svg = open(emoji_file(e)).read()
            pg.set_content(f'<html><body style="margin:0;background:transparent"><div style="width:{px}px;height:{px}px">{svg}</div>'
                           f'<style>svg{{width:{px}px;height:{px}px;display:block}}</style></body></html>')
            pg.screenshot(path="/tmp/_emo.png", omit_background=True)
            out[e] = Image.open("/tmp/_emo.png").convert("RGBA").copy()
        b.close()
    return out

# ---------- content setup per type ----------
items = []          # things that pop in one by one during the "question" phase
if TYPE == "emoji_guess":
    EM = load_emojis(P["emojis"]); items = P["emojis"]
elif TYPE == "odd_one_out":
    EM = load_emojis([P["base"], P["odd"]])
    cols, rows = P.get("cols", 6), P.get("rows", 6)
    if "pos" not in P:
        random.seed(P.get("number", 1) * 7); P["pos"] = [random.randrange(cols), random.randrange(rows)]
    items = ["grid"]
elif TYPE == "scramble":
    items = list(P["letters"])
else:
    items = ["q"]

T_INTRO = 1.0
T_ITEM = {"emoji_guess": 0.45, "scramble": 0.18}.get(TYPE, 0.0)
t_q_end = T_INTRO + len(items) * T_ITEM + 0.5
N = int(P.get("seconds", {"odd_one_out": 10, "riddle": 8}.get(TYPE, 7)))
t_cd0 = t_q_end; t_reveal = t_cd0 + N
TOTAL = t_reveal + 4.6
NF = int(TOTAL * FPS)

# ---------- static background ----------
bg = Image.new("RGB", (W, H), BG)
g = Image.new("L", (W, H), 0); ImageDraw.Draw(g).ellipse((-200, 300, W + 200, H - 300), fill=90)
g = g.filter(ImageFilter.GaussianBlur(220))
bg = Image.composite(Image.new("RGB", (W, H), (70, 40, 130)), bg, g)
random.seed(P.get("number", 1))
floaters = [(random.uniform(0, W), random.uniform(0, H), random.uniform(.6, 1.5), random.choice([YEL, PINK, (123, 92, 255), WHITE]),
             random.uniform(.05, .11), random.uniform(0, 6.28)) for _ in range(16)]
confetti = [(random.uniform(-1, 1), random.uniform(-1.6, -0.6), random.choice([YEL, PINK, (123, 92, 255), WHITE, GREEN]),
             random.uniform(10, 22)) for _ in range(90)]

def text_c(d, xy, s, f, fill, anchor="mm", stroke=0, sf=None):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sf)
def fit(s, maxw, start, bold=True):
    size = start
    while size > 30:
        f = font(size, bold)
        if max(f.getlength(l) for l in s.split("\n")) <= maxw: return f
        size -= 4
    return font(30, bold)

HOOK = P.get("hook", "CAN YOU SOLVE THIS?")
hook_f = fit(HOOK, 940, 96)
ANS = P.get("answer", "")
CARD_BOX = (70, 470, W - 70, 1060) if TYPE != "odd_one_out" else (60, 450, W - 60, 1130)

# grid geometry for odd_one_out
if TYPE == "odd_one_out":
    gx0, gy0, gx1, gy1 = CARD_BOX[0] + 40, CARD_BOX[1] + 40, CARD_BOX[2] - 40, CARD_BOX[3] - 40
    cell = min((gx1 - gx0) / cols, (gy1 - gy0) / rows)
    esz = int(cell * 0.82)
    E_base = EM[P["base"]].resize((esz, esz), Image.LANCZOS); E_odd = EM[P["odd"]].resize((esz, esz), Image.LANCZOS)
    ox = gx0 + ((gx1 - gx0) - cell * cols) / 2; oy = gy0 + ((gy1 - gy0) - cell * rows) / 2
    def cell_c(c, r): return ox + cell * c + cell / 2, oy + cell * r + cell / 2

def draw_content(im, d, t, revealed):
    if TYPE == "emoji_guess":
        n = len(items); sz = min(230, int(820 / n) - 20); gap = 24
        tw = n * sz + (n - 1) * gap; x = W / 2 - tw / 2; y = 680 if not revealed else 640
        for j, e in enumerate(items):
            k = ease_out_back((t - (T_INTRO + j * T_ITEM)) / 0.35)
            if k <= 0: x += sz + gap; continue
            s = max(1, int(sz * k)); em = EM[e].resize((s, s), Image.LANCZOS)
            wob = 6 * math.sin(t * 4 + j)
            im.paste(em, (int(x + sz / 2 - s / 2), int(y - s / 2 + wob)), em); x += sz + gap
        if revealed:
            kk = ease_out_back((t - t_reveal) / 0.4)
            f2 = fit(ANS.upper(), 860, 96)
            text_c(d, (W / 2, 920 - (1 - kk) * 40), ANS.upper(), f2, YEL, stroke=6, sf=INK)
    elif TYPE == "odd_one_out":
        k = clamp((t - T_INTRO) / 0.5)
        if k <= 0: return
        oc, orow = P["pos"]
        for r in range(rows):
            for c in range(cols):
                kk = ease_out_back((t - T_INTRO - 0.02 * (r * cols + c) * 0.5) / 0.3)
                if kk <= 0: continue
                cx, cy = cell_c(c, r); e = E_odd if (c, r) == (oc, orow) else E_base
                s = max(1, int(esz * min(kk, 1.15)))
                em = e if s == esz else e.resize((s, s), Image.LANCZOS)
                if revealed and (c, r) != (oc, orow):
                    em = em.copy(); a = em.getchannel("A").point(lambda v: int(v * 0.3)); em.putalpha(a)
                im.paste(em, (int(cx - s / 2), int(cy - s / 2)), em)
        if revealed:
            cx, cy = cell_c(oc, orow); kk = ease_out_back((t - t_reveal) / 0.4); r0 = cell * 0.62 * max(kk, .01)
            d.ellipse((cx - r0, cy - r0, cx + r0, cy + r0), outline=YEL, width=12)
    elif TYPE == "riddle":
        k = clamp((t - T_INTRO) / 0.4)
        qf = fit(P["question"], 860, 92)
        y = 700 if not revealed else 640
        d.multiline_text((W / 2, y), P["question"], font=qf, fill=WHITE + (int(255 * k),), anchor="mm", align="center", spacing=20)
        if revealed:
            kk = ease_out_back((t - t_reveal) / 0.4); f2 = fit(ANS.upper(), 860, 100)
            text_c(d, (W / 2, 940 - (1 - kk) * 40), ANS.upper(), f2, YEL, stroke=6, sf=INK)
    elif TYPE == "scramble":
        word = ANS.upper() if revealed else P["letters"].upper()
        n = len(word); ts = min(130, int(880 / n) - 12); gap = 12; tw = n * ts + (n - 1) * gap
        x0 = W / 2 - tw / 2; y = 690
        for j, ch in enumerate(word):
            k = ease_out_back((t - (T_INTRO + j * T_ITEM)) / 0.3) if not revealed else ease_out_back((t - t_reveal - j * 0.06) / 0.3)
            if k <= 0: continue
            x = x0 + j * (ts + gap); yy = y - (1 - k) * 50
            d.rounded_rectangle((x, yy - ts / 2, x + ts, yy + ts / 2), 22, fill=(YEL if revealed else WHITE) + (int(255 * clamp(k)),))
            text_c(d, (x + ts / 2, yy + 4), ch, font(int(ts * 0.62)), INK)
        if P.get("hint") and t >= T_INTRO + 0.6 and not revealed:
            text_c(d, (W / 2, 900), "Hint: " + P["hint"], fit("Hint: " + P["hint"], 820, 56, False), PINK)

def frame(i):
    t = i / FPS
    im = bg.copy(); d = ImageDraw.Draw(im, "RGBA")
    for (x, y, s, c, op, ph) in floaters:
        yy = (y - t * 22 * s) % (H + 200) - 100
        d.text((x + 12 * math.sin(t + ph), yy), "?", font=font(int(70 * s)), fill=c + (int(255 * op),), anchor="mm")
    pill = f"PUZZLE #{P.get('number', 1)}"; pf = font(44)
    pw = pf.getlength(pill) + 70; k = ease_out_back(t / 0.5)
    if k > 0:
        x0 = W / 2 - pw / 2; y0 = 140 - (1 - k) * 80
        d.rounded_rectangle((x0, y0, x0 + pw, y0 + 76), 38, fill=PINK); text_c(d, (W / 2, y0 + 38), pill, pf, INK)
    k = ease_out_back((t - 0.2) / 0.5)
    if k > 0:
        hl = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); text_c(ImageDraw.Draw(hl), (W / 2, 130), HOOK, hook_f, YEL, stroke=8, sf=INK)
        sc = max(0.01, k); hl = hl.resize((int(W * sc), int(260 * sc)))
        im.paste(hl, (int(W / 2 - hl.width / 2), int(320 - hl.height / 2)), hl)
    k = clamp((t - 0.4) / 0.4)
    if k > 0:
        x0, y0, x1, y1 = CARD_BOX
        d.rounded_rectangle((x0, y0 + (1 - k) * 60, x1, y1 + (1 - k) * 60), 48, fill=CARD + (int(255 * k),), outline=(255, 255, 255, int(40 * k)), width=4)
    revealed = t >= t_reveal
    draw_content(im, d, t, revealed)
    cy_ring = 1290 if TYPE == "odd_one_out" else 1230
    if t_cd0 <= t < t_reveal:
        rem = t_reveal - t; frac = rem / N; cx, cy, r = W / 2 + 150, cy_ring, 115
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(30, 14, 58, 255))
        d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * frac, fill=YEL if rem > 3 else PINK, width=22)
        pulse = 1 + 0.12 * max(0, 1 - (math.ceil(rem) - rem) * 4)
        text_c(d, (cx, cy), str(math.ceil(rem)), font(int(105 * pulse)), WHITE)
        text_c(d, (W / 2, cy_ring + 200), P.get("cta", "Comment your answer below!"), font(54, False), WHITE)
    if revealed:
        ke = clamp((t - t_reveal - 0.5) / 0.4)
        if ke > 0 and P.get("explain"):
            ef = fit(P["explain"], 860, 58, False)
            d.multiline_text((W / 2, 1010 if TYPE != "odd_one_out" else 1190), P["explain"], font=ef, fill=PINK + (int(255 * ke),), anchor="mm", align="center")
        tt = t - t_reveal
        if tt < 2.5:
            for (vx, vy, c, s) in confetti:
                x = W / 2 + vx * 900 * tt; y = 760 + vy * 1100 * tt + 1400 * tt * tt
                d.rectangle((x, y, x + s, y + s * 0.6), fill=c)
        kf = clamp((t - t_reveal - 1.6) / 0.4)
        if kf > 0:
            yb = 1290 if TYPE == "odd_one_out" else 1200
            text_c(d, (W / 2, yb - 40), "Did you get it?", font(78), WHITE + (int(255 * kf),))
            d.rounded_rectangle((180, yb + 40, W - 180, yb + 160), 60, fill=YEL + (int(255 * kf),))
            text_c(d, (W / 2, yb + 100), "FOLLOW FOR DAILY PUZZLES", font(48), INK + (int(255 * kf),))
    km = ease_out_back((t - 0.1) / 0.6); bob = 14 * math.sin(t * 3.2); m = mascot
    if revealed and t - t_reveal < 0.6:
        s = 1 + 0.15 * math.sin((t - t_reveal) / 0.6 * math.pi); m = mascot.resize((int(MS * s), int(MS * s)))
    if t_cd0 <= t < t_reveal:
        m = m.rotate(6 * math.sin(t * 5), resample=Image.BICUBIC); mx = W / 2 - 170 - m.width / 2; my = cy_ring + bob - 120
    else:
        mx = W / 2 - m.width / 2; my = 1440 + (1 - km) * 500 + bob + (60 if TYPE == "odd_one_out" else 0)
    im.paste(m, (int(mx), int(my - m.height / 2 + 120)), m)
    return im

# ---------- audio ----------
SR = 44100
audio = np.zeros(int((TOTAL + 0.5) * SR))
def add(t0, sig, vol=1.0):
    s = int(t0 * SR); e = min(len(audio), s + len(sig)); audio[s:e] += sig[:e - s] * vol
def tone(f, dur, decay=8):
    tt = np.arange(int(dur * SR)) / SR; return np.sin(2 * np.pi * f * tt) * np.exp(-decay * tt)
def pop(f=600):
    tt = np.arange(int(.12 * SR)) / SR; return np.sin(2 * np.pi * (f + 900 * np.exp(-30 * tt)) * tt) * np.exp(-25 * tt)
random.seed(P.get("number", 1) * 3)
roots = random.choice([[261.6, 329.6, 392.0, 523.3, 392.0, 329.6], [293.7, 370.0, 440.0, 587.3, 440.0, 370.0], [220.0, 277.2, 329.6, 440.0, 329.6, 277.2]])
beat = 60 / random.choice([104, 112, 120]) / 2; k = 0; tb = 0.0
while tb < TOTAL:
    add(tb, tone(roots[k % 6], .4, 9) * .5 + tone(roots[k % 6] * 2, .4, 12) * .15, .10); k += 1; tb += beat
add(0.2, pop(400), .4)
for j in range(len(items)): add(T_INTRO + j * T_ITEM, pop(500 + 60 * (j % 8)), .35)
for s in range(N):
    hi = (N - s) <= 3; add(t_cd0 + s, tone(1500 if hi else 1000, .08, 50), .35 if hi else .25)
for j, f in enumerate([523.3, 659.3, 784.0, 1046.5]): add(t_reveal + j * .07, tone(f, .9, 4), .3)
audio = np.tanh(audio * 1.2) * .8
fade = int(.4 * SR); audio[-fade:] *= np.linspace(1, 0, fade)
wav = OUT + ".wav"
with wave.open(wav, "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((audio * 32767).astype(np.int16).tobytes())

ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                       "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for i in range(NF): ff.stdin.write(frame(i).tobytes())
ff.stdin.close(); ff.wait(); os.remove(wav)
print(f"done {OUT} {TOTAL:.1f}s")
