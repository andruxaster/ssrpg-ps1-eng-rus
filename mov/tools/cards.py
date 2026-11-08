import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,glob,os
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
S=_W+''
FR=S+'/mov/w/fr/MOV/OPEN_00.STR[0][%04d].png'
def frame(i): return np.asarray(Image.open(FR%i).convert('RGB')).astype(np.float32)
FONTS={'mister':S+'/fonts/mister/MisterBrush.ttf',
 'comforter':glob.glob(S+'/fonts/fontsource-comforter-brush-*/package/files/comforter-brush-cyrillic-400-normal.woff')[0],
 'shantell':glob.glob(S+'/fonts/fontsource-shantell-sans-*/package/files/shantell-sans-cyrillic-800-normal.woff')[0],
 'wetpaint':glob.glob(S+'/fonts2/fontsource-rubik-wet-paint-*/package/files/rubik-wet-paint-cyrillic-400-normal.woff')[0]}
# card: (full_frame, frames, bg 'W'/'B', lines, ink color or None to sample)
CARDS=[
 dict(name='kire',  ref=700,frames=range(694,721),bg='W',lines=['Руби']),
 dict(name='samo',  ref=740,frames=range(728,749),bg='B',lines=['Иначе']),
 dict(name='shi',   ref=770,frames=range(749,782),bg='B',lines=['Смерть']),
 dict(name='takab', ref=820,frames=range(803,834),bg='B',lines=['Усмири','тело и дух']),
 dict(name='kakugo',ref=890,frames=range(871,904),bg='B',lines=['Храни','решимость','в сердце']),
 dict(name='michi', ref=940,frames=range(922,957),bg='B',lines=['Следуй','своему Пути']),
]
def inkmask(a,bg):
    return (255-a.min(2))/255 if bg=='W' else a.max(2)/255
def inkcolor(a,bg):
    mm=inkmask(a,bg); m=mm>=np.percentile(mm[mm>0.3],60)
    return np.median(a[m],0)
def render(lines,font,box,scale=1.0):
    """render white-on-black mask fitting box (x0,y0,x1,y1)"""
    x0,y0,x1,y1=box; W=x1-x0; H=y1-y0
    big=4
    def draw(sz):
        f=ImageFont.truetype(font,sz*big)
        ims=[]
        for t in lines:
            l,tp,r,b=f.getbbox(t)
            im=Image.new('L',(r-l+8*big,b-tp+8*big),0)
            ImageDraw.Draw(im).text((4*big-l,4*big-tp),t,font=f,fill=255)
            ims.append(im.crop(im.getbbox()))
        gap=int(sz*0.18*big)
        w=max(i.width for i in ims); h=sum(i.height for i in ims)+gap*(len(ims)-1)
        return ims,w,h,gap
    sz=200
    while True:
        ims,w,h,gap=draw(sz)
        if w<=W*big*scale and h<=H*big*scale: break
        sz-=2
    canvas=Image.new('L',(320*big,240*big),0)
    cx=(x0+x1)/2*big; y=(y0+y1)/2*big-h/2
    for k,i in enumerate(ims):
        # slight stagger like calligraphy columns
        off=(k-(len(ims)-1)/2)*0.0
        canvas.paste(i,(int(cx-i.width/2+off),int(y)))
        y+=i.height+gap
    return np.asarray(canvas.resize((320,240),Image.LANCZOS)).astype(np.float32)/255
def bbox(m,thr=0.3):
    ys,xs=np.nonzero(m>thr); return xs.min(),ys.min(),xs.max()+1,ys.max()+1
def make_card(c,font):
    a=frame(c['ref']); m=inkmask(a,c['bg']); bx=bbox(m)
    cy=(bx[1]+bx[3])/2; hh=max(bx[3]-bx[1],150)/2+6
    box=(22,max(14,cy-hh),298,min(226,cy+hh))
    nm=render(c['lines'],font,box)
    ink=inkcolor(a,c['bg'])
    bgc=np.array([248,248,248],np.float32) if c['bg']=='W' else np.zeros(3,np.float32)
    bgc=np.median(a[m<0.06],0)
    img=bgc*(1-nm[...,None])+ink*nm[...,None]
    return img,nm,ink,bgc
if __name__=='__main__':
    fonts=sys.argv[1].split(',')
    rows=[]
    for fn in fonts:
        row=[]
        for c in CARDS:
            img,_,_,_=make_card(c,FONTS[fn]); row.append(Image.fromarray(img.clip(0,255).astype(np.uint8)))
        rows.append(row)
    orig=[Image.fromarray(frame(c['ref']).astype(np.uint8)) for c in CARDS]
    rows.insert(0,orig)
    out=Image.new('RGB',(320*len(CARDS)//2*1,240*len(rows)))
    out=Image.new('RGB',(320*3,240*2*len(rows)))
    for r,row in enumerate(rows):
        for k,im in enumerate(row): out.paste(im,((k%3)*320,(r*2+k//3)*240))
    out.save(sys.argv[2])
