# 用模拟器在几种拨杆状态下给补丁固件「截图」
import sys, struct, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
FW, OUT = sys.argv[1], sys.argv[2]
sys.argv = [sys.argv[0], FW]
import emu_ui as E, shot as S
from PIL import Image
def bb(port, bit): return 0x42000000 + (port + 8 - 0x40000000) * 32 + bit * 4
GA, GB, GC, GD = 0x40010800, 0x40010C00, 0x40011000, 0x40011400
def setpin(port, bit, v): E.mu.mem_write(bb(port, bit), struct.pack('<I', v))
def scenario(name, mode, vol=45, mute=0, fmt=1, rate=14, gain=(0,0), imp=(0,0), amp=0, volt=(1,0), build=None):
    E.mu.__init__(E.UC_ARCH_ARM, E.UC_MODE_THUMB | E.UC_MODE_MCLASS) if False else None
    def pre(E):
        # 输出模式：值 = (PD1 + PD0*2) * PA7
        setpin(GA, 7, 0 if mode == 0 else 1)
        setpin(GD, 1, mode & 1); setpin(GD, 0, (mode >> 1) & 1)
        setpin(GB, 7, volt[0]); setpin(GC, 0, volt[1])
        setpin(GC, 11, gain[0]); setpin(GC, 12, gain[1]); setpin(GA, 9, imp[0]); setpin(GC, 10, imp[1]); setpin(GC, 6, amp)
        E.mu.mem_write(0x200002be, struct.pack('<H', vol)); E.mu.mem_write(0x20000001, bytes([mute]))
        E.mu.mem_write(0x20000005, bytes([fmt])); E.mu.mem_write(0x20000006, bytes([rate]))
    S.fb.paste((255, 0, 255), (0, 0, 480, 132))
    S.render(build, None if False else os.path.join(OUT, name + '.png'), steps=60, pre=pre)
    return Image.open(os.path.join(OUT, name + '.png'))
os.makedirs(OUT, exist_ok=True)
import importlib
names = []
for args in [dict(name='1_纯解码', mode=1), dict(name='2_前级_音量45', mode=3, vol=45), dict(name='3_耳机_静音', mode=2, mute=1),
             dict(name='4_全端口_DSD', mode=0, fmt=2, rate=20, gain=(1,1), imp=(1,0), amp=1)]:
    importlib.reload(E); importlib.reload(S)
    build = int(os.environ.get('BUILD', '0x800c14c'), 16)
    scenario(build=build, **args); names.append(args['name'])
ims = [Image.open(os.path.join(OUT, n + '.png')) for n in names]
sheet = Image.new('RGB', (960, 264 * len(ims) + 8 * (len(ims) - 1)), (60, 60, 60))
for i, im in enumerate(ims): sheet.paste(im, (0, i * 272))
sheet.save(os.path.join(OUT, '合集.png')); print('ok', names)
