import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import glob,os,sys,re
from fontTools.ttLib import TTFont
from PIL import Image,ImageDraw,ImageFont
S=_W+''
TXT='УБЕЙ или... УМРИ! Успокой тело и разум... Следуй по пути... ибо СУДЬБА ЖДЕТ!'
need=set(TXT)-{' '}
def fontfiles(pkg):
    fs=glob.glob(pkg+'/package/files/*.woff')
    fs=[f for f in fs if 'italic' not in f and not f.endswith('.woff2')]
    best={}
    for f in fs:
        m=re.search(r'-(\d+)-normal\.woff$',f); w=int(m.group(1)) if m else 400
        best.setdefault(w,[]).append(f)
    return best
class Multi:
    def __init__(self,files,sz):
        self.f=[]
        for fn in files:
            try: self.f.append((ImageFont.truetype(fn,sz),set(TTFont(fn).getBestCmap())))
            except Exception: pass
    def cover(self): 
        allc=set().union(*[c for _,c in self.f]) if self.f else set()
        return all(ord(ch) in allc for ch in need)
    def pick(self,ch):
        for f,c in self.f:
            if ord(ch) in c: return f
        return None
if __name__=='__main__':
    rows=[]
    for pkg in sorted(glob.glob(S+'/fonts3/*/')):
        if pkg.endswith('.tgz'): continue
        for w,files in sorted(fontfiles(pkg).items()):
            if w not in (400,700,800,900) : continue
            m=Multi(files,28)
            if not m.cover(): continue
            rows.append((os.path.basename(pkg.rstrip('/')),w,m))
    im=Image.new('RGB',(1400,44*len(rows)),(0,0,0)); d=ImageDraw.Draw(im)
    for k,(n,w,m) in enumerate(rows):
        x=250; d.text((4,k*44+14),'%s %d'%(n[:28],w),fill=(0,255,0))
        for ch in TXT:
            f=m.pick(ch)
            if f is None: x+=10; continue
            d.text((x,k*44+4),ch,font=f,fill=(255,255,255)); x+=d.textlength(ch,font=f)
    im.save(S+'/ru/gfx/fontsheet.png'); print(len(rows))
