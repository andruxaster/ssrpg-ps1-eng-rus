import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import struct
from PIL import Image
S=_W+''
class PSI:
    def __init__(self,d,col):
        self.d=bytearray(d); self.col=col
        self.dataoff=struct.unpack('<I',d[0:4])[0]
        self.ntiles=struct.unpack('<I',d[8:12])[0]
        offs=[]; o=16
        while True:
            v=struct.unpack('<I',d[o:o+4])[0]
            if v==0 or v>=self.dataoff: break
            offs.append(v); o+=4
        self.groups=[]
        for g in offs:
            n=struct.unpack('<I',d[g:g+4])[0]
            ents=[struct.unpack('<4H',d[g+8+8*k:g+16+8*k]) for k in range(n)] if n<500 else []
            self.groups.append((g,n,ents))
    def tile(self,t):
        base=self.dataoff+t*128; out=[[0]*16 for _ in range(16)]
        for y in range(16):
            for x in range(16):
                if base+y*8+x//2>=len(self.d): continue
                b=self.d[base+y*8+x//2]; out[y][x]=(b>>(4*(x&1)))&15
        return out
    def settile(self,t,px):
        base=self.dataoff+t*128
        for y in range(16):
            for x in range(0,16,2):
                self.d[base+y*8+x//2]=(px[y][x]&15)|((px[y][x+1]&15)<<4)
    def color(self,v,pal=0):
        w=struct.unpack('<H',self.col[(pal*16+v)*2:(pal*16+v)*2+2])[0]
        return ((w&31)*8,((w>>5)&31)*8,((w>>10)&31)*8)
    def render(self,gi,pal=0):
        g,n,ents=self.groups[gi]
        if not ents or max(e[0] for e in ents)>640 or max(e[1] for e in ents)>480: return None
        W=max(e[0] for e in ents)+16; H=max(e[1] for e in ents)+16
        im=Image.new('RGB',(W,H),(255,0,255))
        for x,y,t,f in ents:
            p=self.tile(t)
            for yy in range(16):
                for xx in range(16):
                    im.putpixel((x+xx,y+yy),self.color(p[yy][xx],pal))
        return im
def load():
    return PSI(open(S+'/ps1/fs/BTL/BT_COCK.PSI','rb').read(),open(S+'/ps1/fs/BTL/P6_BCOCK.COL','rb').read())
