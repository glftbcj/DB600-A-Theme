import os,pickle,re,collections,struct,sys
d=open(sys.argv[1],'rb').read(); B=0x0800A000
ins=pickle.load(open(os.path.dirname(os.path.abspath(__file__))+'/ins.pkl','rb')); A=sorted(ins); idx={a:k for k,a in enumerate(A)}
def tgt(o):
    try: return int(o.lstrip('#'),16)
    except: return None
# wrappers: within first 12 insns of a function, set r1 to imm then tail-branch/ call same target
wr=collections.defaultdict(dict)
for k,a in enumerate(A):
    m,o,_=ins[a]
    if m in('b.w','b','bl') and o.startswith('#'):
        t=tgt(o)
        for j in range(1,5):
            pm,po,_=ins[A[k-j]]
            mm=re.match(r'(movs|mov\.w|movw) r1, #(0x[0-9a-f]+|\d+)$',po) if True else None
            mm=re.match(r'r1, #(0x[0-9a-f]+|\d+)$',po)
            if pm in('movs','mov.w','movw','mov') and mm:
                wr[t][a]=int(mm.group(1),0); break
cands=sorted(wr.items(),key=lambda x:-len(x[1]))[:3]
for t,v in cands: print('target',hex(t),len(v))
T=int(sys.argv[2],16)
props=collections.Counter(wr[T].values())
print(sorted(props.items()))
for a,p in sorted(wr[T].items())[:8]:
    print(hex(a),p, [ins[A[idx[a]-j]][:2] for j in range(5,0,-1)])
