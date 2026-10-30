import os,pickle,re,struct,sys,collections
d=open(sys.argv[1],'rb').read(); B=0x0800A000
ins=pickle.load(open(os.path.dirname(os.path.abspath(__file__))+'/ins.pkl','rb')); A=sorted(ins)
lo,hi=int(sys.argv[2],16),int(sys.argv[3],16)
def lit(a,o):
    mm=re.search(r'\[pc, #(0x[0-9a-f]+|\d+)\]',o)
    if not mm: return None
    la=((a+4)&~3)+int(mm.group(1),0)
    if 0<=la-B<len(d)-4: return struct.unpack_from('<I',d,la-B)[0]
def desc(v):
    if v is None: return ''
    if B<=v<B+len(d):
        o=v-B; s=d[o:o+24].split(b'\0')[0]
        try:
            t=s.decode('utf-8')
            if len(t)>=2 and all(c.isprintable() for c in t): return '"%s"'%t
        except: pass
        return 'rom:%x'%o
    return hex(v)
calls=collections.Counter()
for a in A:
    if not(lo<=a<hi): continue
    m,o,_=ins[a]
    if m.startswith('ldr') and 'pc' in o: print(hex(a),m,o.split(',')[0],desc(lit(a,o)))
    elif m in('movs','movw','mov.w','mvn','mvns','movt') and '#' in o: print(hex(a),m,o)
    elif m=='bl': print(hex(a),'bl',o); calls[o]+=1
    elif m=='adr': print(hex(a),m,o)
print(calls.most_common(25),file=sys.stderr)
