import sys,capstone
d=open(sys.argv[1],'rb').read(); base=0x80010000-0x800
a=int(sys.argv[2],16); n=int(sys.argv[3])
md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS32+capstone.CS_MODE_LITTLE_ENDIAN)
off=a-base
for ins in md.disasm(d[off:off+n*4],a): print(hex(ins.address),ins.mnemonic,ins.op_str)
