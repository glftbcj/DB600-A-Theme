# contact sheet: stack all PNGs vertically on dark-gray bg with 2x scale
import sys,os,zlib,struct
O=sys.argv[1]
def readpng(p):
    b=open(p,'rb').read(); i=8; w=h=0; idat=b''
    while i<len(b):
        L=struct.unpack('>I',b[i:i+4])[0]; t=b[i+4:i+8]; c=b[i+8:i+8+L]
        if t==b'IHDR': w,h=struct.unpack('>II',c[:8])
        if t==b'IDAT': idat+=c
        i+=12+L
    raw=zlib.decompress(idat); rows=[raw[y*(w*4+1)+1:(y+1)*(w*4+1)] for y in range(h)]
    return w,h,rows
fs=sorted(f for f in os.listdir(O) if f.startswith('img_'))
imgs=[readpng(os.path.join(O,f)) for f in fs]
W=max(w for w,h,r in imgs)+8; rows=[]
for w,h,r in imgs:
    for y in range(h):
        line=bytearray()
        for x in range(W):
            if 4<=x<4+w:
                p=r[y][(x-4)*4:(x-4)*4+4]; a=p[3]/255
                bg=(0,0,0)
                line+=bytes(int(p[k]*a+bg[k]*(1-a)) for k in range(3))
            else: line+=b'\x20\x20\x20'
        rows.append(bytes(line))
    for _ in range(6): rows.append(b'\xff\x00\xff'*W)
raw=b''.join(b'\0'+r for r in rows)
def ch(t,b): return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
open(os.path.join(O,'sheet.png'),'wb').write(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,len(rows),8,2,0,0,0))+ch(b'IDAT',zlib.compress(raw))+ch(b'IEND',b''))
print(fs)
