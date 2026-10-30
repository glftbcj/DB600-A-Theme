# 用 unicorn 跑启动代码的数据拷贝段，导出 main() 开始时的 RAM 内容
import sys; sys.path.insert(0, r'C:\Users\GLFTB\Desktop\DB600\tools\python')
from unicorn import *; from unicorn.arm_const import *
d=open(sys.argv[1],'rb').read(); B=0x0800A000
mu=Uc(UC_ARCH_ARM, UC_MODE_THUMB|UC_MODE_MCLASS)
mu.mem_map(0x08000000, 0x80000); mu.mem_write(B, d)
mu.mem_map(0x20000000, 0x10000)
mu.reg_write(UC_ARM_REG_SP, 0x2000ef40)
mu.emu_start(0x800a130|1, 0x8026ee4, count=20_000_000)
print('stopped at', hex(mu.reg_read(UC_ARM_REG_PC)))
open(sys.argv[2],'wb').write(bytes(mu.mem_read(0x20000000, 0x10000)))
