import sys,os,pickle,re,struct
d=open(sys.argv[1],'rb').read(); B=0x0800A000
ins=pickle.load(open(sys.argv[2],'rb'))
tg=[int(x,16) for x in sys.argv[3:]]
for a,(m,o,s) in sorted(ins.items()):
    v=None
    mm=re.match(r'\w+, \[pc, #(0x[0-9a-f]+|\d+)\]',o)
    if m.startswith('ldr') and mm:
        la=((a+4)&~3)+int(mm.group(1),0)
        if 0<=la-B<len(d)-4: v=struct.unpack_from('<I',d,la-B)[0]
    elif m.startswith('adr'):
        p=o.split('#'); v=((a+4)&~3)+int(p[1],0)
    elif m=='subw' and 'pc' in o:
        v=((a+4)&~3)-int(o.split('#')[1],0)
    elif m=='addw' and 'pc' in o:
        v=((a+4)&~3)+int(o.split('#')[1],0)
    if v is not None:
        for t in tg:
            if t-16<=v<=t+16: print(hex(a),m,o,'->',hex(v))
