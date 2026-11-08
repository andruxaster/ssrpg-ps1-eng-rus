"""Graphic label translation project: screens, file mapping, write-back."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,os,collections
S=_W+''
sys.path.insert(0,S+'/tools')
import scr,relabel
from spr import tile
from rufont import encode_tile
TARGETS=['CHIP1094','CHIPF001','CHIPF002','CHIPF005','CHIP0000','CHIP00B2','CHIP000F']
B=S+'/ru/build'
FILES={}
def orig(name):
    p=S+'/ngcd/en/%s.SPR'%name
    return open(p,'rb').read()
def cur(name):
    if name not in FILES:
        p=B+'/%s.SPR'%name
        FILES[name]=bytearray(open(p,'rb').read() if os.path.exists(p) else orig(name))
    return FILES[name]
def ref(name):
    p=B+'/%s.SPR.ran'%name
    return open(p,'rb').read() if os.path.exists(p) else orig(name)
class GScreen(relabel.Screen):
    def __init__(self,name):
        super().__init__(name)
        self.map={}   # file -> tile offset
        self.okt=set()
        for f in TARGETS:
            d=ref(f); n=len(d)//128
            sig=next((t for t in range(n) if len(set(d[t*128:(t+1)*128]))>4),None)
            if sig is None: continue
            k=self.s.find(d[sig*128:(sig+4)*128])
            while k>=0 and k%128: k=self.s.find(d[sig*128:(sig+4)*128],k+1)
            if k<0: continue
            o=k//128-sig
            ok=sum(1 for t in range(0,n,7) if self.s[(o+t)*128:(o+t+1)*128]==d[t*128:(t+1)*128])
            if ok>=0.3*len(range(0,n,7)):
                self.map[f]=o
                c=cur(f)
                for t in range(n):
                    a=(o+t)*128
                    if a+128>len(self.s): break
                    if self.s[a:a+128]==d[t*128:(t+1)*128]:
                        self.okt.add(o+t); self.s[a:a+128]=c[t*128:(t+1)*128]
        # usage count of tiles
        self.uses=collections.Counter()
        for s_,x,y,cells in scr.sprite_list(self.v):
            for t,pal,fl in cells:
                if t: self.uses[t]+=1
        self.ro=set(t for t,c in self.uses.items() if c>1)
        self.top=scr.render_top(self.v,self.s,y0=0,x0=8)
        self.src=scr.render(self.v,self.s,y0=0,x0=8)
    def wr(self,t): return t not in self.ro and self.owner(t) is not None
    def put(self,x,y,v):
        e=self.src.get((x,y)); tp=self.top.get((x,y))
        if tp and tp!=e and tp[0]!=(e[0] if e else None) and self.wr(tp[0]) and (not e or not self.wr(e[0])):
            self.src[(x,y)]=tp; e=tp
        if not e: return False
        if not self.wr(e[0]): return False
        return super().put(x,y,v)
    def owner(self,t):
        if t not in self.okt: return None
        for f,o in self.map.items():
            if o<=t<o+len(cur(f))//128: return f,t-o
        return None
    def commit(self):
        n=0
        for t,px in self.edited.items():
            ow=self.owner(t)
            if not ow: continue
            f,i=ow
            cur(f)[i*128:(i+1)*128]=encode_tile(px); n+=1
        return n
def save():
    for f,d in FILES.items():
        open(B+'/%s.SPR'%f,'wb').write(d)
