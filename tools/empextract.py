import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,json,glob,os
S=_W+''
sys.path.insert(0,S+'/tools')
from uitab import W
from endec import code_text
def fields(e,j):
    n=len(e)//2; out=[]; i=0
    while i<n:
        if W(e,2*i)!=W(j,2*i):
            s=i
            while i<n and (W(e,2*i)!=W(j,2*i)): i+=1
            while i<n and W(e,2*i)==0xffff: i+=1
            # also absorb JP-equal ffff? done
            ws=[W(e,2*k) for k in range(s,i)]
            txt=[w for w in ws if w!=0xffff]
            out.append({'pos':2*s,'span':i-s,'tiles':txt,'en':''.join(code_text(w+0x212a) if w<1793 else '<%x>'%w for w in txt),
                        'prev':W(e,2*s-2) if s else None})
        else: i+=1
    return out
if __name__=='__main__':
    allf={}
    for p in sorted(glob.glob(S+'/ngcd/en/EMP_*.PRG')):
        f=os.path.basename(p)
        e=open(p,'rb').read(); j=open(S+'/ngcd/jp/'+f,'rb').read()
        allf[f]=fields(e,j)
    json.dump(allf,open(S+'/ru/ui/emp.json','w'),ensure_ascii=False)
    import collections
    spans=collections.Counter(); uniq=collections.Counter(); prev=collections.Counter()
    for f,fl in allf.items():
        for x in fl: spans[x['span']]+=1; uniq[x['en']]+=1; prev[x['prev']]+=1
    print('files',len(allf),'fields',sum(spans.values()),'uniq',len(uniq))
    print(sorted(spans.items()))
    print(prev.most_common(15))
    bad=[(f,x) for f,fl in allf.items() for x in fl if '<' in x['en']]
    print('bad',len(bad),bad[:5])
