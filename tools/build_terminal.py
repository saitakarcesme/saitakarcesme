"""Render a looping terminal that turns its code into a night landscape."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import random

ROOT=Path(__file__).resolve().parents[1]
W,H,FPS,SECONDS=640,360,15,16
FONT=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',13)
SMALL=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',11)
BG='#0b1018';INK='#0e1621';GREEN='#9bd7a4';WHITE='#d9e5ee';DIM='#607489';BLUE='#83b8d7';AMBER='#e8c48e'
rng=random.Random(23)
stars=[(rng.randrange(32,609),rng.randrange(61,190),rng.random()) for _ in range(65)]

def base():
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    d.rounded_rectangle((15,15,624,344),radius=9,fill=INK,outline='#2b394b',width=1)
    d.rounded_rectangle((16,16,623,45),radius=8,fill='#182330')
    d.rectangle((16,35,623,45),fill='#182330')
    for x,c in [(31,'#ba7377'),(47,'#c8ac72'),(63,'#86ad91')]:d.ellipse((x,27,x+6,33),fill=c)
    title='~/saitakarcesme'
    d.text(((W-d.textlength(title,font=SMALL))/2,24),title,font=SMALL,fill=DIM)
    return im

def terminal(t):
    im=base();d=ImageDraw.Draw(im)
    lines=[
      (0.4,'$ whoami',GREEN),
      (1.6,'saitakarcesme',WHITE),
      (2.3,'$ ls projects',GREEN),
      (3.5,'Akorith  LocalBot  PocketLore  OpenMirror',WHITE),
      (4.5,'$ python world.py',GREEN),
      (5.7,'sky    = night()',BLUE),
      (6.2,'peaks  = curiosity()',BLUE),
      (6.7,'lights = ideas()',AMBER),
      (7.2,'while awake:',GREEN),
      (7.7,'    build(something_good)',WHITE),
    ]
    for i,(start,s,c) in enumerate(lines):
        if t<start:continue
        count=min(len(s),int((t-start)*32))
        y=66+i*23
        d.text((34,y),s[:count],font=FONT,fill=c)
        if count<len(s) and int(t*3)%2==0:
            xx=34+d.textlength(s[:count],font=FONT)
            d.rectangle((xx+2,y+3,xx+8,y+14),fill=GREEN)
    return im

def landscape(t):
    im=base();d=ImageDraw.Draw(im)
    d.rectangle((16,46,623,343),fill=INK)
    for x,y,k in stars:
        v=int(90+65*(.5+.5*math.sin(t*1.1+k*6)))
        d.point((x,y),fill=(v,v+8,min(255,v+22)))
        if k>.96:d.line((x-1,y,x+1,y),fill=BLUE)
    # Moon, layered peaks and a quiet lake.
    d.ellipse((495,73,519,97),fill=AMBER)
    d.ellipse((487,67,514,92),fill=INK)
    mountains=[
        ([(16,220),(73,160),(104,180),(175,98),(247,182),(285,144),(360,219),(623,220)],'#202e43'),
        ([(16,228),(62,204),(120,220),(219,151),(304,225),(358,181),(414,217),(464,141),(553,216),(623,185),(623,257),(16,257)],'#2c4053'),
    ]
    for points,c in mountains:d.polygon(points,fill=c)
    d.line([(73,160),(104,180),(175,98),(247,182)],fill='#567386',width=1)
    d.polygon([(164,110),(175,98),(195,121),(180,116),(177,120)],fill='#acc3cf')
    d.line([(358,181),(414,217),(464,141),(553,216)],fill='#597b88',width=1)
    d.polygon([(451,159),(464,141),(480,157),(467,153),(462,158)],fill='#a1bdc7')
    d.rectangle((16,245,623,343),fill='#142a36')
    d.polygon([(16,233),(97,242),(166,228),(254,240),(354,237),(397,244),(397,249),(16,250)],fill='#172a31')
    d.line((16,250,623,250),fill='#42696e')
    for i in range(45):
        yy=253+(i*17)%85;xx=25+(i*71)%580
        shift=int(4*math.sin(t*.7+i))
        d.line((xx+shift,yy,min(621,xx+12+(i%4)*6+shift),yy),fill='#274957')
    for i in range(15):
        yy=254+i*5;shift=int(3*math.sin(t+i*.6))
        span=int(18-i*.7)
        d.line((508-span+shift,yy,508+span+shift,yy),fill='#6c7161' if i<5 else '#375155')
    # Pines and one warmly lit cabin, representing an idea taking shape.
    for x,h in [(38,32),(57,43),(84,26),(116,36),(146,23),(555,41),(586,29),(608,37)]:
        y=247
        d.rectangle((x-1,y-h,x+1,y),fill='#101f29')
        for layer in range(3):
            top=y-h+layer*8;wide=5+layer*4
            d.polygon([(x,top),(x-wide,top+16),(x+wide,top+16)],fill='#1e3940' if layer%2 else '#142c34')
    d.rectangle((289,228,324,245),fill='#344345')
    d.polygon([(281,229),(306,211),(332,229)],fill='#18242d')
    d.line((285,225,306,211,328,226),fill='#708174')
    d.rectangle((301,231,309,245),fill='#172833')
    for x in [292,314]:
        d.rectangle((x,231,x+5,237),fill=AMBER)
        d.line((x+2,231,x+2,237),fill='#8c7658')
    d.rectangle((317,215,321,223),fill='#344345')
    for i in range(3):
        xx=318+int(3*math.sin(t*.6+i));yy=210-i*6
        d.line((xx,yy,xx+4,yy),fill='#35414e')
    d.text((35,312),'> keep building.',font=FONT,fill=GREEN)
    if int(t*2)%2==0:d.rectangle((169,315,175,326),fill=GREEN)
    return im

SOURCE=terminal(8.8)
DEST=landscape(12)
# The luminous code pixels become the luminous terrain pixels.
def samples(im,region,step):
    p=im.load();out=[]
    for y in range(region[1],region[3],step):
        for x in range(region[0],region[2],step):
            c=p[x,y]
            if max(c)>100:out.append((x,y,c))
    return out
origin=samples(SOURCE,(30,60,610,300),3)
target=samples(DEST,(28,60,613,330),3)
rng.shuffle(target)
particles=[(a,target[i%len(target)],rng.random()) for i,a in enumerate(origin)]

def frame(n):
    t=n/FPS
    if t<8.8:return terminal(t)
    if t<11.8:
        p=(t-8.8)/3;ease=p*p*(3-2*p)
        im=Image.blend(SOURCE,landscape(t),ease)
        d=ImageDraw.Draw(im)
        for (sx,sy,sc),(tx,ty,tc),k in particles:
            x=sx+(tx-sx)*ease+math.sin(p*math.pi)*math.sin(k*12)*30
            y=sy+(ty-sy)*ease-math.sin(p*math.pi)*(14+k*40)
            c=tuple(int(a+(b-a)*ease) for a,b in zip(sc,tc))
            d.rectangle((int(x),int(y),int(x)+1,int(y)+1),fill=c)
        return im
    im=landscape(t)
    if t>15:
        im=Image.blend(im,terminal(0),min(1,(t-15)/.8))
    return im

def main():
    frames=[frame(n) for n in range(FPS*SECONDS)]
    sheet=Image.new('RGB',(640,360))
    for i in range(16):sheet.paste(frames[i*FPS].resize((160,90)),((i%4)*160,(i//4)*90))
    palette=sheet.quantize(colors=128)
    indexed=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
    durations=[round((n+1)*1000/FPS/10)*10-round(n*1000/FPS/10)*10 for n in range(len(frames))]
    destination=ROOT/'infinite-terminal.gif'
    indexed[0].save(destination,save_all=True,append_images=indexed[1:],duration=durations,loop=0,optimize=True,disposal=1)
    preview=ROOT.parent/'output/infinite-terminal';preview.mkdir(parents=True,exist_ok=True)
    frames[6*FPS].save(preview/'terminal.png');frames[13*FPS].save(preview/'landscape.png')
    print(f'{destination}: {destination.stat().st_size:,} bytes, {sum(durations)} ms')

if __name__=='__main__':main()
