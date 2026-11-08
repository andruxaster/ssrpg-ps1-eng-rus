"""Russian boot text crawl: rebuild sprite bank C_ALL pkg 0x82800 entry 4 (one group per line)."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,struct,glob,os
import numpy as np
from PIL import Image,ImageDraw,ImageFont
S=_W+''
sys.path.insert(0,S+'/ps1ui'); import fpsi
PKG=0x82800; ENT=4
LINES={0:'1788 год.',
 1:'Мирная эпоха Токугава.',
 2:'Истинный Бусидо',
 3:'был почти забыт.',
 4:'Но в тени истории',
 5:'ожили чудовища...',
 6:'Против демонов',
 7:'встали храбрецы.',
 8:'Сильные духом,',
 9:'они вступили',
 10:'на путь битв...',
 11:'Люди звали их',
 12:'«самураями»...',
 13:'Их верность пути,',
 14:'их образ жизни',
 15:'зовут «Духом самурая»!',
 17:'Производство',
 18:['SNK','Fuji Television','ASATSU']}
FD=glob.glob(S+'/fonts2/fontsource-zen-antique-*/package/files/')[0]
SZ=int(os.environ.get('CRAWLSZ','14'))
FC=ImageFont.truetype(FD+'zen-antique-cyrillic-400-normal.woff',SZ*4)
FL=ImageFont.truetype(FD+'zen-antique-latin-400-normal.woff',SZ*4)
from fontTools.ttLib import TTFont
CMC=set(TTFont(FD+'zen-antique-cyrillic-400-normal.woff').getBestCmap())
def render(t):
    W=len(t)*SZ*4+64; im=Image.new('L',(W,16*4),0); d=ImageDraw.Draw(im); x=8
    l,top,r,bot=FC.getbbox('ЙДдруБ')
    yo=-top+(64-(bot-top))//2
    for ch in t:
        f=FC if ord(ch) in CMC else FL
        d.text((x,yo),ch,font=f,fill=255); x+=f.getlength(ch)
    a=np.asarray(im.resize((W//4,16),Image.LANCZOS)).astype(float)/255
    q=np.clip(np.round(a*6.4),0,6).astype(int)
    xs=np.nonzero(q.any(0))[0]
    return q[:,xs.min():xs.max()+1]
def build():
    c=bytearray(open(S+'/ps1/fs/FLD/C_ALL.BIN','rb').read())
    t,a,s=struct.unpack_from('<3I',c,PKG+4+12*ENT)
    d=bytes(c[PKG+a:PKG+a+s]); b=fpsi.Bank(d)
    dataoff,A,NG,NT=struct.unpack_from('<IHHI',d,0)
    assert NG==len(b.groups)
    tiles=[]; tidx={}
    def tile_id(p):
        key=p.tobytes()
        if key not in tidx: tidx[key]=len(tiles); tiles.append(p)
        return tidx[key]
    groups=[]
    for gi,(go,e) in enumerate(b.groups):
        if gi not in LINES:   # keep original glyphs (e.g. the English title)
            ne=[(x,y,tile_id(np.array(b.tile(tt))),f) for x,y,tt,f in e]; groups.append(ne); continue
        xs=[q[0] for q in e]; ys=[q[1] for q in e]
        cx=(min(xs)+max(xs)+16)/2
        lines=LINES[gi] if isinstance(LINES[gi],list) else [LINES[gi]]
        ytop=min(ys); ybot=max(ys)+16
        nl=len(lines); pitch=(ybot-ytop)//nl if nl>1 else 16
        ne=[]
        for li,txt in enumerate(lines):
            q=render(txt); h,w=q.shape
            x0=int(round(cx-w/2)); y0=ytop+li*pitch if nl>1 else -16
            ncol=(w+15)//16
            pad=np.zeros((16,ncol*16),int); pad[:,:w]=q
            for k in range(ncol):
                p=pad[:,k*16:(k+1)*16]
                if not p.any(): continue
                ne.append((x0+16*k,y0,tile_id(p),0))
        groups.append(ne)
    nt=len(tiles); assert nt<=NT,('too many tiles',nt,NT)
    # serialize
    hdr=16+4*NG; body=bytearray(); offs=[]
    for ne in groups:
        offs.append(hdr+len(body))
        body+=struct.pack('<II',len(ne),0)
        for x,y,tt,f in ne: body+=struct.pack('<4H',x&0xffff,y&0xffff,tt,f)
    newoff=hdr+len(body)
    out=bytearray(struct.pack('<IHHII',newoff,A,NG,nt,0))+b''.join(struct.pack('<I',o) for o in offs)+body
    for p in tiles:
        tb=bytearray(128)
        for y in range(16):
            for x in range(0,16,2): tb[y*8+x//2]=(p[y][x]&15)|((p[y][x+1]&15)<<4)
        out+=tb
    assert len(out)<=s,(len(out),s)
    out+=b'\0'*(s-len(out))
    return bytes(out),nt
def preview(bank,path):
    b=fpsi.Bank(bank); rows=[]
    for gi in range(len(b.groups)):
        im=b.render(gi,[(0,0,0)]+[(v*42,v*42,v*42) for v in range(1,16)])
        if im: rows.append(im)
    W=330; H=sum(r.height+4 for r in rows); o=Image.new('RGB',(W,H),(0,0,0)); y=0
    for r in rows: o.paste(r,((W-r.width)//2,y)); y+=r.height+4
    o.resize((W*2,H*2),Image.NEAREST).save(path)
if __name__=='__main__':
    bank,nt=build(); print('tiles',nt)
    preview(bank,S+'/ps1ui/gfx/crawl_preview.png')
