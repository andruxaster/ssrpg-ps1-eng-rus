import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,pickle,json,struct,collections
sys.path.insert(0,_W+'/tools')
S=_W+''
tbl={int(k,16):v for k,v in json.load(open(S+'/out/ps1_sjis2glyph.json')).items()}
NJP=1859
def free_codes():
    out=[]
    for lead in list(range(0x85,0x89))+list(range(0x98,0xa0))+list(range(0xe0,0xeb)):
        for trail in range(0x40,0xfd):
            if trail==0x7f: continue
            c=(lead<<8)|trail
            if lead==0x88 and trail>=0x9f: continue
            if lead==0x98 and trail<0x9f: pass
            if tbl.get(c,0)==0: out.append(c)
    return out
def assign(pairs):
    fc=free_codes()
    order=[p for p,_ in collections.Counter(pairs).most_common()]
    m={}
    for k,p in enumerate(order):
        m[p]=(fc[k],NJP+k)
    return m
def encode_items(items,pmap):
    b=bytearray()
    for it in items:
        if isinstance(it,tuple):
            if it[0]=='pair':
                c=pmap[it[1]][0]; b+=bytes([c>>8,c&255])
            elif it[0]=='raw': b+=it[1]
            else: b+=b'\x06\x00'
        else: b+=it
    return bytes(b)
