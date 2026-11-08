import struct
def subarchives(d):
    res=[]
    for off in range(0,len(d),2048):
        n=struct.unpack('<I',d[off:off+4])[0]
        if not (1<=n<=64): continue
        ok=True; ents=[]
        prev=4+12*n
        for k in range(n):
            t,o,s=struct.unpack('<3I',d[off+4+12*k:off+16+12*k])
            if o!=prev or s>0x400000: ok=False;break
            ents.append((t,o,s)); prev=o+s
        if ok: res.append((off,ents))
    return res
