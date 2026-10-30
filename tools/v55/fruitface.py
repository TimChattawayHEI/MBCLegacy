"""Tim's Meshy fruit machine -> tools/v55/img/fruitface.png: cut the cabinet off the wall, blank the payout boxes and button tray
(the game draws its own), and size it to 236x238 so it draws 2x on the 960x540 screen. Run art.py after to copy it to web/."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
from PIL import Image, ImageDraw
import numpy as np, json
src=Image.open(os.path.join(HERE, 'img', 'src', 'fruitface_meshy.png')).convert('RGB'); A=np.array(src).astype(int)
X0,Y0,X1,Y1=44,28,604,592
crop=A[Y0:Y1,X0:X1]; h,w=crop.shape[0]//2,crop.shape[1]//2
nat=crop.reshape(h,2,w,2,3).mean((1,3))
r,g,b=nat[...,0],nat[...,1],nat[...,2]; br=nat.max(2)
cab=((r>80)&(r>g+12)&(g>b+5)&(g>0.42*r))|((br>120)&(np.abs(r-g)<25)&(np.abs(g-b)<30))
L=np.full(h,np.nan)
for y in range(h):
    for x in range(0,110):
        if cab[y,x:x+3].all(): L[y]=x; break
ys=np.arange(h); ok=~np.isnan(L); Ls=np.interp(ys,ys[ok],L[ok])
Lm=np.array([np.median(Ls[max(0,y-6):y+7]) for y in range(h)])
Lm=np.minimum(Lm,22.0)
for y in range(1,h): Lm[y]=min(Lm[y],Lm[y-1])
cx=(323-X0)/2; Rm=2*cx-Lm
H2,W2=h*2,w*2
alpha=np.zeros((H2,W2),np.uint8)
for y in range(6,H2):
    l=Lm[y//2]*2; rr=Rm[y//2]*2+1
    alpha[y,int(max(0,l)):int(min(W2,rr+1))]=255
rgb=np.clip((crop-128)*1.06+128,0,255).astype(np.uint8)
full=Image.fromarray(np.dstack([rgb,alpha]),'RGBA')
d=ImageDraw.Draw(full)
P=lambda x,y:(x-X0,y-Y0)
for a,b_,c,d_ in [(183,117,276,195),(365,117,460,195)]:
    d.rectangle((*P(a,b_),*P(c,d_)),fill=(246,238,214,255))
d.rectangle((*P(118,438),*P(512,494)),fill=(26,22,30,255))
d.rectangle((*P(118,438),*P(512,494)),outline=(150,156,170,255),width=2)
TW=236; s=TW/W2; TH=round(H2*s)
out=full.resize((TW,TH),Image.LANCZOS)
a=np.array(out); a[...,3]=np.where(a[...,3]>140,255,0); out=Image.fromarray(a)
out.save(os.path.join(HERE, 'img', 'fruitface.png'))
