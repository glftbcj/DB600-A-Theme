// A 主题主界面：只在主题 = UI1 时生效，UI2 完全走原版
// 原理：原版建好主界面后，隐藏旧装饰、重新摆放原有文字、加几样新装饰；
//       顶部刷新函数里涉及音量条 / 标题牌的几个调用改成走这里。
#include "fw.h"
#include "a_assets.h"

#define MAGIC 0x41A7E3E5u
struct a_state {
    uint32_t magic;
    uint8_t on;                 // 1 = 当前屏幕是 A 主题主界面，指针有效
    uint8_t dot_on[3];          // PCM / DSD / MQA 是否点亮
    lv_obj_t *volfill, *vollbl;
    // ---- 菜单
    uint8_t menu_on;            // 1 = 当前屏幕是 A 风格菜单
    int8_t m_last[6];           // 上次画的状态：项、调整中、选项值、语言、时钟失联、当前设置值
    lv_obj_t *m_row[6], *m_hl, *m_name, *m_val, *m_seg[4], *m_hint;
    // ---- 语言选择界面
    uint8_t lang_on;
};
#define G ((struct a_state *)0x2000FC00)   // 栈顶 0x2000EF40 以上没人用

static inline bool active(void) { return G->magic == MAGIC && G->on && THEME == 0; }
static void hide(lv_obj_t *o) { if (o && !(OBJ_FLAGS(o) & LV_OBJ_FLAG_HIDDEN)) lv_obj_add_flag(o, LV_OBJ_FLAG_HIDDEN); }
static void show(lv_obj_t *o) { if (o && (OBJ_FLAGS(o) & LV_OBJ_FLAG_HIDDEN)) lv_obj_clear_flag(o, LV_OBJ_FLAG_HIDDEN); }
static lv_obj_t *child(int i) { return lv_obj_get_child(SCREEN, i); }

static void place(lv_obj_t *o, const lv_font_t *f, uint32_t color, uint8_t al, int x, int y) {
    if (!o) return;
    if (f) lv_obj_set_style_text_font(o, f, 0);
    if (color) lv_obj_set_style_text_color(o, lv_color_hex(color), 0);
    lv_obj_align(o, al, x, y);
}
static lv_obj_t *new_img(const lv_img_dsc_t *src, int x, int y) {
    lv_obj_t *o = lv_img_create(SCREEN);
    lv_img_set_src(o, src);
    lv_obj_align(o, AL_TOP_LEFT, x, y);
    return o;
}
static lv_obj_t *new_label(const char *t, const lv_font_t *f, uint32_t color, uint8_t al, int x, int y) {
    lv_obj_t *o = lv_label_create(SCREEN);
    lv_label_set_text(o, t);
    place(o, f, color, al, x, y);
    return o;
}

static void update_volume(void) {
    char buf[12];
    int v = VOLUME; if (v > 100) v = 100;
    lv_obj_set_size(G->volfill, (lv_coord_t)(v * 480 / 100), 2);
    fw_sprintf(buf, "VOL %d", v);
    lv_label_set_text(G->vollbl, buf);
}
static void color_fmt_labels(void) {
    for (int i = 0; i < 3; i++)
        lv_obj_set_style_text_color(child(9 + 2 * i), lv_color_hex(G->dot_on[i] ? 0x0B0B0C : 0x6E685F), 0);
}

// ---- 替换 3 处 build_main 调用
void a_build_main(void) {
    G->magic = MAGIC; G->on = 0;
    fw_build_main();
    if (THEME != 0) return;

    // 主界面子对象顺序（模拟器核实）：0 输入框 1 输入值 2「输入」3 输出框 4 输出值 5「输出」
    // 6 采样率框 7 采样率 8/10/12 格式点 9/11/13 格式字 14..21 状态框+字 22 刻度 23 分隔线 24 指针 25 标题牌 26 标题字 27 状态行
    static const uint8_t old_deco[] = {0, 3, 6, 14, 16, 18, 20, 22, 23, 24, 25};
    for (unsigned i = 0; i < sizeof old_deco; i++) hide(child(old_deco[i]));

    // 新装饰：顶栏线（兼音量底轨）、底栏线、两条竖线、顶栏琥珀点
    new_img(&a_img_hline, 0, 22);
    new_img(&a_img_hline, 0, 109);
    new_img(&a_img_vline, 108, 23);
    new_img(&a_img_vline, 371, 23);
    new_img(&a_img_dot, 10, 8);
    G->volfill = new_img(&a_img_volbar, 0, 21);
    G->vollbl = new_label("VOL", &a_font_small, 0xC9C2B6, AL_TOP_LEFT, 22, 3);
    hide(G->volfill); hide(G->vollbl);

    // 中间三栏
    place(child(2), &fw_font_cn21, 0x8C857B, AL_TOP_LEFT, 12, 38);     // 「输入」
    place(child(1), &a_font_io, 0, AL_TOP_LEFT, 12, 58);               // USB（颜色由固件字面量给）
    place(child(5), &fw_font_cn21, 0x8C857B, AL_TOP_RIGHT, -12, 38);   // 「输出」
    place(child(4), &a_font_io, 0, AL_TOP_RIGHT, -12, 58);             // 解码4V
    place(child(7), &a_font_rate, 0, AL_CENTER, 0, 0);                 // 采样率（琥珀色由固件字面量给）

    // 顶栏右侧 PCM / DSD / MQA 小方块（图片由固件按格式切换，已指向新图）
    static const int8_t dx[3] = {-78, -44, -10};
    for (int i = 0; i < 3; i++) {
        lv_obj_align(DOT_OBJ(i), AL_TOP_RIGHT, dx[i], 4);
        lv_obj_set_style_text_font(child(9 + 2 * i), &a_font_small, 0);
        lv_obj_align_to(child(9 + 2 * i), DOT_OBJ(i), AL_CENTER, 0, 0);
    }
    color_fmt_labels();

    // 底栏：FIL-2 | L | 0Ω | OFF
    place(MAIN_OBJ(0x10), &a_font_small, 0xC9C2B6, AL_CENTER, -96, 55);  // 滤波器
    place(MAIN_OBJ(0x18), &a_font_small, 0xC9C2B6, AL_CENTER, -32, 55);  // 增益
    place(MAIN_OBJ(0x14), &a_font_small, 0xC9C2B6, AL_CENTER, 32, 55);   // 阻抗
    place(MAIN_OBJ(0x1c), &a_font_small, 0xC9C2B6, AL_CENTER, 96, 55);   // 耳放
    new_label("|", &a_font_small, 0x4A453F, AL_CENTER, -64, 55);
    new_label("|", &a_font_small, 0x4A453F, AL_CENTER, 0, 55);
    new_label("|", &a_font_small, 0x4A453F, AL_CENTER, 64, 55);

    // 状态行（遥控开关 / IIC Err）放顶栏中间
    place(MAIN_OBJ(0x20), &fw_font_cn21, 0xFF6A3D, AL_TOP_MID, 0, 1);

    // 标题字（纯解码器 / 提示 / 静音）放顶栏左侧
    // 建界面时原版已给它上过色（黑 / 红），这里按 A 主题重上：静音橙红，其余暖白
    place(TOP_OBJ(0x10), &fw_font_cn21, (*(volatile uint8_t *)0x20000001) ? 0xFF6A3D : 0xE8E4DC, AL_TOP_LEFT, 22, 1);

    G->on = 1;
    // 按当前状态显示音量：标题字隐藏 = 音量模式
    if (OBJ_FLAGS(TOP_OBJ(0x10)) & LV_OBJ_FLAG_HIDDEN) { show(G->volfill); show(G->vollbl); }
    update_volume();
}

// ---- 替换所有 lv_obj_clean 调用：屏幕被清空时作废 A 主题指针
void a_clean(lv_obj_t *o) {
    if (o == SCREEN) { G->on = 0; G->menu_on = 0; G->lang_on = 0; }
    lv_obj_clean(o);
}

// ---- 顶部刷新函数 update_top（0x80100A0）里的调用
void a_needle_align(lv_obj_t *o, uint8_t al, lv_coord_t x, lv_coord_t y) {   // 音量变化
    if (!active()) { lv_obj_align(o, al, x, y); return; }
    update_volume();
}
void a_needle_show(lv_obj_t *o, uint32_t f) {                               // 进入音量模式：指针
    if (!active()) lv_obj_clear_flag(o, f);
}
void a_vol_show(lv_obj_t *o, uint32_t f) {                                  // 进入音量模式：刻度
    if (!active()) { lv_obj_clear_flag(o, f); return; }
    show(G->volfill); show(G->vollbl);
}
void a_vol_hide(lv_obj_t *o, uint32_t f) {                                  // 进入标题模式：刻度
    lv_obj_add_flag(o, f);
    if (active()) { hide(G->volfill); hide(G->vollbl); }
}
void a_tag_show(lv_obj_t *o, uint32_t f) {                                  // 进入标题模式：标题牌
    if (!active()) lv_obj_clear_flag(o, f);
}
void a_title_color(lv_obj_t *o, lv_color_t c, uint32_t sel) {               // 标题字颜色
    if (active()) c = lv_color_hex(c == 0 ? 0xE8E4DC : 0xFF6A3D);         // 黑 → 暖白，红 → 橙红
    lv_obj_set_style_text_color(o, c, sel);
}
void a_title_align(lv_obj_t *o, const lv_obj_t *base, uint8_t al, lv_coord_t x, lv_coord_t y) {
    if (!active()) { lv_obj_align_to(o, base, al, x, y); return; }
    lv_obj_set_style_text_font(o, &fw_font_cn21, 0);
    lv_obj_align(o, AL_TOP_LEFT, 22, 1);
}

// ---- 主界面刷新里切换格式点图片（只替换 UI1 分支那一处）
void a_dot_src(lv_obj_t *o, const void *src) {
    lv_img_set_src(o, src);
    if (G->magic != MAGIC) return;
    for (int i = 0; i < 3; i++)
        if (DOT_OBJ(i) == o) G->dot_on[i] = (src == &a_img_chip_on);
    if (active()) color_fmt_labels();
}

// ---- 自己的字库取字形
static const a_glyph_t *find(const lv_font_t *f, uint32_t u) {
    const a_font_dsc_t *d = f->dsc;
    int lo = 0, hi = d->n - 1;
    while (lo <= hi) {
        int m = (lo + hi) >> 1;
        if (d->gl[m].unicode == u) return &d->gl[m];
        if (d->gl[m].unicode < u) lo = m + 1; else hi = m - 1;
    }
    return 0;
}
bool a_font_get_dsc(const lv_font_t *f, lv_font_glyph_dsc_t *o, uint32_t letter, uint32_t next) {
    (void)next;
    const a_glyph_t *g = find(f, letter);
    if (!g) return false;
    o->adv_w = g->adv; o->box_w = g->w; o->box_h = g->h;
    o->ofs_x = g->ox; o->ofs_y = g->oy; o->bpp = 4; o->is_placeholder = 0;
    return true;
}
const uint8_t *a_font_get_bmp(const lv_font_t *f, uint32_t letter) {
    const a_glyph_t *g = find(f, letter);
    return g ? ((const a_font_dsc_t *)f->dsc)->bmp + g->off : 0;
}

// ================= A 风格设置菜单 =================
void a_menu_update(uint8_t init);
// 固件菜单状态（0x20000218）：+1 当前项 0..5，+2 是否调整中，+3 调整中的选项值，+4/+5 范围
#define MENU_ST(off) (*(volatile int8_t *)(0x20000218 + (off)))
#define EXT_CLK_LOSS (*(volatile uint8_t *)0x200000a6)
#define MENU_ITEM(lang, i)    (*(const char *const *)(0x0802AC40 + 0x50 * (lang) + 4 * (i)))
#define MENU_OPT(lang, it, i) (*(const char *const *)(0x0802A380 + 0x460 * (lang) + 0x50 * (it) + 4 * (i)))
FN(0x800e764, void, fw_build_menu, (void));
FN(0x800b7a8, void, fw_menu_update, (uint8_t init));
static const int8_t item_setting[6] = {0x0a, 0x0c, -1, 0x1c, 0x24, -1};   // 每项对应的设置变量偏移

static inline bool menu_active(void) { return G->magic == MAGIC && G->menu_on && THEME == 0; }

void a_build_menu(void) {
    G->magic = MAGIC; G->menu_on = 0;
    fw_build_menu();
    if (THEME != 0) return;
    for (int i = 0; i < 6; i++) G->m_last[i] = -100;
    G->m_hl = new_img(&a_img_msel, 6, 6);
    for (int i = 0; i < 6; i++) G->m_row[i] = new_label("", &a_font_item, 0x8C857B, AL_TOP_LEFT, 14, 7 + 20 * i);
    new_img(&a_img_vline2, 138, 6);
    G->m_name = new_label("", &a_font_item, 0x8C857B, AL_TOP_LEFT, 150, 8);
    G->m_val = new_label("", &a_font_val, 0xFFB547, AL_TOP_LEFT, 150, 36);
    for (int i = 0; i < 4; i++) G->m_seg[i] = new_img(&a_img_seg_off, 150 + 44 * i, 88);
    G->m_hint = new_label("", &a_font_hint, 0x6E685F, AL_TOP_RIGHT, -10, 112);
    G->menu_on = 1;
    a_menu_update(0);
}

void a_menu_update(uint8_t init) {
    fw_menu_update(init);
    if (!menu_active()) return;
    // 原版菜单的所有对象（标题、选中框、选项底板、顶部刻度/指针/标题牌）每次刷新后都保持隐藏
    for (int i = 0; i < 8; i++) hide(child(i));

    int lang = SET_U16(0x16) ? 1 : 0;
    int item = MENU_ST(1), edit = MENU_ST(2) ? 1 : 0, val = MENU_ST(3);
    if (item < 0 || item > 5) return;
    int loss = (EXT_CLK_LOSS && item == 3) ? 1 : 0;
    int cur = item_setting[item] >= 0 ? SET_U16(item_setting[item]) : 0;
    int8_t now[6] = {(int8_t)item, (int8_t)edit, (int8_t)val, (int8_t)lang, (int8_t)loss, (int8_t)cur};
    bool same = true;
    for (int i = 0; i < 6; i++) if (now[i] != G->m_last[i]) same = false;
    if (same) return;
    bool relabel = now[3] != G->m_last[3];
    for (int i = 0; i < 6; i++) G->m_last[i] = now[i];

    // 左侧列表
    for (int i = 0; i < 6; i++) {
        if (relabel) lv_label_set_text(G->m_row[i], MENU_ITEM(lang, i));
        uint32_t c = i != item ? 0x8C857B : (edit ? 0xFFB547 : 0x0B0B0C);
        lv_obj_set_style_text_color(G->m_row[i], lv_color_hex(c), 0);
    }
    lv_img_set_src(G->m_hl, edit ? &a_img_medit : &a_img_msel);
    lv_obj_align(G->m_hl, AL_TOP_LEFT, 6, 6 + 20 * item);

    // 右侧：项名、数值、刻度格
    lv_label_set_text(G->m_name, MENU_ITEM(lang, item));
    int shown = edit ? val : cur;
    const char *t;
    if (loss && !edit)        t = a_menu_extra[2][lang];          // 时钟失联
    else if (edit)            t = MENU_OPT(lang, item, shown);
    else if (item == 2)       t = a_menu_extra[0][lang];          // 复位：恢复出厂设置
    else if (item == 5)       t = a_menu_extra[1][lang];          // 返回：回到主界面
    else                      t = MENU_OPT(lang, item, shown);
    if (!t) t = "";
    if (edit) {
        char buf[48];
        fw_sprintf(buf, "< %s >", t);
        lv_label_set_text(G->m_val, buf);
    } else {
        lv_label_set_text(G->m_val, t);
    }
    lv_obj_set_style_text_color(G->m_val, lv_color_hex(loss && !edit ? 0xFF6A3D : 0xFFB547), 0);
    for (int i = 0; i < 4; i++) {
        if (item <= 1) { show(G->m_seg[i]); lv_img_set_src(G->m_seg[i], i <= shown ? &a_img_seg_on : &a_img_seg_off); }
        else hide(G->m_seg[i]);
    }
    lv_label_set_text(G->m_hint, a_menu_hint[lang * 2 + edit]);
}

// ================= 语言选择界面 / 开机「正在启动」界面 =================
// 语言界面子对象：0 底板图 1「中文」2「English」3 下划线（固件按语言把它对齐到 x=-55 或 +45）
FN(0x800e3a0, void, fw_build_lang, (void));
FN(0x800babc, void, fw_lang_update, (uint8_t init));
FN(0x800f144, void, fw_build_prompt, (void));
FN(0x8024b64, void, lv_obj_set_size2, (lv_obj_t *o, lv_coord_t w, lv_coord_t h));
FN(0x8024d7c, void, lv_obj_set_style_bg_color, (lv_obj_t *o, lv_color_t c, uint32_t sel));

void a_lang_update(uint8_t init) {
    fw_lang_update(init);
    if (!(G->magic == MAGIC && G->lang_on && THEME == 0)) return;
    bool cn = SET_U16(0x16) != 0;
    lv_obj_set_style_text_color(child(1), lv_color_hex(cn ? 0xFFB547 : 0x6E685F), 0);
    lv_obj_set_style_text_color(child(2), lv_color_hex(cn ? 0x6E685F : 0xFFB547), 0);
}
void a_build_lang(void) {
    G->magic = MAGIC; G->lang_on = 0;
    fw_build_lang();
    if (THEME != 0) return;
    hide(child(0));
    place(child(1), &a_font_val, 0, AL_CENTER, -55, -6);
    place(child(2), &a_font_val, 0, AL_CENTER, 45, -6);
    lv_obj_set_size2(child(3), 76, 2);
    lv_obj_set_style_bg_color(child(3), lv_color_hex(0xFFB547), 0);
    new_label("语言 · LANGUAGE", &a_font_item, 0x8C857B, AL_TOP_MID, 0, 8);
    new_img(&a_img_hline, 0, 30);
    new_label(a_menu_hint[4], &a_font_hint, 0x6E685F, AL_TOP_MID, 0, 98);
    new_label(a_menu_hint[5], &a_font_hint, 0x6E685F, AL_TOP_MID, 0, 114);
    G->lang_on = 1;
    a_lang_update(0);
}
// 开机界面子对象：0 底板图 1「正在启动 / STARTING」2 跳动的点
void a_build_prompt(void) {
    fw_build_prompt();
    if (THEME != 0) return;
    hide(child(0));
    place(child(1), &a_font_val, 0xE8E4DC, AL_CENTER, 0, -14);
    place(child(2), &a_font_val, 0xFFB547, AL_CENTER, 0, 16);
    new_img(&a_img_dot, 237, 8);
}
