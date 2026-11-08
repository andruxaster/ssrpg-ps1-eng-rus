import sys,os
sys.path.insert(0,os.path.dirname(__file__))
import numpy as np
from PIL import Image
import cards
S=cards.S; OUT=S+'/mov/rep'; os.makedirs(OUT,exist_ok=True)
FONT=cards.FONTS[os.environ.get('CARDFONT','mister')]
# extended frame ranges (include faint fade frames)
RANGES={'kire':range(694,721),'samo':range(728,749),'shi':range(749,782),
        'takab':range(800,834),'kakugo':range(868,904),'michi':range(919,957)}
xml=['<?xml version="1.0"?>','<str-replace version="0.3">']
done=[]
for c in cards.CARDS:
    img,nm,ink,bgc=cards.make_card(c,FONT)
    ref=cards.frame(c['ref']); rm=cards.inkmask(ref,c['bg'])
    core=rm>0.6
    for i in RANGES[c['name']]:
        a=cards.frame(i)
        diff=np.abs(a-ref).max(2)
        if diff.mean()<0.5: out=img; kind='static'
        elif c['bg']=='B' and (lambda k:np.abs(a-ref*k).mean()<2.5)((a*ref).sum()/(ref*ref).sum()):
            k=(a*ref).sum()/(ref*ref).sum()
            if np.abs(1-k)<0.03: k=1.0
            out=bgc+(img-bgc)*k; kind='fade %.2f'%k
            if k<0.02: continue
        else:
            keep=diff>40
            # grow keep a bit to hold antialiased slash edges
            from scipy.ndimage import binary_dilation
            keep=binary_dilation(keep,iterations=1)
            out=np.where(keep[...,None],a,img); kind='composite %.3f'%keep.mean()
            if keep.mean()<0.002: out=img; kind='static~'
        fn='f%04d.png'%i
        Image.fromarray(np.clip(out,0,255).round().astype(np.uint8)).save(OUT+'/'+fn)
        xml.append('  <replace frame="%d">%s</replace>'%(i,fn))
        done.append((i,c['name'],kind))
xml.append('</str-replace>')
open(OUT+'/replace.xml','w').write('\n'.join(xml)+'\n')
for d in done:
    if d[2]!='static': print(*d)
print(len(done),'frames')
