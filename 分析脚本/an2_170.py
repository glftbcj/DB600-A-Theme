import sys,os,pickle
ins=pickle.load(open(os.path.dirname(os.path.abspath(__file__))+'/ins_170.pkl','rb'))
A=sorted(ins)
def show(a0,a1):
    for a in A:
        if a0<=a<a1: print(hex(a),*ins[a][:2])
mode=sys.argv[1]
if mode=='range': show(int(sys.argv[2],16),int(sys.argv[3],16))
elif mode=='seq':
    CMD,DAT=0x8004968,0x8004978
    out=[];last=None
    for k,a in enumerate(A):
        m,o,_=ins[a]
        if m=='bl' and int(o.lstrip('#'),16) in(CMD,DAT):
            t=int(o.lstrip('#'),16); v='?'
            for j in range(1,4):
                pm,po,_=ins[A[k-j]]
                if po.startswith('r0, #'): v=po.split('#')[1];break
                if po.startswith('r0,'): v=pm+' '+po;break
            if last is None or a-last>0x40: out.append('\n@%x '%a)
            out.append(('\nC%s:'%v) if t==CMD else ' %s'%v); last=a
    print(''.join(out))
elif mode=='callers':
    t=int(sys.argv[2],16)
    for a in A:
        m,o,_=ins[a]
        if m in('bl','b.w','b') and o.startswith('#') and int(o.lstrip('#'),16)==t: print(hex(a))
