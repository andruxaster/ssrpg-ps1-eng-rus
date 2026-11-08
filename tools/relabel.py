"""Redraw sprite text labels: erase EN text in a screen rect, draw Russian text, write back into tile data."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,collections,glob,os,hashlib
S=_W+''
sys.path.insert(0,S+'/tools')
import scr,pixfont
from spr import tile
from rufont import encode_tile
class Screen:
    def __init__(self,name):
        self.v=open(S+'/emu/cd/g_%s.v'%name,'rb').read(); self.s=bytearray(open(S+'/emu/cd/g_%s.s'%name,'rb').read())
        self.src=scr.render(self.v,self.s,y0=0,x0=8)
        self.edited={}   # tile -> 16x16 pixel list
    def tilepx(self,t):
        if t not in self.edited: self.edited[t]=tile(self.s,t)
        return self.edited[t]
    def get(self,x,y):
        e=self.src.get((x,y))
        if not e: return None
        t,tx,ty,pal,val=e
        return self.tilepx(t)[ty][tx]
    def put(self,x,y,v):
        e=self.src.get((x,y))
        if not e: return False
        t,tx,ty,pal,val=e
        self.tilepx(t)[ty][tx]=v; return True
def relabel(sc,rect,text,font='pix',pitch=7,text_idx=None,align='center',dy=0,body=None,shadow=None,bg_idx=None,font_h=7):
    x0,y0,x1,y1=rect
    vals=collections.Counter(sc.get(x,y) for y in range(y0,y1+1) for x in range(x0,x1+1) if sc.get(x,y) is not None)
    # background sample: border ring
    ring=collections.Counter()
    for x in range(x0-3,x1+4):
        for y in (y0-3,y0-2,y1+2,y1+3):
            v=sc.get(x,y); 
            if v is not None: ring[v]+=1
    for y in range(y0,y1+1):
        for x in (x0-3,x0-2,x1+2,x1+3):
            v=sc.get(x,y)
            if v is not None: ring[v]+=1
    if text_idx is None:
        text_idx=set(range(1,12))
    text_idx=set(text_idx)
    # body/shadow colours
    tc=collections.Counter({v:c for v,c in vals.items() if v in text_idx})
    order=[v for v,_ in tc.most_common()]
    if body is None: body=order[0] if order else 15
    if shadow is None: shadow=order[1] if len(order)>1 else None
    # erase: iterative neighbour fill
    todo=[(x,y) for y in range(y0,y1+1) for x in range(x0,x1+1) if sc.get(x,y) in text_idx]
    for it in range(20):
        nxt=[]
        for x,y in todo:
            nb=[sc.get(x+dx,y+dy2) for dx,dy2 in ((1,0),(-1,0),(0,1),(0,-1),(2,0),(-2,0),(0,2),(0,-2))]
            nb=[v for v in nb if v is not None and v not in text_idx]
            if nb: sc.put(x,y,collections.Counter(nb).most_common(1)[0][0] if bg_idx is None else bg_idx)
            else: nxt.append((x,y))
        todo=nxt
        if not todo: break
    # draw text
    W=x1-x0+1; H=y1-y0+1
    if font=='dlg':
        import rufont
        t=text; w=len(t)*8; ox=x0+(W-w)//2 if align=='center' else x0; oy=y0+(H-16)//2+dy
        for i,ch in enumerate(t):
            if ch==' ': continue
            hp=rufont.half4(ch,i%2)
            for y in range(16):
                for x in range(8):
                    v=hp[y][x]
                    if v in (9,10,1): sc.put(ox+i*8+x,oy+y,body)
                    elif v==2 and shadow is not None: sc.put(ox+i*8+x,oy+y,shadow)
        return dict(text_idx=sorted(text_idx),body=body,shadow=shadow,width=w,avail=W)
    if font=='pix2' or (font=='pix' and '\n' in text):
        lines=text.split('\n')
        for pitch in (7,6,5):
            bms=[pixfont.render_line(l,pitch) for l in lines]
            if max(len(b[0]) for b in bms)<=W: break
        tot=8*len(lines)-1; oy=y0+(H-tot)//2+dy
        for b in bms:
            w=len(b[0]); ox=x0+(W-w)//2 if align=='center' else x0
            for y in range(7):
                for x in range(w):
                    if b[y][x] and shadow is not None and not (y+1<7 and x+1<w and b[y+1][x+1]): sc.put(ox+x+1,oy+y+1,shadow)
            for y in range(7):
                for x in range(w):
                    if b[y][x]: sc.put(ox+x,oy+y,body)
            oy+=8
        return dict(width=max(len(b[0]) for b in bms),avail=W,pitch=pitch)
    if font=='tiny':
        lines=[pixfont.tiny_line(l) for l in text.split('\n')]
        tot=sum(min(len(l),5) for l in lines)+(len(lines)-1)
        oy=y0+(H-tot)//2+dy
        for l in lines:
            w=len(l[0]); ox=x0+(W-w)//2 if align=='center' else x0
            for y in range(len(l)):
                for x in range(w):
                    if l[y][x]:
                        if shadow is not None and not (y+1<len(l) and x+1<w and l[y+1][x+1]): sc.put(ox+x+1,oy+y+1,shadow)
            for y in range(len(l)):
                for x in range(w):
                    if l[y][x]: sc.put(ox+x,oy+y,body)
            oy+=len(l)+1
        return dict(text_idx=sorted(text_idx),body=body,shadow=shadow,width=max(len(l[0]) for l in lines),avail=W)
    t=text
    for pitch in [p for p in (8,7,6,5) if p<=pitch]:
        bm=pixfont.render_line(t,pitch)
        if len(bm[0])<=W: break
    w=len(bm[0]); h=font_h
    ox=x0+(W-w)//2 if align=='center' else x0
    oy=y0+(H-h)//2+dy
    for y in range(h):
        for x in range(w):
            if bm[y][x]:
                if shadow is not None:
                    if not (y+1<h and x+1<w and bm[y+1][x+1]): sc.put(ox+x+1,oy+y+1,shadow)
    for y in range(h):
        for x in range(w):
            if bm[y][x]: sc.put(ox+x,oy+y,body)
    return dict(text_idx=sorted(text_idx),body=body,shadow=shadow,width=w,avail=W)
# ---- map edited sprite-RAM tiles back to files
def build_index(files):
    idx=collections.defaultdict(list)
    for f in files:
        d=open(f,'rb').read()
        for t in range(len(d)//128):
            idx[d[t*128:(t+1)*128]].append((f,t))
    return idx
def preview(sc,fn,scale=3):
    from PIL import Image
    im=Image.new('L',(304,224),0)
    cache={}
    for (x,y),(t,tx,ty,pal,val) in sc.src.items():
        if 0<=x<304 and 0<=y<224:
            if t not in sc.edited and t not in cache: cache[t]=tile(sc.s,t)
            v=sc.edited[t][ty][tx] if t in sc.edited else cache[t][ty][tx]
            im.putpixel((x,y),v*16)
    im.resize((304*scale,224*scale)).save(fn)
