import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,pickle,collections,difflib
sys.path.insert(0,_W+'/tools')
S=_W+''
NG,PS=pickle.load(open(S+'/out/db.pkl','rb'))
def grams(s,n=2): return {s[i:i+n] for i in range(max(1,len(s)-n+1))} if s else set()
idx=collections.defaultdict(set)
for i,m in enumerate(NG):
    for g in grams(m['n']): idx[g].add(i)
def ratio(a,b):
    if not a or not b: return 0.0
    return difflib.SequenceMatcher(None,a,b,autojunk=False).ratio()
# group PS messages by chunk to know neighbors
bychunk=collections.defaultdict(list)
for i,m in enumerate(PS): bychunk[(m['file'],m['scene'],m['chunk'])].append(i)
nbr={}
for key,lst in bychunk.items():
    for a,i in enumerate(lst):
        nbr[i]=(lst[a-1] if a>0 else None, lst[a+1] if a+1<len(lst) else None)
ngpos={ (m['file'],m['idx']):i for i,m in enumerate(NG)}
cache={}
def cands(n):
    c=collections.Counter()
    for g in grams(n):
        for j in idx.get(g,()): c[j]+=1
    return [j for j,_ in c.most_common(25)]
res={}
for i,m in enumerate(PS):
    n=m['n']
    if len(n)==0: continue
    key=(n,)+tuple(PS[x]['n'] if x is not None else None for x in nbr[i])
    if key in cache: res[i]=cache[key]; continue
    best=(0,None,0)
    for j in cands(n):
        r=ratio(n,NG[j]['n'])
        ctx=0
        p,q=nbr[i]
        f,k=NG[j]['file'],NG[j]['idx']
        for x,dk in ((p,-1),(q,1)):
            if x is None: continue
            jj=ngpos.get((f,k+dk))
            if jj is not None: ctx+=ratio(PS[x]['n'],NG[jj]['n'])
        sc=r+0.25*ctx
        if sc>best[0]: best=(sc,j,r)
    res[i]=best; cache[key]=best
pickle.dump(res,open(S+'/out/match.pkl','wb'))
rs=[res[i][2] for i in res]
import statistics
print(len(res), statistics.mean(rs), [sum(r>=t for r in rs)/len(rs) for t in (0.9,0.8,0.7,0.6,0.5,0.4)])
