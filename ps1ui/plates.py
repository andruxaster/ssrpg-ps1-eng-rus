import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,collections
S=_W+''
sys.path.insert(0,S+'/ps1ui'); sys.path.insert(0,S+'/tools')
import psi,pixfont
p=psi.PSI(open(S+'/ps1ui/gfx/BT_COCK.PSI','rb').read(),open(S+'/ps1/fs/BTL/P6_BCOCK.COL','rb').read())
edits={}
def px(t):
    if t not in edits: edits[t]=p.tile(t)
    return edits[t]
def comp(gi):
    g,n,ents=p.groups[gi]; C={}
    for x,y,t,f in ents:
        for yy in range(16):
            for xx in range(16): C[(x+xx,y+yy)]=(t,xx,yy)
    return C
def get(C,x,y): t,tx,ty=C[(x,y)]; return px(t)[ty][tx]
def put(C,x,y,v): t,tx,ty=C[(x,y)]; px(t)[ty][tx]=v
ROMAN={'I':['..######..','....##....','....##....','....##....','....##....','....##....','....##....','....##....','....##....','..######..'],}
def roman(s):
    # build glyph by composing I and V strokes
    I=['###','.#.','.#.','.#.','.#.','.#.','.#.','.#.','.#.','###']
    V=['##...##','.#...#.','.#...#.','.#...#.','..#.#..','..#.#..','..#.#..','...#...','...#...','...#...']
    I=['##','##','##','##','##','##','##','##','##','##']
    V=['##....##','##....##','.##..##.','.##..##.','.##..##.','..####..','..####..','..####..','...##...','...##...']
    parts=[I if c=='I' else V for c in s]
    rows=[]
    for y in range(10):
        rows.append('.'.join(pp[y] for pp in parts))
    return rows
def draw_mask(C,x0,y0,w,h,rows):
    mh=len(rows); mw=len(rows[0])
    ox=x0+(w-mw)//2; oy=y0+(h-mh)//2
    on=set((ox+x,oy+y) for y in range(mh) for x in range(mw) if rows[y][x]=='#')
    for (x,y) in on:
        for dx,dy in ((1,0),(0,1)):
            q=(x+dx,y+dy)
            if q not in on and q in C and get(C,*q)!=1: put(C,q[0],q[1],0xe)
    for (x,y) in on: put(C,x,y,1)
def erase(C,x0,y0,x1,y1):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1):
            if (x,y) in C and get(C,x,y) in (1,0xe): put(C,x,y,0xc)
for gi,label in ((2,'ВЕЩИ'),(3,'ПРИЕМЫ')):
    C=comp(gi)
    erase(C,34,1,77,14)
    bm=pixfont.render_line(label,8 if len(label)<=5 else 7)[:7]
    rows=[''.join('#' if v else '.' for v in r) for r in bm]
    draw_mask(C,34,1,44,14,rows)
C=comp(2)
for r,y0 in enumerate((17,34)):
    for c,x0 in enumerate((25,49,73)):
        erase(C,x0,y0,x0+16,y0+13)
        draw_mask(C,x0,y0,17,14,roman(['I','II','III','IV','V','VI'][r*3+c]))
use=collections.Counter(e[2] for g,n,ents in p.groups for e in ents)
print('edited',len(edits),'shared',[(t,use[t]) for t in edits if use[t]>1])
for t,P in edits.items(): p.settile(t,P)
open(S+'/ps1ui/gfx/BT_COCK.PSI','wb').write(p.d)
from PIL import Image
o=Image.new('RGB',(320,140))
o.paste(p.render(1).crop((0,0,320,64)),(0,0)); o.paste(p.render(3).crop((0,0,320,64)),(0,70))
o.crop((0,0,140,140)).resize((560,560),Image.NEAREST).save(S+'/ps1ui/gfx/panels_new.png')
