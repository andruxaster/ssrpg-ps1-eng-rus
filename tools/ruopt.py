import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,collections,pickle,json
sys.path.insert(0,_W+'/tools')
import rubuild,rupairs
def optimize(lines,budget,iters=5,verbose=True):
    naive=collections.Counter()
    for l in lines:
        s=l.replace(rupairs.NAME,'  ')
        if len(s)%2: s+=' '
        for i in range(0,len(s),2):
            p=s[i:i+2]
            if rubuild.needs_new(p): naive[p]+=1
    P=set(p for p,_ in naive.most_common(budget))
    for it in range(iters):
        use=collections.Counter(); forced=collections.Counter(); bad=0
        def cost(p):
            if not rubuild.needs_new(p) or p in P: return 0
            return 1000
        res=[]
        for l in lines:
            c,cells=rupairs.encode_line(l,cost)
            res.append(cells)
            for x in cells:
                if x[0]=='pair' and rubuild.needs_new(x[1]):
                    use[x[1]]+=1
                    if x[1] not in P: forced[x[1]]+=1
            if c>=1000: bad+=1
        allp=set(use)
        if verbose: print('iter',it,'P',len(P),'used',len(allp),'forced',len(forced),'lines with forced',bad, list(forced)[:5] if len(forced)<5 else '')
        optimize.last_forced=forced
        if len(allp)<=budget: return allp,res
        # keep most used, include forced weighted
        score=collections.Counter(use)
        for p,c in forced.items(): score[p]+=c
        P=set(p for p,_ in score.most_common(budget))
    # final squeeze: ban least-used pairs until it fits
    banned=set()
    for rnd in range(60):
        use=collections.Counter(); res=[]
        def cost(p):
            if not rubuild.needs_new(p): return 0
            if p in banned: return 10**6
            return 0 if p in P else 1000
        for l in lines:
            c,cells=rupairs.encode_line(l,cost); res.append(cells)
            for x in cells:
                if x[0]=='pair' and rubuild.needs_new(x[1]): use[x[1]]+=1
        if verbose: print('squeeze',rnd,'used',len(use),'banned',len(banned))
        if len(use)<=budget: return set(use),res
        P=set(use)
        for p,cnt in sorted(use.items(),key=lambda x:x[1])[:len(use)-budget]:
            banned.add(p)
    return set(use),res
if __name__=='__main__':
    lines=rubuild.all_lines()
    B=len(rubuild.FREE)+len(rubuild.EXT)
    print('lines',len(lines),'budget',B,'existing reusable',len(rubuild.existing))
    P,res=optimize(lines,B)
    print('final pairs',len(P))
