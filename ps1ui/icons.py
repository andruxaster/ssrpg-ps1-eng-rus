import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,json,collections
S=_W+''
sys.path.insert(0,S+'/ps1ui'); sys.path.insert(0,S+'/tools')
import psi
p=psi.load()
M=json.load(open(S+'/ps1ui/gfx/ng_icon_masks.json'))
def parse(s): return [[1 if c=='#' else 0 for c in r] for r in s.strip().split('\n')]
M['rescue']=parse('''
................
......####......
......####......
......####......
......####......
..############..
..############..
..############..
..############..
......####......
......####......
......####......
......####......
................
................
................''')
M['form']=parse('''
................
.......##.......
......####......
......####......
.......##.......
.....######.....
..##..####..##..
.####.####.####.
.####.#..#.####.
..##..#..#..##..
.######..######.
..####....####..
..####....####..
..#..#....#..#..
..#..#....#..#..
................''')
# usage of tiles across groups
use=collections.Counter()
for g,n,ents in p.groups:
    for e in ents: use[e[2]]+=1
def composite(gi):
    g,n,ents=p.groups[gi]; C={}
    for x,y,t,f in ents:
        for yy in range(16):
            for xx in range(16): C[(x+xx,y+yy)]=(t,xx,yy)
    return C
edits={}
def px(t):
    if t not in edits: edits[t]=p.tile(t)
    return edits[t]
C=composite(1)
order=[['sword','special','run','rescue'],['bag','armor','mask','form']]
for r,(y0) in enumerate((5,28)):
    for c,name in enumerate(order[r]):
        x0=26+20*c
        m=M[name]
        # interior 18 x 17: x0..x0+17, y0..y0+16
        for y in range(17):
            for x in range(18):
                t,tx,ty=C[(x0+x,y0+y)]; P=px(t)
                if P[ty][tx] in (1,0xe): P[ty][tx]=0xc
        oy=y0+(17-16)//2; ox=x0+1
        on=set((ox+x,oy+y) for y in range(16) for x in range(16) if m[y][x])
        for (x,y) in on:
            for dx,dy in ((1,0),(0,1)):
                q=(x+dx,y+dy)
                if q not in on and x0<=q[0]<x0+18 and y0<=q[1]<y0+17:
                    t,tx,ty=C[q]; px(t)[ty][tx]=0xe
        for (x,y) in on:
            t,tx,ty=C[(x,y)]; px(t)[ty][tx]=1
shared=[t for t in edits if use[t]>1]
print('edited tiles',len(edits),'shared',shared)
for t,P in edits.items(): p.settile(t,P)
open(S+'/ps1ui/gfx/BT_COCK.PSI','wb').write(p.d)
from PIL import Image
p.render(1).crop((0,0,120,64)).resize((480,256),Image.NEAREST).save(S+'/ps1ui/gfx/g1_new.png')
