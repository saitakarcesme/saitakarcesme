"""Draw a cozy pixel-art coding desk with rain, typing and coffee steam."""
from pathlib import Path
from PIL import Image,ImageDraw
import math
import random
from build_pixel_city import text

ROOT=Path(__file__).resolve().parents[1]
W,H,SCALE,FPS,SECONDS=320,180,2,12,12
C={'wall':'#282438','dark':'#171e2d','trim':'#554458','wood':'#986d62',
   'edge':'#ce9876','shadow':'#533e49','floor':'#292b3b','sky':'#192b43',
   'city':'#273a53','rain':'#54718a','blue':'#96bfca','amber':'#efc58b',
   'green':'#80a69b','pink':'#c78f9f','cream':'#e7d8ba','ink':'#121e2a',
   'code':'#6ba7a7','dimmer':'#345060','plant':'#528a79','leaf':'#78a994'}
rng=random.Random(31)
rain=[(rng.randrange(21,148),rng.randrange(24,112),rng.randrange(3,7)) for _ in range(58)]
city=[(x,rng.randrange(67,91),rng.randrange(11,19)) for x in range(20,150,12)]
def rect(d,b,c):d.rectangle(b,fill=C.get(c,c))

def frame(n):
 t=n/FPS;phase=2*math.pi*n/(FPS*SECONDS)
 im=Image.new('RGB',(W,H),C['wall']);d=ImageDraw.Draw(im)
 # Restrained wall texture, warm plaster and a window into the blue night.
 for y in range(9,144,9):
  for x in range((y%3)*4,320,24):d.point((x,y),fill='#30293d')
 rect(d,(0,143,319,179),'floor');rect(d,(0,141,319,143),'trim')
 for y in range(152,180,10):
  d.line((0,y,319,y),fill='#343143')
  for x in range((y%4)*9,320,70):d.line((x,y,x,y+9),fill='#343143')
 rect(d,(15,18,153,116),'dark');rect(d,(18,21,150,113),'trim')
 rect(d,(21,24,147,110),'sky')
 d.ellipse((111,34,120,43),fill=C['cream']);d.ellipse((107,31,116,40),fill=C['sky'])
 for x,y,w in city:
  rect(d,(x,y,x+w,109),'city')
  for wx in range(x+3,x+w-2,4):
   for wy in range(y+5,104,7):
    if (wx+wy)%3==0:rect(d,(wx,wy,wx+1,wy+2),'dimmer' if wx%2 else '#6e7776')
 # Rain is clipped to the window and wraps every twelve seconds.
 for x,y,length in rain:
  yy=24+(y-24+n*87/(FPS*SECONDS))%87
  xx=x-int((yy-24)/24)
  if 23<xx<145 and yy+length<110:d.line((xx,yy,xx-1,yy+length),fill=C['rain'])
 # Glass highlights and mullions keep the rain clearly behind the desk.
 d.line((27,26,27,107),fill='#354961');d.line((30,26,30,77),fill='#354961')
 rect(d,(82,21,85,113),'trim');rect(d,(18,79,150,82),'trim')
 rect(d,(12,114,156,118),'wood');rect(d,(12,114,156,114),'edge')
 # Drawn curtains, loosely hanging at the sides.
 for x in [7,155]:
  rect(d,(x,15,x+7,108),'shadow');rect(d,(x+2,15,x+3,108),'trim')
  rect(d,(x-1,81,x+8,83),'edge')
 rect(d,(6,13,166,15),'trim')
 # Books, a little poster and a trailing plant on a shelf.
 rect(d,(186,20,305,24),'wood');rect(d,(186,20,305,20),'edge')
 for x,h,c in [(190,14,'pink'),(196,17,'blue'),(202,13,'green'),(208,16,'amber')]:
  rect(d,(x,20-h,x+4,19),c);d.line((x+1,17,x+3,17),fill=C['shadow'])
 rect(d,(232,3,277,19),'dark');rect(d,(234,5,275,17),'cream')
 text(d,237,9,'CREATE',C['shadow'])
 rect(d,(288,11,301,19),'shadow');rect(d,(287,11,302,12),'edge')
 for x,y in [(290,8),(296,6),(299,9),(303,15),(304,21),(302,26)]:
  rect(d,(x-2,y-1,x+2,y+1),'plant');d.point((x,y),fill=C['leaf'])
 d.line((299,12,305,20,302,28),fill=C['plant'])
 # A clock is decorative, without pretending to show live time.
 d.ellipse((280,37,302,59),fill=C['trim']);d.ellipse((282,39,300,57),fill=C['cream'])
 d.line((291,48,291,42),fill=C['shadow']);d.line((291,48,296,50),fill=C['shadow'])
 # A rug anchors the foreground.
 d.polygon([(101,151),(265,151),(287,170),(84,170)],fill='#464254')
 d.line((103,154,263,154),fill='#625361');d.line((90,167,281,167),fill='#625361')
 # The lamp casts a pixelated pool of warm light across the desk.
 d.polygon([(160,57),(145,121),(215,121),(168,57)],fill='#453744')
 d.polygon([(161,58),(153,120),(194,120),(167,58)],fill='#51404a')
 rect(d,(31,124,293,132),'wood');rect(d,(29,122,295,125),'edge')
 rect(d,(35,133,41,163),'shadow');rect(d,(278,133,284,163),'shadow')
 rect(d,(43,133,80,151),'shadow');rect(d,(45,135,78,145),'wood')
 d.line((58,137,65,137),fill=C['edge'])
 d.line((31,128,291,128),fill='#ad7e68')
 # Monitor: tiny colored code lines are typed and scroll gently.
 rect(d,(183,51,276,113),'dark');rect(d,(185,53,274,110),'trim')
 rect(d,(188,56,271,106),'ink');rect(d,(188,56,271,62),'dimmer')
 for x,c in [(191,'pink'),(195,'amber'),(199,'green')]:d.point((x,59),fill=C[c])
 text(d,228,57,'LOCAL',C['blue'])
 rect(d,(190,64,195,103),'dark')
 for row in range(8):
  y=66+row*4;indent=(row%3)*4
  length=[43,21,35,52,17,39,27,46][row]
  progress=(n//3)%24
  if row==7:length=min(length,progress*2)
  d.line((199+indent,y,199+indent+min(length,63-indent),y),fill=C[['code','blue','pink','amber'][row%4]])
  if row%2==0:d.line((201+indent,y,206+indent,y),fill=C['pink'])
  d.point((192,y),fill=C['dimmer'])
 if n%12<6:rect(d,(201+min((n//3)%24*2,46),94,202+min((n//3)%24*2,46),96),'cream')
 rect(d,(226,114,232,120),'trim');rect(d,(216,120,244,121),'shadow')
 # Keyboard, mouse, cables and a handwritten notebook.
 d.polygon([(183,116),(262,116),(268,122),(178,122)],fill='#5b6170')
 for y in [118,120]:
  for x in range(187,259,5):d.line((x,y,x+2,y),fill=C['dark'])
 rect(d,(280,117,286,122),'cream');d.line((283,117,283,119),fill=C['wood'])
 d.line((284,116,284,111,279,108,279,75),fill=C['dark'])
 d.polygon([(61,116),(84,113),(95,119),(72,122)],fill=C['cream'])
 d.line((81,114,84,120),fill=C['wood']);d.line((65,117,77,116),fill=C['wood'])
 d.line((68,119,79,118),fill=C['wood'])
 d.line((94,116,110,112),fill=C['amber'])
 # Tea and steam, breathing slowly rather than flickering.
 rect(d,(130,114,143,120),'cream');rect(d,(131,113,142,115),'wood')
 d.arc((140,114,148,120),270,90,fill=C['cream'])
 d.line((130,121,146,121),fill=C['shadow'])
 for k in range(3):
  yy=111-((n*17/(FPS*SECONDS)+k*5)%17);xx=136+int(math.sin(phase*2+k)*2)
  d.line((xx,yy,xx+2,yy-2),fill='#948181' if k%2 else '#b3a18e')
 # The articulated desk lamp and its warm shade.
 d.line((167,121,171,89,159,62),fill=C['trim'],width=3)
 d.line((168,120,172,89,160,62),fill=C['edge'])
 rect(d,(159,120,178,122),'shadow')
 d.polygon([(153,50),(167,50),(172,60),(148,60)],fill=C['amber'])
 rect(d,(150,60,170,61),'cream')
 # A sleeping cat curls up on the empty left side of the desk.
 cy=120-(1 if math.sin(phase)>.35 else 0)
 d.ellipse((39,cy-11,59,cy),fill='#b48676')
 rect(d,(38,cy-10,44,cy-4),'wood')
 d.polygon([(37,cy-9),(38,cy-14),(41,cy-10),(44,cy-13),(45,cy-6)],fill='#b48676')
 d.line((38,cy-7,40,cy-7),fill=C['shadow'])
 d.arc((46,cy-9,59,cy+1),20,300,fill=C['shadow'],width=2)
 # A coder in a soft hoodie, hands moving a pixel over the keyboard.
 rect(d,(211,108,239,145),'dark')
 d.rounded_rectangle((207,111,240,146),radius=7,fill='#484453')
 d.rounded_rectangle((206,108,236,136),radius=6,fill='#766176')
 d.line((208,112,208,131),fill='#a17a8c')
 d.ellipse((212,90,231,111),fill='#d1a388')
 d.polygon([(211,92),(216,87),(227,87),(231,92),(230,104),(225,102),(224,97),(214,97),(213,105),(211,102)],fill='#302b37')
 rect(d,(228,100,232,105),'edge');d.point((230,99),fill=C['dark'])
 d.line((231,98,237,98),fill=C['blue']);d.point((236,99),fill=C['dark'])
 d.polygon([(234,115),(247,117),(250,120),(238,121)],fill='#766176')
 hand=1 if n%8<4 else 0
 rect(d,(247,117-hand,251,119-hand),'edge')
 rect(d,(208,139,239,145),'dark');rect(d,(211,145,215,157),'trim')
 d.line((223,146,223,158),fill=C['trim'],width=2)
 d.line((210,160,239,160),fill=C['dark'],width=2)
 for x in [209,225,239]:rect(d,(x,160,x+2,162),'dark')
 # A floor plant and a small stack of books make the room feel inhabited.
 rect(d,(13,147,27,161),'shadow');rect(d,(11,144,29,147),'wood')
 for x,y in [(16,140),(22,137),(15,131),(24,127),(21,119)]:
  d.line((20,145,x,y),fill=C['plant'])
  d.ellipse((x-4,y-3,x+3,y+1),fill=C['leaf' if y%2 else 'plant'])
 for x,y,w,c in [(298,154,18,'pink'),(300,150,15,'cream'),(298,146,17,'green')]:
  rect(d,(x,y,x+w,y+3),c);d.line((x+3,y+1,x+w-2,y+1),fill=C['shadow'])
 return im.resize((W*SCALE,H*SCALE),Image.Resampling.NEAREST)

def main():
 frames=[frame(n) for n in range(FPS*SECONDS)]
 sheet=Image.new('RGB',(640,360))
 for i in range(16):sheet.paste(frames[i*8].resize((160,90)),((i%4)*160,(i//4)*90))
 palette=sheet.quantize(colors=128)
 indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
 durations=[round((n+1)*1000/FPS/10)*10-round(n*1000/FPS/10)*10 for n in range(len(frames))]
 destination=ROOT/'coding-desk.gif'
 indexed[0].save(destination,save_all=True,append_images=indexed[1:],duration=durations,loop=0,optimize=True,disposal=1)
 preview=ROOT.parent/'output/coding-desk';preview.mkdir(parents=True,exist_ok=True)
 frames[48].save(preview/'preview.png')
 print(f'{destination}: {destination.stat().st_size:,} bytes, {sum(durations)} ms')

if __name__=='__main__':main()
