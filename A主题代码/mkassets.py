# 生成 A 主题要用的新字库和新图片，输出 a_assets.c / a_assets.h
# 字体：Barlow Condensed（OFL）、Noto Sans SC（OFL），在 tools/fonts
import sys, os
sys.path.insert(0, r'C:\Users\GLFTB\Desktop\DB600\tools\python')
from PIL import Image, ImageDraw, ImageFont

FD = r'C:\Users\GLFTB\Desktop\DB600\tools\fonts'
OUT = os.path.dirname(os.path.abspath(__file__))
src = []   # C 源码行
hdr = ['#pragma once', '#include "lvgl_min.h"']

def ttf(name, size, weight=None):
    f = ImageFont.truetype(os.path.join(FD, name), size)
    if weight: f.set_variation_by_axes([weight])
    return f

def render_glyph(font, ch):
    """返回 (adv, box_w, box_h, ofs_x, ofs_y, 4bpp 字节)；ofs_y = 字形底边相对基线向上的距离"""
    pad, base = 40, 120
    im = Image.new('L', (260, 180), 0)
    ImageDraw.Draw(im).text((pad, base), ch, fill=255, font=font, anchor='ls')
    bb = im.getbbox()
    adv = round(font.getlength(ch))
    if not bb:
        return adv, 0, 0, 0, 0, b''
    x0, y0, x1, y1 = bb
    w, h = x1 - x0, y1 - y0
    if w % 2: w += 1                     # 4bpp 每行凑满整字节
    crop = im.crop((x0, y0, x0 + w, y1))
    px = crop.tobytes()
    out = bytearray()
    for i in range(0, len(px), 2):
        out.append(((px[i] * 15 + 127) // 255) << 4 | ((px[i + 1] * 15 + 127) // 255))
    return adv, w, h, x0 - pad, base - y1, bytes(out)

def make_font(cname, chars, pick, line_h, base_line):
    """pick(ch) -> PIL 字体；每个字可以用不同字体和字号"""
    chars = sorted(set(chars))
    bm = bytearray(); glyphs = []
    for ch in chars:
        adv, w, h, ox, oy, data = render_glyph(pick(ch), ch)
        glyphs.append((ord(ch), len(bm), adv, w, h, ox, oy)); bm += data
    src.append('static const uint8_t %s_bmp[] = {%s};' % (cname, ','.join(str(b) for b in bm) or '0'))
    src.append('static const a_glyph_t %s_gl[] = {' % cname)
    for u, off, adv, w, h, ox, oy in glyphs:
        src.append('  {%d,%d,%d,%d,%d,%d,%d},' % (u, off, adv, w, h, ox, oy))
    src.append('};')
    src.append('static const a_font_dsc_t %s_dsc = {%s_bmp, %s_gl, %d};' % (cname, cname, cname, len(glyphs)))
    src.append('const lv_font_t %s = {a_font_get_dsc, a_font_get_bmp, %d, %d, 0, 0, 0, &%s_dsc, 0, 0};'
               % (cname, line_h, base_line, cname))
    hdr.append('extern const lv_font_t %s;' % cname)
    print('%s: %d glyphs, %d bytes bitmap' % (cname, len(glyphs), len(bm)))

# ---- 大号采样率字库：数字大号，k/H/z 小号（同一行基线对齐）
big = ttf('BarlowCondensed-SemiBold.ttf', 56)
small_unit = ttf('BarlowCondensed-Medium.ttf', 20)
rate_chars = set('0123456789. kHzNLOCKMUTE')
make_font('a_font_rate', rate_chars, lambda c: small_unit if c in 'kHz' else big, 46, 4)

# ---- 中号输入/输出字库
mid_lat = ttf('BarlowCondensed-Bold.ttf', 30)
mid_cjk = ttf('NotoSansSC.ttf', 21, 700)
io_words = ['USB', 'BT', 'I²S', 'OPT', 'COA', 'AES', '蓝牙', '光纤', '同轴', '数字平衡',
            'ALL', 'DAC', 'PHONE', 'PRE', '全端口', '解码', '耳机', '前级', '8V', '4V', '6V', '&', ' ']
make_font('a_font_io', ''.join(io_words), lambda c: mid_cjk if ord(c) > 0x2000 else mid_lat, 30, 5)

# ---- 小号字库：PCM/DSD/MQA、底部状态行、音量
sm = ttf('BarlowCondensed-SemiBold.ttf', 15)
make_font('a_font_small', set('FILDH-0123456789ΩLMSOFNPCQAV |%'), lambda c: sm, 16, 3)


# ---- 菜单用字库：菜单项、数值、按键提示（文字取自固件自己的菜单表，含义不变）
import struct as _st
_fw = open(r'C:\Users\GLFTB\Desktop\2026-10-24+夏日之音DB600 MCU程序17-0 旧屏 UI选择菜单2.bin', 'rb').read(); _B = 0x0800A000
def _s(v): return _fw[v - _B:v - _B + 32].split(b'\0')[0].decode() if _B <= v < _B + len(_fw) else ''
menu_items = [_s(_st.unpack_from('<I', _fw, 0x20c40 + 0x50 * lg + 4 * i)[0]) for lg in range(2) for i in range(6)]
menu_opts = [_s(_st.unpack_from('<I', _fw, 0x20380 + lg * 0x460 + it * 0x50 + 4 * i)[0]) for lg in range(2) for it in range(5) for i in range(4)]
MENU_EXTRA = {'reset': ('FACTORY RESET', '恢复出厂设置'), 'back': ('BACK TO MAIN', '回到主界面'), 'loss': ('CLOCK LOSS', '时钟失联')}
HINTS = ('UP/DN SELECT  ·  OK ENTER', 'UP/DN ADJUST  ·  OK SAVE', '上下 选择  ·  确定 进入', '上下 调整  ·  确定 保存', '旋钮 选择  ·  按键 确认', 'TURN TO SELECT  ·  PRESS TO CONFIRM')
def cjk_or(lat, cjk): return lambda c: cjk if ord(c) > 0x2000 and c != '·' else lat
make_font('a_font_item', ''.join(menu_items) + '语言 · LANGUAGE', cjk_or(ttf('BarlowCondensed-Medium.ttf', 17), ttf('NotoSansSC.ttf', 14, 500)), 18, 4)
make_font('a_font_val', ''.join(menu_opts) + ''.join(a + b for a, b in MENU_EXTRA.values()) + '<>中文English正在启动STARTING.',
          cjk_or(ttf('BarlowCondensed-SemiBold.ttf', 32), ttf('NotoSansSC.ttf', 24, 700)), 32, 6)
make_font('a_font_hint', ''.join(HINTS), cjk_or(ttf('BarlowCondensed-Medium.ttf', 14), ttf('NotoSansSC.ttf', 12, 500)), 14, 3)
def cstr(t): return '"' + ''.join('\\x%02x' % b for b in t.encode()) + '"'
src.append('const char *const a_menu_extra[3][2] = {%s};' % ','.join('{%s,%s}' % (cstr(a), cstr(b)) for a, b in MENU_EXTRA.values()))
src.append('const char *const a_menu_hint[6] = {%s};' % ','.join(cstr(h) for h in HINTS))
hdr += ['extern const char *const a_menu_extra[3][2];', 'extern const char *const a_menu_hint[6];']

# ---- 图片：TRUE_COLOR_ALPHA（RGB565 小端 + 透明度）
def hx(s): s = s.lstrip('#'); return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))
def img(cname, w, h, pixfn):
    data = bytearray()
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixfn(x, y)
            v = (r >> 3) << 11 | (g >> 2) << 5 | (b >> 3)
            data += bytes((v & 0xff, v >> 8, a))
    src.append('static const uint8_t %s_px[] = {%s};' % (cname, ','.join(str(b) for b in data)))
    src.append('const lv_img_dsc_t %s = {{5, 0, 0, %d, %d}, %d, %s_px};' % (cname, w, h, len(data), cname))
    hdr.append('extern const lv_img_dsc_t %s;' % cname)

def rrect(w, h, r, fill, edge=None, S=4):
    """抗锯齿圆角矩形，edge=None 表示实心"""
    def cov(x, y, x0, y0, x1, y1, rr):
        n = 0
        for sy in range(S):
            for sx in range(S):
                px = x + (sx + .5) / S; py = y + (sy + .5) / S
                if px < x0 or px > x1 or py < y0 or py > y1: continue
                cx = min(max(px, x0 + rr), x1 - rr); cy = min(max(py, y0 + rr), y1 - rr)
                if (px - cx) ** 2 + (py - cy) ** 2 <= rr * rr: n += 1
        return n / (S * S)
    def f(x, y):
        o = cov(x, y, 0, 0, w, h, r)
        if edge is None: return fill + (round(255 * o),)
        i = cov(x, y, 1, 1, w - 1, h - 1, max(r - 1, 0))
        a = o - i                                   # 只画边框
        return edge + (round(255 * a),)
    return f

AMBER, EDGE, LINE = hx('FFB547'), hx('3A3631'), hx('34302C')
img('a_img_chip_on', 30, 14, rrect(30, 14, 2, AMBER))
img('a_img_chip_off', 30, 14, rrect(30, 14, 2, None, EDGE))
img('a_img_dot', 6, 6, rrect(6, 6, 3, AMBER))
img('a_img_hline', 480, 2, lambda x, y: LINE + (255 if y == 0 else 0,))   # 1px 的图固件不画，做 2px、下半透明
img('a_img_vline', 2, 86, lambda x, y: LINE + (255 if x == 0 else 0,))
img('a_img_volbar', 480, 2, lambda x, y: AMBER + (255,))
img('a_img_msel', 124, 18, rrect(124, 18, 3, AMBER))          # 菜单选中行
img('a_img_medit', 124, 18, rrect(124, 18, 3, None, AMBER))   # 菜单调整中
img('a_img_seg_on', 38, 6, rrect(38, 6, 1, AMBER))
img('a_img_seg_off', 38, 6, rrect(38, 6, 1, hx('2A2724')))
img('a_img_vline2', 2, 120, lambda x, y: LINE + (255 if x == 0 else 0,))

open(os.path.join(OUT, 'a_assets.c'), 'w', encoding='utf-8').write(
    '// 由 mkassets.py 生成，不要手改\n#include "a_assets.h"\n' + '\n'.join(src) + '\n')
open(os.path.join(OUT, 'a_assets.h'), 'w', encoding='utf-8').write('\n'.join(hdr) + '\n')
print('ok')
