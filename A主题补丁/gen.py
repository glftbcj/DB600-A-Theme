# A 主题替换 UI1（黑色主题）：只写 UI1 专用的图片数据和颜色字面量，尺寸/格式/描述符都不动
import sys, struct, zlib, os, hashlib
SRC, OUT, PNGDIR = sys.argv[1], sys.argv[2], sys.argv[3]
d = bytearray(open(SRC, 'rb').read())
os.makedirs(PNGDIR, exist_ok=True)

def hx(s): s = s.lstrip('#'); return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))
BLACK = hx('000000'); FILL = hx('121110'); EDGE = hx('3A3631'); EDGE2 = hx('4A453F')
DIM = hx('6E685F'); TICK = hx('8C857B'); AMBER = hx('FFB547'); HOT = hx('FF6A3D'); SEL = hx('3A2810')

def png(path, w, h, px):
    raw = b''.join(b'\x00' + bytes(v for p in px[y*w:(y+1)*w] for v in p) for y in range(h))
    ch = lambda t, b: struct.pack('>I', len(b)) + t + b + struct.pack('>I', zlib.crc32(t + b) & 0xffffffff)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)) + ch(b'IDAT', zlib.compress(raw)) + ch(b'IEND', b''))

def rrect_cov(w, h, x0, y0, x1, y1, r, S=4):
    """圆角矩形覆盖率（0..1），超采样抗锯齿"""
    cov = [0.0] * (w * h)
    for y in range(h):
        for x in range(w):
            n = 0
            for sy in range(S):
                for sx in range(S):
                    px = x + (sx + .5) / S; py = y + (sy + .5) / S
                    if px < x0 or px > x1 or py < y0 or py > y1: continue
                    cx = min(max(px, x0 + r), x1 - r); cy = min(max(py, y0 + r), y1 - r)
                    if (px - cx) ** 2 + (py - cy) ** 2 <= r * r: n += 1
            cov[y * w + x] = n / (S * S)
    return cov

def mix(a, b, t): return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))

def frame(w, h, r, fill, edge, bw=1):
    """黑底上的圆角框：外圈 edge 色，内部 fill 色，角外透明"""
    outer = rrect_cov(w, h, 0, 0, w, h, r)
    inner = rrect_cov(w, h, bw, bw, w - bw, h - bw, max(r - bw, 0))
    px = []
    for i in range(w * h):
        if outer[i] == 0: px.append((0, 0, 0, 0)); continue
        c = mix(edge, fill, inner[i])
        px.append(c + (round(255 * outer[i]),))
    return px

def hline(px, w, y, x0, x1, col, a=255):
    for x in range(x0, x1): px[y * w + x] = col + (a,)

def decode_idx8(p, w, h):
    pal = [d[p+4*k:p+4*k+4] for k in range(256)]
    return [(pal[i][2], pal[i][1], pal[i][0], pal[i][3]) for i in d[p+1024:p+1024+w*h]]

def write_idx8(p, w, h, px, name):
    # 量化到 ≤256 色：先精确，超了就逐步降精度
    for q in (1, 2, 4, 8, 16):
        qp = [tuple((v // q) * q + (q // 2 if q > 1 else 0) if k < 3 else min(255, (v // q) * q + (q // 2 if q > 1 else 0)) for k, v in enumerate(c)) if c[3] else (0, 0, 0, 0) for c in px]
        cols = sorted(set(qp))
        if len(cols) <= 256: break
    else: raise SystemExit('too many colors ' + name)
    idx = {c: i for i, c in enumerate(cols)}
    pal = b''.join(bytes((c[2], c[1], c[0], c[3])) for c in cols) + b'\0' * 4 * (256 - len(cols))
    data = pal + bytes(idx[c] for c in qp)
    assert len(data) == 1024 + w * h
    d[p:p+len(data)] = data
    png(os.path.join(PNGDIR, name + '.png'), w, h, qp)
    print('%-12s %dx%d @%06x colors=%d q=%d' % (name, w, h, p, len(cols), q))

def check_dsc(dsc, cf, w, h, p):
    hd, sz, ptr = struct.unpack_from('<III', d, dsc)
    assert hd & 0x1f == cf and (hd >> 10) & 0x7ff == w and (hd >> 21) & 0x7ff == h and ptr - 0x0800A000 == p, hex(dsc)
    return sz

# ---- 1. 采样率框 125x35（UI1 专用）
w, h = 125, 35; check_dsc(0x3880c, 10, w, h, 0x372f4)
px = frame(w, h, 4, FILL, EDGE2)
hline(px, w, h - 3, 48, 77, AMBER)          # 底部一小段琥珀色，呼应 A 主题强调色
write_idx8(0x372f4, w, h, px, 'ui1_rate_125x35')

# ---- 2. 输入/输出框 81x51（UI1 专用，左右共用）
w, h = 81, 51; check_dsc(0x3a238, 10, w, h, 0x38e14)
px = frame(w, h, 4, FILL, EDGE)
hline(px, w, 25, 10, 71, EDGE2)             # 原图白线在第 25 行，改成暗灰细线
write_idx8(0x38e14, w, h, px, 'ui1_io_81x51')

# ---- 3. 状态小块 31x16（UI1 专用，4 个共用；上面的字固定白色）
w, h = 31, 16; check_dsc(0x38e08, 10, w, h, 0x38818)
write_idx8(0x38818, w, h, frame(w, h, 3, hx('1C1915'), DIM), 'ui1_chip_31x16')

# ---- 4. 菜单选中框 127x36（UI1 专用；里面的字固定白色）
w, h = 127, 36; check_dsc(0x4177c, 10, w, h, 0x401a0)
write_idx8(0x401a0, w, h, frame(w, h, 4, SEL, AMBER), 'ui1_menusel_127x36')

# ---- 5. 分隔线 465x4（UI1 专用）：暗灰细线，中间一段琥珀色渐隐
w, h = 465, 4; check_dsc(0x3ad88, 10, w, h, 0x3a244)
px = [(0, 0, 0, 0)] * (w * h)
for x in range(w):
    t = max(0.0, 1 - abs(x - w / 2) / 90)
    c = mix(EDGE, AMBER, t)
    px[1 * w + x] = c + (255,); px[2 * w + x] = c + (round(120 * t),) if t > 0 else (0, 0, 0, 0)
write_idx8(0x3a244, w, h, px, 'ui1_line_465x4')

# ---- 6. 音量刻度 474x39（UI1 专用）：保留原图字形，按亮度重新着色；90 以后用橙红
w, h = 474, 39; check_dsc(0x33e6c, 10, w, h, 0x2f234)
src = decode_idx8(0x2f234, w, h)
mx = max((max(c[:3]) for c in src if c[3]), default=1)
px = []
for i, c in enumerate(src):
    if c[3] == 0: px.append((0, 0, 0, 0)); continue
    x = i % w
    t = max(c[:3]) / mx
    tint = HOT if x >= 410 else TICK
    px.append(tuple(round(v * (0.35 + 0.65 * t)) for v in tint) + (c[3],))
write_idx8(0x2f234, w, h, px, 'ui1_scale_474x39')

# ---- 7. 指示点 6x6 TC_ALPHA（UI1 专用，RGB565 小端 + A）
w, h = 6, 6; check_dsc(0x46e14, 5, w, h, 0x46da8)
cov = rrect_cov(w, h, 0, 0, 6, 6, 3)
r, g, b = AMBER; v565 = (r >> 3) << 11 | (g >> 2) << 5 | (b >> 3)
dot = b''.join(struct.pack('<HB', v565, round(255 * c)) for c in cov)
d[0x46da8:0x46da8 + 108] = dot
png(os.path.join(PNGDIR, 'ui1_dot_6x6.png'), w, h, [AMBER + (round(255 * c),) for c in cov])
print('ui1_dot_6x6 ok')

# ---- 8. UI1 专用文字颜色：代码里是 字面量×4 = 实际颜色，所以写入 颜色>>2
def patch_col(off, old, new, what):
    cur = struct.unpack_from('<I', d, off)[0]
    assert cur == old, (hex(off), hex(cur))
    assert new & 3 == 0
    struct.pack_into('<I', d, off, new >> 2)
    print('color @%05x %-14s #%06X -> #%06X (literal %06X)' % (off, what, old * 4, new, new >> 2))
patch_col(0x149c, 0x3d73a1, 0xFFB544, 'sample-rate')
patch_col(0x2560, 0x3d73a1, 0xE8E4DC, 'in/out main')
patch_col(0x1ab0, 0x3d73a1, 0xE8E4DC, 'in/out update')

open(OUT, 'wb').write(d)
print('wrote', OUT, len(d), hashlib.sha256(d).hexdigest())
