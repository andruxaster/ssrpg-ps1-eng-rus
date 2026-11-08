import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,os,re
S=_W+''
sys.path.insert(0,S+'/tools')
import bfixocr,bfixmap,bfixtr,pixfont
COL=[1,1,2,2,4,4,5,0]
SHORT={'Плазменный клинок':'Плазм. клинок','Плазменный рывок':'Плазм. рывок','Тайный меч: Марево':'Марево','Благородный разрез':'Благ. разрез'}
def splits(t):
    ws=t.split(' '); res=[]
    for i in range(1,len(ws)): res.append((' '.join(ws[:i]),' '.join(ws[i:])))
    for m in re.finditer('-',t):
        i=m.end(); res.append((t[:i],t[i:].strip()))
    res.append((t,''))
    return res
def layout(t,wpx):
    t=t.upper().replace('Ё','Е')
    for pitch in (8,7,6,5):
        best=None
        for a,b in splits(t):
            la=len(pixfont.render_line(a,pitch)[0]) if a else 0
            lb=len(pixfont.render_line(b,pitch)[0]) if b else 0
            ind=pitch if lb+pitch<=wpx else 0
            m=max(la,lb+ind)
            if m<=wpx and (best is None or m<best[0]): best=(m,a,b,ind)
        if best: return pitch,best
    return None
def encode_fix(px):
    b=bytearray(32)
    for ci,x0 in enumerate((4,6,0,2)):
        for y in range(8): b[ci*8+y]=(px[y][x0]&15)|((px[y][x0+1]&15)<<4)
    return bytes(b)
def build(outdir,preview=None):
    D=bfixtr.dicts(); fails=[]
    allrecs=bfixocr.ocr()
    for bi,recs in allrecs.items():
        f=bytearray(open(S+'/ngcd/en/BFIX%04X.FIX'%bi,'rb').read())
        # drop records that fully contain other records (bogus)
        rr=[r for r in recs if not any(o is not r and o[1]>=r[1] and o[1]+o[0]<=r[1]+r[0] and o[0]<r[0] for o in recs)]
        for w,s,a,b in rr:
            k=bfixtr.key(a+b)
            ru=bfixtr.EXTRA.get(k) or D.get(k)
            ru=SHORT.get(ru,ru)
            if not ru: fails.append((bi,a,b)); continue
            L=layout(ru,w*8)
            if not L: fails.append((bi,'TOO LONG',ru,w)); continue
            pitch,(m,la,lb,ind)=L
            img=[[0]*(w*8) for _ in range(16)]
            for row,(txt,x0) in enumerate(((la,0),(lb,ind))):
                if not txt: continue
                bm=pixfont.render_line(txt,pitch)
                for y in range(7):
                    for x,v in enumerate(bm[y]):
                        if v and x0+x<w*8: img[row*8+y][x0+x]=COL[y]
            top,bot=bfixmap.region_tiles(s,w)
            for c in range(w):
                for r,ts in enumerate((top,bot)):
                    px=[img[r*8+y][c*8:(c+1)*8] for y in range(8)]
                    f[ts[c]*32:(ts[c]+1)*32]=encode_fix(px)
            if preview is not None: preview.append((bi,w,img,ru))
        open(os.path.join(outdir,'BFIX%04X.FIX'%bi),'wb').write(f)
    return fails
if __name__=='__main__':
    from PIL import Image
    pv=[]
    fails=build(S+'/ru/build',pv)
    print('fails',fails)
    H=sum(18 for _ in pv); im=Image.new('L',(20*8*2+10,(len(pv)+1)//2*18),0)
    for i,(bi,w,img,ru) in enumerate(pv):
        x0=(i%2)*170; y0=(i//2)*18
        for y in range(16):
            for x in range(w*8):
                if img[y][x]: im.putpixel((x0+x,y0+y),80+img[y][x]*30)
    im.resize((im.width*2,im.height*2),Image.NEAREST).save(S+'/ru/gfx/bfix_ru.png')
    print(len(pv))
