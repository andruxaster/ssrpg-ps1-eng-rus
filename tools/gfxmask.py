import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys
S=_W+''
sys.path.insert(0,S+'/tools')
import gfx,relabel
from PIL import Image
def mask(name,box,fn,scale=4):
    sc=gfx.GScreen(name)
    x0,y0,x1,y1=box
    relabel.preview(sc,'/tmp/_p.png',scale=1)
    im=Image.open('/tmp/_p.png').convert('RGB')
    px=im.load()
    for y in range(y0,y1):
        for x in range(x0,x1):
            e=sc.src.get((x,y))
            if not e: continue
            t=e[0]
            if t in sc.ro or not sc.owner(t):
                r,g,b=px[x,y]; px[x,y]=(min(255,r+120),g//2,b//2)
    for x in range(x0,x1,8):
        pass
    im=im.crop(box).resize(((x1-x0)*scale,(y1-y0)*scale),Image.NEAREST)
    im.save(fn)
if __name__=='__main__':
    mask(sys.argv[1],tuple(map(int,sys.argv[2:6])),sys.argv[6])
