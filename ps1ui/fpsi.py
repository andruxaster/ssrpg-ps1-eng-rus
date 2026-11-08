"""PSI-like sprite banks (type 7 chunks) inside field packages."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import struct,sys
from PIL import Image
S=_W+''
sys.path.insert(0,S+'/tools')
import fld
def s16(v): return v-65536 if v>=32768 else v
class Bank:
    def __init__(self,d):
        self.d=bytearray(d)
        self.dataoff,self.a,self.b,self.ntiles=struct.unpack_from('<IHHI',d,0)
        offs=[]; o=16
        while o<self.dataoff:
            v=struct.unpack_from('<I',d,o)[0]
            if v==0 or v>=self.dataoff: break
            offs.append(v); o+=4
        self.groups=[]
        for g in offs:
            n=struct.unpack_from('<I',d,g)[0]
            if n>600: continue
            e=[struct.unpack_from('<4H',d,g+8+8*k) for k in range(n)]
            self.groups.append((g,[(s16(x),s16(y),t,f) for x,y,t,f in e]))
    def tile(self,t):
        base=self.dataoff+t*128
        return [[(self.d[base+y*8+x//2]>>(4*(x&1)))&15 for x in range(16)] for y in range(16)]
    def settile(self,t,px):
        base=self.dataoff+t*128
        for y in range(16):
            for x in range(0,16,2): self.d[base+y*8+x//2]=(px[y][x]&15)|((px[y][x+1]&15)<<4)
    def render(self,gi,colors=None):
        g,e=self.groups[gi]
        e=[q for q in e if q[2]<self.ntiles]
        if not e: return None
        x0=min(q[0] for q in e); y0=min(q[1] for q in e)
        W=max(q[0] for q in e)-x0+16; H=max(q[1] for q in e)-y0+16
        if W>1024 or H>1024: return None
        im=Image.new('RGB',(W,H),(255,0,255))
        for x,y,t,f in e:
            p=self.tile(t)
            for yy in range(16):
                for xx in range(16):
                    v=p[yy][xx]
                    if v: im.putpixel((x-x0+xx,y-y0+yy),colors[v] if colors else (v*17,)*3)
        return im
def packages(d): return fld.subarchives(d)
