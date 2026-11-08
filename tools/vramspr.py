import struct,sys
def sprites(path):
    v=open(path,'rb').read()
    W=lambda i: struct.unpack('<H',v[2*i:2*i+2])[0]
    out=[]; h=0; x=y=0
    for spr in range(1,381):
        scb3=W(0x8200+spr); scb4=W(0x8400+spr); scb2=W(0x8000+spr)
        if scb3&0x40:
            x=(x+ ((scb2>>8)&0xf)+1) if False else x+16
        else:
            h=scb3&0x3f; y=(496-(scb3>>7))&0x1ff; x=scb4>>7
        if h==0: continue
        ts=[]
        for r in range(min(h,32)):
            lo=W(spr*64+r*2); at=W(spr*64+r*2+1)
            ts.append(((lo|(((at>>4)&0xf)<<16)), at>>8, at&3))
        out.append((spr,x&0x1ff,y,h,ts))
    return out
if __name__=='__main__':
    for s in sprites(sys.argv[1]):
        tl=[t[0]-22784 for t in s[4]]
        print(s[0],'x',s[1],'y',s[2],'h',s[3],'pal',s[4][0][1],tl[:12])
