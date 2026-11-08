import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,pickle,collections
sys.path.insert(0,_W+'/tools')
import conv2
S=_W+''
NG,PS=pickle.load(open(S+'/out/db.pkl','rb')); res=pickle.load(open(S+'/out/match.pkl','rb'))
acc=pickle.load(open(S+'/out/accepted.pkl','rb'))
out={}
fail=collections.Counter()
for i,m in enumerate(PS):
    if i not in acc: continue
    it=conv2.build(m['raw'],NG[acc[i]]['enw'])
    if it is None: fail['build']+=1; continue
    out[i]=it
import json,glob
tr={}
for f in glob.glob(S+'/tr/out_*.json'): tr.update(json.load(open(f)))
groups=json.load(open(S+'/tr/groups.json'))
ntr=0
for gid,ids in groups.items():
    t=tr.get(gid)
    if not t: continue
    for i in ids:
        if i in out: continue
        it=conv2.build_text(PS[i]['raw'],t)
        if it is None: fail['tr']+=1; continue
        out[i]=it; ntr+=1
print('own translations applied',ntr)
pickle.dump(out,open(S+'/out/converted.pkl','wb'))
pairs=collections.Counter()
for it in out.values():
    for x in it:
        if isinstance(x,tuple) and x[0]=='pair': pairs[x[1]]+=1
print('converted',len(out),'of',len(PS),fail,'distinct pairs',len(pairs))
chars=collections.Counter(c for p in pairs for c in p)
print(sorted(chars))
pickle.dump(pairs,open(S+'/out/pairs.pkl','wb'))
