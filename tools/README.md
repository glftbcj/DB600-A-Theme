# tools 目录（不进 Git，按下面重新准备）

| 目录 | 内容 | 来源 |
|---|---|---|
| `arm-gnu-toolchain-14.2.rel1/` | Arm GNU Toolchain 14.2.Rel1（Windows x86_64） | https://developer.arm.com/-/media/Files/downloads/gnu/14.2.rel1/binrel/arm-gnu-toolchain-14.2.rel1-mingw-w64-x86_64-arm-none-eabi.zip ，SHA256 f074615953f76036e9a51b87f6577fdb4ed8e77d3322a6f68214e92e7859888f，解压到这个目录 |
| `python/` | unicorn 2.1.4、capstone 5.0.x、pillow | `python -m pip install --target python unicorn capstone pillow` |
| `fonts/` | BarlowCondensed-Medium / SemiBold / Bold.ttf、NotoSansSC.ttf（可变字重），均为 OFL 授权 | https://github.com/google/fonts/raw/main/ofl/barlowcondensed/ 和 https://github.com/google/fonts/raw/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf （保存为 NotoSansSC.ttf） |

分析脚本里的 `ins_170.pkl`（反汇编缓存）用 `python -I 分析脚本/an1_170.py <17-0 固件>` 重新生成；`ram_170.bin` 用 `ramimg.py` 生成。
