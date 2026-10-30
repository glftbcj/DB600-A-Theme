# 动态测试：运行中切换拨杆/音量/提示、进出菜单、UI2 像素对比、英文
import sys, os, struct, importlib
sys.path.insert(0, r'C:\Users\GLFTB\Desktop\DB600\tools\python')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PATCH = 'C:/Users/GLFTB/Desktop/DB600/输出/DB600-17-0-A主题-第三步.bin'
ORIG = 'C:/Users/GLFTB/Desktop/2026-10-24+夏日之音DB600 MCU程序17-0 旧屏 UI选择菜单2.bin'
OUT = 'C:/Users/GLFTB/Desktop/DB600/输出/模拟截图-第三步'
from PIL import Image
SYM={l.split()[0]:int(l.split()[1],16) for l in open('C:/Users/GLFTB/Desktop/DB600/输出/sym.txt')}
AB, AC = SYM['a_build_main'], SYM['a_clean']
def bb(port, bit): return 0x42000000 + (port + 8 - 0x40000000) * 32 + bit * 4
GA, GD = 0x40010800, 0x40011400
def env(fw, theme=0, lang=1):
    sys.argv = ['x', fw]; os.environ['THEME'] = str(theme)
    import emu_ui as E, shot as S; importlib.reload(E); importlib.reload(S)
    scr = E.boot(); E.mu.mem_write(0x200002b6, struct.pack('<H', lang))
    E.mu.hook_add(E.UC_HOOK_CODE, S.on_flush, begin=S.FLUSH, end=S.FLUSH)
    def pin(port, bit, v): E.mu.mem_write(bb(port, bit), struct.pack('<I', v))
    def mode(m): pin(GA, 7, 0 if m == 0 else 1); pin(GD, 1, m & 1); pin(GD, 0, (m >> 1) & 1)
    def tick(n=30):
        for _ in range(n): E.call(0x8026670, 50); E.call(0x80266e8)
    def snap(name): S.fb.resize((960, 264)).save(os.path.join(OUT, name + '.png')); return S.fb.copy()
    E.mu.mem_write(0x20000005, bytes([1])); E.mu.mem_write(0x20000006, bytes([11]))
    return E, S, scr, pin, mode, tick, snap
os.makedirs(OUT, exist_ok=True)

# 1. 运行中切换
E, S, scr, pin, mode, tick, snap = env(PATCH)
mode(1); E.mu.mem_write(0x200002be, struct.pack('<H', 30))
E.call(AB); tick(); snap('d1_开机纯解码')
mode(3); tick(); snap('d2_拨到前级')
E.mu.mem_write(0x200002be, struct.pack('<H', 80)); tick(); snap('d3_音量80')
pin(0x40011000, 11, 1); tick(); snap('d4_改增益出提示')
# 2. 进菜单再回来（两遍），中途改主题再改回
for k in range(2):
    E.call(AC, E.u32(0x20000248)); E.call(0x80266c4, E.u32(0x20000204)); E.call(SYM['a_build_menu']); tick(10)
    snap('d5_菜单_%d' % k)
    E.call(AC, E.u32(0x20000248)); E.call(0x80266c4, E.u32(0x20000230)); E.call(AB); tick(10)
snap('d6_回主界面')
print('动态测试完成，对象数', len(E.children(scr)))

# 3. UI2 像素对比
imgs = []
for fw in (ORIG, PATCH):
    E, S, scr, pin, mode, tick, snap = env(fw, theme=1)
    mode(3); E.mu.mem_write(0x200002be, struct.pack('<H', 45))
    E.call(0x800c14c if fw == ORIG else AB); tick(); imgs.append(S.fb.copy())
diff = sum(1 for a, b in zip(imgs[0].getdata(), imgs[1].getdata()) if a != b)
print('UI2 原版 vs 补丁 不同像素数:', diff)
imgs[1].resize((960, 264)).save(os.path.join(OUT, 'u2_补丁版UI2.png'))

# 4. 英文
E, S, scr, pin, mode, tick, snap = env(PATCH, lang=0)
mode(1); E.call(AB); tick(); snap('e1_英文纯解码')
mode(3); tick(); snap('e2_英文前级')
print('ok')
