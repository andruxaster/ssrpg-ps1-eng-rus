import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,pickle,json,re,collections,glob,math
sys.path.insert(0,_W+'/tools')
import ngtok,ngmsg
S=_W+''
NG,PS=pickle.load(open(S+'/out/db.pkl','rb'))
# EN messages directly from EN files (incl. extra EN-only files/messages)
msgs=[]
for f in sorted(glob.glob(S+'/ngcd/en/MSGD*.PRG')):
    name=f.split('/')[-1]
    jpmap={m['idx']:m['jp'] for m in NG if m['file']==name}
    for idx,(o,w) in enumerate(ngmsg.messages(f)):
        pages,ch=ngtok.structure(w)
        texts=[ngtok.page_text(p) for p in pages]
        menu=None
        if ch:
            if ch['kind']=='menu':
                opts=[]
                for row in ch['opts']:
                    for m in re.finditer(r'([A-F])\s+(.+?)(?=\s{2,}[A-F]\s|$)',row): opts.append(m.group(2).strip())
                menu={'kind':'menu','options':opts}
            else: menu={'kind':'yn','options':[o.strip() for o in ch['opts']]}
        alltxt=' '.join(texts)+' '+(' '.join(menu['options']) if menu else '')
        ok=bool(alltxt.strip()) and '{' not in alltxt.replace('{NAME}','')
        msgs.append(dict(file=name,idx=idx,pages=texts,choice=menu,jp=jpmap.get(idx,''),ok=ok))
json.dump(msgs,open(S+'/ru/tr/msgs.json','w'),ensure_ascii=False)
groups=collections.OrderedDict()
for k,m in enumerate(msgs):
    if not m['ok']: continue
    key=json.dumps([m['pages'],m['choice']],ensure_ascii=False)
    groups.setdefault(key,[]).append(k)
items=[]
for gid,(key,ks) in enumerate(groups.items()):
    k=ks[0]; m=msgs[k]
    ctx=[]
    for d in range(-3,4):
        j=k+d
        if d==0: ctx.append({'self':True}); continue
        if 0<=j<len(msgs) and msgs[j]['file']==m['file'] and msgs[j]['ok']:
            ctx.append({'en':' / '.join(msgs[j]['pages'])})
    items.append({'id':gid,'file':m['file'],'pages':m['pages'],'choice':m['choice'],'jp':m['jp'],'context':ctx})
json.dump({str(g):ks for g,ks in enumerate(groups.values())},open(S+'/ru/tr/groups.json','w'))
N=24; per=math.ceil(len(items)/N)
for b in range(N):
    json.dump(items[b*per:(b+1)*per],open(f'{S}/ru/tr/batch_{b:02d}.json','w'),ensure_ascii=False,indent=0)
print(len(msgs),sum(m['ok'] for m in msgs),len(items),sum(len(' '.join(i['pages'])) for i in items))
