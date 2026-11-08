import sys,numpy as np
from PIL import Image
def load(p): return np.frombuffer(open(p,'rb').read(),'<u2').reshape(512,1024)
def rgb15(v):
    r=(v&31)<<3; g=((v>>5)&31)<<3; b=((v>>10)&31)<<3
    return np.stack([r,g,b],-1).astype(np.uint8)
def as4(v):
    # each u16 = 4 pixels 4bpp, grayscale
    a=np.stack([(v>>(4*k))&15 for k in range(4)],-1).reshape(512,4096)
    return (a*17).astype(np.uint8)
if __name__=='__main__':
    v=load(sys.argv[1])
    Image.fromarray(rgb15(v)).save(sys.argv[2]+'_16.png')
    Image.fromarray(as4(v)).save(sys.argv[2]+'_4.png')
