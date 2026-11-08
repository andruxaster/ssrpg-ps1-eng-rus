import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,json,re,collections
S=_W+''
sys.path.insert(0,S+'/tools')
from endec import code_text
tiles=json.load(open(S+'/ru/tiles.json'))
SPECIAL=set([7])
for k in tiles['keep']:
    s=code_text(k+0x212a)
    if '{' in s or 'BLK' in s: SPECIAL.add(k)
def tokens_from_words(ws,raw=False):
    """words (no 0xffff) -> display string with tokens; <0> shown as \\n"""
    out=''
    for v in ws:
        t=v if raw else v-0x212a
        if (raw and v<1793) or (not raw and 0<=t<1793):
            if t in SPECIAL: out+='{T%d}'%t
            else: out+=code_text(t+0x212a)
        elif v==0 and not raw: out+='\n'
        else: out+='<%x>'%v
    return out
TOK=re.compile(r'(\{T\d+\}|<[0-9a-f]+>|\n)')
def line_widths(s):
    """tiles per line; text segments padded to even"""
    ws=[0]
    for part in TOK.split(s):
        if not part: continue
        if part=='\n': ws.append(0)
        elif part.startswith('{T'): ws[-1]+=1
        elif part.startswith('<'): pass
        else: ws[-1]+=(len(part)+1)//2
    return ws
