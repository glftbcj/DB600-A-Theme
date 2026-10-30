# 开机流程：语言选择 → 正在启动 → 主界面（自动），以及 UI2 对比
import sys, os, struct
exec(open('test_dyn.py', encoding='utf-8').read().split('# 1. 运行中切换')[0])
OUT = 'C:/Users/GLFTB/Desktop/DB600/输出/模拟截图-第三步'; os.makedirs(OUT, exist_ok=True)
shots = []
E, S, scr, pin, mode, tick, snap = env(PATCH, lang=1)
mode(1)
E.call(SYM['a_build_lang']); tick(5); shots.append(snap('b1_语言_中文'))
E.mu.mem_write(0x200002b6, struct.pack('<H', 0)); tick(5); shots.append(snap('b2_语言_English'))
E.mu.mem_write(0x200002b6, struct.pack('<H', 1)); tick(3)
# 按确认：同固件 0x8018152 起的顺序（清屏、删语言定时器、建开机界面）
E.call(AC, E.u32(0x20000248)); E.call(0x80266c4, E.u32(0x20000250)); E.call(SYM['a_build_prompt'])
tick(2); shots.append(snap('b3_正在启动_1')); tick(6); shots.append(snap('b4_正在启动_2'))
for _ in range(200):
    tick(1)
    if len(E.children(E.u32(0x20000248))) > 20: break
tick(30); shots.append(snap('b5_自动进入主界面'))
print('主界面对象数', len(E.children(E.u32(0x20000248))))
from PIL import Image
sh = Image.new('RGB', (968, 136 * 3), (60, 60, 60))
for i, im in enumerate(shots): sh.paste(im.resize((480, 132)), ((i % 2) * 488, (i // 2) * 136))
sh.save(os.path.join(OUT, '开机合集.png'))
# UI2：语言界面、开机界面像素对比
for nm, fo, fp in (('语言', 0x800e3a0, SYM['a_build_lang']), ('开机', 0x800f144, SYM['a_build_prompt'])):
    ims = []
    for fw, fn in ((ORIG, fo), (PATCH, fp)):
        E, S, scr, pin, mode, tick, snap = env(fw, theme=1); E.call(fn); tick(4); ims.append(S.fb.copy())
    print('UI2', nm, '原版 vs 补丁 不同像素:', sum(1 for a, b in zip(ims[0].getdata(), ims[1].getdata()) if a != b))
