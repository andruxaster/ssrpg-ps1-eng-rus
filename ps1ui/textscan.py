import sys,glob,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import fpsi
from PIL import Image,ImageDraw
S=fpsi.S
def scan(files,out,minasp=2.2):
    items=[]; seen=set()
    for fn in files:
        c=open(S+'/ps1/fs/'+fn,'rb').read()
        for off,ents in fpsi.packages(c):
            for k,(t,o,s) in enumerate(ents):
                if t&0xffff!=7: continue
                blob=c[off+o:off+o+s]
                if hash(blob) in seen: continue
                seen.add(hash(blob))
                try: b=fpsi.Bank(blob)
                except Exception: continue
                for gi in range(len(b.groups)):
                    try: im=b.render(gi)
                    except Exception: continue
                    if im and im.width>=40 and im.width/im.height>=minasp and im.height<=int(os.environ.get("MAXH","999")):
                        items.append(('%s %x/%d/%d'%(fn.split('/')[-1][:-4],off,k,gi),im))
    W=1600; x=y=0; rowh=0; pos=[]
    for k,im in items:
        if x+im.width>W: x=0; y+=rowh+12; rowh=0
        pos.append((x,y)); x+=im.width+6; rowh=max(rowh,im.height)
    o=Image.new('RGB',(W,y+rowh+12),(40,40,90)); d=ImageDraw.Draw(o)
    for (px,py),(k,im) in zip(pos,items):
        o.paste(im,(px,py+10)); d.text((px,py),k,fill=(255,255,0))
    o.save(out); return len(items),o.size
if __name__=='__main__':
    print(scan(sys.argv[2:],sys.argv[1]))
