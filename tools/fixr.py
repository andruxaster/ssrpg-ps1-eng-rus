import struct
def fixtile(f,t):
    b=f[t*32:(t+1)*32]; px=[[0]*8 for _ in range(8)]
    if len(b)<32: return px
    for ci,(x0) in enumerate((4,6,0,2)):
        for y in range(8):
            v=b[ci*8+y]; px[y][x0]=v&15; px[y][x0+1]=v>>4
    return px
def render(vram,fix):
    from PIL import Image
    W=lambda i: struct.unpack('<H',vram[2*i:2*i+2])[0]
    im=Image.new('L',(320,256),0)
    for col in range(40):
        for row in range(32):
            e=W(0x7000+col*32+row); t=e&0xfff
            p=fixtile(fix,t)
            for y in range(8):
                for x in range(8):
                    if p[y][x]: im.putpixel((col*8+x,row*8+y),40+p[y][x]*13)
    return im
