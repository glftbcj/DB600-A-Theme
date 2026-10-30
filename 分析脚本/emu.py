import os,pickle,re,struct,sys
d=open(sys.argv[1],'rb').read(); B=0x0800A000
ins=pickle.load(open(os.path.dirname(os.path.abspath(__file__))+'/ins.pkl','rb')); A=sorted(ins)
lo,hi=int(sys.argv[2],16),int(sys.argv[3],16)
F={0x801f78c:'img_create',0x80201ac:'img_set_src',0x8021644:'align',0x8021660:'align_to',0x8020570:'label_create',
   0x8020e4c:'label_set_text',0x8024df6:'set_font',0x8024ddc:'set_text_color',0x801bc76:'color_hex',0x801bcfe:'color_hex2'}
names={}
for l in open(os.path.dirname(os.path.abspath(__file__))+'/list.txt'):
    p=l.split(); names[B+int(p[0],16)]='IMG'+p[2]
names.update({0x8036e30:'FONT_cn21',0x8030f14:'FONT_cn73',0x8031a80:'FONT_num39'})
def s32(v): return v-(1<<32) if v&0x80000000 else v
R={}
def val(x):
    x=x.strip()
    if x.startswith('#'): return int(x[1:],0)&0xffffffff
    return R.get(x)
def show(v):
    if v is None: return '?'
    if v in names: return names[v]
    if B<=v<B+len(d):
        s=d[v-B:v-B+30].split(b'\0')[0]
        try:
            t=s.decode(); 
            if t and t.isprintable(): return '"%s"'%t
        except: pass
        return 'rom:%x'%(v-B)
    sv=s32(v)
    return str(sv) if -2000<sv<2000 else hex(v)
for a in A:
    if not(lo<=a<hi): continue
    m,o,_=ins[a]; ops=[x.strip() for x in o.split(',')]
    try:
        if m.startswith('ldr') and 'pc' in o:
            mm=re.search(r'#(0x[0-9a-f]+|\d+)\]',o); la=((a+4)&~3)+int(mm.group(1),0)
            R[ops[0]]=struct.unpack_from('<I',d,la-B)[0]
        elif m=='adr':
            R[ops[0]]=((a+4)&~3)+int(ops[1][1:],0)
        elif m in('movs','mov.w','movw','mov') and len(ops)==2:
            R[ops[0]]=val(ops[1])
        elif m in('mvn','mvns') and ops[1].startswith('#'):
            R[ops[0]]=(~int(ops[1][1:],0))&0xffffffff
        elif m in('subs','sub','sub.w','adds','add','add.w') and len(ops)==3 and ops[2].startswith('#'):
            b=val(ops[1]); k=int(ops[2][1:],0)
            R[ops[0]]=None if b is None else ((b-k) if m.startswith('sub') else (b+k))&0xffffffff
        elif m in('subs','adds') and len(ops)==2 and ops[1].startswith('#'):
            b=val(ops[0]); k=int(ops[1][1:],0)
            R[ops[0]]=None if b is None else ((b-k) if m.startswith('sub') else (b+k))&0xffffffff
        elif m=='bl':
            t=int(o[1:],16); n=F.get(t,hex(t))
            print(hex(a),n,show(R.get('r1')),show(R.get('r2')),show(R.get('r3')))
            for r in('r0','r1','r2','r3','ip'): R[r]=None
        elif ops and re.match(r'r\d+|sb|sl|fp|ip|lr',ops[0]) and m not in('cmp','cbz','cbnz','str','strh','strb','str.w','strh.w','strb.w','push','pop','b','bx','beq','bne','tst','it','ite') and not m.startswith('b') and not m.startswith('st'):
            R[ops[0]]=None
    except Exception as e:
        pass
