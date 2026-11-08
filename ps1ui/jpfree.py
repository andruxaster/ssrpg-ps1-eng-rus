import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,json,glob,os,struct,pickle
S=_W+''
sys.path.insert(0,S+'/tools'); sys.path.insert(0,S+'/ps1ui')
import needed,ps1all,uitext
tbl=needed.tbl
mask={}
for o in uitext.load():
    mask.setdefault(o['file'],[]).append((o['off'],o['off']+o['jpbytes']))
def rd(fn):
    d=bytearray(open(S+'/ps1/fs/'+fn,'rb').read())
    for a,b in mask.get(fn,[]): d[a:b]=b'\0'*(b-a)
    return bytes(d)
codes=set()
NG,PS=pickle.load(open(S+'/out/db.pkl','rb')); out=pickle.load(open(S+'/ru_ps1/out/converted.pkl','rb'))
for i,m in enumerate(PS):
    if i not in out or m['file']=='FLD/F_IZU.BIN': codes|=needed.runs(m['raw'],1)
codes|=needed.runs(rd('SLPS_008.14'),2)
others=[os.path.relpath(f,S+'/ps1/fs') for f in glob.glob(S+'/ps1/fs/**/*',recursive=True) if os.path.isfile(f) and not f.endswith('.STR') and '/SND/' not in f and '/FLD/F_' not in f and not f.endswith('SLPS_008.14') and not f.endswith('FONT.PS')]
for f in others: codes|=needed.runs(rd(f),3 if f not in mask else 1)
for f in sorted(glob.glob(S+'/ps1/fs/FLD/F_*.BIN')):
    fn='FLD/'+f.split('/')[-1]; d,st=ps1all.scenes(fn)
    for k,sec,sz in st:
        base=sec*2048; n=struct.unpack('<I',d[base:base+4])[0]&0xff
        if n==0 or n>64: codes|=needed.runs(d[base:base+sz],3); continue
        for q in range(n):
            t,o,s=struct.unpack('<3I',d[base+4+12*q:base+16+12*q])
            if t&0xffff==0xa or s==0 or t&0xffff in (4,5,6): continue
            codes|=needed.runs(d[base+o:base+o+s],3)
used={tbl[c] for c in codes}|set(range(0,300))
free=[i for i in range(1859) if i not in used]
print('free',len(free))
json.dump(free,open(S+'/ru_ps1/out/jp_free_all.json','w'))
