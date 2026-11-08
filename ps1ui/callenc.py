"""Encode C_ALL new-game texts with the existing pair set (DP spacing)."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import json,pickle,sys
S=_W+''
sys.path.insert(0,S+'/tools')
import rupairs
def encode_all(pm,W=24):
    t=json.load(open(S+'/ps1ui/tr/call.json')); out={}; bad=[]
    for k,v in t.items():
        if not v: out[k]=b''; continue
        c,cells=rupairs.encode_line(v,lambda p:0 if p in pm else 10**6,W)
        if cells is None or c>=10**6: bad.append((k,v)); continue
        b=b''
        for cell in cells:
            code=pm[cell[1]][0]; b+=bytes([code>>8,code&255])
        out[k]=b
    return out,bad
if __name__=='__main__':
    pm=pickle.load(open(S+'/ru_ps1/out/pmap_final.pkl','rb'))
    o,bad=encode_all(pm); print('bad',bad); print(sum(len(v)+2 for v in o.values()))

def enc_text(t,pm,W=48):
    c,cells=rupairs.encode_line(t,lambda p:0 if p in pm else 10**6,W)
    if cells is None or c>=10**6: raise KeyError('no pairs for %r'%t)
    b=b''
    for cell in cells:
        code=pm[cell[1]][0]; b+=bytes([code>>8,code&255])
    return b
