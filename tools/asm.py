R={'zero':0,'at':1,'v0':2,'v1':3,'a0':4,'a1':5,'a2':6,'a3':7,'t0':8,'t1':9,'t2':10,'t3':11,'s0':16,'gp':28,'sp':29,'ra':31}
def r(op,rs,rt,rd,sh,fn): return (op<<26)|(R[rs]<<21)|(R[rt]<<16)|(R[rd]<<11)|(sh<<6)|fn
def i(op,rs,rt,imm): return (op<<26)|(R[rs]<<21)|(R[rt]<<16)|(imm&0xffff)
def andi(rt,rs,imm): return i(0x0c,rs,rt,imm)
def ori(rt,rs,imm): return i(0x0d,rs,rt,imm)
def addiu(rt,rs,imm): return i(0x09,rs,rt,imm)
def sltiu(rt,rs,imm): return i(0x0b,rs,rt,imm)
def lui(rt,imm): return i(0x0f,'zero',rt,imm)
def lw(rt,off,base): return i(0x23,base,rt,off)
def sw(rt,off,base): return i(0x2b,base,rt,off)
def beq(rs,rt,off): return i(0x04,rs,rt,off)
def bne(rs,rt,off): return i(0x05,rs,rt,off)
def sll(rd,rt,sh): return r(0,'zero',rt,rd,sh,0)
def addu(rd,rs,rt): return r(0,rs,rt,rd,0,0x21)
def jr(rs): return r(0,rs,'zero','zero',0,8)
def j(t): return (2<<26)|((t>>2)&0x3ffffff)
def jal(t): return (3<<26)|((t>>2)&0x3ffffff)
NOP=0
