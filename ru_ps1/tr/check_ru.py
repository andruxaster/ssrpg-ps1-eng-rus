import json,sys,re
b=json.load(open(sys.argv[1])); o=json.load(open(sys.argv[2]))
ok=re.compile(r"^(?:[А-ЯЕа-яе0-9 .,!?'()\-:/]|GP|\{NAME\})*$")
err=0
for it in b:
    k=str(it['id'])
    if k not in o: print('missing',k); err+=1; continue
    r=o[k]
    if len(r.get('pages',[]))!=len(it['pages']): print('page count',k); err+=1
    texts=list(r.get('pages',[]))
    if it['choice']:
        opts=r.get('options',[])
        if len(opts)!=len(it['choice']['options']): print('options count',k); err+=1
        for x in opts:
            if len(x)>12: print('option too long',k,x); err+=1
        texts+=opts
        q=r.get('question')
        if it['choice'].get('question') and not q: print('question missing',k); err+=1
        if q:
            if len(q)>32: print('question too long',k,q); err+=1
            texts.append(q)
    for t in texts:
        if not ok.match(t) or 'ё' in t or 'Ё' in t: print('bad chars',k,repr(t)); err+=1
    en=sum(p.count('{NAME}') for p in it['pages']); ru=sum(p.count('{NAME}') for p in r.get('pages',[]))
    if en!=ru: print('NAME count',k); err+=1
    for e,t in zip(it['pages'],r.get('pages',[])):
        if len(t)>max(40,len(e)*1.6): print('too long',k,len(e),len(t)); err+=1
print('errors',err,'items',len(b),'translated',len(o))
