"""Edit a tile file in sheet space (32 tiles per row), using relabel's API."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys
S=_W+''
sys.path.insert(0,S+'/tools')
import gfx
from spr import tile
COLS=32
class Sheet:
    def __init__(self,f,cols=COLS,base=0,count=None):
        self.f=f; self.d=gfx.cur(f); self.cols=cols; self.edited={}; self.base=base
        self.n=count if count else len(self.d)//128-base
        self.src={}
    def _t(self,x,y):
        t=(y//16)*self.cols+x//16
        return t+self.base if 0<=x<self.cols*16 and 0<=t<self.n and y>=0 else None
    def tilepx(self,t):
        if t not in self.edited: self.edited[t]=tile(self.d,t)
        return self.edited[t]
    def get(self,x,y):
        t=self._t(x,y)
        return None if t is None else self.tilepx(t)[y%16][x%16]
    def put(self,x,y,v):
        t=self._t(x,y)
        if t is None: return False
        self.tilepx(t)[y%16][x%16]=v; return True
    def commit(self):
        from rufont import encode_tile
        for t,px in self.edited.items(): self.d[t*128:(t+1)*128]=encode_tile(px)
        return len(self.edited)
    def dump(self,x0,y0,x1,y1):
        for y in range(y0,y1):
            print('%4d '%y+''.join('%x'%self.get(x,y) if self.get(x,y) is not None else '.' for x in range(x0,x1)))
