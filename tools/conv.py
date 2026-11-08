import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,re,textwrap
sys.path.insert(0,_W+'/tools')
import enparse
NAME=enparse.NAME
W=32          # chars per line
NAMEW=10      # width reserved for inserted name
def toks(raw): return [raw[i:i+2] for i in range(0,len(raw),2)]
def ischar(w): return w[0]>=0x81
def parse_ps1(raw):
    """returns pages, choice. page = dict(pre,mid,post,sep,nchars)"""
    t=toks(raw); i=0
    pages=[]; page=dict(pre=[],mid=[],post=[],sep=None,n=0,text='')
    choice=None
    while i<len(t):
        w=t[i]
        if w==b'\0\0': break
        if w in (b'\x07\0',b'\x08\0'):
            choice=t[i:]; break
        if ischar(w):
            page['n']+=1; page['text']+=w.decode('cp932','replace'); i+=1; continue
        if w in (b'\x03\0',b'\x0f\0',b'\x04\0'):
            page['sep']=w; pages.append(page); page=dict(pre=[],mid=[],post=[],sep=None,n=0,text=''); i+=1; continue
        tok=[w]
        if w==b'\x0a\0' and i+1<len(t): tok=[w,t[i+1]]; i+=1
        i+=1
        if w==b'\x02\0': page['text']+='\n'; continue
        if w[0]==5: continue          # drop typing waits
        if w==b'\x06\0':
            page['mid'].append((page['n'],tok,'name')); page['text']+=NAME; continue
        if page['n']==0: page['pre']+=tok
        else: page['mid'].append((page['n'],tok,'ctl'))
    if page['n'] or page['pre'] or page['mid'] or not pages: pages.append(page)
    # move trailing ctl (no text after) to post
    for p in pages:
        while p['mid'] and p['mid'][-1][0]==p['n'] and p['mid'][-1][2]=='ctl':
            p['post']=p['mid'].pop()[1]+p['post']
    return pages,choice
def split_text_over(segs_text,weights):
    """distribute EN text (string) over len(weights) parts by word boundaries"""
    words=segs_text.split(' ')
    total=sum(len(x)+1 for x in words); tw=sum(weights) or 1
    out=[];cur=[];acc=0;k=0;target=weights[0]/tw*total
    for wd in words:
        if k<len(weights)-1 and acc+len(wd)/2>target and cur:
            out.append(' '.join(cur)); cur=[]; k+=1; target+=weights[k]/tw*total
        cur.append(wd); acc+=len(wd)+1
    out.append(' '.join(cur))
    while len(out)<len(weights): out.append('')
    return out
def wrap(text):
    # name placeholder counts NAMEW wide
    t=text.replace(NAME,'\x03'*NAMEW)
    lines=textwrap.wrap(t,W,break_long_words=True,break_on_hyphens=False)
    out=[]
    for l in lines:
        l=re.sub('\x03{%d}'%NAMEW,NAME,l)
        l=l.replace('\x03','')
        out.append(l)
    return out or ['']
def cells(line):
    """line -> list of ('pair',str2) / ('name',)"""
    out=[];pend=''
    for ch in line:
        if ch==NAME:
            if pend==' ': out.append(('raw',b'\x81\x40')); pend=''
            elif pend: out.append(('pair',pend+' ')); pend=''
            elif out and out[-1]==('pair','  '): out[-1]=('raw',b'\x81\x40')
            out.append(('name',)); continue
        pend+=ch
        if len(pend)==2: out.append(('pair',pend)); pend=''
    if pend: out.append(('pair',pend+' '))
    # strip trailing blank pairs
    while out and out[-1]==('pair','  '): out.pop()
    return out
def build(pages,choice,en_segs,en_choice):
    """returns list of items: bytes tokens or ('pair',s) / ('name',) ; None if impossible"""
    P=[p for p in pages]
    # choice handling
    qtext=None; opts=None
    if choice is not None:
        if en_choice is None: return None
        ct=toks(b''.join(choice))
        nopt=sum(1 for w in ct if w==b'\x09\0')
        opts=en_choice[1]
        if len(opts)!=nopt: return None
        if ct[0]==b'\x07\0':
            # question = last sentence of EN text if short
            if en_segs:
                last=en_segs[-1]
                sents=re.split(r'(?<=[?.!])\s+',last)
                q=sents[-1]
                if len(q)<=W and q.endswith('?'):
                    qtext=q; rest=' '.join(sents[:-1]).strip()
                    en_segs=en_segs[:-1]+([rest] if rest else [])
                else:
                    qtext='Yes or no?' if len(opts)==2 else 'Choose.'
            else: qtext='Choose.'
    # map EN text onto PS1 pages
    textpages=[p for p in P if p['n']>0 or any(m[2]=='name' for m in p['mid'])]
    if not textpages and en_segs:
        textpages=P[:1]
    entxt=' '.join(en_segs).strip()
    if textpages:
        if len(en_segs)==len(textpages): parts=en_segs
        else: parts=split_text_over(entxt,[max(1,p['n']) for p in textpages])
    else: parts=[]
    assign={id(p):parts[k] for k,p in enumerate(textpages)}
    out=[]
    for pi,p in enumerate(P):
        txt=assign.get(id(p),'')
        out+= [p['pre'][k:k+1][0] for k in range(len(p['pre']))]
        portrait=[w for w in p['pre'] if w[0]==1][-1:]  # repeat on continuation
        lines=wrap(txt) if txt else []
        # mid ctl tokens: proportional placement by line index
        ctl=[(pos/(p['n'] or 1),tok) for pos,tok,kind in p['mid'] if kind=='ctl']
        nl=len(lines)
        groups=[lines[k:k+2] for k in range(0,nl,2)] or [[]]
        for gi,g in enumerate(groups):
            if gi>0:
                out.append(b'\x03\0'); out+=portrait
            for li,l in enumerate(g):
                if li==1: out.append(b'\x02\0')
                lineidx=gi*2+li
                for c in cells(l): out.append(c)
                # ctl tokens whose relative position falls in this line
                for (r,tok) in list(ctl):
                    if r*nl <= lineidx+1 or lineidx==nl-1:
                        out+=tok; ctl.remove((r,tok))
        for (r,tok) in ctl: out+=tok
        out+=p['post']
        if p['sep'] is not None: out.append(p['sep'])
    if choice is not None:
        ct=toks(b''.join(choice))
        out.append(ct[0])
        if ct[0]==b'\x07\0':
            for c in cells(qtext): out.append(c)
        for o in opts:
            out.append(b'\x09\0')
            for c in cells(o[:W]): out.append(c)
    out.append(b'\0\0')
    return out
