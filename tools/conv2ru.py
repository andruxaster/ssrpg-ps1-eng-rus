import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,re
sys.path.insert(0,_W+'/tools')
import conv,enparse
from conv import toks,cells,wrap,W,NAME
def split_weighted(text,weights):
    if len(weights)==1: return [text]
    # candidate break points: sentence ends preferred
    words=text.split(' ')
    n=len(text); tw=sum(weights)
    bounds=[]; pos=0; cand=[]
    for k,wd in enumerate(words[:-1]):
        pos+=len(wd)+1
        sent= bool(re.search(r'[.!?)…]$',wd))
        cand.append((pos,k+1,sent))
    out=[];start=0;acc=0;used=0
    for wi in range(len(weights)-1):
        acc+=weights[wi]; target=acc/tw*n
        best=None
        for pos,k,sent in cand:
            if k<=used: continue
            cost=abs(pos-target)/(n or 1)-(0.12 if sent else 0)
            if best is None or cost<best[0]: best=(cost,k)
        if best is None: out.append(''); continue
        k=best[1]
        out.append(' '.join(words[used:k])); used=k
    out.append(' '.join(words[used:]))
    return out
def runs_ps1(pages):
    runs=[]
    for p in pages:
        port=[w for w in p['pre'] if w[0]==1]
        voice=any(w[0] in (0x0a,0x0e,0x10) for w in p['pre']+p['post']) or any(t[0][0] in (0x0a,0x0e,0x10) for _,t,k in p['mid'] if k=='ctl')
        key=port[-1] if port else (runs[-1]['key'] if runs and not port and runs[-1]['key'] is not None and False else None)
        if runs and not voice and not runs[-1]['voice'] and (not port or port[-1]==runs[-1]['key']) and runs[-1]['key'] is not None or (runs and not port and not voice and not runs[-1]['voice']):
            runs[-1]['pages'].append(p)
        else:
            runs.append(dict(key=port[-1] if port else None,pages=[p],voice=voice))
    return runs
def emit_run(run,txt,out):
    pages=run['pages']; first=pages[0]
    portrait=[w for w in first['pre'] if w[0]==1][-1:]
    # tokens: pre of first page; mids (ctl) + posts of all pages collected; names
    out+=first['pre']
    ctl=[]
    total=sum(max(1,p['n']) for p in pages) or 1; base=0
    for p in pages:
        for pos,tok,kind in p['mid']:
            if kind=='ctl': ctl.append(((base+pos)/total,tok))
        base+=max(1,p['n'])
    tailtok=[]
    for p in pages[1:]:
        tailtok+= [w for w in p['pre'] if w[0]!=1]
    for p in pages: tailtok+=p['post']
    lines=wrap(txt) if txt else []
    nl=len(lines)
    groups=[lines[k:k+2] for k in range(0,nl,2)] or [[]]
    for gi,g in enumerate(groups):
        if gi>0:
            out.append(b'\x03\0'); out+=portrait
        for li,l in enumerate(g):
            if li==1: out.append(b'\x02\0')
            lineidx=gi*2+li
            for (r,tok) in list(ctl):
                if r*nl<lineidx+0.5:
                    out+=tok; ctl.remove((r,tok))
            out+=cells(l)
    for r,tok in ctl: out+=tok
    out+=tailtok
    sep=pages[-1]['sep']
    return sep
ZEN=str.maketrans('０１２３４５６７８９','0123456789')
def fix_prices(raw,segs):
    try: jp=raw.decode('cp932','replace').translate(ZEN)
    except Exception: return segs
    nums=re.findall(r'金\s*(\d+)',jp)
    if not nums: return segs
    k=[0]
    def rep(m):
        if k[0]<len(nums):
            v=nums[k[0]]; k[0]+=1
            return (m.group(2) if m.group(1) is None else '')+v+' GP'
        return m.group(0)
    return [re.sub(r'(\{N\}|\d+)?(\s*)GP',rep,s) for s in segs]
def build(raw,en_words):
    segs,ench=enparse.parse(en_words); spk=enparse.parse.spk
    return build_core(raw,segs,spk,ench,None)
def build_text(raw,tr):
    pages,choice=conv.parse_ps1(raw)
    tp=[p for p in pages if p['n']>0 or any(k=='name' for _,_,k in p['mid'])]
    segs=[t.replace('{NAME}',NAME) for t in tr.get('pages',[])]
    spk=[]
    for p in tp:
        port=[w for w in p['pre'] if w[0]==1]
        spk.append(port[-1] if port else None)
    if len(spk)!=len(segs): spk=[None]*len(segs)
    # make consecutive pages of same/None portrait separate runs only if PS1 groups them; mimic runs_ps1 keys
    ench=None; q=None
    if choice is not None:
        ench=('yn',tr.get('options',[])); q=tr.get('question')
    return build_core(raw,segs,spk,ench,q,True)
def build_core(raw,segs,spk,ench,qover,pagewise=False):
    pages,choice=conv.parse_ps1(raw)
    segs=fix_prices(raw,segs)
    qtext=None;opts=None
    if choice is not None:
        if ench is None: return None
        ct=toks(b''.join(choice))
        nopt=sum(1 for w in ct if w==b'\x09\0')
        opts=ench[1]
        if len(opts)!=nopt or any(len(o)>W for o in opts): return None
        if ct[0]==b'\x07\0':
            q=None
            if segs and not qover:
                sents=re.split(r'(?<=[?.!])\s+',segs[-1])
                if len(sents[-1])<=W and sents[-1].endswith('?'):
                    q=sents[-1]; rest=' '.join(sents[:-1]).strip()
                    segs=segs[:-1]+([rest] if rest else []); spk=spk[:len(segs)]
            qtext=(q[0].upper()+q[1:]) if q else ('Да или нет?' if nopt==2 else 'Выберите.')
            if qover: qtext=qover
    runs=runs_ps1(pages)
    textruns=[r for r in runs if any(p['n'] for p in r['pages']) or any(k=='name' for p in r['pages'] for _,_,k in p['mid'])]
    if not textruns and segs: textruns=runs[:1]
    # EN runs by speaker
    enruns=[]
    for s,k in zip(segs,spk):
        if enruns and enruns[-1][0]==k and k is not None: enruns[-1][1].append(s)
        else: enruns.append([k,[s]])
    entexts=[' '.join(x[1]) for x in enruns]
    istext=lambda p: p['n']>0 or any(k=='name' for _,_,k in p['mid'])
    ntp=sum(1 for r in textruns for p in r['pages'] if istext(p))
    if pagewise and textruns and ntp==len(segs):
        parts=[];c=0
        for r in textruns:
            m=sum(1 for p in r['pages'] if istext(p)); parts.append(' '.join(segs[c:c+m])); c+=m
    elif textruns:
        if len(entexts)==len(textruns): parts=entexts
        else: parts=split_weighted(' '.join(entexts),[sum(max(1,p['n']) for p in r['pages']) for r in textruns])
    else: parts=[]
    assign={id(r):parts[k] for k,r in enumerate(textruns)}
    out=[]
    for r in runs:
        sep=emit_run(r,assign.get(id(r),''),out)
        if sep is not None: out.append(sep)
    if choice is not None:
        ct=toks(b''.join(choice)); out.append(ct[0])
        if ct[0]==b'\x07\0': out+=cells(qtext)
        for o in opts:
            out.append(b'\x09\0'); out+=cells(o)
    out.append(b'\0\0')
    return out
def show(items):
    s=''
    for it in items:
        if isinstance(it,tuple): s+= it[1] if it[0]=='pair' else ('_' if it[0]=='raw' else '{NAME}')
        else: s+='<%02x%02x>'%(it[0],it[1])
    return s
