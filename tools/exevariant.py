import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,pickle,struct
S=_W+''
nd,files,nf=pickle.load(open(S+'/build/layout_full.pkl','rb'))
orig=bytearray(open(S+'/ps1/fs/SLPS_008.14','rb').read())
new=nd['/SLPS_008.14;1'][1]
# diff regions
diffs=[]
i=0
while i<len(orig):
    if orig[i]!=new[i]:
        j=i
        while j<len(orig) and (orig[j]!=new[j] or (j-i)%4): j+=1
        diffs.append((i,j)); i=j
    else: i+=1
def region(o):
    a=o-0x800+0x80010000
    if 0x800c0f30<=a<0x800c6000: return 'table'
    if 0x80151f7c<=a<0x8015227c: return 'tramp'
    if a in (0x80023cc0,0x80023cc4,0x80029220): return 'hook'
    if 0x800c5d00<=a<0x800c5e00+0x200: return 'filetable'
    return 'other'
import collections
c=collections.Counter(region(a) for a,b in diffs); print(c)
mode=sys.argv[1]
ex=bytearray(orig)
for a,b in diffs:
    if region(a) in mode.split(','): ex[a:b]=new[a:b]
keep={'/SLPS_008.14;1':(nd['/SLPS_008.14;1'][0],bytes(ex))}
for k,v in nd.items():
    if k!='/SLPS_008.14;1' and ('filetable' in mode or 'other' in mode): keep[k]=v
pickle.dump((keep,files,nf),open(S+'/build/layout.pkl','wb'))
