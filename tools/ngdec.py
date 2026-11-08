import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import json,struct,sys
S=_W+''
from PIL import Image
# glyph idx -> char via PS1 table assumed for kana; use alignment map
ng={int(k,16):v for k,v in json.load(open(S+'/out/ngcd_code2char.json')).items()}
def dec(words):
    o=''
    for v in words:
        if v in ng: o+=ng[v]
        elif 0x2100<=v<0x2900: o+='〓'
        else: o+=f'<{v:x}>'
    return o
def msgs(fn):
    d=open(fn,'rb').read()
    w=[struct.unpack('>H',d[i:i+2])[0] for i in range(0,len(d)-1,2)]
    return w
