import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,pickle,collections,json,glob,re
S=_W+''
sys.path.insert(0,S+'/tools')
import conv2ru as conv2
NG,PS=pickle.load(open(S+'/out/db.pkl','rb'))
acc=pickle.load(open(S+'/out/accepted.pkl','rb'))
msgs=json.load(open(S+'/ru/tr/msgs.json')); rg=json.load(open(S+'/ru/tr/groups.json')); rtr={}
for f in glob.glob(S+'/ru/tr/out_*.json'): rtr.update(json.load(open(f)))
man=json.load(open(S+'/ru/tr/manual.json')) if True else {}
pos={(m['file'],m['idx']):k for k,m in enumerate(msgs)}
m2g={i:g for g,ids in rg.items() for i in ids}
def ru_for_ng(j):
    n=NG[j]; k=pos.get((n['file'],n['idx']))
    if k is None: return None
    g=m2g.get(k)
    t=rtr.get(g) if g else None
    if t is None: return None
    t=dict(t)
    ch=msgs[k].get('choice')
    if ch and 'options' not in t and ch.get('options'): t['options']=ch['options']
    return t
out={}; fail=collections.Counter(); src={}
for i,m in enumerate(PS):
    if i not in acc: continue
    t=ru_for_ng(acc[i])
    if not t: fail['nort']+=1; continue
    it=conv2.build_text(m['raw'],t)
    if it is None: fail['build']+=1; continue
    out[i]=it; src[i]='ng'
tg=json.load(open(S+'/tr/groups.json')); ptr={}
for f in glob.glob(S+'/ru_ps1/tr/out_*.json'): ptr.update(json.load(open(f)))
for gid,ids in tg.items():
    t=ptr.get(gid)
    for i in ids:
        if i in out: continue
        if not t: fail['ps1_untr']+=1; continue
        it=conv2.build_text(PS[i]['raw'],t)
        if it is None: fail['ps1build']+=1; continue
        out[i]=it; src[i]='ps1'
pickle.dump(out,open(S+'/ru_ps1/out/converted.pkl','wb'))
pairs=collections.Counter()
for it in out.values():
    for x in it:
        if isinstance(x,tuple) and x[0]=='pair': pairs[x[1]]+=1
print('converted',len(out),'of',len(PS),dict(fail),'distinct pairs',len(pairs))
print(''.join(sorted(set(c for p in pairs for c in p))))
pickle.dump(pairs,open(S+'/ru_ps1/out/pairs.pkl','wb'))
