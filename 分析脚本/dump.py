import sys,struct,zlib,os
d=open(sys.argv[1],'rb').read(); O=sys.argv[2]
def png(path,w,h,rows):
    raw=b''.join(b'\x00'+bytes(r) for r in rows)
    def ch(t,b): return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
    open(path,'wb').write(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+ch(b'IDAT',zlib.compress(raw))+ch(b'IEND',b''))
items=[l.split() for l in open(sys.argv[3])]
for dsc,cf,wh,sz,p in items:
    w,h=map(int,wh.split('x')); p=int(p,16)
    rows=[]
    if cf=='IDX8':
        pal=[d[p+4*k:p+4*k+4] for k in range(256)]  # lv_color32: B,G,R,A
        px=p+1024
        for y in range(h):
            r=[]
            for x in range(w):
                c=pal[d[px+y*w+x]]; r+= [c[2],c[1],c[0],c[3]]
            rows.append(r)
    else: # TC_ALPHA 16bit RGB565 + A
        for y in range(h):
            r=[]
            for x in range(w):
                o=p+(y*w+x)*3; v=d[o]|d[o+1]<<8; a=d[o+2]
                r+=[(v>>11)*255//31,((v>>5)&63)*255//63,(v&31)*255//31,a]
            rows.append(r)
    png(os.path.join(O,'img_%s_%s.png'%(dsc,wh)),w,h,rows)
    print('ok',dsc,wh)
