import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,collections,random,glob
S=_W+''
sys.path.insert(0,S+'/tools')
from brush import layout,SCREENS
from spr import tile
from rufont import encode_tile
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from fontTools.ttLib import TTFont
import os
FONTS={'shantell':('fonts/fontsource-shantell-sans-*','shantell-sans-%s-800-normal.woff'),
 'caveat':('fonts/fontsource-caveat-*','caveat-%s-700-normal.woff'),
 'comforter':('fonts/fontsource-comforter-brush-*','comforter-brush-%s-400-normal.woff'),
 'ruslan':('fonts2/fontsource-ruslan-display-*','ruslan-display-%s-400-normal.woff'),
 'neucha':('fonts/fontsource-neucha-*','neucha-%s-400-normal.woff'),
 'marck':('fonts/fontsource-marck-script-*','marck-script-%s-400-normal.woff'),
 'lobster':('fonts/fontsource-lobster-*','lobster-%s-400-normal.woff')}
BF=os.environ.get('BRUSHFONT','shantell')
if BF=='mister':
    FD=S+'/fonts/mister/'; FN='MisterBrush.ttf'
else:
    FD=glob.glob(S+'/'+FONTS[BF][0]+'/package/files/')[0]; FN=FONTS[BF][1]
def font(sz):
    return (ImageFont.truetype(FD+(FN%'cyrillic' if '%' in FN else FN),sz),ImageFont.truetype(FD+(FN%'latin' if '%' in FN else FN),sz))
CMAP=set(TTFont(FD+(FN%'cyrillic' if '%' in FN else FN)).getBestCmap())
def render_line(txt,sz):
    cy,la=font(sz)
    W=int(sz*len(txt)*1.0)+40; H=int(sz*1.6)
    im=Image.new('L',(W,H),0); d=ImageDraw.Draw(im); x=10
    for ch in txt:
        f=cy if ord(ch) in CMAP else la
        d.text((x,int(sz*0.2)),ch,font=f,fill=255); x+=d.textlength(ch,font=f)*0.97
    bb=im.getbbox(); return im.crop(bb)
TEXT={'kill':[[('УБЕ',0,128),('Й',144,192)]],'or':['ИЛИ…'.replace('…','...')],'bekilled':[None,'УМРИ!'],
      'calm':['Успокой','тело','и разум...'],'follow':['Следуй','по','пути...'],
      'destiny':['ибо','СУДЬБА','ЖДЕТ!']}
def process(name,chip,out,preview):
    cells=layout(name,chip)
    xs=[k[0] for k in cells]; ys=[k[1] for k in cells]
    x0,y0=min(xs),min(ys); W=max(xs)-x0+16; H=max(ys)-y0+16
    en=[[None]*W for _ in range(H)]
    for (x,y),(t,pal) in cells.items():
        p=tile(chip,t)
        for yy in range(16):
            for xx in range(16): en[y-y0+yy][x-x0+xx]=p[yy][xx]
    hist=collections.Counter(v for r in en for v in r if v is not None)
    bg=hist.most_common(1)[0][0]
    # ink = most common non-bg; intermediates ranked by ink-neighbour ratio
    others=[c for c,_ in hist.most_common() if c!=bg]
    ink=others[0]
    def inkratio(c):
        n=k=0
        for y in range(1,H-1):
            for x in range(1,W-1):
                if en[y][x]==c:
                    for dy,dx in ((0,1),(1,0),(0,-1),(-1,0)):
                        n+=1; k+= en[y+dy][x+dx]==ink
        return k/max(n,1)
    mids=sorted(others[1:],key=inkratio,reverse=True)
    # line bands from EN ink rows
    rows=[y for y in range(H) if any(en[y][x] not in (None,bg) for x in range(W))]
    bands=[]
    for y in rows:
        if bands and y-bands[-1][1]<=6: bands[-1][1]=y
        else: bands.append([y,y])
    bands=[b for b in bands if b[1]-b[0]>=8]
    lines=TEXT[name]
    assert len(bands)==len(lines),(name,bands,lines)
    alpha=Image.new('L',(W,H),0)
    jobs=[]
    for (ya,yb),txt in zip(bands,lines):
        if txt is None: continue
        if isinstance(txt,list):
            for t,a_,b_ in txt: jobs.append((ya,yb,t,a_,b_-1))
        else:
            xsb=[x for y in range(ya,yb+1) for x in range(W) if en[y][x] not in (None,bg)]
            jobs.append((ya,yb,txt,min(xsb),max(xsb)))
    for ya,yb,txt,xa,xb in jobs:
        bh=yb-ya+1; bw=xb-xa+1
        avail=[[en[y][x] is not None for x in range(W)] for y in range(H)]
        best=None; TOL=0.015
        for sz in range(min(int(bh*1.6),70 if name=='kill' else 999),10,-1):
            im0=render_line(txt,sz)
            if im0.height>bh+12 or im0.width>bw+16: continue
            px0=im0.load()
            pts=[(xx,yy) for yy in range(im0.height) for xx in range(im0.width) if px0[xx,yy]>128]
            tot=len(pts)
            cx=xa+(bw-im0.width)//2; cy=ya+(bh-im0.height)//2
            cand=None
            for dy in range(-8,9,2):
                for dx in range(-20,21,2):
                    ox,oy=cx+dx,cy+dy
                    if ox<max(3,xa-4) or oy<2 or ox+im0.width>min(W-3,xb+4) or oy+im0.height>H-2: continue
                    bad=sum(1 for xx,yy in pts if not avail[oy+yy][ox+xx])
                    sc=bad/tot+abs(dx)*0.0002+abs(dy)*0.0002
                    if cand is None or sc<cand[0]: cand=(sc,sz,ox,oy,im0)
            if cand and cand[0]<=TOL: best=cand; break
            if cand and (best is None or cand[0]<best[0]): best=cand
        sc,sz,ox,oy,img=best
        print(name,txt,'size',sz,'clipped %.3f'%sc)
        # roughen: ragged dry-brush edges
        random.seed(hash(txt)&0xffff)
        bl=img.filter(ImageFilter.GaussianBlur(1.0))
        nz=Image.new('L',img.size); nzp=nz.load()
        for y in range(img.height):
            for x in range(img.width): nzp[x,y]=random.randint(0,255)
        nz=nz.filter(ImageFilter.GaussianBlur(0.7))
        bp=bl.load(); nzp=nz.load(); px=img.load()
        for y in range(img.height):
            for x in range(img.width):
                v=bp[x,y]+(nzp[x,y]-128)*1.6
                px[x,y]=255 if v>150 else (140 if v>135 else 0)
        alpha.paste(img,(ox,oy),img)
    A=alpha.load()
    newpix={}
    for (x,y),(t,pal) in cells.items():
        p=[[0]*16 for _ in range(16)]
        for yy in range(16):
            for xx in range(16):
                a=A[x-x0+xx,y-y0+yy]
                if a>170: v=ink
                elif a>100 and mids: v=mids[0]
                elif a>45 and len(mids)>1: v=mids[1]
                else: v=bg
                p[yy][xx]=v
        newpix[t]=p
        out[t*128:(t+1)*128]=encode_tile(p)
    # preview
    pv=Image.new('L',(W,H),60)
    for (x,y),(t,pal) in cells.items():
        p=newpix[t]
        for yy in range(16):
            for xx in range(16):
                v=p[yy][xx]; pv.putpixel((x-x0+xx,y-y0+yy),255 if v==ink else (170 if v in mids[:1] else (110 if v in mids[1:2] else 0)))
    preview.append(pv)
    return bg,ink,mids
if __name__=='__main__':
    chip=open(S+'/ngcd/en/CHIP00B2.SPR','rb').read(); out=bytearray(chip); pvs=[]
    for n in TEXT: print(n,process(n,chip,out,pvs))
    W=sum(p.width for p in pvs)+10*len(pvs); H=max(p.height for p in pvs)
    o=Image.new('L',(W,H),128); x=0
    for p in pvs: o.paste(p,(x,0)); x+=p.width+10
    o.resize((W*2,H*2)).save(S+'/ru/intro/br_ru_%s.png'%BF)
    open(S+'/ru/intro/CHIP00B2_brush_%s.SPR'%BF,'wb').write(out)
