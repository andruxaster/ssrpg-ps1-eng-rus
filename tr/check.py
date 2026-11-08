# usage: python3 check.py batch_XX.json out_XX.json
import json,sys,re
b=json.load(open(sys.argv[1])); o=json.load(open(sys.argv[2]))
ok=re.compile(r"^[A-Za-z0-9 .,!?'()\-:/+{}]*$")
err=0
for it in b:
    k=str(it['id'])
    if k not in o: print('missing',k); err+=1; continue
    r=o[k]
    if len(r.get('pages',[]))!=len(it['pages']): print('page count',k,len(r.get('pages',[])),len(it['pages'])); err+=1
    texts=list(r.get('pages',[]))
    if it['choice']:
        if it['choice']['kind']=='question' and not r.get('question'): print('no question',k); err+=1
        if len(r.get('options',[]))!=len(it['choice']['options']): print('options count',k); err+=1
        texts+= [r.get('question') or '']+list(r.get('options',[]))
        if r.get('question') and len(r['question'])>32: print('question >32',k); err+=1
        for x in r.get('options',[]):
            if len(x)>16: print('option >16',k,x); err+=1
    for t in texts:
        if not ok.match(t): print('bad chars',k,repr(t)); err+=1
        if '{' in t.replace('{NAME}',''): print('bad brace',k); err+=1
    jpn=sum(p['jp'].count('{NAME}') for p in it['pages'])
    enn=sum(t.count('{NAME}') for t in r.get('pages',[]))
    if jpn!=enn: print('NAME count',k,jpn,enn); err+=1
print('errors',err,'items',len(b),'translated',len(o))
