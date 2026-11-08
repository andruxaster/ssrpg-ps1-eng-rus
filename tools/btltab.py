import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import struct,sys
S=_W+''
sys.path.insert(0,S+'/tools')
from endec import code_text
def read(d,T=0x5045a,n=None):
    W=lambda i: struct.unpack('>H',d[i:i+2])[0]
    base=T+struct.unpack('>h',d[T:T+2])[0]
    out=[]; i=T+2
    while True:
        off,ln=W(i),W(i+2)
        if ln>64 or (n is not None and len(out)>=n): break
        ws=[W(base+2*(off+q)) for q in range(ln)]
        out.append((i,off,ln,ws)); i+=4
    return base,out
def txt(ws): return ''.join(code_text(w+0x212a) if w<1793 else '<%x>'%w for w in ws)
if __name__=='__main__':
    d=open(S+'/ngcd/en/PROG.PRG','rb').read()
    base,out=read(d)
    print(hex(base),len(out))
    for k,(i,off,ln,ws) in enumerate(out): print(k,hex(i),off,ln,repr(txt(ws)))
