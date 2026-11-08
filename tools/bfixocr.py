import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,pickle,json
S=_W+''
sys.path.insert(0,S+'/tools')
import bfixmap
LAB='EAINSRLDOTGHCPWFMKUBY-ZVQXO1'
glyphs=pickle.load(open(S+'/ru/gfx/glyphs.pkl','rb'))
G={g:LAB[i] for i,g in enumerate(glyphs)}
MAP=[(0x38,0),(0x8a,1),(0xe4,2),(0x13a,3),(0x1da,4),(0x18c,5),(0x22c,6),(0x282,7),(0x2c8,8),(0x312,9),(0x36c,10),(0x39e,11)]
def ocr():
    offs,bl=bfixmap.blocks()
    out={}
    for o,bi in MAP:
        f=open(S+'/ngcd/en/BFIX%04X.FIX'%bi,'rb').read()
        recs=[]
        for w,s in sorted(set(bl[o][2]),key=lambda x:x[1]):
            top,bot=bfixmap.region_tiles(s,w)
            def row(ts): return ''.join(G.get(f[t*32:(t+1)*32],' ' if not any(f[t*32:(t+1)*32]) else '?') for t in ts)
            recs.append((w,s,row(top),row(bot)))
        out[bi]=recs
    return out
if __name__=='__main__':
    for bi,recs in ocr().items():
        print('BFIX',bi)
        for w,s,a,b in recs: print('   %2d %3d |%s|%s|'%(w,s,a,b))
