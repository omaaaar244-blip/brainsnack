"""Minimal black-screen renderer (new identity, 2026-11-05).
usage: python3 renderers/minimal.py puzzles/NNNN.json videos/NNNN.mp4

types:
  find_glyph : {"type":"find_glyph","hook":"FIND THE 8","base":"B","odd":"8","cols":9,"rows":13,
                "pos":[6,9],"seconds":5,"sub":"Only sharp eyes see it"}
               plain single-image hunt (the market's "find the number" format), short so it loops.
  fact       : {"type":"fact","hook":"THIS SOUNDS FAKE","emoji":"🪐","lines":["...","..."],
                "beat":2.6,"outro":"Follow for one wild fact a day"}
               black screen, one line of text at a time, big emoji.
Fonts: Inter (OFL) in assets/. Emoji: Twemoji (CC-BY 4.0).
"""
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(sys.argv[1])); OUT = sys.argv[2]
TYPE = P["type"]
W, H, FPS = 1080, 1920, 30
BLACK = (8, 8, 10); WHITE = (245, 245, 245); YEL = (255, 214, 0); RED = (255, 64, 64); GREY = (150, 150, 155)
FB = os.path.join(D, "assets/Inter-Bold.otf"); FK = os.path.join(D, "assets/Inter-Black.otf")
_fc = {}
def font(s, black=False):
    k = (int(s), black)
    if k not in _fc: _fc[k] = ImageFont.truetype(FK if black else FB, int(s))
    return _fc[k]
def clamp(t): return max(0.0, min(1.0, t))
def ease(t): t = clamp(t); return 1 - (1 - t) ** 3
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

def load_emoji(e, px=420):
    cps = [f"{ord(c):x}" for c in e]
    path = None
    for cand in ("-".join(cps), "-".join(c for c in cps if c != "fe0f")):
        p = os.path.join(D, "assets/twemoji", cand + ".svg")
        if os.path.exists(p): path = p; break
    if not path: raise SystemExit(f"no twemoji for {e!r}")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": px, "height": px})
        pg.set_content(f'<html><body style="margin:0;background:transparent"><div style="width:{px}px;height:{px}px">'
                       f'{open(path).read()}</div><style>svg{{width:{px}px;height:{px}px;display:block}}</style></body></html>')
        tmp = OUT + ".emo.png"; pg.screenshot(path=tmp, omit_background=True); b.close()
    im = Image.open(tmp).convert("RGBA").copy(); os.remove(tmp); return im

# ---------------- timeline ----------------
if TYPE == "find_glyph":
    N = int(P.get("seconds", 5)); t_cd0 = 0.4; t_reveal = t_cd0 + N; TOTAL = t_reveal + 2.6
    cols, rows = P["cols"], P["rows"]; oc, orow = P["pos"]
    gx0, gy0, gx1, gy1 = 50, 450, W - 50, 1660
    cell = min((gx1 - gx0) / cols, (gy1 - gy0) / rows)
    gf = font(cell * 0.86)
    ox = gx0 + ((gx1 - gx0) - cell * cols) / 2; oy = gy0 + ((gy1 - gy0) - cell * rows) / 2
else:
    LINES = P["lines"]; BEAT = P.get("beat", 2.6); EMO = load_emoji(P["emoji"])
    t_lines0 = 0.6; t_out = t_lines0 + len(LINES) * BEAT; TOTAL = t_out + 2.2

NF = int(TOTAL * FPS)
hook_f = font(104, True)
while hook_f.getlength(P["hook"]) > 960: hook_f = font(hook_f.size - 4, True)

def frame(i):
    t = i / FPS
    im = Image.new("RGB", (W, H), BLACK); d = ImageDraw.Draw(im, "RGBA")
    k = ease(t / 0.25)
    d.text((W / 2, 250 - (1 - k) * 30), P["hook"], font=hook_f, fill=YEL + (int(255 * k),), anchor="mm")
    if TYPE == "find_glyph":
        if P.get("sub"):
            d.text((W / 2, 370), P["sub"], font=font(54), fill=WHITE, anchor="mm")
        revealed = t >= t_reveal
        for r in range(rows):
            for c in range(cols):
                ch = P["odd"] if (c, r) == (oc, orow) else P["base"]
                a = 255 if not revealed or (c, r) == (oc, orow) else 70
                d.text((ox + cell * c + cell / 2, oy + cell * r + cell / 2), ch, font=gf, fill=WHITE + (a,), anchor="mm")
        if not revealed:
            rem = t_reveal - t
            if t >= t_cd0:
                d.text((W / 2, 1760), str(math.ceil(rem)), font=font(120, True), fill=(RED if rem <= 2 else WHITE), anchor="mm")
        else:
            cx, cy = ox + cell * oc + cell / 2, oy + cell * orow + cell / 2
            rr = cell * 0.7 * (0.4 + 0.6 * ease((t - t_reveal) / 0.3))
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=RED, width=10)
            d.text((W / 2, 1760), P.get("end", "Did you find it?"), font=font(70, True), fill=YEL, anchor="mm")
    else:
        # emoji gently floating
        ke = ease((t - 0.2) / 0.5); s = int(360 * (0.6 + 0.4 * ke))
        em = EMO.resize((s, s), Image.LANCZOS); bob = 12 * math.sin(t * 2.2)
        im.paste(em, (int(W / 2 - s / 2), int(560 - s / 2 + bob)), em)
        lf = font(76)
        if t < t_out:
            j = min(len(LINES) - 1, int((t - t_lines0) // BEAT)) if t >= t_lines0 else -1
            if j >= 0:
                kk = ease((t - t_lines0 - j * BEAT) / 0.3)
                txt = LINES[j]; hi = txt.startswith("!"); txt = txt.lstrip("!")
                ls = wrap(txt, lf, 940); y0 = 1150 - (len(ls) - 1) * 50 + (1 - kk) * 40
                for n, l in enumerate(ls):
                    d.text((W / 2, y0 + n * 100), l, font=lf, fill=(YEL if hi else WHITE) + (int(255 * kk),), anchor="mm")
            # progress dots
            for n in range(len(LINES)):
                x = W / 2 + (n - (len(LINES) - 1) / 2) * 44
                d.ellipse((x - 9, 1640 - 9, x + 9, 1640 + 9), fill=(WHITE if n <= j else (60, 60, 64)))
        else:
            kk = ease((t - t_out) / 0.3)
            for n, l in enumerate(wrap(P.get("outro", "Follow for more"), font(72, True), 900)):
                d.text((W / 2, 1150 + n * 95), l, font=font(72, True), fill=YEL + (int(255 * kk),), anchor="mm")
    return im

# ---------------- audio (all synthesised here) ----------------
SR = 44100; audio = np.zeros(int((TOTAL + 0.5) * SR))
def add(t0, sig, vol):
    s = int(t0 * SR); e = min(len(audio), s + len(sig)); audio[s:e] += sig[:e - s] * vol
def tone(f, dur, decay=6):
    tt = np.arange(int(dur * SR)) / SR; return np.sin(2 * np.pi * f * tt) * np.exp(-decay * tt)
# soft pad
tt = np.arange(len(audio)) / SR
pad_notes = [110.0, 164.8] if TYPE == "fact" else [98.0, 146.8]
for f in pad_notes: audio += 0.05 * np.sin(2 * np.pi * f * tt) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.25 * tt))
add(0.0, tone(880, .3, 10), .3)
if TYPE == "find_glyph":
    for s in range(N): add(t_cd0 + s, tone(1400 if N - s <= 2 else 900, .07, 45), .35)
    for j, f in enumerate([523.3, 659.3, 784.0]): add(t_reveal + j * .07, tone(f, .8, 4), .3)
else:
    for j in range(len(LINES)): add(t_lines0 + j * BEAT, tone(660 if j % 2 else 587, .25, 12), .25)
    for j, f in enumerate([440.0, 554.4, 659.3]): add(t_out + j * .08, tone(f, .9, 4), .25)
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
