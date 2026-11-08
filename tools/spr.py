import sys
from PIL import Image
def tile(d,t,bitrev=False):
    px=[[0]*16 for _ in range(16)]
    base=t*128
    for blk,(bx,by) in enumerate([(8,0),(8,8),(0,0),(0,8)]):
        for y in range(8):
            o=base+blk*32+y*4
            b=d[o:o+4]
            for x in range(8):
                bit= (7-x) if bitrev else x
                v=sum(((b[p]>>bit)&1)<<p for p in range(4))
                px[by+y][bx+x]=v
    return px
def render(d,start,count,cols,fn,bitrev=False):
    rows=(count+cols-1)//cols
    im=Image.new('L',(cols*17,rows*17),30)
    for k in range(count):
        t=start+k
        if (t+1)*128>len(d): break
        p=tile(d,t,bitrev)
        for y in range(16):
            for x in range(16):
                if p[y][x]: im.putpixel(((k%cols)*17+x,(k//cols)*17+y),min(255,60+p[y][x]*13))
    im.resize((im.width*2,im.height*2),Image.NEAREST).save(fn)
if __name__=='__main__':
    d=open(sys.argv[1],'rb').read()
    render(d,int(sys.argv[2],0),int(sys.argv[3]),32,sys.argv[4],len(sys.argv)>5)
