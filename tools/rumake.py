import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,json,glob,collections,pickle,struct,re,os
sys.path.insert(0,_W+'/tools')
import rubuild,ruopt,rupairs,ngmsg,ngtok,rufont,endec
from rubuild import msgs,BASE,NT
S=rubuild.S
OUT=S+'/ru/build'; os.makedirs(OUT,exist_ok=True)
plans=rubuild.plan_all()
# EN structures per message
files=sorted(glob.glob(S+'/ngcd/en/MSGD*.PRG'))
enw={}
k=0
for f in files:
    for idx,(o,w) in enumerate(ngmsg.messages(f)):
        assert msgs[k]['file']==f.split('/')[-1] and msgs[k]['idx']==idx
        enw[k]=w; k+=1
# strict strings
strict=[]
chstr={}
for k,pl in plans.items():
    if not pl['choice']: continue
    pages,ch=ngtok.structure(enw[k])
    if pl['choice'][0]=='yn':
        chstr[k]=('dp',pl['choice'][1])
    else:
        ss=rubuild.menu_rows_ru(ch['opts'],pl['choice'][1])
        chstr[k]=('strict',ss); strict+=ss
strict_pairs=set()
for s in strict:
    for c in rubuild.strict_cells(s):
        if rubuild.needs_new(c[1]): strict_pairs.add(c[1])
lines=[l for pl in plans.values() for pg in pl['pages'] for l in pg]+[o for v in chstr.values() if v[0]=='dp' for o in v[1]]
B=len(rubuild.FREE)+len(rubuild.EXT)-len(strict_pairs)
print('lines',len(lines),'strict new pairs',len(strict_pairs),'budget for text',B)
orig_needs=rubuild.needs_new
rubuild.needs_new=lambda p: orig_needs(p) and p not in strict_pairs
P,res=ruopt.optimize(lines,B)
rubuild.needs_new=orig_needs
allnew=sorted(P|strict_pairs)
assert len(allnew)<=len(rubuild.FREE)+len(rubuild.EXT), len(allnew)
slots=rubuild.FREE+rubuild.EXT
pair2tile=dict(rubuild.existing)
for p,t in zip(allnew,slots): pair2tile[p]=t
cost=lambda p: 0 if p in pair2tile else 10**6
# ---- font file
spr=bytearray(open(S+'/ngcd/en/CHIP000F.SPR','rb').read())
maxt=max(pair2tile[p] for p in allnew)
if maxt>=NT: spr+=bytes(128*(maxt+1-NT))
blank=bytes(spr[1*128:2*128])
for p in allnew:
    t=pair2tile[p]
    spr[t*128:(t+1)*128]=rufont.encode_tile(rufont.tile_pixels(p))
open(OUT+'/CHIP000F.SPR','wb').write(spr)
print('font tiles',len(spr)//128,'new pairs',len(allnew))
# ---- messages
def cells_to_words(cells):
    out=[]
    for c in cells:
        if c==('name',): out.append(4)
        else: out.append(BASE+pair2tile[c[1]])
    return out
def build_msg(k):
    pl=plans[k]; w=enw[k]
    pages,ch=ngtok.structure(w)
    if len(pages)!=len(pl['pages']):
        # page structure mismatch (pages without text?) -> align only text pages
        pass
    out=[]
    tp=[p for p in pages]
    for pi,p in enumerate(tp):
        out+=[x for c in p['pre'] for x in c]
        rulines=pl['pages'][pi] if pi<len(pl['pages']) else []
        # EN inline codes with positions
        pos=0; inl=[]
        for kind,val in p['items']:
            if kind=='t': pos+=1
            elif kind=='c':
                if val in ([0],[4]): continue
                inl.append((pos,val))
        entot=max(1,pos)
        cl=[]
        for li,l in enumerate(rulines):
            c,cells=rupairs.encode_line(l,cost)
            assert c<10**6,(k,l)
            cl.append(cells)
        T=sum(len(c) for c in cl)
        # emit with inline codes
        emitted=0; ii=0
        inl.sort(key=lambda x:x[0])
        def flush(upto):
            nonlocal ii
            while ii<len(inl) and (inl[ii][0]>=entot and upto>=T or inl[ii][0]<entot and round(inl[ii][0]/entot*T)<=upto):
                out.extend(inl[ii][1]); ii+=1
        flush(0)
        for li,cells in enumerate(cl):
            if li>0: out.append(0)
            for c in cells:
                out+=cells_to_words([c]); emitted+=1
                flush(emitted)
        flush(T)
        while ii<len(inl): out.extend(inl[ii][1]); ii+=1
    if ch:
        if ch['kind']=='yn': out.append(2)
        else: out.append(0xa)
        kind,ss=chstr[k]
        for s in ss:
            if kind=='dp':
                c,cells=rupairs.encode_line(s,cost); assert c<10**6
                out+=cells_to_words(cells)
            else: out+=cells_to_words(rubuild.strict_cells(s))
            out.append(3)
    out.append(0xffff)
    return out
newfiles={}
sizes=[]
for f in files:
    name=f.split('/')[-1]
    ks=[k for k,m in enumerate(msgs) if m['file']==name]
    data=[]
    for k in ks:
        data.append(build_msg(k) if k in plans else enw[k])
    n=len(ks); tblbytes=2*(n+1)
    words=[tblbytes]; off=0; body=[]
    for m in data:
        words.append(off); body+=m; off+=2*len(m)
    assert off<0x10000,(name,off)
    words+=body
    b=b''.join(struct.pack('>H',x) for x in words)
    newfiles[name]=b
    sizes.append((len(b),os.path.getsize(f),name))
    open(OUT+'/'+name,'wb').write(b)
sizes.sort(reverse=True)
print('largest new',sizes[:3],'largest EN',max(os.path.getsize(f) for f in files))
pickle.dump(pair2tile,open(OUT+'/pair2tile.pkl','wb'))
