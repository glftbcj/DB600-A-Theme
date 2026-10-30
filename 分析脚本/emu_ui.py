# 在模拟器里初始化 LVGL 并跑主界面生成函数，列出屏幕子对象
import sys, struct; sys.path.insert(0, r'C:\Users\GLFTB\Desktop\DB600\tools\python')
from unicorn import *; from unicorn.arm_const import *
FW=sys.argv[1]; d=open(FW,'rb').read(); B=0x0800A000
import os; theme=int(os.environ.get('THEME','0'))
mu=Uc(UC_ARCH_ARM, UC_MODE_THUMB|UC_MODE_MCLASS)
mu.mem_map(0x08000000, 0x80000); mu.mem_write(B, d)
mu.mem_map(0x20000000, 0x10000)
mu.mem_map(0x40000000, 0x30000); mu.mem_map(0x42000000, 0x2000000)  # 外设和位带区当普通内存
mu.mem_map(0xE0000000, 0x100000)
STOP=0x08000100; mu.mem_write(STOP, b'\xfe\xe7')  # b .
def call(fn, *args, limit=50_000_000):
    for i,a in enumerate(args): mu.reg_write([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3][i], a)
    mu.reg_write(UC_ARM_REG_LR, STOP|1)
    mu.emu_start(fn|1, STOP, count=limit)
    return mu.reg_read(UC_ARM_REG_R0)
u32=lambda a: struct.unpack('<I', mu.mem_read(a,4))[0]
u16=lambda a: struct.unpack('<H', mu.mem_read(a,2))[0]
s16=lambda a: struct.unpack('<h', mu.mem_read(a,2))[0]
def boot():
    mu.reg_write(UC_ARM_REG_SP, 0x2000ef40)
    mu.emu_start(0x800a130|1, 0x8026ee4, count=20_000_000)       # 数据拷贝
    mu.reg_write(UC_ARM_REG_SP, 0x2000ef00)
    for fn in (0x80204ac, 0x8024fb0): call(fn)                    # lv_init, 显示注册
    scr=call(0x8025910); mu.mem_write(0x20000248, struct.pack('<I', scr))
    mu.mem_write(0x200002a0, struct.pack('<H',0x4aaa))
    mu.mem_write(0x200002b6, struct.pack('<H',1))                 # 中文
    mu.mem_write(0x200002c4, struct.pack('<H',theme))
    return scr
def children(o):
    sa=u32(o+8)
    if not sa: return []
    return [u32(u32(sa)+4*i) for i in range(u32(sa+4))]
def text(a, n=24):
    try: return bytes(mu.mem_read(a,n)).split(b'\0')[0].decode('utf-8','replace')
    except: return '?'
if __name__=='__main__':
    scr=boot()
    call(0x800c14c)   # build_main
    for i,c in enumerate(children(scr)):
        cls=u32(c)
        print(i, hex(c), 'class', hex(cls), 'area', s16(c+0x14), s16(c+0x16), s16(c+0x18), s16(c+0x1a))
