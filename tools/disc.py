import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,os,struct,pickle,subprocess,re
S=_W+''
OUT=os.environ.get('PS1BUILD',S+'/build')
newdata,files,nextfree=pickle.load(open(OUT+'/layout.pkl','rb'))
SRC=S+'/ps1/Shinsetsu Samurai Spirits - Bushidou Retsuden (Japan).bin'
CUE=S+'/ps1/Shinsetsu Samurai Spirits - Bushidou Retsuden (Japan).cue'
TRACK1=281937
NEWT1=max(TRACK1,nextfree+150)
GROW=NEWT1-TRACK1
name=sys.argv[1] if len(sys.argv)>1 else 'SSRPG_EN'
dst=OUT+f'/{name}.bin'
SYNC=bytes([0]+[0xff]*10+[0])
def bcd(n): return ((n//10)<<4)|(n%10)
def hdr(lba):
    a=lba+150; m,s,f=a//4500,(a//75)%60,a%75
    return bytes([bcd(m),bcd(s),bcd(f),2])
src=open(SRC,'rb')
with open(dst,'wb') as o:
    # copy track1
    src.seek(0); left=TRACK1*2352
    while left>0:
        b=src.read(min(left,1<<24)); o.write(b); left-=len(b)
    # extend track1 with empty mode2 sectors
    for lba in range(TRACK1,NEWT1):
        o.write(SYNC+hdr(lba)+b'\0'*8+b'\0'*(2352-24))
    # audio
    src.seek(TRACK1*2352)
    while True:
        b=src.read(1<<24)
        if not b: break
        o.write(b)
def write_user(o,lba,data2048,sub):
    o.seek(lba*2352); o.write(SYNC+hdr(lba)+sub+data2048)
def read_user(lba):
    with open(dst,'rb') as f:
        f.seek(lba*2352+24); return f.read(2048)
with open(dst,'r+b') as o:
    for path,(lba,data) in newdata.items():
        n=(len(data)+2047)//2048
        for k in range(n):
            chunk=data[k*2048:(k+1)*2048].ljust(2048,b'\0')
            sub=bytes([0,0,0x89 if k==n-1 else 0x08,0])*2
            write_user(o,lba+k,chunk,sub)
    # ISO9660: patch directory records & PVD size
    pvd=bytearray(read_user(16))
    vs=struct.unpack('<I',pvd[80:84])[0]+GROW
    pvd[80:84]=struct.pack('<I',vs); pvd[84:88]=struct.pack('>I',vs)
    o.seek(16*2352+24); o.write(bytes(pvd))
    root_lba=struct.unpack('<I',pvd[156+2:156+6])[0]; root_len=struct.unpack('<I',pvd[156+10:156+14])[0]
    def walk(dlba,dlen,prefix):
        for s in range((dlen+2047)//2048):
            sec=bytearray(read_user(dlba+s)); off=0; changed=False
            while off<2048:
                L=sec[off]
                if L==0: break
                nl=sec[off+32]; nm=sec[off+33:off+33+nl].decode('ascii','replace')
                flags=sec[off+25]; elba=struct.unpack('<I',sec[off+2:off+6])[0]; elen=struct.unpack('<I',sec[off+10:off+14])[0]
                if nm not in ('\x00','\x01'):
                    p=prefix+'/'+nm
                    if flags&2: walk(elba,elen,p)
                    elif p in newdata:
                        nlba,data=newdata[p]
                        nlen=max(len(data),files[p][1]) if nlba==files[p][0] else len(data)
                        sec[off+2:off+6]=struct.pack('<I',nlba); sec[off+6:off+10]=struct.pack('>I',nlba)
                        sec[off+10:off+14]=struct.pack('<I',nlen); sec[off+14:off+18]=struct.pack('>I',nlen)
                        changed=True
                off+=L
            if changed:
                o.seek((dlba+s)*2352+24); o.write(bytes(sec))
    walk(root_lba,root_len,'')
assert os.path.exists(S+'/tools/eccfix'),'tools/eccfix not built: gcc -O2 -o tools/eccfix tools/eccfix.c'
r=subprocess.run([S+'/tools/eccfix',dst,'0',str(NEWT1)],capture_output=True,text=True); print(r.stdout.strip())
# cue
cue=open(CUE).read()
def shift(m):
    mm,ss,ff=int(m.group(2)),int(m.group(3)),int(m.group(4))
    fr=(mm*60+ss)*75+ff
    if fr>=TRACK1 or (fr>0): fr+=GROW if fr>=TRACK1-200 else 0
    return f'{m.group(1)}{fr//4500:02d}:{(fr//75)%60:02d}:{fr%75:02d}'
cue=re.sub(r'(INDEX \d\d )(\d\d):(\d\d):(\d\d)',shift,cue)
cue=re.sub(r'FILE ".*?"',f'FILE "{name}.bin"',cue)
open(OUT+f'/{name}.cue','w').write(cue)
print(cue); print('track1',NEWT1,'grow',GROW)
