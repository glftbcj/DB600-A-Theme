import sys,re
d=open(sys.argv[1],'rb').read()
lo=int(sys.argv[2],16)
for m in re.finditer(rb'(?:[\x20-\x7e]|[\xc2-\xf4][\x80-\xbf]{1,3}){2,}',d[lo:]):
    try: s=m.group().decode('utf-8')
    except: continue
    if len(s.strip())<2: continue
    if not re.search(r'[A-Za-z一-鿿]{2}|Ω|kHz|%',s): continue
    print(hex(lo+m.start()),repr(s))
