import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,pickle,json,re,collections
sys.path.insert(0,_W+'/tools')
import conv,conv2
S=conv2.enparse.endec.halves.S
NG,PS=pickle.load(open(S+'/out/db.pkl','rb')); out=pickle.load(open(S+'/out/converted.pkl','rb'))
def ps_pages(raw):
    pages,choice=conv.parse_ps1(raw)
    res=[]
    for p in pages:
        t=p['text']
        # insert name markers
        port=[w for w in p['pre'] if w[0]==1]
        if p['n']==0 and not any(k=='name' for _,_,k in p['mid']): continue
        res.append({'portrait':('%02x'%port[-1][1]) if port else None,'jp':t.replace(conv.NAME,'{NAME}')})
    ch=None
    if choice is not None:
        ct=conv.toks(b''.join(choice)); parts=[];cur=''
        for w in ct[1:]:
            if w==b'\x09\0': parts.append(cur); cur=''
            elif w==b'\0\0': break
            elif w[0]>=0x81: cur+=w.decode('cp932','replace')
        parts.append(cur)
        ch={'kind':'question' if ct[0]==b'\x07\0' else 'menu','question':parts[0] if ct[0]==b'\x07\0' else None,'options':parts[1:]}
    return res,ch
def en_plain(items):
    s=conv2.show(items)
    s=re.sub(r'<0200>',' ',s); s=re.sub(r'<0300>|<0f00>|<0400>',' / ',s); s=re.sub(r'<[0-9a-f]{4}>','',s)
    return ' '.join(s.split())
bychunk=collections.defaultdict(list)
for i,m in enumerate(PS): bychunk[(m['file'],m['scene'],m['chunk'])].append(i)
pos={}
for key,lst in bychunk.items():
    for a,i in enumerate(lst): pos[i]=(key,a)
groups={}
for i,m in enumerate(PS):
    if i in out or not m['n'] or m['file']=='FLD/F_TEST.BIN': continue
    pages,ch=ps_pages(m['raw'])
    if not pages and not ch: continue
    gk=json.dumps([[p['jp'] for p in pages],ch],ensure_ascii=False)
    groups.setdefault(gk,[]).append(i)
items=[]
for gid,(gk,ids) in enumerate(groups.items()):
    i=ids[0]; pages,ch=ps_pages(PS[i]['raw'])
    key,a=pos[i]; lst=bychunk[key]
    ctx=[]
    for b in range(max(0,a-4),min(len(lst),a+5)):
        if b==a: ctx.append({'self':True}); continue
        j=lst[b]; pg,_=ps_pages(PS[j]['raw'])
        ctx.append({'jp':' / '.join(p['jp'].replace('\n',' ') for p in pg),'portraits':[p['portrait'] for p in pg],'en':en_plain(out[j]) if j in out else None})
    items.append({'id':gid,'file':PS[i]['file'],'pages':pages,'choice':ch,'context':ctx})
json.dump(items,open(S+'/tr/items.json','w'),ensure_ascii=False)
json.dump({str(k):v for k,v in enumerate(groups.values())},open(S+'/tr/groups.json','w'))
print(len(items), sum(len(p['jp']) for it in items for p in it['pages']))
print(collections.Counter(it['file'] for it in items).most_common())
