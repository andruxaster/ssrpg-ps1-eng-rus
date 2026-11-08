import sys,glob,struct,collections,json,os
S=sys.argv[1]
def pattern(seq):
    m={};return tuple(m.setdefault(x,len(m)) for x in seq)
# NGCD runs
ng=[]
for f in sorted(glob.glob(S+'/ngcd/jp/MSGD*.PRG')):
    d=open(f,'rb').read(); run=[]
    for i in range(0,len(d)-1,2):
        v=struct.unpack('>H',d[i:i+2])[0]
        if 0x2100<=v<0x2900: run.append(v)
        else:
            if len(run)>=8: ng.append(tuple(run))
            run=[]
# PS1 runs
ps=[]
for f in sorted(glob.glob(S+'/ps1/fs/FLD/*.BIN'))+[S+'/ps1/fs/BTL/BIN_PARA.PAC',S+'/ps1/fs/SLPS_008.14']:
    d=open(f,'rb').read(); i=0; run=[]
    while i<len(d)-1:
        h=d[i]
        if (0x81<=h<=0x9f or 0xe0<=h<=0xea) and 0x40<=d[i+1]<=0xfc:
            run.append(d[i:i+2].decode('sjis','replace')); i+=2
        else:
            if len(run)>=8: ps.append(tuple(run))
            run=[]; i+=1
idx=collections.defaultdict(set)
for r in ps: idx[pattern(r)].add(r)
votes=collections.defaultdict(collections.Counter)
matched=0
for r in set(ng):
    c=idx.get(pattern(r))
    if c and len(c)==1:
        p=next(iter(c)); matched+=1
        for a,b in zip(r,p): votes[a][b]+=1
print('ng runs',len(set(ng)),'ps runs',len(set(ps)),'matched',matched)
# iterate: consistency filter
mp={a:c.most_common(1)[0][0] for a,c in votes.items()}
print('mapped codes',len(mp))
json.dump({hex(a):b for a,b in mp.items()},open(S+'/out/ngcd_code2char.json','w'),ensure_ascii=False)
for a in sorted(mp)[:80]: print(hex(a),mp[a],sum(votes[a].values()),end=' | ')
