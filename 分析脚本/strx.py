import sys; sys.stdout.reconfigure(encoding="utf-8")
import sys,os,pickle,re,struct,bisect
d=open(sys.argv[1],'rb').read(); B=0x0800A000
ins=pickle.load(open(sys.argv[2],'rb')); A=sorted(ins)
pushes=[a for a in A if ins[a][0] in('push','push.w','stmdb') and 'lr' in ins[a][1]]
def func(a):
    i=bisect.bisect_right(pushes,a)-1; return pushes[i] if i>=0 else 0
strs={}
for m in re.finditer(rb'(?:[\x20-\x7e]|[\xc2-\xf4][\x80-\xbf]{1,3}){2,}\x00',d[:0x52000]):
    try: s=m.group()[:-1].decode()
    except: continue
    if len(s)>=2 and re.search(r'[A-Za-z0-9一-鿿%Ω]',s): strs[B+m.start()]=s
refs={}
for a in A:
    m,o,_=ins[a]; v=None
    mm=re.match(r'\w+, \[pc, #(0x[0-9a-f]+|\d+)\]',o)
    if m.startswith('ldr') and mm:
        la=((a+4)&~3)+int(mm.group(1),0)
        if 0<=la-B<len(d)-4: v=struct.unpack_from('<I',d,la-B)[0]
    elif m.startswith('adr'): v=((a+4)&~3)+int(o.split('#')[1],0)
    elif m=='subw' and 'pc' in o: v=((a+4)&~3)-int(o.split('#')[1],0)
    elif m=='addw' and 'pc' in o: v=((a+4)&~3)+int(o.split('#')[1],0)
    if v in strs: refs.setdefault(v,[]).append(a)
# pointer tables
for o in range(0,len(d)-4,4):
    v=struct.unpack_from('<I',d,o)[0]
    if v in strs and o>=0x20000: refs.setdefault(v,[]).append(-(B+o))
for v in sorted(strs):
    r=refs.get(v,[])
    if not r: continue
    print('%x %-22r %s'%(v-B,strs[v],' '.join(('tbl@%x'%(-x-B)) if x<0 else '%x(f%x)'%(x,func(x)) for x in r[:6])))
