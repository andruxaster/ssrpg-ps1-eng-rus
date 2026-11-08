import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,glob,json,re,pickle,struct
sys.path.insert(0,_W+'/tools')
import ngmsg,endec,ps1all,ps1msg
S=ngmsg.S
t2p={int(k):v for k,v in json.load(open(S+'/out/ngtile2ps1.json')).items()}
def jpchar(v):
    t=v-0x212a
    if t==269: return '・'
    if t in t2p and t2p[t][0]==1: return '　'
    if t in t2p and t2p[t][1]<30: return t2p[t][2]
    return '〓'
STRIP=set('　・、。！？「」（）…～〜ー,.!? 　　')
def norm(s):
    s=re.sub(r'（[ぁ-ゖ　\s]+）','',s)
    return ''.join(ch for ch in s if ch not in STRIP)
# NGCD
NG=[]
for f in sorted(glob.glob(S+'/ngcd/jp/MSGD*.PRG')):
    name=f.split('/')[-1]
    jm=ngmsg.messages(f); em=ngmsg.messages(S+'/ngcd/en/'+name)
    if len(jm)!=len(em): print('count mismatch',name,len(jm),len(em))
    for i,((o1,a),(o2,b)) in enumerate(zip(jm,em)):
        jp=''.join(jpchar(v) for v in a if 0x2100<=v<0x2900)
        NG.append(dict(file=name,idx=i,jpw=a,enw=b,jp=jp,n=norm(jp)))
# PS1
PS=[]
for fn,sidx,sec,j,t,off,s,ch in ps1all.all_msg_chunks():
    n,offs,msgs=ps1msg.messages(ch)
    for k,(o,tk) in enumerate(msgs):
        if o==0: continue
        txt=''
        i=0
        while i<len(tk):
            w=tk[i]
            if w==b'\x0e\x00' and i+2<len(tk) and tk[i+1]==b'\x0a\x00': i+=3; continue
            if w[0]>=0x81:
                try: txt+=w.decode('cp932')
                except: pass
            i+=1
        PS.append(dict(file=fn,scene=sidx,chunk=j,k=k,raw=b''.join(tk),jp=txt,n=norm(txt)))
pickle.dump((NG,PS),open(S+'/out/db.pkl','wb'))
print(len(NG),len(PS))
