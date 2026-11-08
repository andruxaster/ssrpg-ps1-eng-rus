"""Battle-time raw-tile strings in PROG: tables A (messages), B (item descs), C (item names), D (hero records)."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,json,glob,re,struct
S=_W+''
sys.path.insert(0,S+'/tools')
import btltab
from uiunits import tokens_from_words,TOK
from empextract import fields
EN=open(S+'/ngcd/en/PROG.PRG','rb').read(); JPP=open(S+'/ngcd/jp/PROG.PRG','rb').read()
TABS={'A':0x5045a,'B':0x50884,'C':0x7b540}
BT=json.load(open(S+'/ru/ui/tr/battle.json'))
def _dicts():
    units=json.load(open(S+'/ru/ui/units.json'))
    ru={}
    for f in glob.glob(S+'/ru/ui/tr/out_*.json'): ru.update(json.load(open(f)))
    first={}; items={}; byen={}
    for u in units:
        r=ru.get(u['id'])
        if r is None: continue
        byen[u['en'].strip()]=r
        if 'описание предмета' in u['kind']: first[u['en'].split('\n')[0].strip()]=r.split('\n')[0]
        if 'название предмета' in u['kind']: items[re.sub(r'\s','',u['en'])]=r
    items['SmellingSalts']=items.get('SmellingSalt')
    return first,items,byen
def fix(s): return s.replace('ё','е').replace('Ё','Е')
def parts(s): return [p for p in TOK.split(s) if p]
def table_strings():
    """returns {tab: [(en_text, ru_text)]}"""
    first,items,byen=_dicts()
    out={}
    for tab,T in TABS.items():
        base,ents=btltab.read(EN,T)
        L=[]
        for k,(i,off,ln,ws) in enumerate(ents):
            en=tokens_from_words(ws,raw=True)
            r=None
            if tab=='A': r=BT['A'].get(str(k))
            elif tab=='B': r=BT['B'].get(str(k)) or first.get(en.strip())
            else: r=items.get(re.sub(r'\s','',en))
            L.append((en, fix(r) if r is not None else en))
        out[tab]=L
    return out
def hero_fields():
    lo,hi=0x781f0,0x7aa00
    fl=fields(EN[lo:hi],JPP[lo:hi])
    res=[]; skip=set()
    for n,x in enumerate(fl):
        if n in skip: continue
        pos=lo+x['pos']
        if x['span'] in (1,4) and n+1<len(fl):   # split field: merge with next
            nx=fl[n+1]; skip.add(n+1)
            span=6 if x['span']==4 else 16
        else: span=6 if x['span']<=6 else 16
        ws=[struct.unpack('>H',EN[pos+2*k:pos+2*k+2])[0] for k in range(span)]
        ws=[w for w in ws if w!=0xffff]
        res.append((pos,span,tokens_from_words(ws,raw=True)))
    return res
def hero_strings():
    first,items,byen=_dicts()
    out=[]
    for pos,span,en in hero_fields():
        k=en.strip()
        r=BT['D'].get(k) or byen.get(k) or byen.get(en)
        out.append((pos,span,en,fix(r) if r else None))
    return out
if __name__=='__main__':
    for tab,L in table_strings().items():
        print(tab,sum(1 for e,r in L if r==e and e.strip()),'untranslated')
    hs=hero_strings()
    print('hero',len(hs),[ (hex(p),e) for p,s,e,r in hs if r is None])
    print([ (hex(p),s,e) for p,s,e,r in hs if s==6])
