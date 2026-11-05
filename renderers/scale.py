"""Scale / ranking list renderer (2026-11-05): rows appear one by one, each bigger than the last.
usage: python3 renderers/scale.py puzzles/NNNN.json videos/NNNN.mp4
json: {"type":"scale","hook":"HOW LONG LIGHT TAKES TO REACH YOU","rows":[["🌙","Moon","1.3 seconds"],...],
       "beat":1.9,"punch":"...","outro":"..."}
Fonts: Inter (OFL). Emoji: Twemoji (CC-BY 4.0). Audio synthesised here.
"""
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(sys.argv[1])); OUT = sys.argv[2]
W, H, FPS = 1080, 1920, 30
BG = (6, 10, 28); WHITE = (245, 245, 245); YEL = (255, 214, 0); CYAN = (90, 220, 255); GREY = (140, 150, 175)
FB = os.path.join(D, "assets/Inter-Bold.otf"); FK = os.path.join(D, "assets/Inter-Black.otf")
def font(s, black=False): return ImageFont.truetype(FK if black else FB, int(s))
def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

def load_emojis(chars, px=200):
    from playwright.sync_api import sync_playwright
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": px, "height": px})
        for e in chars:
            cps = [f"{ord(c):x}" for c in e]; path = None
            for cand in ("-".join(cps), "-".join(c for c in cps if c != "fe0f")):
                f = os.path.join(D, "assets/twemoji", cand + ".svg")
                if os.path.exists(f): path = f; break
            if not path: raise SystemExit(f"no twemoji for {e!r}")
            pg.set_content(f'<html><body style="margin:0;background:transparent"><div style="width:{px}px;height:{px}px">'
                           f'{open(path).read()}</div><style>svg{{width:{px}px;height:{px}px;display:block}}</style></body></html>')
            tmp = OUT + ".emo.png"; pg.screenshot(path=tmp, omit_background=True)
            out[e] = Image.open(tmp).convert("RGBA").copy(); os.remove(tmp)
        b.close()
    return out

ROWS = P["rows"]; BEAT = P.get("beat", 1.9)
EM = load_emojis([r[0] for r in ROWS])
t0 = 0.8; t_punch = t0 + len(ROWS) * BEAT + 0.3; TOTAL = t_punch + 3.6; NF = int(TOTAL * FPS)
hf = font(84, True)
def wrap(text, f, maxw):
    out, line = [], ""
    for w in text.split():
        c = (line + " " + w).strip()
        if f.getlength(c) <= maxw: line = c
        else: out.append(line); line = w
    return out + [line]
HOOK = wrap(P["hook"], hf, 960)
random_stars = np.random.default_rng(5).uniform(0, 1, (120, 3))
ROW_H = 150; Y0 = 600

def frame(i):
    t = i / FPS
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im, "RGBA")
    for sx, sy, sb in random_stars:
        a = int(60 + 120 * sb * (0.6 + 0.4 * math.sin(t * 2 + sx * 20)))
        r = 1 + 2 * sb; d.ellipse((sx * W - r, sy * H - r, sx * W + r, sy * H + r), fill=(255, 255, 255, a))
    k = ease(t / 0.3)
    for n, l in enumerate(HOOK):
        d.text((W / 2, 170 + n * 98 - (1 - k) * 30), l, font=hf, fill=YEL + (int(255 * k),), anchor="mm")
    for j, (e, name, val) in enumerate(ROWS):
        kk = ease((t - t0 - j * BEAT) / 0.35)
        if kk <= 0: continue
        y = Y0 + j * ROW_H; x = 70 + (1 - kk) * 120; a = int(255 * kk)
        em = EM[e].resize((110, 110), Image.LANCZOS)
        if a < 255: em.putalpha(em.getchannel("A").point(lambda v: int(v * kk)))
        im.paste(em, (int(x), int(y - 55)), em)
        d.text((x + 140, y), name, font=font(62), fill=WHITE + (a,), anchor="lm")
        d.text((W - 70, y), val, font=font(62, True), fill=CYAN + (a,), anchor="rm")
        if j < len(ROWS) - 1: d.line((70, y + ROW_H / 2, W - 70, y + ROW_H / 2), fill=(255, 255, 255, int(30 * kk)), width=2)
    kp = ease((t - t_punch) / 0.4)
    if kp > 0:
        for n, l in enumerate(wrap(P["punch"], font(64, True), 940)):
            d.text((W / 2, 1500 + n * 84 + (1 - kp) * 30), l, font=font(64, True), fill=YEL + (int(255 * kp),), anchor="mm")
        ko = ease((t - t_punch - 1.6) / 0.4)
        if ko > 0: d.text((W / 2, 1780), P.get("outro", ""), font=font(50), fill=GREY + (int(255 * ko),), anchor="mm")
    return im

SR = 44100; audio = np.zeros(int((TOTAL + 0.5) * SR)); tt = np.arange(len(audio)) / SR
def add(t0_, sig, vol):
    s = int(t0_ * SR); e = min(len(audio), s + len(sig)); audio[s:e] += sig[:e - s] * vol
def tone(f, dur, decay=6):
    x = np.arange(int(dur * SR)) / SR; return np.sin(2 * np.pi * f * x) * np.exp(-decay * x)
for f in (82.4, 123.5, 164.8): audio += 0.045 * np.sin(2 * np.pi * f * tt) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * tt + f))
scale = [392.0, 440.0, 493.9, 587.3, 659.3, 784.0, 880.0]
for j in range(len(ROWS)): add(t0 + j * BEAT, tone(scale[j % 7], .5, 7), .28)
for j, f in enumerate([523.3, 659.3, 784.0, 1046.5]): add(t_punch + j * .08, tone(f, 1.0, 3.5), .22)
audio = np.tanh(audio * 1.2) * .8; fade = int(.5 * SR); audio[-fade:] *= np.linspace(1, 0, fade)
wav = OUT + ".wav"
with wave.open(wav, "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((audio * 32767).astype(np.int16).tobytes())
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                       "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for i in range(NF): ff.stdin.write(frame(i).tobytes())
ff.stdin.close(); ff.wait(); os.remove(wav)
print(f"done {OUT} {TOTAL:.1f}s")
