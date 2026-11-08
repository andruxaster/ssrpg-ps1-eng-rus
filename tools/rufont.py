import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,pickle
sys.path.insert(0,_W+'/tools')
sys.path.insert(0,_W+'/ru/font')
import spr,halves,labels,cyr
S=halves.S
D=halves.d
order,first,u=pickle.load(open(S+'/out/halves.pkl','rb'))
hid={h:i for i,h in enumerate(order)}
# map char -> half id (most frequent)
best={}
for i,lab in labels.LAB.items():
    if len(lab)!=1: continue
    if lab not in best or u[order[i]]>u[order[best[lab]]]: best[lab]=i
def half_from_tile(t,side):
    p=spr.tile(D,t); x0=0 if side==0 else 8
    return [[p[y][x0+x] for x in range(8)] for y in range(16)]
# find a tile where half id appears on given side
where={}
for t in range(halves.NT):
    L,R=halves.halves(t)
    where.setdefault((hid[L],0),t); where.setdefault((hid[R],1),t)
BG={0:half_from_tile(1,0),1:half_from_tile(1,1)}
def mask_of(ch):
    if ch in cyr.FROM_LATIN: ch=cyr.FROM_LATIN[ch]
    if ch in cyr.CAPS: rows=cyr.CAPS[ch].strip().split('\n'); top=1
    elif ch in cyr.LOWER: rows=cyr.LOWER[ch].strip().split('\n'); top=4
    elif ch in cyr.TALL: rows=cyr.TALL[ch].strip().split('\n'); top=1
    else: return None
    m=[[0]*8 for _ in range(16)]
    for y,r in enumerate(rows):
        for x,c in enumerate(r[:8]):
            if c=='#': m[top+y][x]=1
    return m
def synth(mask,side):
    bg=BG[side]; p=[row[:] for row in bg]
    for y in range(16):
        for x in range(8):
            if mask[y][x]: p[y][x]=9
    for y in range(16):
        for x in range(8):
            if mask[y][x]: continue
            if (x>0 and mask[y][x-1]) or (x>0 and y>0 and mask[y-1][x-1]) or (y>0 and mask[y-1][x]):
                p[y][x]=2
    return p
def half4(ch,side):
    if ch in cyr.FROM_LATIN: ch=cyr.FROM_LATIN[ch]
    if ch in best:
        h=best[ch]; t=where.get((h,side))
        if t is None:
            t=where.get((h,1-side)); hp=half_from_tile(t,1-side)
            return hp
        return half_from_tile(t,side)
    m=mask_of(ch)
    if m is None: raise KeyError(ch)
    return synth(m,side)
def tile_pixels(pair):
    a=half4(pair[0],0); b=half4(pair[1],1)
    return [a[y]+b[y] for y in range(16)]
def encode_tile(px):
    out=bytearray(128)
    for blk,(bx,by) in enumerate([(8,0),(8,8),(0,0),(0,8)]):
        for y in range(8):
            for p in range(4):
                v=0
                for x in range(8):
                    if (px[by+y][bx+x]>>p)&1: v|=1<<x
                out[blk*32+y*4+p]=v
    return bytes(out)
CHARSET=set(cyr.FROM_LATIN)|set(cyr.CAPS)|set(cyr.LOWER)|set(cyr.TALL)|set(best)
