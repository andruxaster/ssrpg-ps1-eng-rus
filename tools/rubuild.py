import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,json,glob,collections,pickle,struct,re
sys.path.insert(0,_W+'/tools')
import ngmsg,ngtok,rupairs,endec,rufont
S=_W+''
TR=S+'/ru/tr'
NT=1793; BASE=0x212a
msgs=json.load(open(TR+'/msgs.json'))
groups=json.load(open(TR+'/groups.json'))
tr={}
for f in glob.glob(TR+'/out_*.json'): tr.update(json.load(open(f)))
msg2tr={}
for gid,ks in groups.items():
    if gid in tr:
        for k in ks: msg2tr[k]=tr[gid]
_man=json.load(open(TR+'/manual.json'))
for k,key in {1131:'A',1192:'A',4380:'A',4713:'A',1132:'B',1193:'B',4714:'B2',1133:'C',4382:'C',1194:'D',4715:'D',4381:'E',5021:'F',7435:'G'}.items():
    msg2tr[k]={'pages':[_man[key]]}
    msgs[k]['ok']=True
import os
# --- number-code fixes: apply by identical EN message words
import ngmsg as _ng
_enw=[]
for _f in sorted(glob.glob(S+'/ngcd/en/MSGD*.PRG')):
    for _o,_w in _ng.messages(_f): _enw.append(tuple(_w))
_nf=json.load(open(TR+'/num_fix.json'))
_sig={_enw[int(k)]:v for k,v in _nf.items()}
for _k,_w in enumerate(_enw):
    if _w in _sig:
        old_opts=(msg2tr.get(_k) or {}).get('options')
        msg2tr[_k]={'pages':_sig[_w]}
        if old_opts: msg2tr[_k]['options']=old_opts
        msgs[_k]['ok']=True
for _k,_w in enumerate(_enw):
    _pg,_ch=ngtok.structure(list(_w))
    if _ch is None and msgs[_k].get('choice'):
        print('choice dropped (was param):',_k); msgs[_k]['choice']=None
tiles=json.load(open(S+('/ru/tiles_ui.json' if os.environ.get('RUUI') else '/ru/tiles.json')))
FREE=tiles['free']; EXT=list(range(NT, 0x2900-BASE))
# reusable existing tiles: pair text -> tile (only pairs made of non-Cyrillic chars, found in kept tiles)
keep=set(tiles['keep'])
existing={}
for t in range(NT):
    a,b=endec.tile2[t]
    if a in endec.labels.LAB and b in endec.labels.LAB:
        s=endec.labels.LAB[a]+endec.labels.LAB[b]
        if len(s)==2 and t in keep: existing.setdefault(s,t)
CYR=re.compile('[А-Яа-я]')
def needs_new(p): return p not in existing
# ---------- build per-message plans
def ru_message_plan(k):
    m=msgs[k]; t=msg2tr.get(k)
    if not m['ok'] or t is None: return None
    return t
def all_lines():
    L=[]
    for k,m in enumerate(msgs):
        t=ru_message_plan(k)
        if not t: continue
        for p in t['pages']:
            L+=rupairs.wrap(p.replace("'","'"))
    return L

# ---------- choice strings (strict layout)
def menu_rows_ru(ch_en_rows,opts_ru):
    rows=[];k=0
    for row in ch_en_rows:
        labs=[(m.start(),m.group(1)) for m in re.finditer(r'(?:(?<=\s)|^)([A-F])(?=\s{2,})',row)]
        out=list(' '*len(row))
        for j,(col,lab) in enumerate(labs):
            out[col]=lab
            m=re.match(r'[A-F](\s+)',row[col:]); ncol=col+1+len(m.group(1))
            end=labs[j+1][0]-1 if j+1<len(labs) else len(row)
            name=opts_ru[k] if k<len(opts_ru) else ''; k+=1
            name=name[:max(0,end-ncol)]
            for q,chh in enumerate(name): out[ncol+q]=chh
        s=''.join(out).rstrip()
        if len(s)%2: s+=' '
        rows.append(s)
    return rows
def strict_cells(s):
    if len(s)%2: s+=' '
    return [('pair',s[i:i+2]) for i in range(0,len(s),2)]
def norm(t):
    t=re.sub(r'\{T(\d+)\}',lambda m:chr(0xE000+int(m.group(1))),t)
    t=re.sub(r'([А-Яа-я])\1{2,}',r'\1\1',t)
    t=re.sub(r'-([А-Я])',lambda m:'-'+m.group(1).lower(),t)
    return t
def plan_all():
    """returns per message: dict(lines per page, choice strings)"""
    plans={}
    for k,m in enumerate(msgs):
        t=msg2tr.get(k)
        if not m['ok'] or t is None: continue
        words=None
        pl={'pages':[rupairs.wrap(norm(p)) for p in t['pages']],'choice':None}
        if m['choice']:
            if m['choice']['kind']=='yn':
                pl['choice']=('yn',[o for o in t.get('options',[])])
            else:
                pl['choice']=('menu',t.get('options',[]))
        plans[k]=pl
    return plans
