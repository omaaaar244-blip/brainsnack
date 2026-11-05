"""Tiny animated story with generated piano (2026-11-05).
usage: python3 renderers/story.py puzzles/NNNN.json videos/NNNN.mp4
json: {"type":"story","scenes":[{"t":3.5,"text":"...","near":1,"far":1}, ...],"end":"...","end_t":4}
  near/far: 1 = that window's light is on, 0 = off, "blink" = blinking.
Night valley, two houses (a near one and a far one on a hill), snow, stars. All drawn here, music synthesised here.
"""
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(sys.argv[1])); OUT = sys.argv[2]
W, H, FPS = 1080, 1920, 30
F = os.path.join(D, "assets/Inter-Bold.otf")
def font(s): return ImageFont.truetype(F, int(s))
SC = P["scenes"]; starts = np.cumsum([0] + [s["t"] for s in SC]); T_END = starts[-1]; TOTAL = T_END + P.get("end_t", 4.5)
NF = int(TOTAL * FPS)
rng = np.random.default_rng(11)
stars = rng.uniform(0, 1, (160, 3)); snow = rng.uniform(0, 1, (140, 3))

# static background: sky gradient + hills + houses (lights drawn per frame)
sky = Image.new("RGB", (W, H)); sd = ImageDraw.Draw(sky)
for y in range(H):
    k = y / H; sd.line((0, y, W, y), fill=(int(8 + 22 * k), int(10 + 18 * k), int(30 + 40 * k)))
for sx, sy, sb in stars:
    r = 1 + 2 * sb; sd.ellipse((sx * W - r, sy * H * 0.55 - r, sx * W + r, sy * H * 0.55 + r), fill=(230, 230, 255))
sd.ellipse((820, 260, 940, 380), fill=(240, 236, 210))          # moon
sd.ellipse((850, 250, 970, 370), fill=(int(8 + 22 * .16), int(10 + 18 * .16), int(30 + 40 * .16)))  # crescent cut
def hill(d, pts, col): d.polygon(pts, fill=col)
hill(sd, [(0, 1180), (250, 1050), (520, 980), (760, 1010), (1080, 1100), (1080, H), (0, H)], (22, 28, 52))
hill(sd, [(0, 1500), (300, 1380), (650, 1420), (1080, 1350), (1080, H), (0, H)], (14, 18, 36))
def house(d, x, y, s, col):
    d.rectangle((x, y, x + 120 * s, y + 90 * s), fill=col)
    d.polygon([(x - 15 * s, y), (x + 60 * s, y - 60 * s), (x + 135 * s, y), ], fill=col)
    return (x + 42 * s, y + 25 * s, x + 78 * s, y + 60 * s)
FAR = house(sd, 690, 925, 0.55, (10, 12, 26))
NEAR = house(sd, 170, 1330, 1.6, (6, 8, 18))
WARM = (255, 200, 110)

def light_on(state, t):
    if state == "blink": return (math.sin(t * 5) > -0.2)
    return bool(state)

def wrap(text, f, maxw):
    out, line = [], ""
    for w in text.split():
        c = (line + " " + w).strip()
        if f.getlength(c) <= maxw: line = c
        else: out.append(line); line = w
    return out + [line]
TF = font(64)

def frame(i):
    t = i / FPS
    im = sky.copy()
    j = int(np.searchsorted(starts, t, side="right") - 1)
    sc = SC[min(j, len(SC) - 1)] if t < T_END else {"near": P.get("end_near", 1), "far": P.get("end_far", 1)}
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
    for box, st, rad in ((NEAR, sc.get("near", 1), 260), (FAR, sc.get("far", 0), 110)):
        if light_on(st, t):
            cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            g.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=WARM + (70,))
    glow = glow.filter(ImageFilter.GaussianBlur(60)); im.paste(glow, (0, 0), glow)
    d = ImageDraw.Draw(im, "RGBA")
    for box, st in ((NEAR, sc.get("near", 1)), (FAR, sc.get("far", 0))):
        d.rectangle(box, fill=WARM if light_on(st, t) else (30, 34, 50))
    for sx, sy, sb in snow:
        y = (sy * H + t * (40 + 50 * sb)) % H; x = sx * W + 20 * math.sin(t * .8 + sx * 30)
        r = 2 + 3 * sb; d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, int(120 + 100 * sb)))
    # captions
    if t < T_END:
        lt = t - starts[j]; a = min(1, lt / 0.5, max(0, (SC[j]["t"] - lt) / 0.4))
        txt = SC[j]["text"]
    else:
        lt = t - T_END; a = min(1, lt / 0.8); txt = P["end"]
    for n, l in enumerate(wrap(txt, TF, 920)):
        d.text((W / 2, 520 + n * 86), l, font=TF, fill=(250, 245, 235, int(255 * a)), anchor="mm")
    return im

# ---------- music: slow piano, A minor -> F -> C -> G ----------
SR = 44100; audio = np.zeros(int((TOTAL + 1) * SR))
def piano(f, dur, vol):
    x = np.arange(int(dur * SR)) / SR
    s = sum(np.sin(2 * np.pi * f * h * x) * a for h, a in ((1, 1), (2, .45), (3, .2), (4, .1)))
    return s * np.exp(-2.2 * x) * (1 - np.exp(-80 * x)) * vol
def add(t0, sig):
    s = int(t0 * SR); e = min(len(audio), s + len(sig))
    if e > s: audio[s:e] += sig[:e - s]
chords = [[220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [130.8, 196.0, 261.6], [196.0, 246.9, 293.7]]
melody = [659.3, 587.3, 523.3, 493.9, 523.3, 440.0, 493.9, 392.0]
bar = 2.4; t = 0.0; k = 0
while t < TOTAL - 0.5:
    ch = chords[k % 4]
    add(t, piano(ch[0] / 2, 3.0, .22))
    for n, f in enumerate(ch): add(t + .3 * n, piano(f, 2.4, .12))
    add(t + 1.2, piano(melody[(2 * k) % 8], 1.8, .13)); add(t + 1.8, piano(melody[(2 * k + 1) % 8], 1.8, .11))
    t += bar; k += 1
# simple echo for space
dl = int(.32 * SR); wet = np.zeros_like(audio); wet[dl:] = audio[:-dl] * .35; wet[2 * dl:] += audio[:-2 * dl] * .15
audio = np.tanh((audio + wet) * 1.1) * .8
fi = int(1.0 * SR); audio[:fi] *= np.linspace(0, 1, fi); audio = audio[:int(TOTAL * SR)]
fo = int(1.5 * SR); audio[-fo:] *= np.linspace(1, 0, fo)
wav = OUT + ".wav"
with wave.open(wav, "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((audio * 32767).astype(np.int16).tobytes())
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                       "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for i in range(NF): ff.stdin.write(frame(i).convert("RGB").tobytes())
ff.stdin.close(); ff.wait(); os.remove(wav)
print(f"done {OUT} {TOTAL:.1f}s")
