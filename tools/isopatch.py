import struct,sys,os
def patch_iso(src,dst,newfiles):
    iso=bytearray(open(src,'rb').read())
    def sec(l): return iso[l*2048:(l+1)*2048]
    pvd=16*2048
    vs=struct.unpack('<I',iso[pvd+80:pvd+84])[0]
    root=iso[pvd+156:pvd+156+34]
    rl=struct.unpack('<I',root[2:6])[0]; rlen=struct.unpack('<I',root[10:14])[0]
    recs={}
    def walk(lba,ln):
        for s in range((ln+2047)//2048):
            base=(lba+s)*2048; off=0
            while off<2048:
                L=iso[base+off]
                if L==0: break
                nl=iso[base+off+32]; nm=iso[base+off+33:base+off+33+nl].decode('ascii','replace')
                fl=iso[base+off+25]
                el=struct.unpack('<I',iso[base+off+2:base+off+6])[0]; en=struct.unpack('<I',iso[base+off+10:base+off+14])[0]
                if nm not in ('\x00','\x01'):
                    if fl&2: walk(el,en)
                    else: recs[nm.split(';')[0]]=(base+off,el,en)
                off+=L
    walk(rl,rlen)
    end=len(iso)//2048
    moved=0
    for name,data in newfiles.items():
        roff,el,en=recs[name]
        need=(len(data)+2047)//2048; have=(en+2047)//2048
        if need<=have:
            iso[el*2048:el*2048+have*2048]=data+bytes(have*2048-len(data))
            nl=el
        else:
            nl=end; iso+=data+bytes(need*2048-len(data)); end+=need; moved+=1
        iso[roff+2:roff+6]=struct.pack('<I',nl); iso[roff+6:roff+10]=struct.pack('>I',nl)
        iso[roff+10:roff+14]=struct.pack('<I',len(data)); iso[roff+14:roff+18]=struct.pack('>I',len(data))
    vs2=len(iso)//2048
    if vs2>vs:
        iso[pvd+80:pvd+84]=struct.pack('<I',vs2); iso[pvd+84:pvd+88]=struct.pack('>I',vs2)
    open(dst,'wb').write(iso)
    return moved
