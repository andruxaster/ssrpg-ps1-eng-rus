import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,json
S=_W+''
sys.path.insert(0,S+'/ps1ui')
import psi
from PIL import Image
p=psi.PSI(open(S+'/ps1ui/gfx/BT_COCK.PSI','rb').read(),open(S+'/ps1/fs/BTL/P6_BCOCK.COL','rb').read())
M=json.load(open(S+'/ps1ui/gfx/ng_icon_masks.json'))
src=open(S+'/ps1ui/icons.py').read()
for name in ('rescue','form'):
    blk=src.split("M['%s']=parse('''"%name)[1].split("''')")[0]
    M[name]=[[1 if c=='#' else 0 for c in r] for r in blk.strip().split('\n')]
names={28:'sword',29:'special',30:'bag',31:'mask',32:'form'}
for gi,name in names.items():
    g,n,ents=p.groups[gi]
    m=M[name]
    im=Image.new('L',(16,16))
    for y in range(16):
        for x in range(16): im.putpixel((x,y),255*m[y][x])
    big=im.resize((28,28),Image.NEAREST)
    on=set((x+2,y+2) for y in range(28) for x in range(28) if big.getpixel((x,y))>128)
    ring=set((x+dx,y+dy) for x,y in on for dx in (-1,0,1) for dy in (-1,0,1))-on
    canvas=[[0]*32 for _ in range(32)]
    for x,y in ring:
        if 0<=x<32 and 0<=y<32: canvas[y][x]=1
    for x,y in on: canvas[y][x]=2
    for x,y,t,f in ents:
        ox=(x-65536 if x>32767 else x)+16; oy=(y-65536 if y>32767 else y)+16
        tile=[[canvas[oy+yy][ox+xx] for xx in range(16)] for yy in range(16)]
        p.settile(t,tile)
open(S+'/ps1ui/gfx/BT_COCK.PSI','wb').write(p.d)
o=Image.new('RGB',(5*40,40),(60,60,60))
for k,gi in enumerate(range(28,33)):
    for x,y,t,f in p.groups[gi][2]:
        ox=(x-65536 if x>32767 else x)+16; oy=(y-65536 if y>32767 else y)+16
        P=p.tile(t)
        for yy in range(16):
            for xx in range(16):
                if P[yy][xx]: o.putpixel((k*40+ox+xx,oy+yy),p.color(P[yy][xx]))
o.resize((800,160),Image.NEAREST).save(S+'/ps1ui/gfx/markers_new.png')
print('ok')
