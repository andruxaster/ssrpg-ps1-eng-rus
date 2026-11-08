import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,collections,json
sys.path.insert(0,_W+'/tools')
import spr
S=_W+''
INK={0,1,3,8,9,10}
d=open(S+'/ngcd/en/CHIP000F.SPR','rb').read()
NT=len(d)//128
def mask(t):
    p=spr.tile(d,t)
    return [[1 if p[y][x] in INK else 0 for x in range(16)] for y in range(16)]
def halves(t):
    m=mask(t)
    L=tuple(tuple(r[0:8]) for r in m); R=tuple(tuple(r[8:16]) for r in m)
    return L,R
