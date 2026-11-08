import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys
S=_W+''
sys.path.insert(0,S+'/tools')
import gfx,relabel
T={'text_idx':{9,2}}
LABELS={
'status':[((40,14,71,28),'СТАТУС',dict(font='tiny',**T)),((88,14,119,28),'ВЕЩИ',dict(font='tiny',**T)),((136,14,167,28),'ПРИЕМЫ',dict(font='tiny',**T)),((184,14,215,28),'ЭКИП.',dict(font='tiny',**T)),((232,14,263,28),'ОПЦИИ',dict(font='tiny',**T)),
          ((160,49,183,59),'СИЛ',dict(pitch=8)),((160,65,183,75),'АТК',dict(pitch=8)),((160,81,183,91),'УДЧ',dict(pitch=8)),((224,49,247,59),'СКР',dict(pitch=8)),((224,65,247,75),'ЗЩТ',dict(pitch=8)),((224,81,247,91),'УКЛ',dict(pitch=8)),
          ((166,99,214,120),'ОПЫТ',dict(pitch=8))],
'special':[((56,67,95,76),'НУЖНО',dict(pitch=7)),((26,191,86,206),'АТАКА\nСТИХИЕЙ',dict(pitch=8))],
'options':[((40,47,103,62),'КЛЮЧ. ВЕЩИ',dict(pitch=7))],
'input':[],
'vinput':[],
'bitems':[((19,180,60,186),'ВЕЩИ',dict(pitch=7,text_idx={2},body=2,shadow=7,font_h=7))],
'battle':[((19,180,60,186),'ПРИЕМЫ',dict(pitch=6,text_idx={2},body=2,shadow=7,font_h=7))],
'settings2':[((24,44,87,62),'НАСТРОЙКИ',dict(pitch=7)),((120,61,157,78),'БЫСТРО',dict(pitch=6)),((230,61,263,78),'МЕДЛ.',dict(pitch=6)),
          ((40,79,87,94),'СКОРОСТЬ\nТЕКСТА',dict(pitch=6)),((40,111,87,126),'СКОРОСТЬ\nБОЯ',dict(pitch=6)),((40,143,135,158),'СПОСОБ ВВОДА\nПРИЕМОВ',dict(pitch=8))],
}
def shift_arrow(sc):
    snap={(x,y):sc.get(x,y) for x in range(150,172) for y in range(62,79)}
    for x in range(159,168):
        for y in range(62,79):
            if snap[(x-3,y)] in (9,2,1,10,0xa) or snap[(x,y)] in (9,2,1,10,0xa): sc.put(x,y,snap[(x-3,y)])
    for x in range(156,159):
        for y in range(62,79):
            if snap[(x,y)] in (9,2,1,10,0xa): sc.put(x,y,sc.get(x,y-16))
import pixfont
def texture_fill(sc,rect,region,skip):
    import collections
    tex=collections.defaultdict(collections.Counter)
    X0,Y0,X1,Y1=region
    for y in range(Y0,Y1):
        for x in range(X0,X1):
            if any(a<=x<=c and b<=y<=d for a,b,c,d in skip): continue
            v=sc.get(x,y)
            if v in (0xc,0xd,0xe,0xf): tex[(x%16,y%32)][v]+=1
    x0,y0,x1,y1=rect
    for y in range(y0,y1+1):
        for x in range(x0,x1+1):
            if tex[(x%16,y%32)]: sc.put(x,y,tex[(x%16,y%32)].most_common(1)[0][0])
GRAD=[0xc,0xc,0x7,0x7,0xb,0xa,0x8,0x8]
def outline_text(sc,rect,lines,pitch=7,outline=1,shadow=2):
    x0,y0,x1,y1=rect; W=x1-x0+1; H=y1-y0+1
    bms=[pixfont.render_line(l,pitch) for l in lines]
    bms=[[r for r in bm if True][:7] for bm in bms]
    tot=len(bms)*9+(len(bms)-1)*1
    oy=y0+(H-tot)//2+1
    for bm in bms:
        w=len(bm[0]); ox=x0+(W-w)//2
        on=set((ox+x,oy+y) for y in range(len(bm)) for x in range(w) if bm[y][x])
        ring=set((x+dx,y+dy) for x,y in on for dx in (-1,0,1) for dy in (-1,0,1))-on
        sh=set((x+1,y+1) for x,y in ring)-on-ring
        for p in sh: sc.put(*p,shadow)
        for p in ring: sc.put(*p,outline)
        for x,y in on: sc.put(x,y,GRAD[y-oy])
        oy+=10
CH_RECTS=[(120,66,207,87),(120,90,207,111)]
def chapter_titles(sc):
    for r in CH_RECTS: texture_fill(sc,r,(110,40,215,135),CH_RECTS)
    outline_text(sc,CH_RECTS[0],['ПАДЕНИЕ','ТЕМНЫХ НЕБЕС'])
    outline_text(sc,CH_RECTS[1],['ПЛАЧ БЛЕДНЫХ','ЦВЕТОВ'])
BIGF=S+'/fonts/fontsource-pixelify-sans-5.3.0/package/files/pixelify-sans-cyrillic-700-normal.woff'
BGR=[0xe,0x7,0x7,0x7,0xc,0xc,0xc,0xc,0xc,0xf,0xf,0xa,0xa,0x9,0x9,0x9,0x9]
def big_text(sc,x0,ytop,text,size=17):
    from PIL import Image,ImageFont,ImageDraw
    f=ImageFont.truetype(BIGF,size)
    im=Image.new('1',(400,50)); d=ImageDraw.Draw(im); d.fontmode='1'; d.text((4,10),text,font=f,fill=1)
    r=Image.new('1',(60,50)); dr=ImageDraw.Draw(r); dr.fontmode='1'; dr.text((4,10),'Н',font=f,fill=1); rt=r.getbbox()[1]
    bb=im.getbbox()
    on=set((x0+x-bb[0],ytop+y-rt) for y in range(bb[1],bb[3]) for x in range(bb[0],bb[2]) if im.getpixel((x,y)))
    ring=set((x+dx,y+dy) for x,y in on for dx in (-1,0,1) for dy in (-1,0,1))-on
    sh=set((x+1,y+1) for x,y in ring)-on-ring
    for p in sh: sc.put(*p,8)
    for p in ring: sc.put(*p,1)
    for x,y in on: sc.put(x,y,BGR[max(0,min(len(BGR)-1,y-ytop))])
    return bb[2]-bb[0]
VI_RECTS=[(119,65,264,88),(119,89,264,112)]
def vinput(sc):
    for x0,y0,x1,y1 in VI_RECTS:
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):
                tp=sc.top.get((x,y))
                if tp and sc.wr(tp[0]): sc.tilepx(tp[0])[tp[2]][tp[1]]=0
    print('  vinput widths',big_text(sc,121,68,'ФАЙТИНГ ВВОД'),big_text(sc,121,92,'ВЫБОР В МЕНЮ'))
PRE={'settings2':[shift_arrow],'input':[chapter_titles],'vinput':[vinput]}
def run(names=None,preview=True,save=True):
    for name,labs in LABELS.items():
        if names and name not in names: continue
        sc=gfx.GScreen(name)
        for fn in PRE.get(name,[]): fn(sc)
        for rect,txt,kw in labs:
            kw=dict(kw); kw.setdefault('body',9); kw.setdefault('shadow',2)
            r=relabel.relabel(sc,rect,txt,**kw)
            if r.get('width',0)>r.get('avail',999): print('  WARN wide',name,txt,r)
        if preview: relabel.preview(sc,S+'/ru/gfx/prev_%s.png'%name)
        print(name,'tiles committed',sc.commit(),'map',sc.map)
    if save: gfx.save()

# direct sheet-space labels (32 tiles per row)
import sheet
STRIPS=[('CHIP000F',2,25,[((16*i,10,16*i+15,15),t,dict(font='tiny',text_idx={9,1,3,8,0xa},shadow=1)) for i,t in enumerate(['НЕТ','ОГН','ЛЕД','ВЕТ','ЭЛК','СВТ','ТЬМ'])]
                          +[((176,0,239,15),'ТЕКУЩАЯ\nСТИХИЯ',dict(pitch=8,text_idx={9,2}))]),
        ('CHIP000F',1543,10,[((0,0,47,15),'УРОВЕНЬ\nОРУЖИЯ',dict(pitch=6,text_idx={9,2})),((48,0,159,15),'УЖЕ ДОСТИГНУТ\nМАКС. УРОВЕНЬ',dict(pitch=8,text_idx={9,2}))]),
        ('CHIP000F',1554,27,[((0,0,63,15),'СМЕНА\nСТИХИИ',dict(pitch=8,text_idx={9,2})),((64,0,111,15),'ЗАКАЛКА\nОРУЖИЯ',dict(pitch=6,text_idx={9,2})),
                             ((128,0,223,15),'ПАДЕНИЕ\nТЕМНЫХ НЕБЕС',dict(pitch=8,text_idx={9,2})),((224,0,319,15),'ПЛАЧ БЛЕДНЫХ\nЦВЕТОВ',dict(pitch=8,text_idx={9,2}))])]
SHEET={
'CHIPF001':[((400,432,463,447),'ВЫХОД В МЕНЮ',dict(font='tiny',text_idx={9,2})),((464,432,511,447),'ВЕРНУТЬСЯ',dict(font='tiny',text_idx={9,2})),
   ((320,512,367,527),'ТЕКУЩАЯ\nСТИХИЯ',dict(pitch=6)),
   ((400,522,415,527),'ОГН',dict(font='tiny',shadow=0)),((416,522,431,527),'ЛЕД',dict(font='tiny',shadow=0)),((432,522,447,527),'ВЕТ',dict(font='tiny',shadow=0)),
   ((448,522,463,527),'ЭЛК',dict(font='tiny',shadow=0)),((464,522,479,527),'СВТ',dict(font='tiny',shadow=0)),((480,522,495,527),'ТЬМ',dict(font='tiny',shadow=0)),((496,522,511,527),'НЕТ',dict(font='tiny',shadow=0)),
   ((64,528,111,543),'УРОВЕНЬ\nОРУЖИЯ',dict(pitch=6)),((128,528,191,543),'за ур.',dict(font='dlg')),((224,528,351,543),'УЖЕ ДОСТИГНУТ\nМАКС. УРОВЕНЬ',dict(pitch=8))],
}
def run_sheets(preview=True):
    from PIL import Image
    for f,labs in SHEET.items():
        sh=sheet.Sheet(f)
        for rect,txt,kw in labs:
            kw=dict(kw); kw.setdefault('body',9); kw.setdefault('shadow',2)
            r=relabel.relabel(sh,rect,txt,**kw)
            if r.get('width',0)>r.get('avail',999): print('  WARN wide',f,txt,r)
        if preview:
            ys=sorted(set(r[1]//16 for r,_,_ in labs))
            im=Image.new('L',(512,16*len(ys)))
            for j,row in enumerate(ys):
                for y in range(16):
                    for x in range(512):
                        v=sh.get(x,row*16+y); im.putpixel((x,j*16+y),(v or 0)*16)
            im.resize((1024,32*len(ys)),Image.NEAREST).save(S+'/ru/gfx/sheet_%s.png'%f)
        print(f,'sheet tiles',sh.commit())
    for f,b,c,labs in STRIPS:
        sh=sheet.Sheet(f,cols=c,base=b,count=c)
        for rect,txt,kw in labs:
            kw=dict(kw); kw.setdefault('body',9); kw.setdefault('shadow',2)
            r=relabel.relabel(sh,rect,txt,**kw)
            if r.get('width',0)>r.get('avail',999): print('  WARN wide',f,txt,r)
        if preview:
            im=Image.new('L',(c*16,16))
            for y in range(16):
                for x in range(c*16): im.putpixel((x,y),(sh.get(x,y) or 0)*16)
            im.resize((c*48,48),Image.NEAREST).save(S+'/ru/gfx/strip_%d.png'%b)
        print(f,b,'strip tiles',sh.commit())

if __name__=='__main__':
    run(sys.argv[1:] or None,save=False); run_sheets(); gfx.save()
