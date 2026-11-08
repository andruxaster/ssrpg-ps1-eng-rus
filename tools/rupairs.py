import textwrap,collections,math
NAMEW=10
NAME='\x01'
def wrap(text,W=31):
    t=text.replace('{NAME}',NAME*NAMEW)
    lines=textwrap.wrap(t,W,break_long_words=True,break_on_hyphens=False)
    out=[]
    for l in lines:
        # collapse name run back
        while NAME*NAMEW in l: l=l.replace(NAME*NAMEW,'\x02',1)
        l=l.replace(NAME,'')
        out.append(l.replace('\x02',NAME))
    return out or ['']
def width(cells):
    w=0
    for c in cells: w+= NAMEW if c==('name',) else 2
    return w
def encode_line(line,cost,W=32):
    """DP: returns (total_cost, cells) ; cells = list of ('pair',s) or ('name',)
    cost(pair)-> penalty. Options: double a space; one leading space."""
    INF=10**12
    n=len(line)
    # state: (pos, pending char or None, width_used) -> (cost, back)
    from functools import lru_cache
    import sys
    sys.setrecursionlimit(10000)
    best={}
    def go(i,pend,w):
        key=(i,pend,w)
        if key in best: return best[key]
        if w>W: return (INF,None)
        if i==n:
            if pend is None: r=(0,[])
            else:
                c=cost(pend+' '); r=(c,[('pair',pend+' ')]) if w+2<=W else (INF,None)
            best[key]=r; return r
        ch=line[i]
        res=(INF,None)
        if ch==NAME:
            if w+NAMEW>W: best[key]=(INF,None); return best[key]
            if pend is None:
                c,rest=go(i+1,None,w+NAMEW); res=(c,[('name',)]+rest) if rest is not None else (INF,None)
            else:
                c0=cost(pend+' '); c,rest=go(i+1,None,w+2+NAMEW)
                if rest is not None: res=(c0+c,[('pair',pend+' '),('name',)]+rest)
            best[key]=res; return res
        opts=[ch] if ch!=' ' else [' ','  ']
        if i==0 and pend is None and ch!=' ': opts=[ch,' '+ch]
        for o in opts:
            extra=(len(o)-1)*(1 if ch==' ' else 3)
            p=pend; cells=[]; cc=extra; ww=w
            for c2 in o:
                if p is None: p=c2
                else:
                    pr=p+c2; cc+=cost(pr); cells.append(('pair',pr)); p=None; ww+=2
            c,rest=go(i+1,p,ww)
            if rest is None or c>=INF: continue
            if cc+c<res[0]: res=(cc+c,cells+rest)
        best[key]=res; return res
    r=go(0,None,0)
    # strip trailing blank pair
    cells=r[1] or []
    while cells and cells[-1]==('pair','  '): cells=cells[:-1]
    return r[0],cells
