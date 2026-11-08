import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
# flow-based emission of a Russian message using EN control-code skeleton
import sys,re
sys.path.insert(0,_W+'/tools')
import ngtok,rupairs
NAME=rupairs.NAME; NAMEW=rupairs.NAMEW
W=31
def page_inline(p):
    pos=0; inl=[]; endnl=False
    for kind,val in p['items']:
        if kind=='t': pos+=1
        elif kind=='c':
            if val in ([0],[4]): continue
            inl.append((pos,val))
    # did page end with explicit newline (last code(s) after text are [0])?
    tail=[]
    for kind,val in reversed(p['items']):
        if kind=='t' or kind=='ws': break
        tail.append(val)
    endnl=[0] in tail
    return max(1,pos),inl,endnl
def flow_tokens(pages,ru_pages):
    toks=[]
    for pi,p in enumerate(pages):
        txt=ru_pages[pi] if pi<len(ru_pages) else ''
        txt=txt.replace('{NAME}',NAME)
        entot,inl,endnl=page_inline(p)
        pre=p['pre']
        nums=[c for c in pre if c[0]==5]+[c for pos,c in inl if c[0]==5]
        if '{N}' in txt: pre=[c for c in pre if c[0]!=5]
        if pre: toks.append(('m',[x for c in pre for x in c]))
        if '{N}' in txt:
            assert txt.count('{N}')==len(nums),(txt,nums)
            for q,c in enumerate(nums): txt=txt.replace('{N}',chr(0xF800+c[1]),1)
            inl=[(pos,c) for pos,c in inl if c[0]!=5]
        words=txt.split()
        # positions of word starts in chars
        total=max(1,len(' '.join(words)))
        starts=[];c=0
        for w_ in words: starts.append(c); c+=len(w_)+1
        # assign inline codes to word index (insert before word j) or end
        slots={}
        for pos,codes in inl:
            if pos>=entot: j=len(words)
            else:
                target=pos/entot*total
                j=min(range(len(words)+1),key=lambda q:abs((starts[q] if q<len(words) else total)-target)) if words else 0
            slots.setdefault(j,[]).extend(codes)
        for j,w_ in enumerate(words):
            if j in slots: toks.append(('m',slots[j]))
            toks.append(('w',w_))
        end=slots.get(len(words),[])
        if end:
            toks.append(('m',end))
        if 8 in end and end[-1]==8: toks.append(('box',))
        elif endnl: toks.append(('nl',))
    return toks
def wrap_flow(toks):
    lines=[[]]; cur=0; breaks=[]
    def wl(w_): return sum(NAMEW if ch==NAME else (8 if ord(ch)>=0xF800 else (2 if ord(ch)>=0xE000 else 1)) for ch in w_)
    for t in toks:
        if t[0] in ('nl','box'):
            if lines[-1] or t[0]=='box':
                breaks.append(t[0]); lines.append([]); cur=0
            continue
        if t[0]=='m': lines[-1].append(t); continue
        L=wl(t[1]); need=L+(1 if cur>0 else 0)
        if cur>0 and cur+need>W:
            breaks.append('nl'); lines.append([]); cur=0; need=L
        lines[-1].append(t); cur+=need
    return lines,breaks
def encode_flow_line(parts,cost):
    """parts: list of ('w',word)/('m',codes). DP with optional doubled spaces between words."""
    INF=10**12
    n=len(parts)
    memo={}
    def go(i,pend,w,first):
        key=(i,pend,w,first)
        if key in memo: return memo[key]
        if w>32: return (INF,None)
        if i==n:
            if pend is None: r=(0,[])
            else:
                r=(cost(pend+' '),[('pair',pend+' ')]) if w+2<=32 else (INF,None)
            memo[key]=r; return r
        kind,val=parts[i]
        best=(INF,None)
        if kind=='m':
            if pend is None:
                c,rest=go(i+1,None,w,first)
                if rest is not None: best=(c,[('m',val)]+rest)
            else:
                c0=cost(pend+' '); c,rest=go(i+1,None,w+2,True)
                if rest is not None: best=(c0+c,[('pair',pend+' '),('m',val)]+rest)
            memo[key]=best; return best
        word=val
        # separator before word
        seps=['',' ']
        if not first: seps=[' ','  ']
        # if previous emitted pair consumed the space (after marker flush) we still put a space
        for sep in seps:
            extra=(0 if sep=='' else 2) if first else (0 if sep==' ' else 1)
            s=sep+word
            p=pend; cells=[]; cc=extra; ww=w; ok=True
            for ch in s:
                if ch==NAME or ord(ch)>=0xE000:
                    if p is not None: cc+=cost(p+' '); cells.append(('pair',p+' ')); p=None; ww+=2
                    if ch==NAME: cells.append(('name',)); ww+=NAMEW
                    elif ord(ch)>=0xF800: cells.append(('m',[5,ord(ch)-0xF800])); ww+=8
                    else: cells.append(('tile',ord(ch)-0xE000)); ww+=2
                    continue
                if p is None: p=ch
                else: cc+=cost(p+ch); cells.append(('pair',p+ch)); p=None; ww+=2
            c,rest=go(i+1,p,ww,False)
            if rest is None or c>=INF: continue
            if cc+c<best[0]: best=(cc+c,cells+rest)
        memo[key]=best; return best
    r=go(0,None,0,True)
    return r
def line_strings(lines):
    out=[]
    for parts in lines:
        out.append(' '.join(v for k,v in parts if k=='w'))
    return out
