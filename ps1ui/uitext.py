"""PS1 UI: load translations -> per-occurrence RU text; pair list."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import json,glob
S=_W+''
def load():
    U=json.load(open(S+'/ps1ui/units.json')); inv=json.load(open(S+'/ps1ui/inventory.json'))
    tr={}
    for f in glob.glob(S+'/ps1ui/tr/out_*.json'): tr.update(json.load(open(f)))
    import os
    if os.path.exists(S+'/ps1ui/tr/fix.json'): tr.update(json.load(open(S+'/ps1ui/tr/fix.json')))
    occ=[]
    long=json.load(open(S+'/ps1ui/tr/fix_long.json')) if os.path.exists(S+'/ps1ui/tr/fix_long.json') else {}
    for u in U:
        t=tr.get(str(u['uid']))
        if not t: continue
        for i in u['ids']:
            x=inv[i]; tt=t[:x['max_chars']]
            lt=long.get(str(u['uid']))
            if lt and len(lt)<=x['max_chars']: tt=lt
            occ.append(dict(file=x['file'],off=x['off'],jpbytes=x['jpbytes'],max_chars=x['max_chars'],ru=tt))
    if os.path.exists(S+'/ps1ui/tr/extra.json'): occ+=json.load(open(S+'/ps1ui/tr/extra.json'))
    return occ
def pairs_of(t):
    if len(t)%2: t+=' '
    return [t[i:i+2] for i in range(0,len(t),2)]
def ui_pairs():
    s=set()
    for o in load():
        if o['file']!='MSG/COMN.MSG': s.update(pairs_of(o['ru']))
    import os
    if os.path.exists(S+'/ps1ui/tr/comn.json'):
        for v in json.load(open(S+'/ps1ui/tr/comn.json')).values():
            for x in v:
                if isinstance(x,str): s.update(pairs_of(x))
    return s
