import sys,os,pickle,struct,re,collections
d=open(sys.argv[1],'rb').read(); B=0x08000000
ins=pickle.load(open(os.path.dirname(os.path.abspath(__file__))+'/ins.pkl','rb'))
# literal pool loads ldr rX,[pc,#imm]
refs=collections.Counter(); where=collections.defaultdict(list)
for a,(m,o,s) in ins.items():
    mm=re.match(r'(r\d+|sb|sl|fp|ip|lr), \[pc, #(0x[0-9a-f]+|\d+)\]',o)
    if m.startswith('ldr') and mm:
        la=((a+4)&~3)+int(mm.group(2),0)
        if la-B+4<=len(d):
            v=struct.unpack_from('<I',d,la-B)[0]
            if B+0x1f000<=v<B+len(d): refs[v]+=1; where[v].append(a)
print('code end guess: last insn addr in pkl', hex(max(ins)))
for v,c in sorted(refs.items()): print(hex(v),c, ' '.join(hex(x) for x in where[v][:3]))
