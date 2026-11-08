"""RU PS1: build converted.pkl with pair optimization, then pmap."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,pickle,collections,json,glob
S=_W+''
sys.path.insert(0,S+'/tools')
import conv,conv2ru,rupairs,encode
sys.path.insert(0,S+'/ps1ui')
import uitext
UIP=uitext.ui_pairs() if __import__('os').environ.get('WITHUI') else set()
print('ui pairs',len(UIP))
BUDGET=int(__import__("os").environ.get("BUDGET","1360"))
NG,PS=pickle.load(open(S+'/out/db.pkl','rb'))
acc=pickle.load(open(S+'/out/accepted.pkl','rb'))
msgs=json.load(open(S+'/ru/tr/msgs.json')); rg=json.load(open(S+'/ru/tr/groups.json')); rtr={}
for f in glob.glob(S+'/ru/tr/out_*.json'): rtr.update(json.load(open(f)))
pos={(m['file'],m['idx']):k for k,m in enumerate(msgs)}
m2g={i:g for g,ids in rg.items() for i in ids}
tg=json.load(open(S+'/tr/groups.json')); ptr={}
for f in glob.glob(S+'/ru_ps1/tr/out_*.json'): ptr.update(json.load(open(f)))
def ru_for_ng(j):
    n=NG[j]; k=pos.get((n['file'],n['idx']))
    if k is None: return None
    g=m2g.get(k); t=rtr.get(g) if g else None
    if t is None: return None
    t=dict(t); ch=msgs[k].get('choice')
    if ch and 'options' not in t and ch.get('options'): t['options']=ch['options']
    return t
jobs={}
for i in acc:
    t=ru_for_ng(acc[i])
    if t: jobs[i]=t
for gid,ids in tg.items():
    t=ptr.get(gid)
    if not t: continue
    for i in ids:
        if i not in jobs: jobs[i]=t
import re as _re
J2R=json.load(open(S+'/ps1ui/jp2ru.json'))
J2R.update({'銀の宝鈴':'Серебряный колокол','黄泉返しのリンゴ':'Яблоко воскрешения','いやしの水':'Целебная вода','スターメイル':'Звездные латы',
 'マリア像':'Статуэтка Марии','力の素':'Эликсир силы','天聖酒':'Святое сакэ','愛妻の指輪':'Кольцо любимой жены','時の後ろ髪':'Прядь времени',
 '破邪の札':'Талисман против зла','箱根手形':'Пропуск в Хаконэ','精霊石':'Камень духов','聖の粉':'Святая пыль','酢豚':'Свинина в кисло-сладком соусе',
 '隠密手形':'Тайный пропуск','シーフリング':'Кольцо вора','かんざし':'Шпилька','アトラスの涙':'Слеза Атласа'})
_rx=_re.compile(r'^(は|達は、)?「?([^「」]+?)」?を手に入れた[！!・]*$')
nov=0
for i,m in enumerate(PS):
    mm=_rx.match(m['jp'])
    if mm and mm.group(2) in J2R:
        it=J2R[mm.group(2)]
        if mm.group(1)=='は': txt='{NAME} берет '+it+'!'
        elif mm.group(1)=='達は、': txt='{NAME} с отрядом берут '+it+'!'
        else: txt='Получено: '+it+'!'
        jobs[i]={'pages':[txt]}; nov+=1
print('item overrides',nov)
def run(cellfn):
    conv2ru.cells=cellfn
    out={}; fail=collections.Counter()
    for i,t in jobs.items():
        it=conv2ru.build_text(PS[i]['raw'],t)
        if it is None: fail['build']+=1; continue
        out[i]=it
    return out,fail
LINES=[]
def rec(line): LINES.append(line); return conv.cells(line)
run(rec)
lines=sorted(set(LINES))
print('jobs',len(jobs),'lines',len(lines))
naive=collections.Counter()
for l in lines:
    for x in conv.cells(l):
        if x[0]=='pair': naive[x[1]]+=1
print('naive pairs',len(naive))
def topk(cnt,k): return UIP|set([p for p,_ in cnt.most_common() if p not in UIP][:max(0,k-len(UIP))])
P=topk(naive,BUDGET); banned=set()
cache={}
def enc_all(cost):
    use=collections.Counter(); res={}
    for l in lines:
        c,cells=rupairs.encode_line(l,cost,32)
        if not cells and l.strip(): cells=conv.cells(l)
        res[l]=cells
        for x in cells:
            if x[0]=='pair': use[x[1]]+=1
    return use,res
for it in range(6):
    use,res=enc_all(lambda p: 0 if p in P else 1000)
    forced=[p for p in use if p not in P]
    tot=len(set(use)|UIP)
    print('iter',it,'used',tot,'forced',len(forced))
    if tot<=BUDGET: break
    sc=collections.Counter(use); P=topk(sc,BUDGET)
rnd=0
while len(set(use)|UIP)>BUDGET and rnd<80:
    for p,c in sorted([(p,c) for p,c in use.items() if p not in UIP],key=lambda x:x[1])[:len(set(use)|UIP)-BUDGET]: banned.add(p)
    P=set(use)-banned
    use,res=enc_all(lambda p: 10**6 if p in banned else (0 if p in P else 1000)); rnd+=1
    print('squeeze',rnd,'used',len(set(use)|UIP))
def fin(line):
    r=res.get(line)
    if r is None: r=rupairs.encode_line(line,lambda p:0 if p in use else 10**6,32)[1]
    out=[]
    for x in r:
        out.append(('pair',x[1]) if x[0]=='pair' else ('name',))
    return out
out,fail=run(fin)
pairs=collections.Counter()
for it in out.values():
    for x in it:
        if isinstance(x,tuple) and x[0]=='pair': pairs[x[1]]+=1
for p in UIP: pairs[p]+=1
print('converted',len(out),'of',len(PS),dict(fail),'pairs',len(pairs))
OD=S+'/ru_ps1/out'
pickle.dump(out,open(OD+'/converted.pkl','wb')); pickle.dump(pairs,open(OD+'/pairs.pkl','wb'))
pickle.dump(encode.assign(pairs),open(OD+'/pmap.pkl','wb'))
