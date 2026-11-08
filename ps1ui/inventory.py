import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import json,re
S=_W+''
tbl={int(k,16):v for k,v in json.load(open(S+'/out/ps1_sjis2glyph.json')).items()}
def isch(d,j):
    c=(d[j]<<8)|d[j+1]; return c in tbl and tbl[c] not in (0,0xffff)
def scan(d,lo,hi,minlen=1):
    res=[]; i=lo
    while i<hi-1:
        if isch(d,i):
            j=i
            while j<hi-1 and isch(d,j): j+=2
            s=d[i:j].decode('cp932','replace')
            if len(s)>=minlen: res.append((i,j,s))
            i=j
        else: i+=1
    return res
def gap(d,j,hi):
    k=j
    while k<hi and d[k]==0: k+=1
    return k-j
items=[]
def add(file,region,off,end,jp,maxbytes,kind):
    items.append(dict(file=file,region=region,off=off,jp=jp,jpbytes=end-off,max_chars=max(0,maxbytes)//2*2,kind=kind))
exe=open(S+'/ps1/fs/SLPS_008.14','rb').read()
R=[('exe_text',0xc60,0x5400,None),('exe_chars',0xbc190,0xbcd10,17),('exe_tech',0xc8980,0xccfc0,23),('exe_charsel',0xcea60,0xcea90,None),('exe_words',0xe6258,0xe6a10,None)]
for name,lo,hi,cap in R:
    for off,end,s in scan(exe,lo,hi,2 if name!='exe_words' else 1):
        if exe[end]!=0: continue   # not terminated -> skip
        g=gap(exe,end,hi)
        mb=(end-off)+g-1
        if cap: mb=min(mb,cap)
        add('SLPS_008.14',name,off,end,s,mb,name)
for fn,cap,kind in [('BTL/BIN_PARA.PAC',17,'enemy'),('BTL/BIN_OGI.PAC',23,'enemy_attack')]:
    d=open(S+'/ps1/fs/'+fn,'rb').read()
    for off,end,s in scan(d,0,len(d),1):
        if d[end]!=0 or len(s)<1: continue
        g=gap(d,end,len(d)); add(fn,kind,off,end,s,min((end-off)+g-1,cap),kind)
for fn in ['MSG/COMN.MSG','MSG/KMK_S.MSG']:
    d=open(S+'/ps1/fs/'+fn,'rb').read()
    for off,end,s in scan(d,0,len(d),1):
        add(fn,'msg',off,end,s,end-off,'msg')
for k,it in enumerate(items): it['id']=k
# context: neighbours in same file/region
for k,it in enumerate(items):
    nb=[x for x in items[max(0,k-3):k+4] if x['file']==it['file'] and x['region']==it['region']]
    it['context']=[('>> ' if x is it else '')+x['jp'] for x in nb]
json.dump(items,open(S+'/ps1ui/inventory.json','w'),ensure_ascii=False,indent=0)
import collections
print(len(items),collections.Counter(i['region'] for i in items))
print(sum(1 for i in items if i['max_chars']<2))
