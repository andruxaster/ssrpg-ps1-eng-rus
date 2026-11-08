import sys
from PIL import Image
pfx,n,cols,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
sc=float(sys.argv[5]) if len(sys.argv)>5 else 1
ims=[Image.open(f'{pfx}{i}.png') for i in range(1,n+1)]
w,h=ims[0].size; rows=(n+cols-1)//cols; o=Image.new('RGB',(w*cols,h*rows))
for i,im in enumerate(ims): o.paste(im,((i%cols)*w,(i//cols)*h))
o.resize((int(w*cols*sc),int(h*rows*sc))).save(out)
