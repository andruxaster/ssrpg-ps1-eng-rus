"""Russian loading screens (LOGO*.PRG)."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,glob,os,collections
S=_W+''
sys.path.insert(0,S+'/tools')
import logo,pixfont,rufont
from PIL import Image,ImageFont,ImageDraw
FD=S+'/fonts/'
from fontTools.ttLib import TTFont
class FF:
    def __init__(self,pack,fn,sz):
        b=glob.glob(FD+pack+'*/package/files/')[0]
        self.fs=[]
        for sub in ('cyrillic','latin'):
            f=b+fn.replace('cyrillic',sub)
            self.fs.append((ImageFont.truetype(f,sz),set(TTFont(f).getBestCmap())))
        self.size=sz
    HG=dict(zip('АВЕКМНОРСТХаеорсухКк','ABEKMHOPCTXaeopcyxKk'))
    def pick(self,ch):
        for f,cm in self.fs:
            if ord(ch) in cm: return f,ch
        h=self.HG.get(ch)
        if h:
            for f,cm in self.fs:
                if ord(h) in cm: return f,h
        return self.fs[-1][0],ch
def F(pack,fn,sz): return FF(pack,fn,sz)
def bitmap(text,font,thr=128):
    im=Image.new('L',(len(text)*font.size*2+20,font.size*3),0); d=ImageDraw.Draw(im)
    x=10
    for ch in text:
        f,c2=font.pick(ch); d.text((x,font.size//2),c2,font=f,fill=255); x+=d.textlength(c2,font=f)
    bb=im.getbbox(); im=im.crop(bb)
    return [[1 if im.getpixel((x,y))>=thr else 0 for x in range(im.width)] for y in range(im.height)]
def captop(font,ref='Н'):
    im=Image.new('L',(200,font.size*3),0); d=ImageDraw.Draw(im); d.text((10,font.size//2),ref,font=font,fill=255)
    return im.getbbox()
def erase(c,box,idx,fill=None):
    x0,y0,x1,y1=box
    todo=[(x,y) for y in range(y0,y1+1) for x in range(x0,x1+1) if c.px[y][x] in idx]
    if fill is not None:
        for x,y in todo: c.px[y][x]=fill
        return
    for it in range(40):
        nxt=[]
        for x,y in todo:
            nb=[c.px[y+dy][x+dx] for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(2,0),(-2,0),(0,2),(0,-2),(3,0),(-3,0)) if 0<=x+dx<320 and 0<=y+dy<256]
            nb=[v for v in nb if v not in idx]
            if nb: c.px[y][x]=collections.Counter(nb).most_common(1)[0][0]
            else: nxt.append((x,y))
        todo=nxt
        if not todo: break
def draw(c,bm,ox,oy,body,outline=None,shadow=None,sdx=1,sdy=1,pal=None):
    on=set((ox+x,oy+y) for y in range(len(bm)) for x in range(len(bm[0])) if bm[y][x])
    if shadow is not None:
        for x,y in on:
            p=(x+sdx,y+sdy)
            if p not in on: c.px[p[1]][p[0]]=shadow
    if outline is not None:
        ring=set((x+dx,y+dy) for x,y in on for dx in (-1,0,1) for dy in (-1,0,1))-on
        for x,y in ring: c.px[y][x]=outline
    for x,y in on: c.px[y][x]=body if not callable(body) else body(x,y)
    if pal is not None:
        cells=set((x//8,y//8) for x,y in on)
        for cc in cells: c.cp[cc]=pal
def pix_lines(lines,pitch=8):
    return [pixfont.render_line(l,pitch) for l in lines]
def dlg_line(t):
    rows=[[0]*(8*len(t)) for _ in range(16)]
    for i,ch in enumerate(t):
        if ch==' ': continue
        hp=rufont.half4(ch,i%2)
        for y in range(16):
            for x in range(8):
                v=hp[y][x]
                if v in (9,10,1): rows[y][i*8+x]=1
                elif v==2: rows[y][i*8+x]=2
    return rows
def load(n): return logo.Canvas(open(S+'/ngcd/en/%s.PRG'%n,'rb').read())
OUT=S+'/ru/build'
res={}
# 1. translation disclaimer (LOGO_E/J/U)
for n in ['LOGO_E','LOGO_J','LOGO_U']:
    c=load(n)
    erase(c,(40,184,280,231),{6,12},fill=15)
    lines=['ЭТОТ ПЕРЕВОД РАСПРОСТРАНЯЕТСЯ','БЕСПЛАТНО. НЕ ДЛЯ ПРОДАЖИ','И ПРОКАТА. НЕ ИЗГОТАВЛИВАЙТЕ','И НЕ ПРОДАВАЙТЕ КОПИИ','ПЕРЕВЕДЕННОЙ ИГРЫ.']
    for k,l in enumerate(lines):
        bm=pixfont.render_line(l,8 if len(l)*8<=300 else 7); bm=bm[:7]
        w=len(bm[0]); draw(c,bm,(160-w//2)//8*8,184+k*8,6,shadow=12)
    res[n]=c
# 2. fiction note (LOGO000F)
c=load('LOGO000F')
erase(c,(40,184,319,239),{6,8,9,14},fill=15)
for k,l in enumerate(['Эта история вымышлена. Любое сходство','с реальными людьми и историческими','событиями случайно.']):
    bm=dlg_line(l); w=len(bm[0]); ox=(160-w//2)//8*8; oy=184+k*16
    for y in range(16):
        for x in range(w):
            v=bm[y][x]
            if v==1: c.px[oy+y][ox+x]=6
            elif v==2: c.px[oy+y][ox+x]=12
res['LOGO000F']=c
# 3. orange NOW LOADING
fz=F('fontsource-press-start-2p','press-start-2p-cyrillic-400-normal.woff',16)
for k,(x0,y0,x1,y1) in {'B':(136,193,259,207),'C':(24,33,147,47),'G':(24,153,147,167),'H':(24,33,147,47),'K':(144,89,267,103),'N':(24,209,147,223),'U':(144,193,267,207)}.items():
    n='LOGO000'+k; c=load(n)
    cell=c.cp[(x0//8,y0//8)]; pal=c.pals[cell]
    ti=pal.index(0x6f20)
    ol=collections.Counter(c.px[y][x] for y in range(y0-1,y1+2) for x in range(x0-1,x1+2) if c.px[y][x] and c.px[y][x]!=ti and pal[c.px[y][x]]==0).most_common(1)
    ol=ol[0][0] if ol else None
    erase(c,(x0-2,y0-2,x1+2,y1+2),{ti} | ({ol} if ol else set()),fill=0)
    bm=bitmap('ЗАГРУЗКА...',fz)
    w=len(bm[0]); h=len(bm)
    draw(c,bm,max(8,min(312-w,(x0+x1)//2-w//2)),y1-h+1,ti,outline=ol,pal=cell)
    res[n]=c
# 4. small NOW LOADING (LOGO0000)
c=load('LOGO0000')
for C in range(22,38):
    for y in range(8):
        for x in range(8): c.px[28*8+y][C*8+x]=c.px[28*8+y][(C-16)*8+x]
    c.cp[(C,28)]=c.cp[(C-16,28)]
bm=pixfont.render_line('ЗАГРУЗКА',8)[:7]; w=len(bm[0])
draw(c,bm,240-w//2,224,15,shadow=1)
res['LOGO0000']=c
# 5. big brush NOW LOADING... (LOGO0001)
c=load('LOGO0001')
erase(c,(100,190,319,226),{15,11})
for sz in range(34,10,-1):
    fb=F('fontsource-rubik-dirt','rubik-dirt-cyrillic-400-normal.woff',sz)
    bm=bitmap('ЗАГРУЗКА...',fb,100); w=len(bm[0]); h=len(bm)
    if w<=196: break
print('brush size',sz,w,h)
draw(c,bm,205-w//2,222-h,15,shadow=11,sdx=2,sdy=1)
res['LOGO0001']=c
# 6. OMAKE screens
fo=F('fontsource-press-start-2p','press-start-2p-cyrillic-400-normal.woff',24)
ft=F('fontsource-press-start-2p','press-start-2p-cyrillic-400-normal.woff',16)
for n in ['LOGO0002','LOGO000O']:
    c=load(n)
    # find bboxes by colour
    def bbox(cols):
        xs=[];ys=[]
        for (C,R),p in c.cp.items():
            pal=c.pals.get(p,[0]*16)
            for y in range(8):
                for x in range(8):
                    v=c.px[R*8+y][C*8+x]
                    if v and pal[v] in cols and R*8+y>40: xs.append(C*8+x); ys.append(R*8+y)
        return min(xs),min(ys),max(xs),max(ys)
    bo=(58,62,162,92); bt=(80,189,251,213)
    p=c.pals[c.cp[(bo[0]//8,bo[1]//8)]]
    iy,ib,io,iw=p.index(0x4fe0),p.index(0x100f),p.index(0x4f80),p.index(0x7fff)
    erase(c,(bo[0]-1,bo[1]-1,bo[2]+1,bo[3]+1),{iy,ib},fill=iw)
    bm=bitmap('БОНУС',fo); w=len(bm[0]); h=len(bm)
    draw(c,bm,(bo[0]+bo[2])//2-w//2,(bo[1]+bo[3])//2-h//2,iy,outline=ib,shadow=ib,sdx=2,sdy=2)
    erase(c,(bt[0]-1,bt[1]-1,bt[2]+1,bt[3]+1),{io},fill=iw)
    bm=bitmap('спасибо за игру!',ft); w=len(bm[0]); h=len(bm)
    draw(c,bm,160-w//2,bt[3]-h+1,io)
    res[n]=c
sheet=Image.new('RGB',(640,256*((len(res)+1)//2))); dr=ImageDraw.Draw(sheet)
for k,(n,c) in enumerate(sorted(res.items())):
    print(n); b,used,cap=c.build()
    open(OUT+'/%s.PRG'%n,'wb').write(b)
    sheet.paste(c.image(),((k%2)*320,(k//2)*256)); dr.text(((k%2)*320+2,(k//2)*256+2),'%s %d/%d'%(n,used,cap),fill=(0,255,0))
sheet.save(S+'/ru/gfx/logos_ru.png'); print('ok',len(res))
