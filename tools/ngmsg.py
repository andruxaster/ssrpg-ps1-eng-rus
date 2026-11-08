import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,struct,json
sys.path.insert(0,_W+'/tools')
S=_W+''
JPMAP={int(k,16):v for k,v in json.load(open(S+'/out/ngcd_code2char.json')).items()}
def words(fn):
    d=open(fn,'rb').read()
    return [struct.unpack('>H',d[i:i+2])[0] for i in range(0,len(d)-1,2)]
def messages(fn):
    w=words(fn)
    tbl=w[0]//2
    offs=w[1:tbl] if tbl>1 else []
    base=tbl  # word index of message area
    msgs=[]
    for o in offs:
        i=base+o//2; m=[]
        while i<len(w):
            m.append(w[i]); i+=1
            if w[i-1]==0xffff: break
        msgs.append((o,m))
    return msgs
def show_jp(m):
    s=''
    for v in m:
        if 0x2100<=v<0x2900: s+=JPMAP.get(v,'〓')
        else: s+='<%x>'%v
    return s
