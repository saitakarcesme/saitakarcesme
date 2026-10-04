"""Render a monochrome Earth and verified public GitHub profile counters.

python tools/build_digital_earth.py --refresh
Requires Pillow, NumPy and gh. --refresh reads authenticated GitHub APIs.
Coastlines: Natural Earth 1:110m (public domain).
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import argparse
import datetime as dt
import json
import math
import subprocess
from zoneinfo import ZoneInfo
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OWNER='saitakarcesme'
STATS_PATH=ROOT/'assets/profile-stats.json'
W,H,SS,FPS,SECONDS=960,540,2,12,24
CX,CY,R=480,288,176

def github(endpoint,params):
    command=['gh','api',endpoint,'--method','POST' if endpoint=='graphql' else 'GET']
    for key,value in params.items():command+=['-f',f'{key}={value}']
    return json.loads(subprocess.check_output(command,text=True))

def refresh():
    now=dt.datetime.now(dt.timezone.utc)
    start=now-dt.timedelta(days=365)
    fmt=lambda x:x.isoformat(timespec='seconds').replace('+00:00','Z')
    nodes=[];cursor=None;expected=None
    while True:
        after=f',after:{json.dumps(cursor)}' if cursor else ''
        query=f'''query {{ user(login:"{OWNER}") {{ repositories(ownerAffiliations:OWNER,privacy:PUBLIC,first:100{after}) {{ totalCount nodes {{ stargazerCount }} pageInfo {{ hasNextPage endCursor }} }} }} }}'''
        response=github('graphql',{'query':query})
        if response.get('errors'):raise RuntimeError(response['errors'])
        data=response['data']['user']['repositories'];expected=data['totalCount'];nodes+=data['nodes']
        if not data['pageInfo']['hasNextPage']:break
        cursor=data['pageInfo']['endCursor']
    assert len(nodes)==expected
    query=f'''query {{ user(login:"{OWNER}") {{ contributionsCollection(from:"{fmt(start)}",to:"{fmt(now)}") {{ commitContributionsByRepository(maxRepositories:100) {{ repository {{ isPrivate }} contributions {{ totalCount }} }} }} }} }}'''
    response=github('graphql',{'query':query})
    if response.get('errors'):raise RuntimeError(response['errors'])
    contributions=response['data']['user']['contributionsCollection']['commitContributionsByRepository']
    if len(contributions)>=100:raise RuntimeError('Contribution repository limit reached; expand collection before publishing.')
    prs=github('search/issues',{'q':f'type:pr author:{OWNER} is:public','per_page':'1'})
    if prs.get('incomplete_results'):raise RuntimeError('Incomplete PR search')
    stats={'username':OWNER,'repositories':expected,'stars':sum(x['stargazerCount'] for x in nodes),
           'pull_requests':prs['total_count'],'commits':sum(x['contributions']['totalCount'] for x in contributions if not x['repository']['isPrivate']),
           'commit_window_days':365,'updated_at':fmt(now),
           'definitions':{'repositories':'Public repositories owned by the account, including forks',
                          'stars':'Total stars on those public repositories',
                          'pull_requests':'All public pull requests authored by the account',
                          'commits':'Public GitHub commit contributions during the previous 365 days'}}
    STATS_PATH.write_text(json.dumps(stats,indent=2)+'\n')
    print({k:stats[k] for k in ['repositories','stars','pull_requests','commits']},flush=True)
    return stats

def font(size):
    for path in ['/System/Library/Fonts/Menlo.ttc','/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf']:
        if Path(path).exists():return ImageFont.truetype(path,size*SS)
    return ImageFont.load_default(size=size*SS)

FONTS={n:font(n) for n in [10,11,12,13,16,19,44]}
def label(d,x,y,s,size=12,gray=180,align='left'):
    f=FONTS[size];width=d.textlength(s,font=f)/SS
    if align=='center':x-=width/2
    elif align=='right':x-=width
    d.text((round(x*SS),round(y*SS)),s,font=f,fill=gray)

def line(d,points,gray=100,width=1):
    d.line([(round(x*SS),round(y*SS)) for x,y in points],fill=gray,width=width)

def xyz(coords):
    coords=np.radians(np.asarray(coords));lon,lat=coords[:,0],coords[:,1]
    return np.column_stack((np.cos(lat)*np.sin(lon),np.sin(lat),np.cos(lat)*np.cos(lon)))

def geometry():
    data=json.loads((ROOT/'assets/earth-coastlines.geojson').read_text())
    coast=[]
    for feature in data['features']:
        g=feature['geometry']
        paths=[g['coordinates']] if g['type']=='LineString' else g['coordinates']
        for path in paths:coast.append(xyz(path))
    grid=[]
    for latitude in range(-75,76,15):grid.append(xyz([(lon,latitude) for lon in range(-180,181,2)]))
    for longitude in range(-180,180,15):grid.append(xyz([(longitude,lat) for lat in range(-90,91,2)]))
    return coast,grid

COAST,GRID=geometry()
def project(path,angle):
    ca,sa=math.cos(angle),math.sin(angle)
    x=path[:,0]*ca+path[:,2]*sa
    z=-path[:,0]*sa+path[:,2]*ca
    # A small northward view reveals the Arctic rather than a flat circle.
    tilt=math.radians(12)
    y=path[:,1]*math.cos(tilt)-z*math.sin(tilt)
    z=path[:,1]*math.sin(tilt)+z*math.cos(tilt)
    return np.column_stack((CX+R*x,CY-R*y,z))

def stroke_visible(d,path,angle,gray,width):
    p=project(path,angle)
    current=[]
    for x,y,z in p:
        if z>=0:
            current.append((x,y))
        else:
            if len(current)>1:line(d,current,gray,width)
            current=[]
    if len(current)>1:line(d,current,gray,width)

def counter(d,x,y,name,value,note,t):
    # The reveal counts up to the actual fetched value; it never invents growth.
    p=min(1,max(0,t/3));p=1-(1-p)**3
    shown=round(value*p)
    line(d,[(x,y-14),(x+160,y-14)],48)
    label(d,x,y,name,12,160)
    label(d,x,y+23,f'{shown:,}',44,245)
    label(d,x,y+85,note,10,100)
    line(d,[(x,y+112),(x+160,y+112)],30)
    line(d,[(x,y+112),(x+160*p,y+112)],165)

def frame(n,stats):
    t=n/FPS;angle=-math.radians(20)+2*math.pi*n/(FPS*SECONDS)
    im=Image.new('L',(W*SS,H*SS),0);d=ImageDraw.Draw(im)
    label(d,38,26,'SAITAKARCESME',19,235)
    label(d,922,33,'GITHUB / PUBLIC ACTIVITY',11,125,'right')
    line(d,[(38,69),(922,69)],45)
    # Slightly stronger strokes; only the visible hemisphere is drawn.
    d.ellipse(((CX-R)*SS,(CY-R)*SS,(CX+R)*SS,(CY+R)*SS),outline=170,width=2)
    for path in GRID:stroke_visible(d,path,angle,48,2)
    for path in COAST:stroke_visible(d,path,angle,240,3)
    # Sparse cartographic registration marks give the globe breathing room.
    for x,y,dx,dy in [(CX-R-12,CY,-1,0),(CX+R+12,CY,1,0),(CX,CY-R-12,0,-1),(CX,CY+R+12,0,1)]:
        line(d,[(x,y),(x+dx*7,y+dy*7)],100)
    counter(d,38,128,'REPOSITORIES',stats['repositories'],'PUBLIC / INCL. FORKS',t)
    counter(d,38,326,'STARS',stats['stars'],'ACROSS PUBLIC REPOS',t)
    counter(d,762,128,'PULL REQUESTS',stats['pull_requests'],'PUBLIC / ALL TIME',t)
    counter(d,762,326,'COMMITS',stats['commits'],'PUBLIC / LAST 365 DAYS',t)
    label(d,CX,478,'EARTH / 360 DEG',10,95,'center')
    line(d,[(38,508),(922,508)],45)
    label(d,38,519,'PUBLIC CONTRIBUTIONS',10,90)
    # Honest snapshot metadata, rather than a simulated live feed.
    updated=dt.datetime.fromisoformat(stats['updated_at'].replace('Z','+00:00')).astimezone(ZoneInfo('Europe/Luxembourg')).date().isoformat()
    label(d,922,519,'UPDATED '+updated,10,90,'right')
    # White strokes with graded opacity keep antialiasing free of black halos.
    alpha=im.resize((W,H),Image.Resampling.LANCZOS)
    transparent=Image.new('RGBA',(W,H),(255,255,255,0))
    transparent.putalpha(alpha)
    return transparent

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--refresh',action='store_true');args=parser.parse_args()
    stats=refresh() if args.refresh else json.loads(STATS_PATH.read_text())
    frames=[frame(n,stats) for n in range(FPS*SECONDS)]
    durations=[round((n+1)*1000/FPS/10)*10-round(n*1000/FPS/10)*10 for n in range(len(frames))]
    # Animated WebP preserves the full alpha channel and smooth fine strokes.
    destination=ROOT/'digital-earth.webp'
    frames[0].save(destination,save_all=True,append_images=frames[1:],duration=durations,loop=0,lossless=True,method=4)
    preview=ROOT.parent/'output/digital-earth';preview.mkdir(parents=True,exist_ok=True)
    frames[4*FPS].save(preview/'preview.png')
    print(f'{destination}: {destination.stat().st_size:,} bytes / {sum(durations)} ms',flush=True)

if __name__=='__main__':main()
