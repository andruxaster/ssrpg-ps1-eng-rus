import json,sys
b=json.load(open(sys.argv[1]))
a,z=int(sys.argv[2]),int(sys.argv[3])
for x in b[a:z]:
    print(f"## {x['id']} {x['file']}")
    ctx=[]
    for c in x['context']:
        if c.get('self'): ctx.append('[*]')
        elif 'ru' in c: ctx.append('R:'+c['ru'][:70])
        else: ctx.append('E:'+c.get('en','')[:50])
    print('  ctx:',' | '.join(ctx))
    print('  jp:',x['jp'])
    for p in x['pages']: print('  >',p)
    if x['choice']: print('  CH:',x['choice'])
