import sys, os, struct
exec(open('test_dyn.py', encoding='utf-8').read().split('# 1. 运行中切换')[0].replace('第一步', '第二步'))
OUT = 'C:/Users/GLFTB/Desktop/DB600/输出/模拟截图-第三步'; os.makedirs(OUT, exist_ok=True)
AM = SYM['a_build_menu']
shots = []
def st(item, edit=0, val=0): E.mu.mem_write(0x20000219, bytes([item, edit, val & 0xff]))
for lang in (1, 0):
    E, S, scr, pin, mode, tick, snap = env(PATCH, lang=lang)
    E.mu.mem_write(0x200002aa, struct.pack('<H', 2)); E.mu.mem_write(0x200002ac, struct.pack('<H', 1))
    mode(3); E.call(AB); tick(5)
    E.call(AC, E.u32(0x20000248)); E.call(0x80266c4, E.u32(0x20000204)); E.call(AM); tick(5)   # 同固件：清屏、删主界面定时器、建菜单
    for name, args in [('浏览_亮度', (0,)), ('浏览_亮屏时长', (1,)), ('浏览_复位', (2,)), ('浏览_时钟', (3,)),
                       ('浏览_主题', (4,)), ('浏览_返回', (5,)), ('调整_亮度100', (0, 1, 3)), ('调整_主题UI2', (4, 1, 1))]:
        st(*args); tick(3); shots.append(snap('%d_%s' % (lang, name)))
    if lang == 1:
        E.mu.mem_write(0x200000a6, b'\1'); st(3); tick(3); shots.append(snap('1_时钟失联'))
        E.mu.mem_write(0x200000a6, b'\0')
    # 退出菜单回主界面（选「返回」）
    E.call(AC, E.u32(0x20000248)); E.call(0x80266c4, E.u32(0x20000230)); E.call(AB); tick(5); shots.append(snap('%d_回到主界面' % lang))
print('对象数', len(E.children(E.u32(0x20000248))))
from PIL import Image
sh = Image.new('RGB', (968, 136 * ((len(shots) + 1) // 2)), (60, 60, 60))
for i, im in enumerate(shots): sh.paste(im.resize((480, 132)), ((i % 2) * 488, (i // 2) * 136))
sh.save(os.path.join(OUT, '菜单合集.png')); print('ok', len(shots))
