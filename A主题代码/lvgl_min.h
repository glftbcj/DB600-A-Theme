// 固件里 LVGL v8.3 的最小类型定义（布局已对照反汇编核实）
#pragma once
#include <stdint.h>
#include <stdbool.h>

typedef struct _lv_obj_t lv_obj_t;
typedef uint16_t lv_color_t;            // RGB565，不交换字节
typedef int16_t lv_coord_t;

typedef struct {
    uint32_t cf : 5, always_zero : 3, reserved : 2, w : 11, h : 11;
} lv_img_header_t;
typedef struct { lv_img_header_t header; uint32_t data_size; const uint8_t *data; } lv_img_dsc_t;

typedef struct _lv_font_t lv_font_t;
typedef struct {                        // 固件取字形函数写入的偏移：+4 adv … +0xe bpp
    const lv_font_t *resolved_font;
    uint16_t adv_w, box_w, box_h;
    int16_t ofs_x, ofs_y;
    uint8_t bpp : 4, is_placeholder : 1;
} lv_font_glyph_dsc_t;
struct _lv_font_t {                     // dsc 在 +0x10，与固件字库一致
    bool (*get_glyph_dsc)(const lv_font_t *, lv_font_glyph_dsc_t *, uint32_t, uint32_t);
    const uint8_t *(*get_glyph_bitmap)(const lv_font_t *, uint32_t);
    lv_coord_t line_height, base_line;
    uint8_t subpx;
    int8_t underline_position, underline_thickness;
    const void *dsc;
    const lv_font_t *fallback;
    void *user_data;
};

// 自己的字库格式（4bpp，每行整字节）
typedef struct { uint16_t unicode; uint32_t off; uint8_t adv, w, h; int8_t ox, oy; } a_glyph_t;
typedef struct { const uint8_t *bmp; const a_glyph_t *gl; uint16_t n; } a_font_dsc_t;
bool a_font_get_dsc(const lv_font_t *f, lv_font_glyph_dsc_t *o, uint32_t letter, uint32_t next);
const uint8_t *a_font_get_bmp(const lv_font_t *f, uint32_t letter);
