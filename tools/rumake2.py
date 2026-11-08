import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,json,glob,collections,pickle,struct,re,os
sys.path.insert(0,_W+'/tools')
import rubuild,rupairs,ruflow,ngmsg,ngtok,rufont,endec
from rubuild import msgs,BASE,NT
S=rubuild.S
OUT=S+'/ru/build'; os.makedirs(OUT,exist_ok=True)
plans=rubuild.plan_all()
files=sorted(glob.glob(S+'/ngcd/en/MSGD*.PRG'))
enw={};k=0
for f in files:
    for idx,(o,w) in enumerate(ngmsg.messages(f)): enw[k]=w; k+=1
flows={}
for k,pl in plans.items():
    t=rubuild.msg2tr[k]
    pages,ch=ngtok.structure(enw[k])
    ru=[rubuild.norm(p) for p in t['pages']]
    toks=ruflow.flow_tokens(pages,ru)
    lines,breaks=ruflow.wrap_flow(toks)
    flows[k]=(lines,breaks,ch)
# choice strings
chstr={}; strict=[]
for k,pl in plans.items():
    if not pl['choice']: continue
    ch=flows[k][2]
    if pl['choice'][0]=='yn': chstr[k]=('dp',pl['choice'][1])
    else:
        ss=rubuild.menu_rows_ru(ch['opts'],pl['choice'][1]); chstr[k]=('strict',ss); strict+=ss
strict_pairs=set(c[1] for s in strict for c in rubuild.strict_cells(s) if rubuild.needs_new(c[1]))
if os.environ.get('RUUI'):
    for seg in json.load(open(S+'/ru/ui/strict_segments.json')):
        for i in range(0,len(seg),2):
            if rubuild.needs_new(seg[i:i+2]): strict_pairs.add(seg[i:i+2])
    print('strict pairs incl UI',len(strict_pairs))
units=[parts for (lines,b,ch) in flows.values() for parts in lines]
units+=[[('w',o)] for v in chstr.values() if v[0]=='dp' for o in v[1]]
BUD=len(rubuild.FREE)+len(rubuild.EXT)-len(strict_pairs)
need=lambda p: rubuild.needs_new(p) and p not in strict_pairs
def run(P,banned):
    use=collections.Counter(); bad=0
    def cost(p):
        if not need(p): return 0
        if p in banned: return 10**6
        return 0 if p in P else 1000
    for u in units:
        c,cells=ruflow.encode_flow_line(u,cost)
        if cells is None: bad+=1; continue
        for x in cells:
            if x[0]=='pair' and need(x[1]): use[x[1]]+=1
    return use,bad
naive=collections.Counter()
for u in units:
    s=re.sub('[\ue000-\uf8ff]','  ',' '.join(v for kk,v in u if kk=='w').replace(rupairs.NAME,'  '))
    if len(s)%2: s+=' '
    for i in range(0,len(s),2):
        if need(s[i:i+2]): naive[s[i:i+2]]+=1
P=set(p for p,_ in naive.most_common(BUD)); banned=set()
for it in range(40):
    use,bad=run(P,banned)
    print('iter',it,'used',len(use),'budget',BUD,'unencodable',bad)
    if len(use)<=BUD and bad==0: break
    if it<3: P=set(p for p,_ in use.most_common(BUD))
    else:
        P=set(use)
        for p,c in sorted(use.items(),key=lambda x:x[1])[:len(use)-BUD]: banned.add(p)
allnew=sorted(set(use)|strict_pairs)
assert len(allnew)<=len(rubuild.FREE)+len(rubuild.EXT)
slots=rubuild.FREE+rubuild.EXT
pair2tile=dict(rubuild.existing)
for p,t in zip(allnew,slots): pair2tile[p]=t
cost=lambda p: 0 if p in pair2tile else 10**6
spr=bytearray(open(S+'/ngcd/en/CHIP000F.SPR','rb').read())
maxt=max(pair2tile[p] for p in allnew)
if maxt>=NT: spr+=bytes(128*(maxt+1-NT))
for p in allnew:
    t=pair2tile[p]; spr[t*128:(t+1)*128]=rufont.encode_tile(rufont.tile_pixels(p))
open(OUT+'/CHIP000F.SPR','wb').write(spr)
def cw(cells):
    out=[]
    for c in cells:
        if c[0]=='m': out+=c[1]
        elif c==('name',): out.append(4)
        elif c[0]=='tile': out.append(BASE+c[1])
        else: out.append(BASE+pair2tile[c[1]])
    return out
def build_msg(k):
    lines,breaks,ch=flows[k]
    out=[]
    for li,parts in enumerate(lines):
        if li>0 and breaks[li-1]=='nl': out.append(0)
        c,cells=ruflow.encode_flow_line(parts,cost)
        assert cells is not None and c<10**6,(k,parts)
        out+=cw(cells)
    if ch:
        out.append(2 if ch['kind']=='yn' else 0xa)
        kind,ss=chstr[k]
        for s in ss:
            if kind=='dp':
                c,cells=ruflow.encode_flow_line([('w',s)],cost); assert c<10**6
                out+=cw(cells)
            else: out+=cw(rubuild.strict_cells(s))
            out.append(3)
        for cc in ch['codes']: out+=cc
    out.append(0xffff)
    return out
sizes=[]
for f in files:
    name=f.split('/')[-1]
    ks=[k for k,m in enumerate(msgs) if m['file']==name]
    data=[build_msg(k) if k in plans else enw[k] for k in ks]
    words=[2*(len(ks)+1)]; off=0; body=[]
    for m in data: words.append(off); body+=m; off+=2*len(m)
    assert off<0x10000
    b=b''.join(struct.pack('>H',x) for x in words+body)
    open(OUT+'/'+name,'wb').write(b); sizes.append((len(b),name))
print('new pairs',len(allnew),'max msgd',max(sizes))
pickle.dump(pair2tile,open(OUT+'/pair2tile.pkl','wb'))
