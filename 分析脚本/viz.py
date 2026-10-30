import sys,struct,zlib
d=open(sys.argv[1],'rb').read()
lo,hi,W,mode,out=int(sys.argv[2],16),int(sys.argv[3],16),int(sys.argv[4]),sys.argv[5],sys.argv[6]
buf=d[lo:hi]
rows=[]
if mode=='g8':
    H=len(buf)//W
    for y in range(H): rows.append(bytes(buf[y*W:(y+1)*W]))
    ct=0
elif mode=='g4':  # each byte -> 2 pixels, high nibble first
    H=len(buf)//W
    for y in range(H):
        r=bytearray()
        for b in buf[y*W:(y+1)*W]: r+=bytes([(b>>4)*17,(b&15)*17])
        rows.append(bytes(r))
    W*=2; ct=0
elif mode=='rgb565':
    H=len(buf)//(W*2)
    for y in range(H):
        r=bytearray()
        for x in range(W):
            v=buf[(y*W+x)*2]|buf[(y*W+x)*2+1]<<8
            r+=bytes([(v>>11)*255//31,((v>>5)&63)*255//63,(v&31)*255//31])
        rows.append(bytes(r))
    ct=2
raw=b''.join(b'\0'+r for r in rows)
def ch(t,b): return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
open(out,'wb').write(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,len(rows),8,ct,0,0,0))+ch(b'IDAT',zlib.compress(raw))+ch(b'IEND',b''))
print(W,len(rows))
