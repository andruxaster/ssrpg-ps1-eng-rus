import sys
src,dst,off=sys.argv[1],sys.argv[2],int(sys.argv[3])
with open(src,'rb') as f, open(dst,'wb') as o:
    while (s:=f.read(2352)):
        if len(s)<2352: break
        o.write(s[off:off+2048])
