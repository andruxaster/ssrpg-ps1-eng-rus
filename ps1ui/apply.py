"""Patch UI strings into build layout (after build.py)."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,os,pickle
S=_W+''
sys.path.insert(0,S+'/ps1ui')
import uitext
B=os.environ.get('PS1BUILD',S+'/build_ru'); OD=os.environ.get('PS1OUT',S+'/ru_ps1/out')
nd,files,nf=pickle.load(open(B+'/layout.pkl','rb'))
pm=pickle.load(open(OD+'/pmap_final.pkl','rb'))
def key(fn): return '/'+fn+';1'
data={}
def get(fn):
    k=key(fn)
    if k not in data:
        if k in nd: data[k]=bytearray(nd[k][1])
        else: data[k]=bytearray(open(S+'/ps1/fs/'+fn,'rb').read())
    return data[k]
n=0; miss=0
for o in uitext.load():
    if o['file']=='MSG/COMN.MSG': continue
    d=get(o['file']); off=o['off']
    b=b''
    ok=True
    for p in uitext.pairs_of(o['ru']):
        if p not in pm: ok=False; break
        c=pm[p][0]; b+=bytes([c>>8,c&255])
    if not ok: miss+=1; continue
    room=o['max_chars'] if o['max_chars']>=o['jpbytes'] else o['jpbytes']
    assert len(b)<=max(o['jpbytes'],o['max_chars']),(o,len(b))
    if o['file'].startswith('MSG/'):
        # fixed segment: pad with fullwidth spaces to keep message structure
        pad=o['jpbytes']-len(b); assert pad%2==0
        d[off:off+o['jpbytes']]=b+b'\x81\x40'*(pad//2)
    else:
        end=off+o['jpbytes']
        L=max(o['jpbytes'],len(b))
        d[off:off+L+1 if L>=o['jpbytes'] else end]=b+b'\0'*((L+1 if L>=o['jpbytes'] else o['jpbytes'])-len(b))
    n+=1
# ---- rebuild COMN.MSG
import json,struct
cm=json.load(open(S+'/ps1ui/tr/comn.json'))
orig=open(S+'/ps1/fs/MSG/COMN.MSG','rb').read()
nmsg=struct.unpack('<H',orig[0:2])[0]; offs=[struct.unpack('<H',orig[2+2*k:4+2*k])[0] for k in range(nmsg)]
def enc(t):
    if len(t)%2: t+=' '
    b=b''
    for i in range(0,len(t),2):
        c=pm[t[i:i+2]][0]; b+=bytes([c>>8,c&255])
    return b
# keep every message at its original offset (the game addresses some of them directly)
import callenc
out=bytearray(orig)
for k,o in enumerate(offs):
    if o==0 or str(k) not in cm: continue
    e=o
    while orig[e:e+2]!=b'\0\0': e+=2
    slot=e+2-o
    m=b''.join(struct.pack('>H',x) if isinstance(x,int) else callenc.enc_text(x,pm) for x in cm[str(k)])+b'\0\0'
    assert len(m)<=slot,('COMN slot overflow',k,len(m),slot)
    out[o:o+slot]=m+b'\0'*(slot-len(m))
print('COMN.MSG',len(orig),'->',len(out))
assert len(out)<=2048
k='/MSG/COMN.MSG;1'
data[k]=bytearray(out)
ex=bytearray(nd['/SLPS_008.14;1'][1]) if '/SLPS_008.14;1' not in data else data['/SLPS_008.14;1']
lba0,size0=files[k]
ft=ex.find(struct.pack('<II',lba0,size0)); assert ft>=0
struct.pack_into('<II',ex,ft,lba0,len(out)); data['/SLPS_008.14;1']=ex
for fn in ('BTL/BT_COCK.PSI','FIX_00.PFX'):
    gp=S+'/ps1ui/gfx/'+fn.split('/')[-1]
    if os.path.exists(gp):
        nb=open(gp,'rb').read(); assert len(nb)==files[key(fn)][1]
        data[key(fn)]=bytearray(nb)
# ---- T_FLD.MSG: place names (save list etc.); same table format, duplicates shared, 2-byte aligned
import callenc
tf=json.load(open(S+'/ps1ui/tr/tfld.json'))
TK='/MSG/T_FLD.MSG;1'
tb=open(S+'/ps1/fs/MSG/T_FLD.MSG','rb').read()
tn=struct.unpack_from('<H',tb,0)[0]; toffs=struct.unpack_from('<%dH'%tn,tb,2)
tout=bytearray(2+2*tn); tseen={}
for k,o in enumerate(toffs):
    jp=tb[o:tb.index(b'\0',o)].decode('cp932')
    ru=tf[jp]
    if ru not in tseen:
        tseen[ru]=len(tout); tout+=callenc.enc_text(ru,pm,24)+b'\0\0'
    struct.pack_into('<H',tout,2+2*k,tseen[ru])
struct.pack_into('<H',tout,0,tn)
assert len(tout)<=len(tb),(len(tout),len(tb))
data[TK]=tout
ex=data['/SLPS_008.14;1']
lba0,size0=files[TK]
ft=ex.find(struct.pack('<II',lba0,size0)); assert ft>=0,'T_FLD file table'
struct.pack_into('<II',ex,ft,lba0,len(tout))
print('T_FLD.MSG',len(tb),'->',len(tout))
# ---- place names stored per field scene (chunk type 0x1a, 36 bytes) - shown in the save list
sys.path.insert(0,S+'/tools'); import fld
scn=json.load(open(S+'/ps1ui/tr/scene_names_ru.json'))
nsc=0
for fk in [k for k in files if k.startswith('/FLD/F_')]:
    fd=get(fk[1:-2])
    for po,ents in fld.subarchives(fd):
        for t,o,sz in ents:
            if t&0xffff!=0x1a: continue
            raw=bytes(fd[po+o:po+o+sz]).split(b'\0')[0]
            jp=raw.decode('cp932','replace')
            if jp not in scn: continue
            enc=callenc.enc_text(scn[jp],pm,34); assert len(enc)<sz
            fd[po+o:po+o+sz]=enc+b'\0'*(sz-len(enc)); nsc+=1
print('scene names patched',nsc)
# ---- C_ALL.BIN: new-game screen (profiles/chapters/modes text + graphics)
import callenc
CK='/FLD/C_ALL.BIN;1'
ca=bytearray(open(S+'/ps1ui/gfx/C_ALL.BIN','rb').read())
assert len(ca)==files[CK][1]
P=0xa2000; t8,a8,s8=struct.unpack_from('<3I',ca,P+4+12*8); assert t8==0xa
ch=bytes(ca[P+a8:P+a8+s8]); nl=struct.unpack_from('<H',ch,0)[0]
loffs=struct.unpack_from('<%dH'%nl,ch,2)
enc_lines,bad=callenc.encode_all(pm); assert not bad,bad
newc=bytearray(2+2*nl)
for k,o in enumerate(loffs):
    if o==0: continue
    if str(k) in enc_lines: m=enc_lines[str(k)]+b'\0\0'
    else:
        e=ch.index(b'\0',o); m=ch[o:e]+b'\0'; m+=b'\0'*(len(m)%2)
    struct.pack_into('<H',newc,2+2*k,len(newc)); newc+=m
struct.pack_into('<H',newc,0,nl)
assert len(newc)<=s8,(len(newc),s8)
ca[P+a8:P+a8+s8]=newc+b'\0'*(s8-len(newc))
# game over / continue / memory card messages (pkg 0x7f000 entry 1)
go=json.load(open(S+'/ps1ui/tr/call_go.json'))
P2=0x7f000; t1,a1,s1=struct.unpack_from('<3I',ca,P2+4+12*1); assert t1==0xa
gch=bytes(ca[P2+a1:P2+a1+s1]); gn=struct.unpack_from('<H',gch,0)[0]
gout=bytearray(2+2*gn)
for k in range(gn):
    m=b''.join(struct.pack('>H',x) if isinstance(x,int) else callenc.enc_text(x,pm) for x in go[str(k)])+b'\0\0'
    struct.pack_into('<H',gout,2+2*k,len(gout)); gout+=m
struct.pack_into('<H',gout,0,gn)
assert len(gout)<=s1,(len(gout),s1)
ca[P2+a1:P2+a1+s1]=gout+b'\0'*(s1-len(gout))
print('game-over chunk',len(gout),'/',s1)
import crawl
cb,cnt=crawl.build()
tc,ac,sc=struct.unpack_from('<3I',ca,crawl.PKG+4+12*crawl.ENT); assert len(cb)==sc
ca[crawl.PKG+ac:crawl.PKG+ac+sc]=cb
print('crawl tiles',cnt)
data[CK]=ca
print('C_ALL text chunk',len(newc),'/',s8)
for k,v in data.items():
    lba=nd[k][0] if k in nd else files[k][0]
    nd[k]=(lba,bytes(v))
pickle.dump((nd,files,nf),open(B+'/layout.pkl','wb'))
print('patched',n,'missing pairs',miss,'files',list(data))
