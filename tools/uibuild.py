import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,json,re,pickle,struct,os
S=_W+''
sys.path.insert(0,S+'/tools')
from uiunits import TOK
from uitab import W
import uiextract
OUT=S+'/ru/build'
BASE=0x212a
p2t=pickle.load(open(OUT+'/pair2tile.pkl','rb'))
res=json.load(open(S+'/ru/ui/resolved.json'))
def enc(parts,raw=False):
    out=[]
    for p in parts:
        m=re.fullmatch(r'\{T(\d+)\}',p)
        if m: out.append(int(m.group(1))+(0 if raw else BASE)); continue
        m=re.fullmatch(r'<([0-9a-f]+)>',p)
        if m: out.append(int(m.group(1),16)); continue
        if p=='\n': out.append(0); continue
        s=p if len(p)%2==0 else p+' '
        for i in range(0,len(s),2):
            out.append(p2t[s[i:i+2]]+(0 if raw else BASE))
    return out
prog=bytearray(open(S+'/ngcd/en/PROG.PRG','rb').read())
t=json.load(open(S+'/ru/ui/prog_tables.json'))
def table_bytes(tab):
    T=t[tab]; n=T['n']
    msgs=[enc(res['prog']['%s:%d'%(tab,i)])+[0xffff] for i in range(n)]
    offs=[];body=[];seen={}
    for m in msgs:
        k=tuple(m)
        if k not in seen: seen[k]=2*len(body); body+=m
        offs.append(seen[k])
    words=[2+2*n]+offs+body
    assert max(offs)<0x10000
    return b''.join(struct.pack('>H',w) for w in words)
# all refs to table headers
def refs_to(a):
    p=struct.pack('>I',a); r=[]
    for i in range(0,len(prog)-3,2):
        if prog[i:i+4]==p: r.append(i)
    return r
POOLS=[(0x60d62,0x64696,['names','msgs','items','shops','idesc','places']),(0x71d82,0x73acc,['keyitems'])]
FIXED={'menu1':(0x207f0,0x20b2e),'menu2':(0x59f00,None)}
i=0x5a6a0
while prog[i]==0xff: i+=1
FIXED['menu2']=(0x59f00,i&~1)
blobs={k:table_bytes(k) for k in uiextract.TABLES}
report=[]
for k,(a,cap) in FIXED.items():
    b=blobs[k]; assert a+len(b)<=cap,(k,len(b),cap-a)
    prog[a:a+len(b)]=b; report.append((k,len(b),cap-a))
oldrefs={k:refs_to(uiextract.TABLES[k]) for p in POOLS for k in p[2]}
for lo,hi,tabs in POOLS:
    a=lo; used=0
    for k in tabs:
        b=blobs[k]
        for r in oldrefs[k]:
            op=W(prog,r-2); assert op in (0x41f9,0x43f9,0x45f9,0x47f9,0x49f9,0x4bf9,0x4df9),(k,hex(r),hex(op))
            prog[r:r+4]=struct.pack('>I',a)
        prog[a:a+len(b)]=b; a+=len(b)
        if a%2: a+=1
    assert a<=hi,('pool overflow',hex(lo),a-hi)
    if lo==0x60d62: pool1_end=a
    prog[a:hi]=b'\xff'*(hi-a)
    report.append(('pool %x'%lo,a-lo,hi-lo))
# ---- battle tables (raw tile strings with (offset,len) tables)
def btab_bytes(T,base,lists):
    n=len(lists); body=[]; seen={}; ents=[]
    for ws in lists:
        k=tuple(ws)
        if k not in seen: seen[k]=len(body); body+=ws
        ents.append((seen[k],len(ws)))
    tbl=struct.pack('>h',base-T)+b''.join(struct.pack('>HH',o,l) for o,l in ents)
    return tbl,b''.join(struct.pack('>H',w) for w in body)
BT_INPLACE={'A':(0x5045a,0x4ff50,0x5045a),'B':(0x50884,0x505e8,0x50884),'C':(0x7b540,0x7b400,0x7b540)}
extra_at=pool1_end
for tab,(T,b0,b1) in BT_INPLACE.items():
    lists=[enc(ps,raw=True) for ps in res['battle'][tab]]
    n=len(lists)
    tbl,body=btab_bytes(T,b0,lists)
    if b0+len(body)<=b1:
        prog[T:T+len(tbl)]=tbl; prog[b0:b0+len(body)]=body
        report.append(('battle '+tab,'inplace',len(body),b1-b0))
    else:
        NT=extra_at; nb=NT+2+4*n
        tbl,body=btab_bytes(NT,nb,lists)
        assert nb+len(body)<=0x64696,('pool1 overflow for battle',tab)
        prog[NT:NT+len(tbl)]=tbl; prog[nb:nb+len(body)]=body
        extra_at=nb+len(body)
        rf=refs_to(T)
        for r in rf:
            op=W(prog,r-2); assert op in (0x41f9,0x43f9,0x45f9,0x47f9,0x49f9,0x4bf9,0x4df9),(tab,hex(r),hex(op))
            prog[r:r+4]=struct.pack('>I',NT)
        report.append(('battle '+tab,'moved',hex(NT),len(body),len(rf),'refs'))
for pos,span,ps in res['hero']:
    w=enc(ps,raw=True); assert len(w)<=span,(hex(pos),ps)
    w+=[0xffff]*(span-len(w))
    prog[pos:pos+2*span]=b''.join(struct.pack('>H',v) for v in w)
print(report[-4:])
assert len(prog)==0x7b800
open(OUT+'/PROG.PRG','wb').write(prog)
print(report)
# EMP
emp=json.load(open(S+'/ru/ui/emp.json')); n=0
for f,fl in emp.items():
    d=bytearray(open(S+'/ngcd/en/'+f,'rb').read())
    for x in fl:
        w=enc(res['emp']['%s:%d'%(f,x['pos'])],raw=True)
        assert len(w)<=x['span'],(f,x,w)
        w+= [0xffff]*(x['span']-len(w))
        d[x['pos']:x['pos']+2*x['span']]=b''.join(struct.pack('>H',v) for v in w)
    open(OUT+'/'+f,'wb').write(d); n+=1
print('emp files',n)
