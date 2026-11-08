"""Render NG sprites from VRAM+sprite RAM dumps, keeping source map."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import struct,sys
sys.path.insert(0,_W+'/tools')
from spr import tile
def sprite_list(vram):
    W=lambda i: struct.unpack('<H',vram[2*i:2*i+2])[0]
    out=[]; h=0; x=y=0
    for s in range(1,381):
        scb3=W(0x8200+s); scb4=W(0x8400+s)
        if scb3&0x40: x=(x+16)&0x1ff
        else: h=scb3&0x3f; y=(496-(scb3>>7))&0x1ff; x=(scb4>>7)&0x1ff
        if h==0: continue
        cells=[]
        for r in range(min(h,32)):
            lo=W(s*64+r*2); at=W(s*64+r*2+1)
            cells.append((lo|(((at>>4)&0xf)<<16), at>>8, at&3))
        out.append((s,x,y,cells))
    return out
def render(vram,sprram,y0=16,x0=8):
    """returns dict (sx,sy)->(tile,tx,ty,pal,val) of topmost pixel"""
    src={}
    for s,x,y,cells in sprite_list(vram):
        for r,(t,pal,fl) in enumerate(cells):
            if t==0: continue
            p=tile(sprram,t)
            for ty in range(16):
                for tx in range(16):
                    px=tx if not fl&1 else 15-tx; py=ty if not fl&2 else 15-ty
                    v=p[py][px]
                    if not v: continue
                    sx=((x+tx)&0x1ff)-x0; sy=((y+16*r+ty)&0x1ff)-y0
                    if 0<=sx<304 and 0<=sy<224: src[(sx,sy)]=(t,px,py,pal,v)
    return src

def render_top(vram,sprram,y0=16,x0=8):
    """(sx,sy)->(tile,px,py,pal,val) of topmost sprite cell, including transparent pixels"""
    src={}
    for s,x,y,cells in sprite_list(vram):
        for r,(t,pal,fl) in enumerate(cells):
            if t==0: continue
            p=tile(sprram,t)
            for ty in range(16):
                for tx in range(16):
                    px=tx if not fl&1 else 15-tx; py=ty if not fl&2 else 15-ty
                    sx=((x+tx)&0x1ff)-x0; sy=((y+16*r+ty)&0x1ff)-y0
                    if 0<=sx<304 and 0<=sy<224: src[(sx,sy)]=(t,px,py,pal,p[py][px])
    return src
