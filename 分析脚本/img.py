import sys,struct
d=open(sys.argv[1],'rb').read(); B=0x0800A000; N=len(d)
# LVGL v8 lv_img_header_t: cf:5 always_zero:3 reserved:2 w:11 h:11
bpp={4:16,5:24,6:24,7:1,8:2,9:4,10:8,11:1,12:2,13:4,14:8}  # 4=TRUE_COLOR(16bit),5=TC_ALPHA(24),6=TC_CHROMA
found=[]
for i in range(0,N-12,4):
    h,sz,p=struct.unpack_from('<III',d,i)
    cf=h&0x1f; az=(h>>5)&7; w=(h>>10)&0x7ff; hh=(h>>21)&0x7ff
    if az or cf not in bpp or not(1<=w<=480 and 1<=hh<=480): continue
    if not(B<=p<B+N): continue
    b=bpp[cf]
    if cf in(7,8,9,10): exp=(w*b+7)//8*hh + (1<<b)*4
    elif cf>=11: exp=(w*b+7)//8*hh
    else: exp=w*hh*b//8
    if sz==exp and p-B+sz<=N:
        found.append((i,cf,w,hh,sz,p-B))
names={4:'TRUE_COLOR',5:'TC_ALPHA',6:'TC_CHROMA',7:'IDX1',8:'IDX2',9:'IDX4',10:'IDX8',11:'A1',12:'A2',13:'A4',14:'A8'}
tot=0
for i,cf,w,h,sz,p in found:
    tot+=sz; print('dsc@%06x %-10s %3dx%-3d size=%6d data@%06x'%(i,names[cf],w,h,sz,p))
print(len(found),'images, bytes',tot)
