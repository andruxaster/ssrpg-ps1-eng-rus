import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,collections,json
S=_W+''
sys.path.insert(0,S+'/tools')
from vramspr import sprites
from spr import tile
SCREENS={'kill':(17,2,89),'or':(22,92,128),'bekilled':(25,143,203),'calm':(32,238,332),'follow':(43,344,419),'destiny':(52,472,570)}
def layout(name,chip):
    fr,lo,hi=SCREENS[name]
    sp=[s for s in sprites(S+'/emu/cd/bc_%d.bin'%fr) if 250<=s[0]<=330]
    cells={}  # (col,row)->tile
    cols=[s for s in sp if any(lo<=t[0]-22784<=hi for t in s[4]) or all(t[0]-22784 in (91,0,-22784) for t in s[4])]
    sel=[s for s in sp if s[1]<330 or s[1]>480]  # ignore
    out=[]
    for ci,s in enumerate(sp):
        for r,t in enumerate(s[4]):
            tt=t[0]-22784
            if lo<=tt<=hi: cells[(s[1],s[2]+16*r)]=(tt,t[1])
    return cells
if __name__=='__main__':
    from PIL import Image
    chip=open(S+'/ngcd/en/CHIP00B2.SPR','rb').read()
    for name in SCREENS:
        cells=layout(name,chip)
        xs=[k[0] for k in cells]; ys=[k[1] for k in cells]
        x0,y0=min(xs),min(ys); W=max(xs)-x0+16; H=max(ys)-y0+16
        im=Image.new('L',(W,H),0); hist=collections.Counter(); pals=collections.Counter()
        for (x,y),(t,pal) in cells.items():
            p=tile(chip,t); pals[pal]+=1
            for yy in range(16):
                for xx in range(16):
                    hist[p[yy][xx]]+=1
                    im.putpixel((x-x0+xx,y-y0+yy),p[yy][xx]*16)
        im.resize((W*2,H*2)).save(S+'/ru/intro/br_%s.png'%name)
        print(name,len(cells),'box',W,H,'pal',dict(pals),sorted(hist.items()))
