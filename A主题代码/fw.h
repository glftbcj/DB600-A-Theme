// 17-0 固件里的函数和变量地址（静态分析 + 模拟器核实）
#pragma once
#include "lvgl_min.h"

#define FN(addr, ret, name, args) static ret (*const name) args = (ret (*) args)((addr) | 1)

FN(0x801f78c, lv_obj_t *, lv_img_create, (lv_obj_t *parent));
FN(0x80201ac, void, lv_img_set_src, (lv_obj_t *o, const void *src));
FN(0x8020570, lv_obj_t *, lv_label_create, (lv_obj_t *parent));
FN(0x8020e4c, void, lv_label_set_text, (lv_obj_t *o, const char *t));
FN(0x8021644, void, lv_obj_align, (lv_obj_t *o, uint8_t align, lv_coord_t x, lv_coord_t y));
FN(0x8021660, void, lv_obj_align_to, (lv_obj_t *o, const lv_obj_t *base, uint8_t align, lv_coord_t x, lv_coord_t y));
FN(0x8021524, void, lv_obj_add_flag, (lv_obj_t *o, uint32_t f));
FN(0x8021ce4, void, lv_obj_clear_flag, (lv_obj_t *o, uint32_t f));
FN(0x802253a, lv_obj_t *, lv_obj_get_child, (const lv_obj_t *o, int32_t id));
FN(0x8024b64, void, lv_obj_set_size, (lv_obj_t *o, lv_coord_t w, lv_coord_t h));
FN(0x8021cac, void, lv_obj_clean, (lv_obj_t *o));
FN(0x8024df6, void, lv_obj_set_style_text_font, (lv_obj_t *o, const lv_font_t *f, uint32_t sel));
FN(0x8024ddc, void, lv_obj_set_style_text_color, (lv_obj_t *o, lv_color_t c, uint32_t sel));
FN(0x801bc76, lv_color_t, lv_color_hex, (uint32_t c));
FN(0x80105f8, int, fw_sprintf, (char *dst, const char *fmt, ...));

// 原版界面函数
FN(0x800c14c, void, fw_build_main, (void));

#define LV_OBJ_FLAG_HIDDEN 1u
#define OBJ_FLAGS(o) (*(volatile uint32_t *)((uint8_t *)(o) + 0x1c))
enum { AL_TOP_LEFT = 1, AL_TOP_MID = 2, AL_TOP_RIGHT = 3, AL_CENTER = 9 };

// 固件变量
#define SCREEN      (*(lv_obj_t **)0x20000248)
#define SET_U16(off) (*(volatile uint16_t *)(0x200002a0 + (off)))
#define THEME       SET_U16(0x24)        // 0 = UI1（改成 A 主题），1 = UI2
#define VOLUME      SET_U16(0x1e)        // 0..100
#define MAIN_OBJ(off) (*(lv_obj_t **)(0x200001e0 + (off)))   // +4 输入 … +0x20 状态
#define TOP_OBJ(off)  (*(lv_obj_t **)(0x20000234 + (off)))   // +4 刻度 +8 指针 +0xc 标题牌 +0x10 标题字
#define DOT_OBJ(i)    (((lv_obj_t **)0x2000dd90)[i])
extern const lv_font_t fw_font_cn21;     // 0x08036e30，由链接脚本定义
