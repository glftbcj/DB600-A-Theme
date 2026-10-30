import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sys,struct,collections
from capstone import *
d=open(sys.argv[1],'rb').read()
BASE=0x0800A000
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB); md.detail=False
# linear sweep with resync
ins={}
off=0x130
END=int(sys.argv[2],16) if len(sys.argv)>2 else 0x20000
while off<END:
    got=False
    for i in md.disasm(d[off:END],BASE+off):
        ins[i.address]=(i.mnemonic,i.op_str,i.size)
        off=i.address-BASE+i.size; got=True
    if not got or off<END: off+=2
import pickle;pickle.dump(ins,open(sys.argv[1]+'.dis.pkl' if False else __import__('os').path.dirname(__import__('os').path.abspath(__file__))+'/ins.pkl','wb'))
# find bl targets preceded by movs r0,#imm
addrs=sorted(ins)
calls=collections.defaultdict(list)
for k,a in enumerate(addrs):
    m,o,s=ins[a]
    if m=='bl':
        t=int(o.lstrip('#'),16)
        for j in range(1,3):
            if k-j<0: break
            pm,po,_=ins[addrs[k-j]]
            if pm in('movs','mov','mov.w') and po.startswith('r0, #'):
                calls[t].append((a,int(po.split('#')[1],0)));break
lcd={0x11,0x29,0x36,0x3a,0x2a,0x2b,0x2c,0x21,0xb2,0xe0,0xe1}
res=[]
for t,l in calls.items():
    vals=set(v for _,v in l)
    sc=len(vals&lcd)
    if sc>=3: res.append((sc,len(l),t,sorted(vals)[:60]))
for r in sorted(res,reverse=True)[:15]: print(r[0],r[1],hex(r[2]),[hex(x) for x in r[3]])
