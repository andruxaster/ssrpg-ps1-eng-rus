import struct,sys
BIN=sys.argv[1] if len(sys.argv)>1 else None
class Disc:
    def __init__(s,path): s.f=open(path,'rb')
    def raw(s,lba): s.f.seek(lba*2352); return s.f.read(2352)
    def sec(s,lba): return s.raw(lba)[24:24+2048]
    def walk(s):
        pvd=s.sec(16); root=pvd[156:156+34]
        out={}
        def rd(ext,size,path):
            data=b''.join(s.sec(ext+i) for i in range((size+2047)//2048)); i=0
            while i<len(data):
                l=data[i]
                if l==0: i=(i//2048+1)*2048; continue
                r=data[i:i+l]; e=struct.unpack('<I',r[2:6])[0]; sz=struct.unpack('<I',r[10:14])[0]
                fl=r[25]; nl=r[32]; nm=r[33:33+nl]
                if nm not in (b'\0',b'\1'):
                    n=nm.decode().split(';')[0]
                    if fl&2: rd(e,sz,path+n+'/')
                    else: out[path+n]=(e,sz)
                i+=l
        e=struct.unpack('<I',root[2:6])[0]; sz=struct.unpack('<I',root[10:14])[0]
        rd(e,sz,''); return out
if __name__=='__main__':
    d=Disc(BIN)
    for k,v in sorted(d.walk().items(),key=lambda x:x[1]): print(v[0],v[1],k)
