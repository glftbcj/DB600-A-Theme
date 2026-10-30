import sys, os, struct
exec(open('test_dyn.py', encoding='utf-8').read().split('# 1. 运行中切换')[0].replace('第一步', '第二步'))
imgs = []
for fw in (ORIG, PATCH):
    for item, edit, val in ((0, 0, 0), (1, 1, 2)):
        E, S, scr, pin, mode, tick, snap = env(fw, theme=1)
        mode(3); E.call(0x800c14c if fw == ORIG else AB); tick(5)
        E.call(0x8021cac if fw == ORIG else AC, E.u32(0x20000248)); E.call(0x80266c4, E.u32(0x20000204))
        E.call(0x800e764 if fw == ORIG else SYM['a_build_menu']); tick(5)
        E.mu.mem_write(0x20000219, bytes([item, edit, val])); tick(3)
        imgs.append(S.fb.copy())
for k in range(2):
    a, b = imgs[k], imgs[k + 2]
    print('UI2 菜单状态', k, '原版 vs 补丁 不同像素:', sum(1 for x, y in zip(a.getdata(), b.getdata()) if x != y))
