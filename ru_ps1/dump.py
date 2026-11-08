import json,sys
b=json.load(open(sys.argv[1]))
for it in b:
    ctx=[]
    for c in it['context']:
        if c.get('self'): ctx.append('*')
        elif 'ru' in c: ctx.append('RU:'+str(c['ru'])[:120])
        elif 'en' in c: ctx.append('en:'+str(c['en'])[:60])
    print(f"#{it['id']} {it['file']}")
    for p in it['pages']: print('  >',p)
    if it['choice']: print('  CH:',it['choice'])
    print('  jp:',it['jp'][:200])
    if any(x.startswith('RU') for x in ctx): print('  ctx:',' | '.join(ctx)[:400])
