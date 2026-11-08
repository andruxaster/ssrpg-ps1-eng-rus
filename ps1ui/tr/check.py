import json,sys,re
b=json.load(open(sys.argv[1])); o=json.load(open(sys.argv[2]))
ok=re.compile(r"^[А-ЯЕа-яе0-9 .,!?'()\-:/+%]*$|^.*(LV|ON|OFF|GP|HP).*$")
okc=re.compile(r"^(?:[А-ЯЕа-яе0-9 .,!?'()\-:/+%]|LV|ON|OFF|GP|HP)*$")
err=0
for it in b:
    k=str(it['uid'])
    if k not in o: print('missing',k); err+=1; continue
    t=o[k]
    if not isinstance(t,str): print('not string',k); err+=1; continue
    if len(t)>it['max_chars']: print('too long',k,len(t),'>',it['max_chars'],repr(t)); err+=1
    if not okc.match(t) or 'ё' in t or 'Ё' in t: print('bad chars',k,repr(t)); err+=1
print('errors',err,'items',len(b),'translated',len(o))
