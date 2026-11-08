import sys,capstone
md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
d=open(sys.argv[1],'rb').read()
a=int(sys.argv[2],16); end=a+int(sys.argv[3],16)
while a<end:
    ins=list(md.disasm(d[a:a+10],a,1))
    if not ins: print('%06x  %s  dc.w'%(a,d[a:a+2].hex())); a+=2; continue
    i=ins[0]; print('%06x  %-20s %s %s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str)); a+=i.size
