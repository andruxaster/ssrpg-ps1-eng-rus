import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,pickle,struct,collections,importlib
sys.path.insert(0,_W+'/tools')
import halves,labels
order,first,u=pickle.load(open(halves.S+'/out/halves.pkl','rb'))
hid={h:i for i,h in enumerate(order)}
tile2={}
for t in range(halves.NT):
    L,R=halves.halves(t); tile2[t]=(hid[L],hid[R])
def code_text(v,unk=None):
    t=v-0x212a
    if t not in tile2: return '{T%d}'%t
    out=''
    for h in tile2[t]:
        if h in labels.LAB: out+=labels.LAB[h]
        else:
            out+='{%d}'%h
            if unk is not None: unk[h]+=1
    return out
