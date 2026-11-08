import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,pickle,collections
sys.path.insert(0,_W+'/tools')
import halves,labels
S=halves.S
order,first,u=pickle.load(open(S+'/out/halves.pkl','rb'))
# best half bitmap per single character (left-side and right-side variants are identical masks per id)
best={}
for hid,lab in labels.LAB.items():
    if len(lab)!=1: continue
    h=order[hid]
    cnt=u[h]
    if lab not in best or cnt>best[lab][0]: best[lab]=(cnt,h)
HALF={k:v[1] for k,v in best.items()}
HALF[' ']=order[0]
def pair_bitmap(p):
    a=HALF[p[0]]; b=HALF[p[1]]
    rows=[]
    for y in range(16):
        w=0
        for x in range(8):
            if a[y][x]: w|=1<<(15-x)
            if b[y][x]: w|=1<<(7-x)
        rows.append(w)
    return rows
def to_bytes(rows):
    out=bytearray()
    for w in rows: out+=bytes([w&255,w>>8])
    return bytes(out)
