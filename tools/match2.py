import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
# context-based extension of matches
import sys,pickle,collections,difflib
sys.path.insert(0,_W+'/tools')
S=_W+''
NG,PS=pickle.load(open(S+'/out/db.pkl','rb')); res=pickle.load(open(S+'/out/match.pkl','rb'))
pos={(m['file'],m['idx']):j for j,m in enumerate(NG)}
def R(a,b): return difflib.SequenceMatcher(None,a,b,autojunk=False).ratio() if a and b else 0
def accepted(i):
    if i not in res or res[i][1] is None: return False
    r=res[i][2]; n=len(PS[i]['n'])
    return r>=0.75 if n<8 else r>=0.6
acc={i:res[i][1] for i in res if accepted(i)}
bychunk=collections.defaultdict(list)
for i,m in enumerate(PS): bychunk[(m['file'],m['scene'],m['chunk'])].append(i)
added=0
for it in range(3):
    for key,lst in bychunk.items():
        lst=[i for i in lst if len(PS[i]['n'])>0]
        for a,i in enumerate(lst):
            if i in acc: continue
            p=lst[a-1] if a>0 else None; q=lst[a+1] if a+1<len(lst) else None
            cand=None; thr=None
            if p in acc and q in acc:
                jp,jq=acc[p],acc[q]
                if NG[jp]['file']==NG[jq]['file'] and NG[jq]['idx']-NG[jp]['idx']==2:
                    cand=pos[(NG[jp]['file'],NG[jp]['idx']+1)]; thr=0.35
            if cand is None and p in acc:
                c=pos.get((NG[acc[p]]['file'],NG[acc[p]]['idx']+1)); 
                if c is not None: cand=c; thr=0.45
            if cand is None and q in acc:
                c=pos.get((NG[acc[q]]['file'],NG[acc[q]]['idx']-1))
                if c is not None: cand=c; thr=0.45
            if cand is None: continue
            r=R(PS[i]['n'],NG[cand]['n'])
            lr=len(NG[cand]['n'])/max(1,len(PS[i]['n']))
            if r>=thr and 0.4<lr<2.5:
                acc[i]=cand; added+=1
print('base',sum(1 for i in res if accepted(i)),'added',added)
pickle.dump(acc,open(S+'/out/accepted.pkl','wb'))
