import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
OUT="assets/brand_v2/"
def grad(w,h,top,bot):
    a=np.linspace(0,1,h)[:,None,None]; t=np.array(top)[None,None,:]; b=np.array(bot)[None,None,:]
    return Image.fromarray(np.repeat((t*(1-a)+b*a).astype(np.uint8),w,axis=1))
def glow(im,cx,cy,r,col,alpha,blur):
    g=Image.new("RGBA",im.size,(0,0,0,0)); ImageDraw.Draw(g).ellipse((cx-r,cy-r,cx+r,cy+r),fill=col+(alpha,))
    g=g.filter(ImageFilter.GaussianBlur(blur)); im.alpha_composite(g)
rng=np.random.default_rng(3)
# ---------- avatar 800x800 ----------
S=800; im=grad(S,S,(18,16,52),(70,30,90)).convert("RGBA")
d=ImageDraw.Draw(im)
for x,y,b in rng.uniform(0,1,(70,3)):
    r=1.5+3*b; d.ellipse((x*S-r,y*S-r,x*S+r,y*S+r),fill=(255,255,255,int(90+140*b)))
glow(im,400,400,250,(255,170,90),120,90)
glow(im,400,400,170,(255,205,120),200,40)
d=ImageDraw.Draw(im)
d.ellipse((400-150,400-150,400+150,400+150),fill=(255,214,140))
# crescent bite + small spark star
d.ellipse((400-150+95,400-150-55,400+150+95,400+150-55),fill=(0,0,0,0))
im2=Image.new("RGBA",(S,S),(0,0,0,0))
base=grad(S,S,(18,16,52),(70,30,90)).convert("RGBA")
# redo crescent properly with mask
mask=Image.new("L",(S,S),0); md=ImageDraw.Draw(mask)
md.ellipse((250,250,550,550),fill=255); md.ellipse((345,195,645,495),fill=0)
im=grad(S,S,(18,16,52),(70,30,90)).convert("RGBA"); d=ImageDraw.Draw(im)
for x,y,b in rng.uniform(0,1,(70,3)):
    r=1.5+3*b; d.ellipse((x*S-r,y*S-r,x*S+r,y*S+r),fill=(255,255,255,int(90+140*b)))
glow(im,380,420,260,(255,160,90),110,100)
moon=Image.new("RGBA",(S,S),(255,214,140,255)); im.paste(moon,(0,0),mask)
def star(d,cx,cy,R,col):
    pts=[]
    for k in range(8):
        r=R if k%2==0 else R*0.28; a=math.pi/4*k-math.pi/2
        pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    d.polygon(pts,fill=col)
glow(im,560,300,70,(255,240,200),160,25)
d=ImageDraw.Draw(im); star(d,560,300,62,(255,250,235)); star(d,640,420,26,(255,230,180))
im.convert("RGB").save(OUT+"avatar.png")
# ---------- banner 2560x1440 ----------
W,H=2560,1440; b=grad(W,H,(12,12,40),(60,30,80)).convert("RGBA"); d=ImageDraw.Draw(b)
for x,y,s in rng.uniform(0,1,(400,3)):
    r=1+3*s; d.ellipse((x*W-r,y*H*0.8-r,x*W+r,y*H*0.8+r),fill=(255,255,255,int(80+150*s)))
glow(b,2250,330,170,(255,200,130),110,60)
m=Image.new("L",(W,H),0); md=ImageDraw.Draw(m); md.ellipse((2180,260,2320,400),fill=255); md.ellipse((2225,235,2365,375),fill=0)
b.paste(Image.new("RGBA",(W,H),(255,214,140,255)),(0,0),m)
d=ImageDraw.Draw(b)
d.polygon([(0,1000),(500,880),(1100,930),(1700,860),(2560,960),(2560,H),(0,H)],fill=(28,26,62))
d.polygon([(0,1150),(700,1040),(1500,1100),(2560,1020),(2560,H),(0,H)],fill=(16,15,38))
# little glowing windows
for x,y,s in [(820,1020,1.0),(1560,960,0.7),(2150,1010,0.8),(420,1060,0.6)]:
    glow(b,x,y,60*s,(255,190,110),120,25); d=ImageDraw.Draw(b)
    d.rectangle((x-55*s,y-40*s,x+55*s,y+40*s),fill=(10,10,26)); d.polygon([(x-70*s,y-40*s),(x,y-95*s),(x+70*s,y-40*s)],fill=(10,10,26))
    d.rectangle((x-16*s,y-14*s,x+16*s,y+16*s),fill=(255,205,120))
F="assets/Inter-Black.otf"; F2="assets/Inter-Bold.otf"
f1=ImageFont.truetype(F,120); f2=ImageFont.truetype(F2,52)
d.text((W/2,650),"A little bit of everything",font=f1,fill=(255,236,200),anchor="mm")
d.text((W/2,770),"weird facts  •  food  •  tiny stories  •  music",font=f2,fill=(200,190,230),anchor="mm")
b.convert("RGB").save(OUT+"banner.png")
