import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,struct,json
S=_W+''
sys.path.insert(0,S+'/tools')
from uitab import W
from endec import code_text
TABLES={'names':0x60d62,'msgs':0x60dec,'items':0x62b34,'shops':0x634e0,'idesc':0x63542,
        'keyitems':0x71d82,'places':0x73908,'menu1':0x207f0,'menu2':0x59f00}
def txt(ws):
    s=''
    for v in ws:
        if v==0xffff: break
        if 0x212a<=v<0x212a+1793: s+=code_text(v)
        else: s+='<%x>'%v
    return s
def read_table(e,h):
    n=W(e,h); data=h+n
    offs=[W(e,h+2+2*i) for i in range((n-2)//2)]
    out=[]
    for o in offs:
        a=data+o; ws=[]
        while True:
            v=W(e,a); ws.append(v); a+=2
            if v==0xffff: break
        out.append((o,ws))
    return data,offs,out
if __name__=='__main__':
    e=open(S+'/ngcd/en/PROG.PRG','rb').read()
    allt={}
    for k,h in TABLES.items():
        data,offs,out=read_table(e,h)
        uniq={}
        for i,(o,ws) in enumerate(out):
            uniq.setdefault(o,[]).append(i)
        end=max(data+o+2*len(ws) for o,ws in out)
        allt[k]={'hdr':h,'data':data,'end':end,'n':len(offs),'strings':[{'i':i,'off':o,'en':txt(ws),'w':len(ws)-1,'words':ws} for i,(o,ws) in enumerate(out)]}
        print(k,hex(h),'n',len(offs),'uniq',len(uniq),'bytes',end-h)
    json.dump(allt,open(S+'/ru/ui/prog_tables.json','w'),ensure_ascii=False,indent=0)
