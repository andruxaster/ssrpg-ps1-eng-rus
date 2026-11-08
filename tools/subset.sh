#!/bin/bash
# subset.sh NAME python-filter-expr
S=${SSRPG_WORK:-$(cd "$(dirname "$0")/.." && pwd)}
python3 -I - "$2" <<PY
import pickle,sys
S='$S/build'
nd,files,nf=pickle.load(open(S+'/layout_full.pkl','rb'))
keep={k:v for k,v in nd.items() if eval(sys.argv[1])}
print(sorted(keep))
pickle.dump((keep,files,nf),open(S+'/layout.pkl','wb'))
PY
python3 -I $S/tools/disc.py $1 >/dev/null
