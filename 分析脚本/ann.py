import sys,os,pickle,re,struct
sys.stdout.reconfigure(encoding='utf-8')
F=sys.argv[1]; d=open(F,'rb').read(); B=0x0800A000
ins=pickle.load(open(sys.argv[2],'rb')); A=sorted(ins)
N={0x801f78c:'img_create',0x80201ac:'img_set_src',0x8021644:'obj_align',0x8021660:'obj_align_to',0x8020570:'label_create',
 0x8020e4c:'label_set_text',0x8024df6:'set_text_font',0x8024ddc:'set_text_color',0x8024d7c:'set_bg_color',
 0x801bc76:'color_hex',0x801bcfe:'color_hex',0x801bcba:'color_hex',0x801bc98:'color_hex',0x801bcdc:'color_hex',
 0x8021524:'HIDE(add_flag)',0x8021ce4:'SHOW(clear_flag)',0x80105f8:'sprintf',0x800a1ca:'memcpy',
 0x800c14c:'build_main',0x801050c:'build_top(scale/needle/title)',0x80100a0:'update_top',0x800b030:'update_main',
 0x800e3a0:'build_lang',0x800e764:'build_menu',0x800f144:'build_prompt',0x800cc60:'iic_err_record',0x800b01e:'delay_ms?'}
if os.path.exists('names.txt'):
    for l in open('names.txt',encoding='utf-8'):
        p=l.split(None,1)
        if len(p)==2: N[int(p[0],16)]=p[1].strip()
PER={0x40010800:'GPIOA',0x40010C00:'GPIOB',0x40011000:'GPIOC',0x40011400:'GPIOD',0x40011800:'GPIOE',0x40011C00:'GPIOF',0x40012000:'GPIOG'}
REG={0:'CRL',4:'CRH',8:'IDR',0xC:'ODR',0x10:'BSRR',0x14:'BRR'}
def bb(v):
    if 0x42000000<=v<0x44000000:
        off=(v-0x42000000)//32; bit=((v-0x42000000)%32)//4; pa=0x40000000+off
        for b,n in PER.items():
            if b<=pa<b+0x400: return '%s.%s.%d'%(n,REG.get((pa-b)&~3,hex(pa-b)), bit+8*((pa-b)&3))
        return 'BB[%x.%d]'%(pa,bit)
    if 0x22000000<=v<0x22100000:
        off=(v-0x22000000)//32; bit=((v-0x22000000)%32)//4; return 'RAMBB[%x.%d]'%(0x20000000+off,bit)
    return None
strs={}
def sat(v):
    if B<=v<B+len(d):
        s=d[v-B:v-B+40].split(b'\0')[0]
        try:
            t=s.decode()
            if len(t)>=2 and t.isprintable(): return '"%s"'%t
        except: pass
        return 'rom:%x'%(v-B)
    b=bb(v)
    if b: return b
    if 0x20000000<=v<0x20010000: return 'ram:%x'%v
    for base,n in PER.items():
        if base<=v<base+0x400: return '%s+%x'%(n,v-base)
    return hex(v)
lo,hi=int(sys.argv[3],16),int(sys.argv[4],16)
R={}
for a in A:
    if not(lo<=a<hi): continue
    m,o,_=ins[a]; c=''
    mr=re.search(r'\[(r\d+|sb|sl|fp|ip|lr), #(0x[0-9a-f]+|\d+)\]',o)
    if mr and mr.group(1) in R:
        v=R[mr.group(1)]+int(mr.group(2),0); c=sat(v)
    if mr is None:
        mr2=re.search(r'\[(r\d+|sb|sl|fp|ip|lr)\]',o)
        if mr2 and mr2.group(1) in R: c=sat(R[mr2.group(1)])
    mm=re.search(r'\[pc, #(0x[0-9a-f]+|\d+)\]',o)
    if m.startswith('ldr') and mm:
        la=((a+4)&~3)+int(mm.group(1),0)
        if 0<=la-B<len(d)-4:
            v=struct.unpack_from('<I',d,la-B)[0]; c=sat(v); R[o.split(',')[0]]=v
    elif m.startswith('adr'): c=sat(((a+4)&~3)+int(o.split('#')[1],0))
    elif m in('bl','b.w','b') and o.startswith('#'):
        t=int(o[1:],16); c=N.get(t,'')
    dst=o.split(',')[0].strip()
    if not (m.startswith('ldr') and 'pc' in o) and m not in ('str','strb','strh','str.w','strb.w','strh.w','cmp','cmp.w','tst','push','pop','b','bl','cbz','cbnz','stm.w','stm','strd') and not m.startswith('b') and not m.startswith('st') and dst in R:
        if m in('adds','add','add.w') and o.count('#')==1 and o.split(',')[1].strip()==dst: R[dst]+=int(o.split('#')[1],0)
        elif m in('adds','add','add.w') and len(o.split(','))==2 and '#' in o: R[dst]+=int(o.split('#')[1],0)
        elif m in('subs','sub','sub.w') and len(o.split(','))==2 and '#' in o: R[dst]-=int(o.split('#')[1],0)
        else: R.pop(dst,None)
    if m=='bl':
        for r in ('r0','r1','r2','r3','ip','lr'): R.pop(r,None)
    if m in('tbb','tbh'):
        n=None; k=A.index(a)
        for j in range(1,5):
            pm,po,_=ins[A[k-j]]
            mm2=re.match(r'(r\d+), #(0x[0-9a-f]+|\d+)',po)
            if pm.startswith('cmp') and mm2: n=int(mm2.group(2),0); break
        n=n or 16; tb=a+4; cs=[]
        for i in range(n):
            if m=='tbb': off=d[tb-B+i]
            else: off=struct.unpack_from('<H',d,tb-B+2*i)[0]
            cs.append('%d:%x'%(i,tb+2*off))
        c='CASES '+' '.join(cs)
    print('%x  %-7s %-28s %s'%(a,m,o,(';'+c) if c else ''))
