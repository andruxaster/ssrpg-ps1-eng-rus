import json,sys,glob
# usage: build.py out.json part1.txt part2.txt ...
out={}
for fn in sys.argv[2:]:
    cur=None
    for line in open(fn,encoding='utf-8'):
        line=line.rstrip('\n')
        if not line.strip(): continue
        if line.startswith('#'):
            cur={'pages':[]}; out[line[1:].strip()]=cur
        elif line.startswith('?'):
            cur['question']=line[1:]
        elif line.startswith('='):
            cur['options']=line[1:].split('|')
        else:
            cur['pages'].append(line)
json.dump(out,open(sys.argv[1],'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(out))
