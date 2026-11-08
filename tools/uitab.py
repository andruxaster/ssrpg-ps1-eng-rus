import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import struct,sys,collections
S=_W+''
sys.path.insert(0,S+'/tools')
def W(d,a): return struct.unpack('>H',d[a:a+2])[0]
def istext(v): return 0x212a<=v<0x212a+2048 or v<0x10 or v==0xffff
def parse(d,h):
    """MSGD-like table at header h: word0=table bytes; returns list of (off, words) or None"""
    n=W(d,h)
    if n<2 or n%2 or n>0x1000: return None
    base=h+2+n-2  # ? determine below
    return None
def table_at(d,h):
    n=W(d,h)
    if n<2 or n%2 or n>0x2000: return None
    cnt=n//2-1 if False else None
    # layout guess A: header word = size of (header+offsets) => data = h+n
    for data in (h+n, h+2+n):
        k=(data-h-2)//2
        offs=[W(d,h+2+2*i) for i in range(k)]
        if not offs or offs[0]!=0: continue
        if any(offs[i]>offs[i+1] for i in range(len(offs)-1)): continue
        ok=True; strs=[]
        for o in offs:
            a=data+o; s=[]
            while a<len(d)-1 and len(s)<400:
                v=W(d,a); s.append(v); a+=2
                if v==0xffff: break
            if s[-1]!=0xffff or not all(istext(x) for x in s): ok=False;break
            strs.append((o,s))
        if ok: return data,strs
    return None
def refs(d):
    r=collections.defaultdict(list)
    for i in range(0,len(d)-5,2):
        op=W(d,i)
        if op in (0x41f9,0x43f9,0x45f9,0x47f9,0x49f9,0x4bf9,0x4df9,0x207c,0x227c,0x247c,0x267c,0x287c,0x2a7c,0x2c7c):
            a=struct.unpack('>I',d[i+2:i+6])[0]
            if 0x400<a<len(d): r[a].append(i)
    return r
