"""Shared helpers for renderers (2026-11-06): fonts, easing, wrapping, batched Twemoji, synth audio, encode."""
import math, os, subprocess, wave
import numpy as np
from PIL import Image, ImageFont

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS, SR = 1080, 1920, 30, 44100
_fc = {}
FONTS = {"bold": "assets/Inter-Bold.otf", "black": "assets/Inter-Black.otf",
         "round": "assets/fredoka600.ttf", "round7": "assets/fredoka700.ttf"}

def font(s, kind="bold"):
    k = (int(s), kind)
    if k not in _fc: _fc[k] = ImageFont.truetype(os.path.join(D, FONTS[kind]), int(s))
    return _fc[k]

def clamp(t): return max(0.0, min(1.0, t))
def ease(t): t = clamp(t); return 1 - (1 - t) ** 3
def pop(t):  # overshoot ease for stamps
    t = clamp(t); return 1 + 2.2 * (t - 1) ** 3 + 1.2 * (t - 1) ** 2 if t < 1 else 1.0

def wrap(text, f, maxw):
    out = []
    for para in text.split("\n"):
        line = ""
        for w in para.split():
            cand = (line + " " + w).strip()
            if f.getlength(cand) <= maxw: line = cand
            else: out.append(line); line = w
        out.append(line)
    return out

def emoji_path(e):
    cps = [f"{ord(c):x}" for c in e]
    for cand in ("-".join(cps), "-".join(c for c in cps if c != "fe0f")):
        p = os.path.join(D, "assets/twemoji", cand + ".svg")
        if os.path.exists(p): return p
    raise SystemExit(f"no twemoji for {e!r}")

def load_emojis(es, px=400, tmpdir="/tmp"):
    """Render several Twemoji SVGs in one browser session -> {emoji: RGBA image}."""
    es = list(dict.fromkeys(es)); paths = {e: emoji_path(e) for e in es}
    from playwright.sync_api import sync_playwright
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": px, "height": px})
        for e in es:
            pg.set_content(f'<html><body style="margin:0;background:transparent"><div style="width:{px}px;height:{px}px">'
                           f'{open(paths[e]).read()}</div><style>svg{{width:{px}px;height:{px}px;display:block}}</style></body></html>')
            tmp = os.path.join(tmpdir, f"emo_{os.getpid()}.png"); pg.screenshot(path=tmp, omit_background=True)
            out[e] = Image.open(tmp).convert("RGBA").copy(); os.remove(tmp)
        b.close()
    return out

def paste(im, em, cx, cy, size, alpha=1.0):
    if size < 2 or alpha <= 0: return
    e = em.resize((int(size), int(size)), Image.LANCZOS)
    if alpha < 1:
        a = e.getchannel("A").point(lambda v: int(v * alpha)); e.putalpha(a)
    im.paste(e, (int(cx - size / 2), int(cy - size / 2)), e)

class Audio:
    def __init__(self, total): self.a = np.zeros(int((total + 0.5) * SR))
    def add(self, t0, sig, vol):
        s = int(t0 * SR)
        if s >= len(self.a): return
        e = min(len(self.a), s + len(sig)); self.a[s:e] += sig[:e - s] * vol
    @staticmethod
    def tone(f, dur, decay=6, harm=(1.0,)):
        tt = np.arange(int(dur * SR)) / SR
        sig = sum(h * np.sin(2 * np.pi * f * (n + 1) * tt) for n, h in enumerate(harm))
        return sig * np.exp(-decay * tt) * np.minimum(1, tt * 400)
    @staticmethod
    def noise(dur, decay=30):
        tt = np.arange(int(dur * SR)) / SR
        return np.random.default_rng(1).standard_normal(len(tt)) * np.exp(-decay * tt)
    def write(self, path):
        a = np.tanh(self.a * 1.1) * .85
        fade = int(.4 * SR); a[-fade:] *= np.linspace(1, 0, fade)
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((a * 32767).astype(np.int16).tobytes())

def encode(out, frame_fn, total, audio):
    wav = out + ".wav"; audio.write(wav)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(int(total * FPS)): ff.stdin.write(frame_fn(i).convert("RGB").tobytes())
    ff.stdin.close(); ff.wait(); os.remove(wav)
    print(f"done {out} {total:.1f}s")
