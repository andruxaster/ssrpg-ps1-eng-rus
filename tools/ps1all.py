import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,struct,glob
sys.path.insert(0,_W+'/tools')
import ps1msg
S=ps1msg.S
EXE=open(S+'/ps1/fs/SLPS_008.14','rb').read()
def scenes(fname):
    d=open(S+'/ps1/fs/'+fname,'rb').read()
    first=ps1msg.parse_sub(d,0); fs=first[-1][1]+first[-1][2]
    st=ps1msg.scene_table(EXE,len(d),fs)
    return d,st
def all_msg_chunks():
    for f in sorted(glob.glob(S+'/ps1/fs/FLD/F_*.BIN')):
        fn='FLD/'+f.split('/')[-1]
        d,st=scenes(fn)
        for idx,(k,sec,sz) in enumerate(st):
            base=sec*2048
            n=struct.unpack('<I',d[base:base+4])[0]&0xff
            for j in range(n):
                t,o,s=struct.unpack('<3I',d[base+4+12*j:base+16+12*j])
                if t&0xffff==0xa:
                    yield fn,idx,sec,j,t,base+o,s,d[base+o:base+o+s]
