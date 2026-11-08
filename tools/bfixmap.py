import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,struct
S=_W+''
sys.path.insert(0,S+'/tools')
import fixr
d=open(S+'/ngcd/en/PROG.PRG','rb').read()
WT=0x703d2
def blocks():
    offs=[]
    for k in range(40):
        v=struct.unpack('>H',d[WT+2*k:WT+2*k+2])[0]
        if v>0x400 or v<0x30: break
        offs.append(v)
    uniq=sorted(set(offs))
    out={}
    for o in uniq:
        b=WT+o; first=d[b]
        lst=list(d[b:b+first])
        recs=[]
        for e in lst:
            r=b+e; h,w,l,b0=d[r:r+4]
            recs.append((w,(h<<8)|l))
        out[o]=(b,lst,recs)
    return offs,out
def region_tiles(s,w):
    top=[];bot=[]
    s=(s//32)*16+(s%32)
    for c in range(s,s+w):
        band,col=divmod(c,16)
        top.append(32*band+col); bot.append(32*band+16+col)
    return top,bot
if __name__=='__main__':
    offs,bl=blocks()
    print([hex(o) for o in offs])
    bf=[open(S+'/ngcd/en/BFIX%04X.FIX'%i,'rb').read() for i in range(12)]
    def blank(f,t): return not any(f[t*32:(t+1)*32])
    for o,(b,lst,recs) in bl.items():
        scores=[]
        for i,f in enumerate(bf):
            sc=0
            for w,s in recs:
                top,bot=region_tiles(s,w)
                sc+=sum(1 for t in top+bot if t*32<len(f) and not blank(f,t))
            scores.append(sc)
        best=max(range(12),key=lambda i:scores[i])
        print(hex(o),hex(b),len(recs),'best BFIX',best,scores[best],sorted(scores)[-2],[ (w,s) for w,s in recs][:6])
