import os,pickle,re,struct,sys,collections
d=open(sys.argv[1],'rb').read(); B=0x0800A000
ins=pickle.load(open(os.path.dirname(os.path.abspath(__file__))+'/ins.pkl','rb')); A=sorted(ins); idx={a:k for k,a in enumerate(A)}
imgs={B+int(l.split()[0],16):l.split()[2] for l in open(os.path.dirname(os.path.abspath(__file__))+'/list.txt')}
fonts={0x8036e30:'font21',0x8030f14:'font73',0x8031a80:'font39'}
want=dict(imgs); want.update(fonts)
hits=collections.defaultdict(list)
for a,(m,o,s) in ins.items():
    mm=re.match(r'\w+, \[pc, #(0x[0-9a-f]+|\d+)\]',o)
    if m.startswith('ldr') and mm:
        la=((a+4)&~3)+int(mm.group(1),0)
        if 0<=la-B<len(d)-4:
            v=struct.unpack_from('<I',d,la-B)[0]
            if v in want: hits[v].append(a)
for v in sorted(want):
    print('%-8s %x <- %s'%(want[v],v-B,' '.join(hex(x) for x in sorted(hits[v]))))
