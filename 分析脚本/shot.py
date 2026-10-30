# 模拟截图：在模拟器里生成界面并跑 LVGL 刷新，截获刷屏数据存成 PNG
import sys, struct; sys.path.insert(0, r'C:\Users\GLFTB\Desktop\DB600\tools\python')
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import emu_ui as E
from unicorn.arm_const import *
from PIL import Image
FLUSH=0x80136b6; W,H=480,132
fb=Image.new('RGB',(W,H),(255,0,255))
swap=False
def on_flush(mu, addr, size, ud):
    drv=mu.reg_read(UC_ARM_REG_R0); ar=mu.reg_read(UC_ARM_REG_R1); cp=mu.reg_read(UC_ARM_REG_R2)
    x1,y1,x2,y2=struct.unpack('<hhhh', mu.mem_read(ar,8))
    n=(x2-x1+1)*(y2-y1+1); px=mu.mem_read(cp, n*2)
    i=0
    for y in range(y1,y2+1):
        for x in range(x1,x2+1):
            v=px[i]|px[i+1]<<8; i+=2
            if swap: v=((v&0xff)<<8)|(v>>8)
            if 0<=x<W and 0<=y<H: fb.putpixel((x,y),((v>>11)*255//31,((v>>5)&63)*255//63,(v&31)*255//31))
    db=E.u32(drv+0xc); mu.mem_write(db+0x10, b'\0'*8)   # flushing=0
    mu.reg_write(UC_ARM_REG_PC, mu.reg_read(UC_ARM_REG_LR))
def render(build_fn, out, steps=6, pre=None):
    scr=E.boot()
    if pre: pre(E)
    E.mu.hook_add(E.UC_HOOK_CODE, on_flush, begin=FLUSH, end=FLUSH)
    E.call(build_fn)
    for _ in range(steps):
        E.call(0x8026670, 50)      # lv_tick_inc(50)
        E.call(0x80266e8)          # lv_timer_handler
    fb.resize((W*2,H*2), Image.NEAREST).save(out)
    return scr
if __name__=='__main__':
    E.FW=sys.argv[1]
    render(0x800c14c, sys.argv[2])
    print('saved', sys.argv[2])
