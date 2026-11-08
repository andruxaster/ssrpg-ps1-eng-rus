"""Pixel caps font for Cyrillic labels: Press Start 2P based, with condensed variants."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import glob
from PIL import Image,ImageDraw,ImageFont
from fontTools.ttLib import TTFont
FD=_W+'/fonts/'
_b=glob.glob(FD+'fontsource-press-start-2p-*/package/files/')[0]
_fc=ImageFont.truetype(_b+'press-start-2p-cyrillic-400-normal.woff',8)
_fl=ImageFont.truetype(_b+'press-start-2p-latin-400-normal.woff',8)
_cm=set(TTFont(_b+'press-start-2p-cyrillic-400-normal.woff').getBestCmap())
_cache={}
def glyph8(ch):
    """8x8 bitmap list of rows (0/1)"""
    if ch in _cache: return _cache[ch]
    im=Image.new('1',(8,8),0); d=ImageDraw.Draw(im); d.fontmode='1'
    f=_fc if ord(ch) in _cm else _fl
    d.text((0,0),ch,font=f,fill=1)
    px=[[im.getpixel((x,y)) for x in range(8)] for y in range(8)]
    _cache[ch]=px; return px
def glyph(ch,width):
    """glyph condensed to given column count (removing redundant columns)"""
    g=glyph8(ch)
    cols=[[g[y][x] for y in range(8)] for x in range(8)]
    # trim empty trailing columns
    while cols and not any(cols[-1]): cols.pop()
    while cols and not any(cols[0]) and ch!=' ': cols.pop(0)
    if ch==' ': return [[0]*width for _ in range(8)],width
    while len(cols)>width:
        # remove column most similar to a neighbour (prefer interior)
        best=None
        for i in range(1,len(cols)-1):
            sim=sum(a==b for a,b in zip(cols[i],cols[i-1]))+sum(a==b for a,b in zip(cols[i],cols[i+1]))
            if best is None or sim>best[0]: best=(sim,i)
        if best is None: cols.pop(); continue
        cols.pop(best[1])
    w=len(cols)
    return [[cols[x][y] for x in range(w)] for y in range(8)],w
def render_line(txt,pitch):
    """returns rows(8) x width bitmap; pitch=glyph advance (glyph width=pitch-1)"""
    out=[[] for _ in range(8)]
    for ch in txt:
        wd=1 if (ch in 'ЫЖШЩМЮ' and pitch<8) else 0
        g,w=glyph(ch,pitch-1+wd)
        adv=pitch+wd if ch!=' ' else max(3,pitch-2)
        for y in range(8):
            row=g[y]+[0]*(adv-len(g[y]))
            out[y]+=row[:adv]
    return out
_tb=glob.glob(FD+'fontsource-tiny5-*/package/files/')[0]
_tfc=ImageFont.truetype(_tb+'tiny5-cyrillic-400-normal.woff',8)
_tfl=ImageFont.truetype(_tb+'tiny5-latin-400-normal.woff',8)
_tcm=set(TTFont(_tb+'tiny5-cyrillic-400-normal.woff').getBestCmap())
def tiny_line(txt):
    """5px caps line -> rows(8)"""
    W=len(txt)*6+4
    im=Image.new('1',(W,10),0); d=ImageDraw.Draw(im); d.fontmode='1'
    x=0
    for ch in txt:
        f=_tfc if ord(ch) in _tcm else _tfl
        d.text((x,0),ch,font=f,fill=1); x+=d.textlength(ch,font=f)
    bb=im.getbbox()
    if not bb: return [[0] for _ in range(6)]
    r=Image.new('1',(20,10),0); dr=ImageDraw.Draw(r); dr.fontmode='1'; dr.text((0,0),'Н',font=_tfc,fill=1); rb=r.getbbox()
    im=im.crop((0,rb[1],bb[2],max(bb[3],rb[3])))
    return [[im.getpixel((xx,yy)) for xx in range(im.width)] for yy in range(im.height)]
