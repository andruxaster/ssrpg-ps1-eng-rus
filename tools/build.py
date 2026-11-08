import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,os,struct,pickle,json,shutil,subprocess
sys.path.insert(0,_W+'/tools')
import ps1all,ps1msg,encode,glyphs,fldbuild
from asm import *
S=encode.S
OD=os.environ.get('PS1OUT',S+'/out')
OUT=os.environ.get('PS1BUILD',S+'/build'); os.makedirs(OUT,exist_ok=True)
EXEBASE=0x80010000
def eoff(addr): return addr-EXEBASE+0x800
exe=bytearray(open(S+'/ps1/fs/SLPS_008.14','rb').read())
pmap=pickle.load(open(OD+'/pmap.pkl','rb'))
NJP=1859
needed=set(json.load(open(S+'/out/jp_needed.json')))
freeslots=json.load(open(OD+'/jp_free.json')) if os.path.exists(OD+'/jp_free.json') else []
order=sorted(pmap.items(),key=lambda x:x[1][1])
pmap={}
for k,(p,(code,idx)) in enumerate(order):
    pmap[p]=(code, freeslots[k] if k<len(freeslots) else NJP+(k-len(freeslots)))
NPAIR=sum(1 for c,i in pmap.values() if i>=NJP)
print('pairs in JP slots',len(pmap)-NPAIR,'in RAM',NPAIR)
pickle.dump(pmap,open(OD+'/pmap_final.pkl','wb'))
PAIRBASE=0x801f2600
assert PAIRBASE+NPAIR*32<=0x801fd000, hex(PAIRBASE+NPAIR*32)
pass
# ---- SJIS table entries
def tbloff(c):
    a=(0x800b0cb0+2*c) if c<=0xe03f else (0x800b0000-0x73d0+2*c)
    return eoff(a&0xffffffff)
for p,(code,idx) in pmap.items():
    o=tbloff(code); assert struct.unpack('<H',exe[o:o+2])[0]==0
    struct.pack_into('<H',exe,o,idx)
# ---- trampolines in dead code (0x80023c44 unused SJIS->ptr dup, 0x80023368 unreferenced fn)
TP=0x80023c44; TL=0x80023368
HB=(PAIRBASE-NJP*32)&0xffffffff
hb_hi=(HB+0x8000)>>16; hb_lo=(HB-(hb_hi<<16))&0xffff
tp=[andi('v1','a0',0xffff), beq('v1','zero',11), sll('v0','v1',5), sltiu('t0','v1',NJP), beq('t0','zero',4),
    lui('t1',0x8014), addiu('t1','t1',0x381c), jr('ra'), addu('v0','v0','t1'),
    lui('t1',hb_hi), addiu('t1','t1',hb_lo), jr('ra'), addu('v0','v0','t1'),
    jr('ra'), addu('v0','zero','zero')]
N=NPAIR*32
tl=[addiu('sp','sp',(-24)&0xffff), sw('ra',16,'sp'), jal(0x80023b24), NOP,
    lw('a0',0x974,'gp'), lui('t0',PAIRBASE>>16), ori('t0','t0',PAIRBASE&0xffff), ori('t1','zero',60000), addu('a0','a0','t1'),
    lui('t2',N>>16), ori('t2','t2',N&0xffff), addu('t2','a0','t2'),
    lw('t3',0,'a0'), addiu('a0','a0',4), sw('t3',0,'t0'), bne('a0','t2',(-4)&0xffff), addiu('t0','t0',4),
    lw('ra',16,'sp'), addiu('sp','sp',24), jr('ra'), NOP]
assert len(tp)<=31 and len(tl)<=68
for k,w in enumerate(tp): struct.pack_into('<I',exe,eoff(TP+4*k),w)
for k,w in enumerate(tl): struct.pack_into('<I',exe,eoff(TL+4*k),w)
# patch idx->ptr function and loader call
assert struct.unpack('<I',exe[eoff(0x80023cc0):eoff(0x80023cc0)+4])[0]==andi('v1','a0',0xffff)
struct.pack_into('<I',exe,eoff(0x80023cc0),j(TP)); struct.pack_into('<I',exe,eoff(0x80023cc4),NOP)
assert struct.unpack('<I',exe[eoff(0x80029220):eoff(0x80029220)+4])[0]==jal(0x80023b24)
struct.pack_into('<I',exe,eoff(0x80029220),jal(TL))
# ---- FONT
if os.environ.get('RUFONT'):
    import rufont
    def PAIRBMP(p):
        px=rufont.tile_pixels(p); rows=[]
        for y in range(16):
            w=0
            for x in range(16):
                if px[y][x] in (1,9,10): w|=1<<(15-x)
            rows.append(w)
        return rows
else: PAIRBMP=glyphs.pair_bitmap
font=open(S+'/ps1/fs/FONT.PS','rb').read()
newfont=bytearray(font)+b'\0'*(60000-len(font))
pairs_by_idx=sorted(pmap.items(),key=lambda x:x[1][1])
for p,(code,idx) in pairs_by_idx:
    g=glyphs.to_bytes(PAIRBMP(p))
    if idx<NJP: newfont[idx*32:idx*32+32]=g; continue
    assert len(newfont)==60000+(idx-NJP)*32
    newfont+=g
newfont=bytes(newfont)
# ---- file table helpers
FT={}  # name -> offset of (lba,size)
import pycdlib
iso=pycdlib.PyCdlib(); iso.open(S+'/ps1/ps1.iso')
files={}
for dirname,dirs,fl in iso.walk(iso_path='/'):
    for f in fl:
        p=dirname.rstrip('/')+'/'+f; r=iso.get_record(iso_path=p)
        files[p]=(r.extent_location(),r.data_length)
        k=exe.find(struct.pack('<II',r.extent_location(),r.data_length))
        if k>=0: FT[p]=k
iso.close()
TRACK1=281937; LASTFILE=281787
newdata={}     # path -> (lba, bytes)  (for relocated or rewritten files)
nextfree=LASTFILE+2
def place(path,data):
    global nextfree
    lba0,size0=files[path]
    if (len(data)+2047)//2048 <= (size0+2047)//2048:
        newdata[path]=(lba0,data); return lba0
    lba=nextfree; nextfree+= (len(data)+2047)//2048
    newdata[path]=(lba,data); return lba
# FONT relocate
lba=place('/FONT.PS;1',newfont)
struct.pack_into('<II',exe,FT['/FONT.PS;1'],lba,len(newfont))
# ---- FLD files
import glob
log=[]
for f in sorted(glob.glob(S+'/ps1/fs/FLD/F_*.BIN')):
    fn='FLD/'+f.split('/')[-1]; path='/'+fn+';1'
    d,st=ps1all.scenes(fn)
    subs=fldbuild.build_subs(fn)
    if not subs: continue
    # repack all entries sequentially
    out=bytearray(); newents=[]
    # regenerate new sub-archive bytes for every entry
    for idx,(k,sec,sz) in enumerate(st):
        blob=subs.get(idx, d[sec*2048:sec*2048+sz])
        while len(out)%2048: out+=b'\0'
        newsec=len(out)//2048
        out+=blob
        newents.append((k,newsec,len(blob)))
    while len(out)%2048: out+=b'\0'
    for k,newsec,sz in newents: struct.pack_into('<II',exe,k,newsec,sz)
    data=bytes(out)
    lba=place(path,data)
    struct.pack_into('<II',exe,FT[path],lba,len(data) if len(data)>files[path][1] else files[path][1])
    log.append((fn,len(d)//2048,len(data)//2048,lba))
place('/SLPS_008.14;1',bytes(exe))
pickle.dump((newdata,files,nextfree),open(OUT+'/layout.pkl','wb'))
for l in log: print(l)
print('next free',nextfree,'pairs',NPAIR,'reverted',fldbuild.REVERTED[:20],len(fldbuild.REVERTED))
