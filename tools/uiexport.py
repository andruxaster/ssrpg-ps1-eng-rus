import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,json,re,collections
S=_W+''
sys.path.insert(0,S+'/tools')
from uiunits import *
t=json.load(open(S+'/ru/ui/prog_tables.json'))
emp=json.load(open(S+'/ru/ui/emp.json'))
TECH=set(range(19,160))|set(range(181,221))
def group(tab,i,en):
    if tab=='names': return 'имя персонажа',5
    if tab=='items': return 'название предмета/снаряжения (список)',6
    if tab=='shops': return 'название лавки',4
    if tab=='places': return 'название места на карте',7
    if tab=='idesc': return 'описание предмета (окно описания)',13
    if tab=='msgs' and i in TECH: return 'название приема',13
    if tab=='keyitems':
        if i<=24: return 'название ключевого предмета',max(line_widths(t['keyitems']['strings'][j]['en']) [0] for j in range(25))
        if i<=49: return 'описание ключевого предмета',13
        if 289<=i<=327: return 'описание действия приема (меню)',13
    if tab=='keyitems' and (52<=i<=152 or 156<=i<=223 or 228<=i<=239 or 250<=i<=262) and i not in (59+0,) and not (187<=i<=191):
        return 'название приема',13
    if tab in ('menu2',) and 240<=i<=247: return 'описание персонажа (экран выбора)',12
    return None,None
import uiextract
JPMAP={int(k,16):v for k,v in json.load(open(S+'/out/ngcd_code2char.json')).items()}
jprog=open(S+'/ngcd/jp/PROG.PRG','rb').read()
def jtxt(ws,raw=False):
    o=''
    for v in ws:
        if v==0xffff: break
        c=v+0x212a if raw else v
        o+= JPMAP.get(c,'\n' if v==0 and not raw else '<%x>'%v)
    return o
JPT={}
for tab,h in uiextract.TABLES.items():
    try:
        d,offs,out=uiextract.read_table(jprog,h); JPT[tab]=[jtxt(ws) for o,ws in out]
    except Exception as ex: JPT[tab]=[]
units={}  # key: en text -> unit
occ=collections.defaultdict(list)
for tab,T in t.items():
    seen=set()
    for s in T['strings']:
        if s['off'] in seen: continue
        seen.add(s['off'])
        en=tokens_from_words(s['words'][:-1])
        if not en.strip() or re.fullmatch(r'[\s\d\-]*',en): continue   # blanks, '- ', digits
        if re.fullmatch(r'(\{T\d+\}\s*)+',en): continue
        g,lim=group(tab,s['i'],en)
        lw=line_widths(en)
        if g is None:
            g='служебная строка/сообщение'
            lim=max(lw)
            if '<2>' in en or len(lw)>1 or max(lw)>=12: lim=max(max(lw),15) if tab=='msgs' else max(lw)
        jp=JPT[tab][s['i']] if s['i']<len(JPT[tab]) and tab not in ('menu2',) else ''
        occ[en].append((tab,s['i'],g,lim,jp))
for f,fl in emp.items():
    for x in fl:
        en=tokens_from_words(x['tiles'],raw=True)
        if x['span']==6: g,lim='имя врага',6
        else: g,lim='название атаки/действия врага (окно боя)',min(14,max(12,line_widths(en)[0]))
        jb=open(S+'/ngcd/jp/'+f,'rb').read()
        from uitab import W
        jw=[W(jb,x['pos']+2*k) for k in range(x['span'])]
        occ[en].append(('emp',f,g,lim,jtxt(jw,raw=True)))
out=[]
for i,(en,oc) in enumerate(occ.items()):
    spec=[o for o in oc if not o[2].startswith('служеб')] or oc
    gs=sorted(set(o[2] for o in spec)); lim=max(min(o[3] for o in spec),max(line_widths(en)))
    out.append({'id':'u%04d'%i,'en':en,'kind':' / '.join(gs),'max_tiles_per_line':lim,
                'en_tiles':line_widths(en),'where':[list(o[:2]) for o in oc][:4],'n':len(oc),'jp':oc[0][4]})
json.dump(out,open(S+'/ru/ui/units.json','w'),ensure_ascii=False,indent=0)
print(len(out),collections.Counter(u['kind'] for u in out).most_common())
over=[u for u in out if max(u['en_tiles'])>u['max_tiles_per_line']]
print('EN over limit',len(over),[ (u['en'],u['kind']) for u in over][:20])
