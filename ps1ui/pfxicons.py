"""Battle FIX-layer overlays in FIX_00.PFX (tile layout: 16 tiles per row, see EXE 0x80037270/0x800378dc):
 - command highlight frames 3x3 tiles at 928,931,934,937 / 976,979,982,985 -> NGCD-style icons
 - technique slot highlights 2x2 tiles at 940,942,972,974,1004,1006 -> roman numerals I..VI
 - rage label 2x2 tiles at 312 -> 'ГНЕВ'
Run after pfxplates.py (reads/writes ps1ui/gfx/FIX_00.PFX)."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import numpy as np
S=_W+''
src=open(S+'/ps1ui/icons.py').read()
hdr=src[:src.index('# usage of tiles')].replace('p=psi.load()','')
ns={}; exec(hdr,ns); M=ns['M']
G=S+'/ps1ui/gfx/FIX_00.PFX'
d=bytearray(open(G,'rb').read())
O=open(S+'/ps1/fs/FIX_00.PFX','rb').read()
def tile(t,src=None):
    b=np.frombuffer(bytes((src or d)[t*32:t*32+32]),np.uint8); return np.stack([b&15,b>>4],-1).reshape(8,8)
def settile(t,p):
    p=np.asarray(p,np.uint8); d[t*32:t*32+32]=bytes((p[:,0::2]|(p[:,1::2]<<4)).flatten())
def getblock(t0,w,h,src=None): return np.block([[tile(t0+r*16+c,src) for c in range(w)] for r in range(h)]).astype(int)
def putblock(t0,a):
    h,w=a.shape[0]//8,a.shape[1]//8
    for r in range(h):
        for c in range(w): settile(t0+r*16+c,a[r*8:r*8+8,c*8:c*8+8])
# restore any tiles touched by older versions of this script (rows 13..17 of the 512-wide view)
for t in list(range(13*64,18*64))+[313,314,328,329]: d[t*32:t*32+32]=O[t*32:t*32+32]
# ---- command frames
CMDS={928:'sword',931:'special',934:'run',937:'rescue',976:'bag',979:'armor',982:'mask',985:'form'}
for t0,name in CMDS.items():
    a=getblock(t0,3,3,O)
    fr=(a==2)
    rows=[y for y in range(24) if fr[y].sum()>=16]; cols=[x for x in range(24) if fr[:,x].sum()>=12]
    top=max(r for r in rows if r<12); bot=min(r for r in rows if r>12)
    lef=max(c for c in cols if c<12); rig=min(c for c in cols if c>12)
    y0,y1,x0,x1=top+1,bot-1,lef+1,rig-1
    a[y0:y1+1,x0:x1+1]=0
    m=np.array(M[name],np.uint8); ys,xs=np.nonzero(m); m=m[ys.min():ys.max()+1,xs.min():xs.max()+1]
    mh,mw=m.shape; ih,iw=y1-y0+1,x1-x0+1
    if mh>ih or mw>iw:
        from PIL import Image
        mh,mw=min(mh,ih),min(mw,iw); m=(np.array(Image.fromarray(m*255).resize((mw,mh),Image.NEAREST))>0).astype(np.uint8)
    oy=y0+(ih-mh)//2; ox=x0+(iw-mw)//2
    a[oy:oy+mh,ox:ox+mw][m>0]=1
    putblock(t0,a)
# ---- roman numerals for technique slots
I_=['####','.##.','.##.','.##.','.##.','.##.','.##.','.##.','.##.','.##.','.##.','####']
V_=['##...##','##...##','##...##','##...##','.##.##.','.##.##.','.##.##.','.##.##.','..###..','..###..','...#...','...#...']
def glue(*parts):
    rows=[]
    for y in range(12): rows.append('.'.join(p[y] for p in parts))
    return rows
NUM={940:glue(I_),942:glue(I_,I_),972:glue(I_,I_,I_),974:glue(I_,V_),1004:glue(V_),1006:glue(V_,I_)}
for t0,g in NUM.items():
    a=np.zeros((16,16),int); w=len(g[0]); ox=(16-w)//2; oy=2
    on=[(ox+x,oy+y) for y in range(12) for x in range(w) if g[y][x]=='#']
    S_=set(on)
    for x,y in on:
        for dx,dy in ((1,0),(0,1),(1,1)):
            X,Y=x+dx,y+dy
            if (X,Y) not in S_ and X<16 and Y<16: a[Y,X]=2
    for x,y in on: a[y,x]=1
    putblock(t0,a)
# ---- rage label 'ГНЕВ' (2x2 at 312): white plate rows 4..15, 3x5 letters
F3={'Г':['###','#..','#..','#..','#..'],'Н':['#.#','#.#','###','#.#','#.#'],
    'Е':['###','#..','##.','#..','###'],'В':['##.','#.#','##.','#.#','##.']}
a=getblock(312,2,2,O)
a[4:15,0:16]=np.where(a[4:15,0:16]!=0,15,0)
a[5:14,1:16]=15
x=1
for ch in 'ГНЕВ':
    for yy,row in enumerate(F3[ch]):
        for xx,cc in enumerate(row):
            if cc=='#': a[7+yy,x+xx]=1
    x+=4
putblock(312,a)
open(G,'wb').write(d)
