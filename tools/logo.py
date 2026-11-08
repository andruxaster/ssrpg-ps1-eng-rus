"""Neo Geo CD LOGO*.PRG (CDZ loading screen) parse/render/write."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import struct,sys
S=_W+''
sys.path.insert(0,S+'/tools')
import fixr
def W(d,o): return struct.unpack('>H',d[o:o+2])[0]
def parse(d):
    n=W(d,0); recs=[]; o=2
    while True:
        a=struct.unpack('>I',d[o:o+4])[0]
        if a==0xffffffff: break
        typ=W(d,o+2) if False else None
        recs.append(d[o:o+8]); o+=8
    out={}
    for r in recs:
        typ=W(r,2); ptr=struct.unpack('>I',r[4:8])[0]-0x120000
        out[typ]=ptr
    return out
def info(d):
    p=parse(d)
    t1=p[1]; dst=struct.unpack('>I',d[t1:t1+4])[0]; size=struct.unpack('>I',d[t1+4:t1+8])[0]
    tiles_off=t1+8
    # skip ffffffff terminators
    pal=p[2]; mp=p[3]
    return dict(dst=dst,size=size,tiles=tiles_off,pal=pal,map=mp)
def sw(b): return bytes(b[i^1] for i in range(len(b)))
def tiles_fix(d):
    i=info(d); return sw(d[i['tiles']:i['tiles']+i['size']]), i['dst']//64
def palettes(d):
    i=info(d); o=i['pal']; pals={}
    while True:
        n=W(d,o)
        if n>=256 or o+34>i['map']: break
        cols=[W(d,o+2+2*k) for k in range(16)]; pals[n]=cols; o+=34
        if o>=i['map']: break
    return pals
def tmap(d):
    i=info(d); o=i['map']; addr=W(d,o); w=W(d,o+2); h=W(d,o+4)
    ent=[W(d,o+6+2*k) for k in range(w*h)]
    return addr,w,h,ent
def color(c):
    r=((c>>8)&15)<<1|((c>>14)&1); g=((c>>4)&15)<<1|((c>>13)&1); b=(c&15)<<1|((c>>12)&1)
    k=255/31; dk=0.85 if c&0x8000 else 1
    return (int(r*k*dk),int(g*k*dk),int(b*k*dk))
def render(d,order='row'):
    from PIL import Image
    fix,base=tiles_fix(d); pals=palettes(d); addr,w,h,ent=tmap(d)
    im=Image.new('RGB',(320,256))
    c0=(addr-0x7000)//32; r0=(addr-0x7000)%32
    for k,e in enumerate(ent):
        if order=='row': r,c=divmod(k,w)
        else: c,r=divmod(k,h)
        t=e&0xfff; p=e>>12; ti=t-base
        if ti<0 or ti*32>=len(fix): continue
        px=fixr.fixtile(fix,ti); pal=pals.get(p,[0]*16)
        for y in range(8):
            for x in range(8):
                if px[y][x]: im.putpixel(((c0+c)*8+x,(r0+r)*8+y),color(pal[px[y][x]]))
    return im
if __name__=='__main__':
    import glob,os
    from PIL import Image
    fs=sorted(glob.glob(S+'/ngcd/en/LOGO*.PRG'))
    sheet=Image.new('RGB',(320*4,256*((len(fs)+3)//4)))
    from PIL import ImageDraw
    dr=ImageDraw.Draw(sheet)
    for k,f in enumerate(fs):
        d=open(f,'rb').read()
        try: im=render(d,sys.argv[1] if len(sys.argv)>1 else 'row')
        except Exception as e: print(f,e); continue
        sheet.paste(im,((k%4)*320,(k//4)*256)); dr.text(((k%4)*320+2,(k//4)*256+2),os.path.basename(f),fill=(255,0,0))
    sheet.save(S+'/ru/gfx/logos.png'); print(info(open(fs[0],'rb').read()))

class Canvas:
    """indexed canvas 320x256: pal map per cell, idx per pixel"""
    def __init__(self,d):
        self.d=bytearray(d); self.i=info(d)
        self.fix,self.base=tiles_fix(d); self.pals=palettes(d)
        self.addr,self.w,self.h,self.ent=tmap(d)
        self.c0=(self.addr-0x7000)//32; self.r0=(self.addr-0x7000)%32
        self.px=[[0]*320 for _ in range(256)]; self.cp={}
        self.other={}
        for k,e in enumerate(self.ent):
            r,c=divmod(k,self.w); C,R=self.c0+c,self.r0+r
            t=e&0xfff; p=e>>12; ti=t-self.base; self.cp[(C,R)]=p
            if ti<0 or ti*32>=len(self.fix): self.other[(C,R)]=e; continue
            pp=fixr.fixtile(self.fix,ti)
            for y in range(8):
                for x in range(8): self.px[R*8+y][C*8+x]=pp[y][x]
    def ntiles(self):
        return len(set(e&0xfff for e in self.ent))
    def image(self):
        from PIL import Image
        im=Image.new('RGB',(320,256))
        for (C,R),p in self.cp.items():
            pal=self.pals.get(p,[0]*16)
            for y in range(8):
                for x in range(8):
                    v=self.px[R*8+y][C*8+x]
                    if v: im.putpixel((C*8+x,R*8+y),color(pal[v]))
        return im
    def build(self):
        cap=self.i['size']//32
        tiles={}; order=[]; newent=[]
        blank=bytes(32)
        for k in range(len(self.ent)):
            r,c=divmod(k,self.w); C,R=self.c0+c,self.r0+r
            if (C,R) in self.other and not any(self.px[R*8+y][C*8+x] for y in range(8) for x in range(8)):
                newent.append(self.other[(C,R)]); continue
            b=bytearray(32)
            for ci,x0 in enumerate((4,6,0,2)):
                for y in range(8):
                    b[ci*8+y]=self.px[R*8+y][C*8+x0]|(self.px[R*8+y][C*8+x0+1]<<4)
            b=bytes(b)
            if b not in tiles: tiles[b]=len(order); order.append(b)
            newent.append((self.cp[(C,R)]<<12)|(self.base+tiles[b]))
        assert len(order)<=cap,(len(order),cap)
        data=b''.join(order)+bytes(32*(cap-len(order)))
        data=data+bytes(self.i['size']-len(data))
        d=self.d
        d[self.i['tiles']:self.i['tiles']+self.i['size']]=sw(data)
        o=self.i['map']+6
        for k,e in enumerate(newent): d[o+2*k:o+2*k+2]=struct.pack('>H',e)
        return bytes(d),len(order),cap
