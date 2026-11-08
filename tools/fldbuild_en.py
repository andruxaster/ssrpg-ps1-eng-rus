import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,pickle,struct,collections
sys.path.insert(0,_W+'/tools')
import ps1all,ps1msg,encode
S=encode.S
NG,PS=pickle.load(open(S+'/out/db.pkl','rb'))
conv=pickle.load(open(S+'/out/converted.pkl','rb'))
import os
pmap=pickle.load(open(S+'/out/pmap_final.pkl','rb')) if os.path.exists(S+'/out/pmap_final.pkl') and os.environ.get('FINAL') else pickle.load(open(S+'/out/pmap.pkl','rb'))
key2i={(m['file'],m['scene'],m['chunk'],m['k']):i for i,m in enumerate(PS)}
LIMITS={0:0x5c00,1:0x400,2:0x2e4}
REVERTED=[]
def rebuild_chunk(fn,sidx,j,ch,ctype=0xa):
    n,offs,msgs=ps1msg.messages(ch)
    limit=LIMITS.get(ctype>>16,0x5c00)
    revert=set()
    while True:
        out=bytearray(2+2*n); seen={}
        newoffs=[]; growth={}
        for k,(o,tk) in enumerate(msgs):
            if o==0: newoffs.append(0); continue
            if o in seen: newoffs.append(seen[o]); continue
            i=key2i.get((fn,sidx,j,k))
            raw=b''.join(tk)
            if i in conv and k not in revert:
                data=encode.encode_items(conv[i],pmap); growth[k]=len(data)-len(raw)
            else: data=raw
            pos=len(out); out+=data
            seen[o]=pos; newoffs.append(pos)
        struct.pack_into('<H',out,0,n)
        for k,o in enumerate(newoffs):
            if o>0xffff: raise ValueError('offset overflow')
            struct.pack_into('<H',out,2+2*k,o)
        while len(out)%4: out+=b'\0'
        if len(out)<=limit or not growth: break
        worst=max(growth,key=lambda k:growth[k]); revert.add(worst)
    if revert: REVERTED.append((fn,sidx,j,sorted(revert)))
    return bytes(out)
def build_file(fn):
    d,st=ps1all.scenes(fn)
    d=bytearray(d)
    report=[]; newsizes={}
    secs=[sec for k,sec,sz in st]
    for idx,(k,sec,sz) in enumerate(st):
        base=sec*2048
        n=struct.unpack('<I',d[base:base+4])[0]&0xff
        hdr=struct.unpack('<I',d[base:base+4])[0]
        ents=[list(struct.unpack('<3I',d[base+4+12*q:base+16+12*q])) for q in range(n)]
        if not ents or ents[-1][1]+ents[-1][2]!=sz: continue
        if not any(t&0xffff==0xa for t,o,s in ents): continue
        chunks=[]
        for jj,(t,o,s) in enumerate(ents):
            c=bytes(d[base+o:base+o+s])
            if t&0xffff==0xa: c=rebuild_chunk(fn,idx,jj,c)
            chunks.append((t,c))
        hsize=4+12*n
        out=bytearray(struct.pack('<I',hdr)); pos=hsize; body=bytearray()
        for t,c in chunks:
            out+=struct.pack('<3I',t,pos,len(c)); body+=c; pos+=len(c)
        new=bytes(out+body)
        nxt=min([s2 for s2 in secs if s2>sec]+[len(d)//2048])
        span=(nxt-sec)*2048
        report.append((idx,sec,sz,len(new),span))
        newsizes[idx]=(k,len(new))
        if len(new)<=span:
            d[base:base+span]=new+b'\0'*(span-len(new))
    return bytes(d),report,newsizes
def build_subs(fn):
    d,st=ps1all.scenes(fn)
    res={}
    for idx,(k,sec,sz) in enumerate(st):
        base=sec*2048
        hdr=struct.unpack('<I',d[base:base+4])[0]; n=hdr&0xff
        if n==0 or n>64: continue
        ents=[list(struct.unpack('<3I',d[base+4+12*q:base+16+12*q])) for q in range(n)]
        real=[e for e in ents if e!=[0,0,0]]
        if not real or real[0][1]!=4+12*n or max(o+s for t,o,s in real)!=sz: continue
        if not any(t&0xffff==0xa for t,o,s in real): continue
        out=bytearray(struct.pack('<I',hdr)); pos=4+12*n; body=bytearray()
        for jj,(t,o,s) in enumerate(ents):
            if [t,o,s]==[0,0,0]:
                out+=struct.pack('<3I',0,0,0); continue
            c=bytes(d[base+o:base+o+s])
            if t&0xffff==0xa: c=rebuild_chunk(fn,idx,jj,c,t)
            out+=struct.pack('<3I',t,pos,len(c)); body+=c; pos+=len(c)
        res[idx]=bytes(out+body)
    return res
if __name__=='__main__':
    import glob
    tot_over=0
    for f in sorted(glob.glob(S+'/ps1/fs/FLD/F_*.BIN')):
        fn='FLD/'+f.split('/')[-1]
        nd,rep,ns=build_file(fn)
        over=[r for r in rep if r[3]>r[4]]
        grow=sum(r[3]-r[2] for r in rep)
        print(fn,len(rep),'grow',grow,'overflow',[(hex(r[1]),r[3]-r[4]) for r in over])
