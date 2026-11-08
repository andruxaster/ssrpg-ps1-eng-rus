"""Title menu: Cyrillic glyphs in SFIX0000.FIX + strings in PROG.PRG (run after uibuild)."""
import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys
S=_W+''
sys.path.insert(0,S+'/tools')
import pixfont,fixr
B=S+'/ru/build'
fx=bytearray(open(S+'/ngcd/en/SFIX0000.FIX','rb').read())
HG=dict(zip('НОВАРТСЕКМХ','HOBAPTCEKMX'))
NEW='ЯИГЗУЬПЦБ'
CODES=[0xf0,0xf1,0xf2,0xf3,0xf4,0xf5,0xf6,0xf7,0xf8]
ROWC=[7,7,6,5,4,3,2,2]
def enc(px):
    b=bytearray(32)
    for ci,x0 in enumerate((4,6,0,2)):
        for y in range(8): b[ci*8+y]=px[y][x0]|(px[y][x0+1]<<4)
    return bytes(b)
cmap={}
for ch,code in zip(NEW,CODES):
    g=pixfont.glyph8(ch)
    on=set((x,y) for y in range(8) for x in range(8) if g[y][x])
    px=[[0]*8 for _ in range(8)]
    for x,y in on:
        for dx,dy in ((1,0),(0,1),(1,1)):
            if 0<=x+dx<8 and 0<=y+dy<8 and (x+dx,y+dy) not in on: px[y+dy][x+dx]=15
    for x,y in on: px[y][x]=ROWC[y]
    t=0x500+code; fx[t*32:t*32+32]=enc(px); cmap[ch]=code
for k,v in HG.items(): cmap[k]=ord(v)
cmap[' ']=0x20
def s(t): return bytes(cmap[c] for c in t)+b'\0'
blob=s('НОВАЯ ИГРА')+s('ЗАГРУЗИТЬ')+s('ОПЦИИ')+s('БОНУС')
assert len(blob)==33
p=bytearray(open(B+'/PROG.PRG','rb').read())
assert p[0x520d8:0x520e2]==b'GAME START', p[0x520d8:0x520e2]
p[0x520d8:0x520f9]=blob
assert p[0x520fa:0x52102]==bytes.fromhex('000520d8000520e3')
p[0x52102:0x52106]=bytes.fromhex('000520ed')
assert p[0x52106:0x5210a]==bytes.fromhex('000520f3')
open(B+'/PROG.PRG','wb').write(p); open(B+'/SFIX0000.FIX','wb').write(fx)
print('title ok')
