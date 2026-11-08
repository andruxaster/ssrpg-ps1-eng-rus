"""Resolve UI translations per occurrence, produce strict pair segments."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,json,re,glob,collections
S=_W+''
sys.path.insert(0,S+'/tools')
from uiunits import TOK,line_widths,tokens_from_words,SPECIAL
from endec import code_text
TR=S+'/ru/ui/tr'
units=json.load(open(S+'/ru/ui/units.json'))
ru={}
for f in glob.glob(TR+'/out_*.json'): ru.update(json.load(open(f)))
byen={u['en']:u for u in units}
def fix(s): return s.replace('ё','е').replace('Ё','Е')
def parts(s): return [p for p in TOK.split(s) if p]
def resolve(en):
    """en display string -> list of parts (Russian) with padding; None if untranslated/skip"""
    u=byen.get(en)
    if u is None or u['id'] not in ru: return None
    r=fix(ru[u['id']])
    ep=parts(en); rp=parts(r)
    # per line padding: if EN line ends with a blank tile, pad RU line to EN width
    def lines(ps):
        L=[[]]
        for p in ps:
            if p=='\n': L.append([])
            else: L[-1].append(p)
        return L
    el=lines(ep); rl=lines(rp)
    out=[]
    for li,(a,b) in enumerate(zip(el,rl)):
        ew=line_widths(''.join(a))[0]; rw=line_widths(''.join(b))[0]
        endtok=bool(b) and TOK.fullmatch(b[-1]) is not None
        if rw<ew and not endtok and not any(x in ('<2>','<3>') for x in a):
            if b and not TOK.fullmatch(b[-1]):
                seg=b[-1]
                if len(seg)%2: seg+=' '
                b=b[:-1]+[seg+'  '*(ew-rw)]
            else: b=b+['  '*(ew-rw)]
        if li: out.append('\n')
        out+=b
    return out
def segments(ps):
    out=[]
    for p in ps:
        if TOK.fullmatch(p): continue
        s=p if len(p)%2==0 else p+' '
        out.append(s)
    return out
if __name__=='__main__':
    t=json.load(open(S+'/ru/ui/prog_tables.json'))
    emp=json.load(open(S+'/ru/ui/emp.json'))
    res={'prog':{},'emp':{}}; miss=collections.Counter(); segs=collections.Counter()
    for tab,T in t.items():
        for s in T['strings']:
            en=tokens_from_words(s['words'][:-1])
            r=resolve(en)
            if r is None: miss[(tab,en)]+=1; r=parts(en)
            res['prog']['%s:%d'%(tab,s['i'])]=r
            for x in segments(r): segs[x]+=1
    for f,fl in emp.items():
        for x in fl:
            en=tokens_from_words(x['tiles'],raw=True)
            r=resolve(en)
            if r is None: miss[('emp',en)]+=1; r=parts(en)
            res['emp']['%s:%d'%(f,x['pos'])]=r
            for y in segments(r): segs[y]+=1
    import battleui
    res['battle']={}
    for tab,L in battleui.table_strings().items():
        res['battle'][tab]=[parts(r) for e,r in L]
        for ps in res['battle'][tab]:
            for y in segments(ps): segs[y]+=1
    res['hero']=[]
    for pos,span,en,r in battleui.hero_strings():
        ps=parts(r if r else en)
        res['hero'].append((pos,span,ps))
        for y in segments(ps): segs[y]+=1
    json.dump(res,open(S+'/ru/ui/resolved.json','w'),ensure_ascii=False)
    json.dump(sorted(segs),open(S+'/ru/ui/strict_segments.json','w'),ensure_ascii=False)
    pairs=set(x[i:i+2] for x in segs for i in range(0,len(x),2))
    print('resolved prog',len(res['prog']),'emp',len(res['emp']),'segments',len(segs),'distinct pairs',len(pairs))
    print('untranslated (kept EN):',len(miss)); print([k for k in miss][:40])
    chars=collections.Counter(c for x in segs for c in x); print(''.join(sorted(chars)))
