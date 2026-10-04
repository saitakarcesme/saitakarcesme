"""Draw a deterministic, looping pixel city for the GitHub profile.

Run with Pillow installed: python3 tools/build_pixel_city.py
The project signs refer to public repositories; the lights are decorative.
"""
from pathlib import Path
import math
import random
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
W, H, SCALE, FPS, SECONDS = 320, 180, 2, 12, 20
C = {
    'sky': '#0b1025', 'haze': '#151c36', 'far': '#1d2844',
    'farwin': '#354660', 'ink': '#10182a', 'shadow': '#172139',
    'wall': '#283853', 'wall2': '#344763', 'edge': '#4b6279',
    'teal': '#6ec5bf', 'dimteal': '#327879', 'pink': '#d784a5',
    'amber': '#f1c17a', 'dimamber': '#8d7052', 'cream': '#f5e7bc',
    'window': '#172538', 'road': '#1e2a40', 'line': '#59667b',
    'water': '#101d32', 'ripples': '#294253', 'green': '#6fa891',
}
GLYPHS = {
    'A': ['01110','10001','10001','11111','10001','10001','10001'],
    'B': ['11110','10001','10001','11110','10001','10001','11110'],
    'C': ['01111','10000','10000','10000','10000','10000','01111'],
    'D': ['11110','10001','10001','10001','10001','10001','11110'],
    'E': ['11111','10000','10000','11110','10000','10000','11111'],
    'F': ['11111','10000','10000','11110','10000','10000','10000'],
    'G': ['01111','10000','10000','10111','10001','10001','01111'],
    'H': ['10001','10001','10001','11111','10001','10001','10001'],
    'I': ['111','010','010','010','010','010','111'],
    'J': ['00111','00010','00010','00010','10010','10010','01100'],
    'K': ['10001','10010','10100','11000','10100','10010','10001'],
    'L': ['10000','10000','10000','10000','10000','10000','11111'],
    'M': ['10001','11011','10101','10101','10001','10001','10001'],
    'N': ['10001','11001','11001','10101','10011','10011','10001'],
    'O': ['01110','10001','10001','10001','10001','10001','01110'],
    'P': ['11110','10001','10001','11110','10000','10000','10000'],
    'Q': ['01110','10001','10001','10001','10101','10010','01101'],
    'R': ['11110','10001','10001','11110','10100','10010','10001'],
    'S': ['01111','10000','10000','01110','00001','00001','11110'],
    'T': ['11111','00100','00100','00100','00100','00100','00100'],
    'U': ['10001','10001','10001','10001','10001','10001','01110'],
    'V': ['10001','10001','10001','10001','10001','01010','00100'],
    'W': ['10001','10001','10001','10101','10101','10101','01010'],
    'X': ['10001','10001','01010','00100','01010','10001','10001'],
    'Y': ['10001','10001','01010','00100','00100','00100','00100'],
    'Z': ['11111','00001','00010','00100','01000','10000','11111'],
    '/': ['00001','00001','00010','00100','01000','10000','10000'],
    '.': ['0','0','0','0','0','1','1'],
    '-': ['000','000','000','111','000','000','000'],
    ' ': ['000']*7,
}

def text_width(s):
    return sum(len(GLYPHS[c][0])+1 for c in s.upper())-1

def text(d, x, y, s, color):
    for c in s.upper():
        glyph = GLYPHS[c]
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == '1': d.point((x+col,y+row),fill=color)
        x += len(glyph[0])+1

def rect(d, box, color):
    d.rectangle(box, fill=C.get(color, color))

rng = random.Random(17)
stars = [(rng.randrange(8,312),rng.randrange(27,90),rng.randrange(8)) for _ in range(43)]
back = [(x,rng.randrange(72,116),rng.randrange(12,25)) for x in range(-10,320,18)]
buildings = [
    (13,85,65,'POCKETLORE','amber'),
    (86,66,60,'LOCALBOT','teal'),
    (156,43,66,'AKORITH','pink'),
    (232,74,73,'OPENMIRROR','teal'),
]
windows = []
for b,(x,y,w,label,color) in enumerate(buildings):
    for row,wy in enumerate(range(y+20,121,12)):
        for col,wx in enumerate(range(x+7,x+w-8,10)):
            windows.append((b,wx,wy,rng.random()>.26,rng.randrange(8)))

def person(d,x,y,t):
    step = int(t*6)%4
    rect(d,(x-3,y+1,x+5,y+2),'shadow')
    rect(d,(x,y-12,x+3,y-9),'amber')
    rect(d,(x-1,y-13,x+3,y-12),'ink')
    rect(d,(x-1,y-8,x+4,y-4),'teal')
    rect(d,(x+3,y-7,x+5,y-5),'dimteal')
    d.line((x,y-3,x+(1 if step<2 else -1),y),fill=C['cream'])
    d.line((x+3,y-3,x+(4 if step<2 else 2),y),fill=C['cream'])
    rect(d,(x-2,y-7,x-1,y-5),'amber')

def draw_frame(n):
    t=n/FPS
    phase=2*math.pi*n/(FPS*SECONDS)
    im=Image.new('RGB',(W,H),C['sky']);d=ImageDraw.Draw(im)
    rect(d,(0,73,319,135),'haze')
    # A restrained title bar stays readable at profile width.
    text(d,12,12,'SAITAKARCESME',C['cream'])
    text(d,214,12,'AFTER HOURS',C['edge'])
    rect(d,(12,24,307,24),'shadow')
    for x,y,k in stars:
        color='cream' if math.sin(phase+k)>0.75 else 'farwin'
        d.point((x,y),fill=C[color])
        if k==0 and color=='cream':
            d.line((x-1,y,x+1,y),fill=C[color]);d.line((x,y-1,x,y+1),fill=C[color])
    # Crescent moon and a slowly drifting, closed-loop cloud.
    d.ellipse((274,35,287,48),fill=C['cream'])
    d.ellipse((279,32,289,43),fill=C['sky'])
    for cx,cy in [(54,49),(268,59)]:
        shift=int(4*math.sin(phase))
        rect(d,(cx+shift,cy,cx+shift+22,cy+2),'haze')
        rect(d,(cx+shift+4,cy-2,cx+shift+15,cy-1),'haze')
    # The distant city is quiet and desaturated.
    for x,y,w in back:
        rect(d,(x,y,x+w,135),'far')
        for wx in range(x+3,x+w-2,5):
            for wy in range(y+6,125,8):
                if (wx+wy)%3==0:rect(d,(wx,wy,wx+1,wy+2),'farwin')
    for b,(x,y,w,label,color) in enumerate(buildings):
        rect(d,(x+4,y+4,x+w+4,134),'ink')
        rect(d,(x+w-4,y+4,x+w+3,132),'shadow')
        rect(d,(x,y,x+w-5,132),'wall' if b%2==0 else 'wall2')
        rect(d,(x-2,y-3,x+w-4,y),'edge')
        rect(d,(x,y+1,x+1,131),'edge')
        rect(d,(x+3,y+4,x+w-9,y+16),'ink')
        text(d,x+(w-5-text_width(label))//2,y+7,label,C[color])
        rect(d,(x+3,y+18,x+w-9,y+18),'shadow')
        for wb,wx,wy,on,seed in windows:
            if wb!=b:continue
            # Only a few windows change, avoiding a distracting flicker.
            switched = on
            if seed==0: switched = math.sin(phase+wx/9+wy/13)>-.25
            rect(d,(wx-1,wy-1,wx+5,wy+7),'shadow')
            rect(d,(wx,wy,wx+4,wy+5),color if switched else 'window')
            if switched:
                d.line((wx,wy+5,wx+4,wy+5),fill=C['dimamber' if color=='amber' else 'dimteal'])
            d.line((wx+2,wy,wx+2,wy+5),fill=C['wall'])
        # Door, brass handle, pavement-facing light.
        rect(d,(x+w//2-6,122,x+w//2+5,132),'ink')
        rect(d,(x+w//2-4,124,x+w//2+3,132),'dimteal')
        d.point((x+w//2+2,129),fill=C['amber'])
        rect(d,(x-1,132,x+w,134),'edge')
    # Rooftop details distinguish each project.
    rect(d,(23,77,31,81),'shadow');rect(d,(24,73,30,77),'green')
    rect(d,(35,79,41,82),'dimteal');rect(d,(37,75,39,79),'green')
    rect(d,(108,55,123,62),'shadow');rect(d,(109,56,122,61),'dimteal')
    rect(d,(111,57,113,58),'teal');rect(d,(118,57,120,58),'teal')
    d.line((116,55,116,51),fill=C['edge'])
    d.point((116,50),fill=C['amber' if int(t*2)%2 else 'dimamber'])
    rect(d,(179,36,198,39),'shadow')
    d.line((188,35,188,28),fill=C['edge'])
    d.point((188,27),fill=C['pink' if math.sin(phase*4)>0 else 'shadow'])
    d.line((269,70,273,64),fill=C['edge']);d.arc((267,59,278,67),0,180,fill=C['teal'])
    # A cat on the library roof, tail and eyes gently animated.
    cx,cy=63,81
    rect(d,(cx,cy-3,cx+6,cy),'ink');rect(d,(cx+4,cy-6,cx+8,cy-3),'ink')
    d.point((cx+4,cy-7),fill=C['ink']);d.point((cx+8,cy-7),fill=C['ink'])
    d.line((cx,cy-1,cx-3,cy-2,cx-4,cy-4-int(math.sin(phase))),fill=C['ink'])
    if n%120>6:d.point((cx+7,cy-5),fill=C['amber'])
    # Walkable waterfront: planters, a bench, street lights.
    rect(d,(0,135,319,144),'road');rect(d,(0,135,319,135),'edge')
    for x in [7,80,149,225,311]:
        d.line((x,137,x,120),fill=C['edge'])
        rect(d,(x-3,119,x+3,120),'shadow');rect(d,(x-2,121,x+2,122),'amber')
        d.line((x-3,140,x+3,140),fill=C['dimamber'])
    for x in [42,133,248]:
        rect(d,(x,133,x+8,136),'shadow')
        rect(d,(x-1,131,x+9,133),'green');rect(d,(x+2,128,x+6,132),'green')
    rect(d,(196,137,209,138),'amber');rect(d,(196,139,197,141),'shadow')
    rect(d,(208,139,209,141),'shadow')
    # Tiny green pavement tiles nod to the GitHub contribution graph.
    for i in range(20):
        rect(d,(10+i*4,142,12+i*4,143),'dimteal' if i%3 else 'green')
    person(d,int((n/(FPS*SECONDS)*350+14)%350)-15,140,t)
    rect(d,(0,145,319,156),'shadow')
    d.line((0,149,319,149),fill=C['line']);d.line((0,155,319,155),fill=C['line'])
    # One tram crosses fully offscreen before the seamless loop restarts.
    tx=int(370-n/(FPS*SECONDS)*430)
    rect(d,(tx,145,tx+40,153),'dimteal');rect(d,(tx+2,144,tx+37,145),'teal')
    rect(d,(tx+3,147,tx+10,150),'amber')
    for ox in [13,23,32]:rect(d,(tx+ox,147,tx+ox+5,150),'cream')
    rect(d,(tx+2,151,tx+38,152),'shadow')
    d.point((tx+1,150),fill=C['cream'])
    for ox in [7,31]:rect(d,(tx+ox,154,tx+ox+3,155),'ink')
    # Water glints echo the buildings without a noisy full reflection.
    rect(d,(0,158,319,179),'water');rect(d,(0,157,319,157),'edge')
    for x,col in [(35,'dimamber'),(112,'dimteal'),(184,'dimamber'),(267,'dimteal')]:
        for row in range(5):
            shift=int(math.sin(phase+row*1.3+x)*3)
            yy=161+row*3
            d.line((x-8+shift,yy,x+8+shift,yy),fill=C[col if row<3 else 'ripples'])
    for i in range(15):
        x=(i*29+int(3*math.sin(phase+i)))%320
        y=161+(i*7)%17
        d.line((x,y,x+4,y),fill=C['ripples'])
    return im.resize((W*SCALE,H*SCALE),Image.Resampling.NEAREST)

def main():
    frames=[draw_frame(n) for n in range(FPS*SECONDS)]
    # One shared palette avoids per-frame color shifts.
    palette=frames[0].quantize(colors=64,method=Image.Quantize.MEDIANCUT)
    indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    durations=[round((i+1)*1000/FPS/10)*10-round(i*1000/FPS/10)*10 for i in range(len(frames))]
    target=ROOT/'pixel-city.gif'
    indexed[0].save(target,save_all=True,append_images=indexed[1:],duration=durations,loop=0,optimize=True,disposal=1)
    preview=ROOT.parent/'output/pixel-city/preview.png'
    preview.parent.mkdir(parents=True,exist_ok=True)
    frames[FPS*7].save(preview)
    print(f'{target}: {len(frames)} frames, {sum(durations)} ms, {target.stat().st_size:,} bytes')

if __name__=='__main__':main()
