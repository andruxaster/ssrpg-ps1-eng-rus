import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import struct,sys,glob
sys.path.insert(0,_W+'/tools')
S=_W+''
def parse_sub(d,off):
    n=struct.unpack('<I',d[off:off+4])[0]&0xff
    ents=[]
    for k in range(n):
        t,o,s=struct.unpack('<3I',d[off+4+12*k:off+16+12*k]); ents.append([t,o,s])
    return ents
def scene_table(exe,fsize,first_size):
    # find (0,first_size) pairs as u32
    p=struct.pack('<II',0,first_size)
    k=exe.find(p)
    res=[]
    while True:
        sec,sz=struct.unpack('<II',exe[k:k+8])
        if sec*2048>=fsize or (res and sec<=res[-1][1]): break
        res.append((k,sec,sz)); k+=8
    return res
def tokens(b):
    i=0;out=[]
    while i<len(b)-1:
        out.append(b[i:i+2]); i+=2
    return out
def messages(chunk):
    n=struct.unpack('<H',chunk[0:2])[0]
    offs=[struct.unpack('<H',chunk[2+2*k:4+2*k])[0] for k in range(n)]
    msgs=[]
    for k,o in enumerate(offs):
        # read until 00 00 token
        i=o; t=[]
        while i<len(chunk)-1:
            w=chunk[i:i+2]; t.append(w); i+=2
            if w==b'\0\0': break
        msgs.append((o,t))
    return n,offs,msgs
def show(t):
    s=''
    for w in t:
        if w[0]>=0x81:
            try: s+=w.decode('cp932'); continue
            except: pass
        s+='<%02x%02x>'%(w[0],w[1])
    return s
