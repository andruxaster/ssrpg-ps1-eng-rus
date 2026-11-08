import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys
S=_W+''
sys.path.insert(0,S+'/tools')
import pixfont
d=bytearray(open(S+'/ps1/fs/FIX_00.PFX','rb').read())
def ga(x,y):
    t=(y//8)*64+x//8; o=t*32+(y%8)*4+(x%8)//2; return (d[o]>>(4*(x&1)))&15
def pa(x,y,v):
    t=(y//8)*64+x//8; o=t*32+(y%8)*4+(x%8)//2
    d[o]=(d[o]&(0xf0 if not x&1 else 0x0f))|(v<<(4*(x&1)))
GR=[1,1,2,3,4,5,6]
for (x0,x1,label) in ((266,294,'HP'),(306,334,'SP')):
    for y in range(32,39):
        for x in range(x0,x1+1):
            if ga(x,y) in (1,2,3,4,5,6): pa(x,y,7)
    bm=pixfont.render_line(label,8)[:7]
    w=len(bm[0]); ox=x0+(x1-x0+1-w)//2
    for y in range(7):
        for x in range(w):
            if bm[y][x]: pa(ox+x,32+y,GR[y])
open(S+'/ps1ui/gfx/FIX_00.PFX','wb').write(d)
for y in range(40,48): print(''.join('%x'%ga(x,y) if ga(x,y) else '.' for x in range(56,82)))
for y in range(31,40): print(''.join('%x'%ga(x,y) for x in range(258,340)))
