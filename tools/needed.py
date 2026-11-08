import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,pickle,json,glob,struct
sys.path.insert(0,_W+'/tools')
import ps1all,ps1msg
S=ps1all.S
tbl={int(k,16):v for k,v in json.load(open(S+'/out/ps1_sjis2glyph.json')).items()}
def runs(b,minrun):
    chars=set(); i=0; run=[]
    while i<len(b)-1:
        c=(b[i]<<8)|b[i+1]
        if c in tbl and tbl[c] not in (0,0xffff): run.append(c); i+=2
        else:
            if len(run)>=minrun: chars.update(run)
            run=[]; i+=1
    if len(run)>=minrun: chars.update(run)
    return chars
def compute():
    NG,PS=pickle.load(open(S+'/out/db.pkl','rb')); out=pickle.load(open(S+'/out/converted.pkl','rb'))
    codes=set()
    for i,m in enumerate(PS):
        if i not in out or m['file']=='FLD/F_IZU.BIN':
            codes|=runs(m['raw'],1)
    codes|=runs(open(S+'/ps1/fs/SLPS_008.14','rb').read(),2)
    import os
    others=[f for f in glob.glob(S+'/ps1/fs/**/*',recursive=True) if os.path.isfile(f) and not f.endswith('.STR') and '/SND/' not in f and '/FLD/F_' not in f and not f.endswith('SLPS_008.14') and not f.endswith('FONT.PS')]
    for f in others:
        codes|=runs(open(f,'rb').read(),2)
    for f in sorted(glob.glob(S+'/ps1/fs/FLD/F_*.BIN')):
        fn='FLD/'+f.split('/')[-1]; d,st=ps1all.scenes(fn)
        for k,sec,sz in st:
            base=sec*2048; n=struct.unpack('<I',d[base:base+4])[0]&0xff
            if n==0 or n>64: codes|=runs(d[base:base+sz],3); continue
            for q in range(n):
                t,o,s=struct.unpack('<3I',d[base+4+12*q:base+16+12*q])
                if t&0xffff==0xa or s==0: continue
                if t&0xffff in (4,5,6): continue
                codes|=runs(d[base+o:base+o+s],2)
    used={tbl[c] for c in codes}|{0,1}
    # also keep all kana/latin/digits/punct block (glyphs < 300) to be safe
    used|=set(range(0,300))
    return used
if __name__=='__main__':
    u=compute(); print(len(u),'free',1859-len(u))
    json.dump(sorted(u),open(S+'/out/jp_needed.json','w'))
