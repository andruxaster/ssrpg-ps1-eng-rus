import sys
from PIL import Image
fs=sys.argv[2:]; out=sys.argv[1]
ims=[Image.open(f) for f in fs]
cols=min(4,len(ims)); rows=(len(ims)+cols-1)//cols
m=Image.new('RGB',(cols*320,rows*240))
for k,i in enumerate(ims): m.paste(i.resize((320,240)),((k%cols)*320,(k//cols)*240))
m.save(out)
