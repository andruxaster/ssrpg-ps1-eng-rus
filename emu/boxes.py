import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys
from PIL import Image
S=_W+''
n=int(sys.argv[1]); out=sys.argv[2]; tail=int(sys.argv[3]) if len(sys.argv)>3 else 999
keep=[];prev=None
for k in range(1,n+1):
    try: im=Image.open(f'{S}/emu/shots/r{k}.ppm').convert('RGB')
    except: continue
    box=im.crop((0,170,im.width,im.height))
    px=box.get_flattened_data() if hasattr(box,'get_flattened_data') else box.getdata()
    g=sum(1 for r,gg,b in px if gg>60 and r<60 and b<60)
    sig=box.resize((40,10)).tobytes()
    if g>2000 and sig!=prev: keep.append(box); prev=sig
keep=keep[-tail:]
W,H=keep[0].size
m=Image.new('RGB',(W*2,H*((len(keep)+1)//2)))
for i,b in enumerate(keep): m.paste(b,((i%2)*W,(i//2)*H))
m=m.resize((m.width*2,m.height*2),Image.NEAREST); m.save(out); print(len(keep))
