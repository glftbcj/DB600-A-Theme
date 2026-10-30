import sys, os, struct
exec(open('test_dyn.py', encoding='utf-8').read().split('# 1. 运行中切换')[0].replace('第一步', '第二步'))
from unicorn.arm_const import *
AM = SYM['a_build_menu']
E, S, scr, pin, mode, tick, snap = env(PATCH, lang=1)
mode(3); E.call(AB); tick(5); E.call(AC, E.u32(0x20000248)); E.call(AM); tick(5)
E.mu.mem_write(0x200000a6, b'\1'); E.mu.mem_write(0x20000219, bytes([3, 0, 0]))
trace = []
def h(mu, a, s, u):
    trace.append(a)
    if len(trace) > 40: del trace[0]
E.mu.hook_add(E.UC_HOOK_BLOCK, h)
try: tick(3); print('no crash')
except Exception as ex:
    print('ERR', ex, 'pc', hex(E.mu.reg_read(UC_ARM_REG_PC)), [hex(E.mu.reg_read(r)) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_LR)])
    print([hex(x) for x in trace[-25:]])
