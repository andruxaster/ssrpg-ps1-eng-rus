"""Russian graphics for the new-game screens (C_ALL.BIN package 0xa2000, sprite bank entry 17)."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,struct,os
import numpy as np
from PIL import Image,ImageDraw,ImageFont
S=_W+''
sys.path.insert(0,S+'/ps1ui'); sys.path.insert(0,S+'/tools')
import fpsi,rufont
from scipy.ndimage import binary_dilation
PKG=0xa2000; ENT=17
HEADER='Выберите героя'
CHAPTERS=['Сошествие зла','Плач цветка']
MODES=['Файтинг-ввод','Выбор в меню']
NAMES=['Хаомару','Накоруру','Галфорд','Укио','Гэндзюро','Чам-Чам']
import glob
BRUSH=glob.glob(S+'/fonts/fontsource-shantell-sans-*/package/files/shantell-sans-cyrillic-800-normal.woff')[0]
def load():
    c=bytearray(open(S+'/ps1/fs/FLD/C_ALL.BIN','rb').read())
    n=struct.unpack_from('<I',c,PKG)[0]
    t,a,s=struct.unpack_from('<3I',c,PKG+4+12*ENT)
    return c,PKG+a,s
def grid(b,e):
    x0=min(q[0] for q in e); y0=min(q[1] for q in e)
    W=max(q[0] for q in e)-x0+16; H=max(q[1] for q in e)-y0+16
    g=np.zeros((H,W),int)
    for x,y,tt,f in e: g[y-y0:y-y0+16,x-x0:x-x0+16]=b.tile(tt)
    return g,x0,y0
def put(b,e,g,x0,y0):
    done={}
    for x,y,tt,f in e:
        p=g[y-y0:y-y0+16,x-x0:x-x0+16]
        if tt in done: assert (done[tt]==p).all(),('tile conflict',tt)
        done[tt]=p.copy(); b.settile(tt,p.tolist())
def text_mask(txt,pitch=8):
    W=len(txt)*pitch; m=np.zeros((16,W),bool)
    for i,ch in enumerate(txt):
        if ch==' ': continue
        h=np.array(rufont.half4(ch,i%2))
        m[:,i*pitch:i*pitch+8]|=np.isin(h,(1,9,10))
    xs=np.nonzero(m.any(0))[0]
    return m[:,xs.min():xs.max()+1]
def periodic_bg(g,bgvals,period=16):
    H,W=g.shape; out=g.copy()
    for y in range(H):
        for xm in range(period):
            col=g[y,xm::period]; col=col[np.isin(col,bgvals)]
            if len(col):
                v=np.bincount(col).argmax(); out[y,xm::period]=v
    return out
def draw_text(g,txt,y,ink,outline,pitch=8,xc=None,clip=None):
    m=text_mask(txt,pitch); h,w=m.shape
    W=g.shape[1]; x=(W-w)//2 if xc is None else xc-w//2
    big=np.zeros(g.shape,bool); big[y:y+h,x:x+w]=m
    ol=binary_dilation(big,np.ones((3,3),bool))&~big
    if clip is not None: ol&=clip; big&=clip
    g[ol]=outline; g[big]=ink
    return x,x+w
def brush_name(name,W=64,H=32,SZ=int(os.environ.get('PLATESZ','21'))):
    f=ImageFont.truetype(BRUSH,SZ*4); fl=ImageFont.truetype(BRUSH.replace('cyrillic','latin'),SZ*4)
    im=Image.new('L',(SZ*4*len(name)+40,SZ*8),0); dr=ImageDraw.Draw(im); x=20
    for ch in name:
        ff=f if ch.isalpha() else fl
        dr.text((x,SZ*2),ch,font=ff,fill=255); x+=ff.getlength(ch)
    im=im.crop(im.getbbox())
    w=min(W-6,im.width//4); h=im.height//4
    im=im.resize((w*4,h*4),Image.LANCZOS)
    can=Image.new('L',(W*4,H*4),0); can.paste(im,((W*4-im.width)//2,(H*4-im.height)//2))
    a=np.asarray(can.resize((W,H),Image.LANCZOS))>100
    return a,SZ
def plate(name):
    a,sz=brush_name(name)
    g=np.zeros(a.shape,int)
    ol=binary_dilation(a,np.ones((3,3),bool))
    ol2=binary_dilation(ol,np.ones((3,3),bool))
    g[ol2]=15
    ys=np.nonzero(a.any(1))[0]; y0,y1=ys.min(),ys.max()
    for y in range(a.shape[0]):
        fr=(y-y0)/max(1,y1-y0)
        # white on top, fire gradient towards the bottom (as on the original plates)
        v=1 if fr<0.55 else min(9,2+int((fr-0.55)/0.45*8))
        g[y][a[y]]=v
    return g,sz
MENU={1:'НОВАЯ ИГРА',2:'ЗАГРУЗКА',3:'ОПЦИИ',6:'БОНУС',7:'НАЖМИ START'}
def title_menu(c):
    import pixfont
    t,a,s=struct.unpack_from('<3I',c,PKG+4+12*26)
    b=fpsi.Bank(bytes(c[PKG+a:PKG+a+s]))
    ROW=[1,1,2,3,4,5,6,6]
    for gi,txt in MENU.items():
        e=b.groups[gi][1]; g,x0,y0=grid(b,e)
        rows=np.nonzero(g.any(1))[0]; top=rows.min()
        g[:]=0
        W=len(txt)*8; assert W<=g.shape[1],(txt,W,g.shape)
        xs=(g.shape[1]-W)//2
        for i,ch in enumerate(txt):
            if ch==' ': continue
            gl=pixfont.glyph8(ch)
            on=[(x,y) for y in range(8) for x in range(8) if gl[y][x]]
            S_=set(on)
            for x,y in on:
                for dx,dy in ((1,0),(0,1),(1,1)):
                    X,Y=xs+i*8+x+dx,top+y+dy
                    if (x+dx,y+dy) not in S_ and 0<=X<g.shape[1] and Y<g.shape[0]: g[Y,X]=15
            for x,y in on: g[top+y,xs+i*8+x]=ROW[y]
        put(b,e,g,x0,y0)
    c[PKG+a:PKG+a+s]=b.d
def build():
    c,off,size=load()
    b=fpsi.Bank(bytes(c[off:off+size]))
    G=b.groups
    # ---- header (g10): free tiles 98/99 (column x=96) by keeping cols 14/15 plain
    e=G[10][1]; g,x0,y0=grid(b,e)
    bgv=[11,12,13,14,15]
    clean=periodic_bg(g,[12,13,14,15])
    rows=slice(7,26)
    g[rows,64:272]=clean[rows,64:272]   # wipe JP text
    draw_text(g,HEADER,8,6,11,pitch=10,xc=152)
    # columns 14,15 (x=96..128 in strip coords 256..288) must be identical
    g[:,256:272]=g[:,240:256]
    ne=[]
    for (x,y,tt,f) in e:
        if x==96: tt={98:96,99:97}[tt]
        ne.append((x,y,tt,f))
    put(b,ne,g,x0,y0)
    hdr_entries=ne
    # ---- chapters (g6,g7) and modes (g8,g9)
    allbg=[]
    for gi in (6,7,8,9):
        gg,_,_=grid(b,G[gi][1]); allbg.append(gg)
    def redo(gi,txt,newtiles=None):
        e=G[gi][1]
        if newtiles: e=[(x,y,newtiles.get(i,tt),f) for i,(x,y,tt,f) in enumerate(e)]
        g,x0,y0=grid(b,e)
        cl=periodic_bg(np.hstack(allbg) if False else g,[12,13,14,15])
        g[:]=cl
        draw_text(g,txt,0,6,1)
        put(b,e,g,x0,y0); return e
    e6=redo(6,CHAPTERS[0])
    e7=redo(7,CHAPTERS[1],{5:98,6:99})
    e8=redo(8,MODES[0]); e9=redo(9,MODES[1])
    # ---- name plates g0..g5 (64x32)
    szs=[]
    for gi,nm in enumerate(NAMES):
        e=G[gi][1]; g,sz=plate(nm); szs.append(sz)
        gg,x0,y0=grid(b,e); assert gg.shape==g.shape
        put(b,e,g,x0,y0)
    # ---- title menu (entry 26)
    title_menu(c)
    # write group entry changes (g10, g7)
    d=b.d
    for gi,ne in ((10,hdr_entries),(7,e7)):
        goff=G[gi][0]
        for k,(x,y,tt,f) in enumerate(ne):
            struct.pack_into('<4H',d,goff+8+8*k,x&0xffff,y&0xffff,tt,f)
    assert len(d)==size
    c[off:off+size]=d
    return c,szs
def preview(c,out):
    off=load()[1]; size=load()[2]
    b=fpsi.Bank(bytes(c[off:off+size]))
    pal={0:(255,0,255),1:(64,64,64),2:(96,96,96),3:(136,136,136),4:(168,168,168),5:(200,200,200),6:(248,248,248),
         7:(200,180,220),11:(40,10,60),12:(72,24,88),13:(72,24,96),14:(56,16,88),15:(48,8,80)}
    ppal={0:(40,10,60),1:(240,240,240),2:(248,248,80),3:(240,184,0),4:(240,152,0),5:(248,120,0),6:(240,72,0),7:(236,68,0),8:(248,0,0),9:(216,0,0),15:(0,0,0)}
    ims=[]
    for gi in (10,6,7,8,9,0,1,2,3,4,5):
        g,_,_=grid(b,b.groups[gi][1]); P=ppal if gi<6 else pal
        a=np.array([[P.get(v,(255,0,255)) for v in row] for row in g],np.uint8)
        ims.append(Image.fromarray(a))
    W=max(i.width for i in ims[:1])*2; o=Image.new('RGB',(680,32*2+16*2*4+32*2*2+40),(20,20,30)); y=0
    o.paste(ims[0].resize((640,64),Image.NEAREST),(0,0)); y=70
    for k,im in enumerate(ims[1:5]): o.paste(im.resize((im.width*2,32),Image.NEAREST),((k%2)*260,y+(k//2)*36))
    y+=80
    for k,im in enumerate(ims[5:]): o.paste(im.resize((128,64),Image.NEAREST),(k*134 if k<5 else 0,y if k<5 else y+70))
    o.save(out)
if __name__=='__main__':
    c,szs=build(); print('plate font sizes',szs)
    os.makedirs(S+'/ps1ui/gfx',exist_ok=True)
    open(S+'/ps1ui/gfx/C_ALL.BIN','wb').write(c)
    preview(c,S+'/ps1ui/gfx/call_preview.png')
