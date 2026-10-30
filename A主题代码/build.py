# 编译 A 主题代码并打进 17-0 固件副本（原文件不动）
import sys; sys.stdout.reconfigure(encoding="utf-8")
import os, sys, struct, subprocess, hashlib, re
HERE = os.path.dirname(os.path.abspath(__file__))
TC = r'C:\Users\GLFTB\Desktop\DB600\tools\arm-gnu-toolchain-14.2.rel1\bin'
SRC_FW = r'C:\Users\GLFTB\Desktop\2026-10-24+夏日之音DB600 MCU程序17-0 旧屏 UI选择菜单2.bin'
OUT_DIR = os.path.join(os.path.dirname(HERE), '输出')
OUT_FW = os.path.join(OUT_DIR, sys.argv[1] if len(sys.argv) > 1 else 'DB600-17-0-A主题-第三步.bin')
B = 0x0800A000
CODE_AT = 0x0805B100                 # 原程序结束于 0x0805B0AC
FLASH_LIMIT = 0x0807F800             # 设置保存页，绝不能碰
ORIG_SHA = '625118cabfa611c87f9842c0ec07079c899c65315c1278b34b2edb6739e82d67'

def run(*a):
    r = subprocess.run(a, cwd=HERE, capture_output=True, text=True)
    if r.returncode: print(r.stdout, r.stderr); raise SystemExit('失败: ' + a[0])
    return r.stdout

run(sys.executable, '-I', os.path.join(HERE, 'mkassets.py'))
open(os.path.join(HERE, 'link.ld'), 'w').write('''
MEMORY { FLASH (rx) : ORIGIN = 0x%08X, LENGTH = 0x%X }
PROVIDE(fw_font_cn21 = 0x08036e30);
SECTIONS {
  .text : { KEEP(*(.text.a_*)) KEEP(*(.rodata.a_img_*)) *(.text*) *(.rodata*) } > FLASH
  /DISCARD/ : { *(.data*) *(.bss*) *(.ARM.*) *(.comment) }
}
''' % (CODE_AT, FLASH_LIMIT - CODE_AT))
cflags = ['-mcpu=cortex-m3', '-mthumb', '-Os', '-ffreestanding', '-fno-builtin', '-fno-common',
          '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Wno-unused-parameter']
for c in ('a_theme.c', 'a_assets.c'):
    run(os.path.join(TC, 'arm-none-eabi-gcc.exe'), *cflags, '-c', c, '-o', c[:-2] + '.o')
run(os.path.join(TC, 'arm-none-eabi-gcc.exe'), '-mcpu=cortex-m3', '-mthumb', '-nostdlib', '-T', 'link.ld',
    '-Wl,--gc-sections', '-Wl,-Map=a.map', 'a_theme.o', 'a_assets.o', '-lgcc', '-o', 'a.elf')
# 不能有 .data / .bss（没有启动代码给它们初始化）
hdrs = run(os.path.join(TC, 'arm-none-eabi-objdump.exe'), '-h', 'a.elf')
assert '.data' not in hdrs and '.bss' not in hdrs, hdrs
run(os.path.join(TC, 'arm-none-eabi-objcopy.exe'), '-O', 'binary', 'a.elf', 'a.bin')
sym = {}
for l in run(os.path.join(TC, 'arm-none-eabi-nm.exe'), 'a.elf').splitlines():
    p = l.split()
    if len(p) == 3: sym[p[2]] = int(p[0], 16)
code = open(os.path.join(HERE, 'a.bin'), 'rb').read()
assert CODE_AT + len(code) < FLASH_LIMIT
print('新代码+资源 %d 字节，0x%08X..0x%08X' % (len(code), CODE_AT, CODE_AT + len(code)))

fw = bytearray(open(SRC_FW, 'rb').read())
assert hashlib.sha256(fw).hexdigest() == ORIG_SHA, '原版 17-0 文件变了，停止'
fw += b'\xff' * (CODE_AT - B - len(fw)) + code

def dec_bl(a):
    h1, h2 = struct.unpack_from('<HH', fw, a - B)
    s = (h1 >> 10) & 1; j1 = (h2 >> 13) & 1; j2 = (h2 >> 11) & 1
    i1 = 1 - (j1 ^ s); i2 = 1 - (j2 ^ s)
    off = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3ff) << 12) | ((h2 & 0x7ff) << 1)
    if s: off -= 1 << 25
    kind = {0xD000: 'bl', 0x9000: 'b.w'}.get(h2 & 0xD000)
    return kind, a + 4 + off
def enc(a, target, kind):
    off = target - (a + 4); assert -(1 << 24) <= off < (1 << 24) and off % 2 == 0
    s = (off >> 24) & 1; i1 = (off >> 23) & 1; i2 = (off >> 22) & 1
    j1 = 1 - (i1 ^ s); j2 = 1 - (i2 ^ s)
    h1 = 0xF000 | (s << 10) | ((off >> 12) & 0x3ff)
    h2 = (0xD000 if kind == 'bl' else 0x9000) | (j1 << 13) | (j2 << 11) | ((off >> 1) & 0x7ff)
    struct.pack_into('<HH', fw, a - B, h1, h2)

PATCH = [  # (地址, 原指令, 原目标, 新函数)
    (0x8017f14, 'bl', 0x800c14c, 'a_build_main'), (0x8017fce, 'bl', 0x800c14c, 'a_build_main'),
    (0x80180e4, 'b.w', 0x800c14c, 'a_build_main'),
    (0x80100f4, 'bl', 0x8021644, 'a_needle_align'), (0x80101d2, 'bl', 0x8021524, 'a_vol_hide'),
    (0x80101da, 'bl', 0x8021ce4, 'a_tag_show'), (0x80103e2, 'bl', 0x8021ce4, 'a_needle_show'),
    (0x80103ea, 'bl', 0x8021ce4, 'a_vol_show'), (0x80103d8, 'bl', 0x8024ddc, 'a_title_color'),
    (0x801040a, 'bl', 0x8021660, 'a_title_align'), (0x800b418, 'bl', 0x80201ac, 'a_dot_src'),
    (0x8017e2e, 'bl', 0x800e764, 'a_build_menu'),
    (0x8018024, 'bl', 0x800e3a0, 'a_build_lang'), (0x80270da, 'bl', 0x800e3a0, 'a_build_lang'),
    (0x801811c, 'bl', 0x800babc, 'a_lang_update'),
    (0x8018164, 'bl', 0x800f144, 'a_build_prompt'), (0x80270e0, 'bl', 0x800f144, 'a_build_prompt'), (0x8017f32, 'bl', 0x800b7a8, 'a_menu_update'),
] + [(a, None, 0x8021cac, 'a_clean') for a in
     (0x800b84a, 0x8017e22, 0x8017ea8, 0x8017f10, 0x8017fc4, 0x801801a, 0x80180d6, 0x8018158)]
for a, kind, old, fn in PATCH:
    k, t = dec_bl(a)
    assert t == old and k and (kind is None or k == kind), '0x%x 不是预期指令（%s %x）' % (a, k, t)
    enc(a, sym[fn], k)
    assert dec_bl(a) == (k, sym[fn])
    print('  %-4s 0x%08X: 0x%08X -> %s 0x%08X' % (k, a, old, fn, sym[fn]))

def lit(off, old, new, what):
    assert struct.unpack_from('<I', fw, off)[0] == old, hex(off)
    struct.pack_into('<I', fw, off, new); print('  字面量 0x%05X %s: %08X -> %08X' % (off, what, old, new))
lit(0x149c, 0x3d73a1, 0xFFB544 >> 2, 'UI1 采样率色 #FFB544')
lit(0x2560, 0x3d73a1, 0xE8E4DC >> 2, 'UI1 输入/输出值色 #E8E4DC')
lit(0x1ab0, 0x3d73a1, 0xE8E4DC >> 2, 'UI1 输入/输出值色（刷新）')
lit(0x20238, 0x08050e8c, sym['a_img_chip_off'], 'UI1 格式点「灭」图')
lit(0x2023c, 0x08050e14, sym['a_img_chip_on'], 'UI1 格式点「亮」图')

os.makedirs(OUT_DIR, exist_ok=True)
open(OUT_FW, 'wb').write(fw)
print('输出', OUT_FW, len(fw), '字节 SHA256', hashlib.sha256(fw).hexdigest())
open(os.path.join(OUT_DIR, 'sym.txt'), 'w').write(''.join('%s %08x\n' % (k, v) for k, v in sorted(sym.items()) if k.startswith('a_')))
