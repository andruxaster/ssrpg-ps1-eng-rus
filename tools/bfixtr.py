import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,json,glob,re
S=_W+''
sys.path.insert(0,S+'/tools')
import bfixocr
def key(s): return re.sub(r'[^A-Z0-9]','',s.upper().replace('1OO','100'))
def dicts():
    units=json.load(open(S+'/ru/ui/units.json'))
    ru={}
    for f in glob.glob(S+'/ru/ui/tr/out_*.json'): ru.update(json.load(open(f)))
    D={}
    for u in units:
        r=ru.get(u['id'])
        if r and ('прием' in u['kind'] or 'атаки' in u['kind']): D.setdefault(key(u['en']),r)
    bt=json.load(open(S+'/ru/ui/tr/battle.json'))['D']
    for k,v in bt.items(): D.setdefault(key(k),v)
    return D
EXTRA={'REARREPLICAATTACK':'Атака копии сзади','HAZEBLADEFLASH':'Клинок марева -Вспышка-','HAZEBLADELIGHT':'Клинок марева -Свет-',
'HAZEBLADEMIST':'Клинок марева -Туман-','WINDEDGEHONORABLE':'Клинок ветра: благая мгла','KIRINDANCE':'Танец Кирина','SOARINGEARTHSPLITTERSLASH':'Парящий разлом земли','PLASMARUSHREARREPBLADEDOGATTACK':None}
if __name__=='__main__':
    D=dicts(); miss=[]
    for bi,recs in bfixocr.ocr().items():
        for w,s,a,b in recs:
            k=key(a+b)
            if k not in D and k not in EXTRA: miss.append((bi,w,s,a.strip()+' / '+b.strip()))
    print(len(miss)); [print(m) for m in miss]
