import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys
S=_W+''
sys.path.insert(0,S+'/tools')
import rufont
LINES=[(3004,14,"1788 год. Сегунат Токугава"),(3018,15,"правил мирной страной,"),(3033,12,"и кодекс Бусидо"),
(3045,15,"еще не канул в историю."),(3060,15,"Но темные силы начали"),(3075,16,"порождать загадочных тварей..."),
(3091,14,"Однако нашлись те, кто"),(8489,13,"поднял оружие против"),(8502,14,"демонических врагов. Их"),
(8516,14,"отличали несгибаемая воля"),(8530,12,"и сильный дух."),(8542,14,"О них сложили немало"),
(8556,12,"легенд о самураях."),(8568,12,"Тех, кто жил по этому"),(8580,16,"пути, называли носителями..."),(8596,8,"Духа самурая!")]
def half(ch,side):
    h=rufont.half4(ch,side)
    return [[0 if v>=12 else v for v in row] for row in h]
def build(out):
    for start,cnt,txt in LINES:
        assert len(txt)<=2*cnt,(txt,cnt)
        W=cnt*16; img=[[0]*W for _ in range(16)]
        x0=(W-len(txt)*8)//2
        for i,ch in enumerate(txt):
            if ch==' ': continue
            h=half(ch,i%2)
            for y in range(16):
                for x in range(8):
                    if h[y][x]: img[y][x0+i*8+x]=h[y][x]
        for k in range(cnt):
            p=[row[k*16:(k+1)*16] for row in img]
            t=start+k; out[t*128:(t+1)*128]=rufont.encode_tile(p)
if __name__=='__main__':
    import brushru
    chip=bytearray(open(S+'/ru/intro/CHIP00B2_brush.SPR','rb').read())
    build(chip)
    open(S+'/ru/build/CHIP00B2.SPR','wb').write(chip)
    # preview
    from spr import tile
    from PIL import Image
    im=Image.new('L',(16*16,18*len(LINES)),0)
    for r,(st,cnt,_) in enumerate(LINES):
        for c in range(cnt):
            p=tile(chip,st+c)
            for y in range(16):
                for x in range(16):
                    if p[y][x]: im.putpixel((c*16+x,r*18+y),60+p[y][x]*12)
    im.resize((im.width*2,im.height*2)).save(S+'/ru/intro/story_ru.png')
