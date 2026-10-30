import sys, os, struct
exec(open('test_dyn.py', encoding='utf-8').read().split('# 1. 运行中切换')[0])
E, S, scr, pin, mode, tick, snap = env(PATCH)
mode(1); E.call(AB); tick()
mode(3); E.mu.mem_write(0x200002be, struct.pack('<H', 80)); tick()
E.mu.mem_write(0x20000038, b'\0'); tick(); snap('m1_提示结束_音量80')   # 模拟 3 秒后提示被定时器清掉
E.mu.mem_write(0x200002be, struct.pack('<H', 20)); tick(); snap('m2_音量20')
E.mu.mem_write(0x20000001, b'\1'); tick(); snap('m3_静音')
E.mu.mem_write(0x20000001, b'\0'); tick(); snap('m4_解除静音')
mode(1); tick(); E.mu.mem_write(0x20000038, b'\0'); tick(); snap('m5_拨回纯解码')
print('ok')
