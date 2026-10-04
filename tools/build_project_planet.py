"""A looping voyage through stars to a planet of personal projects."""
from pathlib import Path
from PIL import Image,ImageDraw
import math
import random
import numpy as np
from build_pixel_city import text,text_width

ROOT=Path(__file__).resolve().parents[1]
W,H,SCALE,FPS,SECONDS=320,180,2,15,16
rng=random.Random(91)
STARS=[(rng.randrange(W),rng.randrange(H),rng.random()) for _ in range(125)]
Y,X=np.mgrid[0:H,0:W]
BACKGROUND=(8,12,27)

def ease(p):
 p=max(0,min(1,p));return p*p*(3-2*p)

def planet(radius,rotation):
 nx=(X-160)/radius;ny=(Y-111)/radius
 rr=nx*nx+ny*ny;inside=rr<=1
 nz=np.sqrt(np.clip(1-rr,0,1))
 # Stable spherical terrain, with a gentle orbital change in perspective.
 wx=nx*math.cos(rotation)+nz*math.sin(rotation)
 wz=nz*math.cos(rotation)-nx*math.sin(rotation)
 terrain=(np.sin(wx*7.2+ny*3.1)*.45+np.sin(ny*9.7-wz*4.2)*.28+
          np.cos(wx*14+ny*11)*.14+np.sin(wx*23-ny*16)*.06)
 ocean=np.zeros((H,W,3),dtype=float);ocean[:]=(34,82,110)
 land=terrain>.13
 ocean[land]=(80,139,119)
 ocean[terrain>.43]=(120,157,123)
 ocean[terrain>.65]=(169,170,130)
 ocean[(terrain>.09)&(terrain<=.13)]=(130,175,160)
 # Clouds are sparse so the project regions stay readable.
 cloud=(np.sin(ny*17+wx*4)+np.sin(wx*12-wz*5)>1.55)&(ny<-.25)
 ocean[cloud]=(181,207,200)
 illumination=np.clip(-nx*.45-ny*.4+nz*.8,.08,1)
 ocean*= (.32+.68*illumination)[...,None]
 # Thin cyan atmospheric rim, with the brightest edge toward the sun.
 rim=(rr>.955)&inside
 ocean[rim]=np.stack([70+illumination[rim]*30,137+illumination[rim]*45,163+illumination[rim]*42],axis=1)
 alpha=np.where(inside,255,0).astype(np.uint8)
 return Image.fromarray(np.dstack((np.clip(ocean,0,255).astype(np.uint8),alpha)),'RGBA')

PROJECTS=[('AKORITH',-.47,-.22,'#e9bb94'),('POCKETLORE',.32,-.42,'#bcddab'),
          ('OPENMIRROR',-.32,.37,'#94d8dd'),('LOCALBOT',.48,.13,'#d8a9d3')]

def district(d,x,y,name,color,t):
 # Small bases cast shadows onto their world.
 d.ellipse((x-13,y+2,x+13,y+8),fill='#254b51')
 d.line((x-12,y+7,x+12,y+7),fill='#8bada0')
 if name=='AKORITH':
  for ox,h in [(-9,12),(-2,19),(6,9)]:
   d.rectangle((x+ox,y-h,x+ox+5,y+3),fill='#506976')
   d.line((x+ox,y-h,x+ox+5,y-h),fill='#bacbd0')
   for yy in range(y-h+3,y,4):d.point((x+ox+2,yy),fill=color)
  d.line((x,y-20,x,y-26),fill='#899faa')
  d.point((x,y-27),fill=color if int(t*2)%2 else '#596f78')
 elif name=='POCKETLORE':
  d.rectangle((x-9,y-10,x+8,y+3),fill='#899d8d')
  d.polygon([(x-12,y-10),(x,y-18),(x+11,y-10)],fill='#e0c5a1')
  for ox in [-5,2]:d.rectangle((x+ox,y-6,x+ox+2,y-1),fill='#ead39d')
  d.rectangle((x-1,y-3,x+1,y+3),fill='#45636a')
  for ox in [-15,14]:
   d.line((x+ox,y,x+ox,y-10),fill='#6b8b7b')
   d.polygon([(x+ox,y-13),(x+ox-4,y-5),(x+ox+4,y-5)],fill='#a6c6a0')
 elif name=='OPENMIRROR':
  d.rectangle((x-9,y-10,x+9,y+3),fill='#6e98a3')
  for ox in [-6,-1,4]:d.rectangle((x+ox,y-8,x+ox+2,y+1),fill='#ade0df')
  d.line((x-10,y-11,x+10,y-11),fill='#e1eded')
  d.line((x-6,y-6,x-4,y-8),fill='#f0edce')
  d.line((x+3,y-2,x+5,y-4),fill='#f0edce')
 else:
  d.rectangle((x-12,y-6,x+6,y+3),fill='#7a778d')
  d.ellipse((x-12,y-12,x+6,y-1),fill='#b0a7bb')
  d.rectangle((x-9,y-4,x+2,y-1),fill='#e2bfab')
  d.line((x-3,y-13,x-3,y-21),fill='#a3abb7')
  d.arc((x-8,y-25,x+2,y-17),0,180,fill='#d8e2e1')
  rx=x+11+int(math.sin(t)*2)
  d.rectangle((rx,y,rx+6,y+3),fill='#c4adb0')
  d.point((rx+1,y+4),fill='#162d3e');d.point((rx+5,y+4),fill='#162d3e')
  d.point((rx+4,y-1),fill='#e8d6b1')
 # Compact, legible destination labels are attached to each region.
 ly=y+12;tw=text_width(name)
 d.rectangle((x-tw//2-3,ly-2,x+tw//2+3,ly+9),fill='#142739')
 d.line((x-tw//2-3,ly+9,x+tw//2+3,ly+9),fill='#446577')
 text(d,x-tw//2,ly,name,color)

def scene(n):
 t=n/FPS
 approach=ease((t-1)/7)
 radius=4+approach*89
 im=Image.new('RGB',(W,H),BACKGROUND);d=ImageDraw.Draw(im)
 # Motion radiates away from the destination during the flight.
 for sx,sy,k in STARS:
  factor=1+approach*.65
  x=int(160+(sx-160)*factor);y=int(105+(sy-105)*factor)
  if 2<x<318 and 2<y<178:
   v=int(75+80*(.5+.5*math.sin(t*.7+k*9)))
   d.point((x,y),fill=(v,v+7,min(255,v+23)))
   if .1<approach<.95 and k>.85:
    xx=x+int((x-160)*.025);yy=y+int((y-105)*.025)
    d.line((x,y,xx,yy),fill='#566c8c')
 # A moon slips offscreen as the camera closes in.
 mx=int(133-approach*124);my=int(100-approach*67);mr=2+int(approach*4)
 d.ellipse((mx-mr,my-mr,mx+mr,my+mr),fill='#70879c')
 d.ellipse((mx-mr-1,my-mr-2,mx+1,my+1),fill=BACKGROUND)
 if radius>20:
  d.ellipse((160-radius-2,111-radius-2,160+radius+2,111+radius+2),outline='#19384b',width=2)
 globe=planet(radius,-.12+.08*math.sin(t*.3))
 im.paste(globe,(0,0),globe);d=ImageDraw.Draw(im)
 if t>7.6:
  reveal=ease((t-7.6)/1.2)
  layer=Image.new('RGBA',(W,H),(0,0,0,0));ld=ImageDraw.Draw(layer)
  for name,px,py,color in PROJECTS:
   district(ld,int(160+px*radius),int(111+py*radius),name,color,t)
  layer.putalpha(layer.getchannel('A').point(lambda a:int(a*reveal)))
  im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB');d=ImageDraw.Draw(im)
 if t>3:
  title='SAITAKARCESME'
  text(d,(W-text_width(title))//2,8,title,'#dbe6df')
 # A tiny probe orbits the lit limb while the camera lingers.
 if t>8:
  a=(t-8)*.36
  xx=int(160+105*math.cos(a));yy=int(107+63*math.sin(a))
  if 25<yy<176:
   d.line((xx-5,yy,xx+5,yy),fill='#91b6c3')
   d.rectangle((xx-1,yy-2,xx+1,yy+2),fill='#e0c39a')
   d.point((xx,yy-4),fill='#91b6c3')
 if t>14.8:
  im=Image.blend(im,scene(0),ease((t-14.8)/1.2))
 return im

def main():
 frames=[scene(n).resize((W*SCALE,H*SCALE),Image.Resampling.NEAREST) for n in range(FPS*SECONDS)]
 sheet=Image.new('RGB',(640,360))
 for i in range(16):sheet.paste(frames[i*FPS].resize((160,90)),((i%4)*160,(i//4)*90))
 palette=sheet.quantize(colors=128)
 indexed=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
 durations=[round((n+1)*1000/FPS/10)*10-round(n*1000/FPS/10)*10 for n in range(len(frames))]
 target=ROOT/'project-planet.gif'
 indexed[0].save(target,save_all=True,append_images=indexed[1:],duration=durations,loop=0,optimize=True,disposal=1)
 preview=ROOT.parent/'output/project-planet';preview.mkdir(parents=True,exist_ok=True)
 frames[11*FPS].save(preview/'preview.png')
 print(f'{target}: {target.stat().st_size:,} bytes, {sum(durations)} ms')

if __name__=='__main__':main()
