"""
太阳系 3D 模拟程序
使用 Pygame + OpenGL 展示太阳系八大行星的运动轨迹

操作方式：
- 鼠标左键拖动：旋转视角
- 鼠标滚轮：缩放
- I/J/K/L 键：相机前后左右移动（基于当前朝向）
- U/O 键：相机上/下移动
- 空格键：暂停/继续
- +/- 键：调整速度
- A/D 键：水平旋转
- W/S 键：垂直旋转
- R 键：重置视角
- M 键：菜单
- ESC：退出
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import sys

# 作者信息
VERSION = "1.0.0"
AUTHOR_NAME = "JachynRen"
AUTHOR_EMAIL = "784217755@qq.com"
GITHUB_URL = "https://github.com/JachynRen/Solar_system"

# 行星数据：(名称, 轨道半径, 半径, 公转周期(天), 颜色RGB, 初始角度)
PLANETS_DATA = [
    ("水星", 8, 0.35, 88, (0.7, 0.7, 0.7), 0),
    ("金星", 11, 0.55, 225, (1.0, 0.75, 0.4), math.pi / 4),
    ("地球", 15, 0.55, 365, (0.2, 0.5, 1.0), math.pi / 2),
    ("火星", 20, 0.4, 687, (0.9, 0.3, 0.1), math.pi),
    ("木星", 30, 1.8, 4333, (0.85, 0.65, 0.45), 3 * math.pi / 4),
    ("土星", 42, 1.5, 10759, (0.95, 0.85, 0.55), 5 * math.pi / 4),
    ("天王星", 55, 0.9, 30687, (0.5, 0.85, 0.95), 3 * math.pi / 2),
    ("海王星", 68, 0.85, 60190, (0.2, 0.3, 0.9), 7 * math.pi / 4),
]

# 卫星数据：(名称, 父行星, 轨道半径, 半径, 公转周期(天), 颜色RGB, 初始角度)
SATELLITES_DATA = [
    ("月球", "地球", 2.5, 0.2, 27.3, (0.85, 0.85, 0.85), 0),
]

# 星球科普信息
PLANET_INFO = {
    "太阳": {
        "type": "恒星",
        "diameter": "1,392,700 km",
        "distance": "0 km",
        "period": "N/A",
        "temperature": "表面约 5,500°C",
        "description": "太阳是太阳系的中心天体，一颗G型主序星，占太阳系总质量的99.86%。",
    },
    "水星": {
        "type": "类地行星",
        "diameter": "4,879 km",
        "distance": "5,790万 km",
        "period": "88天",
        "temperature": "-173°C ~ 427°C",
        "description": "水星是距太阳最近的行星，也是太阳系中最小的行星，表面布满陨石坑。",
    },
    "金星": {
        "type": "类地行星",
        "diameter": "12,104 km",
        "distance": "1.082亿 km",
        "period": "225天",
        "temperature": "约 462°C",
        "description": "金星是太阳系中最热的行星，浓厚的二氧化碳大气层产生强烈的温室效应。",
    },
    "地球": {
        "type": "类地行星",
        "diameter": "12,756 km",
        "distance": "1.496亿 km",
        "period": "365.25天",
        "temperature": "-89°C ~ 57°C",
        "description": "地球是已知唯一存在生命的天体，拥有液态水海洋和含氧大气层。",
    },
    "月球": {
        "type": "卫星",
        "diameter": "3,474 km",
        "distance": "距地球38.4万 km",
        "period": "27.3天",
        "temperature": "-173°C ~ 127°C",
        "description": "月球是地球唯一的天然卫星，也是人类唯一踏足过的地外天体，对地球潮汐有重要影响。",
    },
    "火星": {
        "type": "类地行星",
        "diameter": "6,792 km",
        "distance": "2.279亿 km",
        "period": "687天",
        "temperature": "-140°C ~ 20°C",
        "description": "火星被称为红色星球，表面富含氧化铁，拥有太阳系最高的火山——奥林帕斯山。",
    },
    "木星": {
        "type": "气态巨行星",
        "diameter": "142,984 km",
        "distance": "7.786亿 km",
        "period": "11.86年",
        "temperature": "约 -110°C（云顶）",
        "description": "木星是太阳系最大的行星，其质量是其他所有行星总和的2.5倍，著名的大红斑是一个持续数百年的风暴。",
    },
    "土星": {
        "type": "气态巨行星",
        "diameter": "120,536 km",
        "distance": "14.34亿 km",
        "period": "29.46年",
        "temperature": "约 -140°C（云顶）",
        "description": "土星以其壮观的环系统闻名，环主要由冰粒和岩石碎片组成，密度比水还低。",
    },
    "天王星": {
        "type": "冰巨行星",
        "diameter": "51,118 km",
        "distance": "28.71亿 km",
        "period": "84.01年",
        "temperature": "约 -195°C",
        "description": "天王星的自转轴几乎平躺在轨道面上，倾斜角达98°，是太阳系中唯一'躺着转'的行星。",
    },
    "海王星": {
        "type": "冰巨行星",
        "diameter": "49,528 km",
        "distance": "45.04亿 km",
        "period": "164.8年",
        "temperature": "约 -200°C",
        "description": "海王星是太阳系最远的行星，拥有最强的风暴，风速可达2,100 km/h。",
    },
}


def _project_3d_to_2d(x3d, y3d, z3d, cam, width, height):
    """将 3D 世界坐标投影到 2D 屏幕坐标。

    严格遵循 OpenGL draw_scene 中的变换顺序。
    OpenGL 的变换是右乘，所以应用到顶点的顺序是从后往前：
        实际渲染顺序: Ry -> Rx -> T(0,0,distance) -> T(-cam.x, -cam.y, -cam.z)
    """
    rx = math.radians(cam['rot_x'])
    ry = math.radians(cam['rot_y'])

    x = float(x3d)
    y = float(y3d)
    z = float(z3d)

    # 1) 先应用绕 Y 轴旋转 (最后声明的变换最先应用)
    cx = x * math.cos(ry) - z * math.sin(ry)
    cz = x * math.sin(ry) + z * math.cos(ry)
    x, z = cx, cz

    # 2) 再应用绕 X 轴旋转
    cy = y * math.cos(rx) - z * math.sin(rx)
    cz = y * math.sin(rx) + z * math.cos(rx)
    y, z = cy, cz

    # 3) 再应用相机距离 T(0, 0, distance)
    z += cam['distance']

    # 4) 最后应用相机平移 T(-cam.x, -cam.y, -cam.z)
    x -= cam['x']
    y -= cam['y']
    z -= cam['z']

    if z <= 0.1:
        return None  # 物体在相机后面

    # 5) 透视投影 (与 gluPerspective 60° FOV 一致)
    fov = 60.0
    aspect = width / height
    f = 1.0 / math.tan(math.radians(fov / 2.0))

    nx = (f / aspect) * (x / z)
    ny = f * (y / z)

    # NDC [-1,1] -> 屏幕像素
    sx = (nx * 0.5 + 0.5) * width
    sy = (-ny * 0.5 + 0.5) * height

    return (sx, sy)


def draw_sphere(radius, color, slices=32, stacks=32):
    """绘制一个球体"""
    glColor3f(*color)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, list(color) + [1.0])

    for i in range(stacks):
        lat0 = math.pi * (-0.5 + i / stacks)
        lat1 = math.pi * (-0.5 + (i + 1) / stacks)

        z0 = math.sin(lat0)
        z1 = math.sin(lat1)
        r0 = math.cos(lat0)
        r1 = math.cos(lat1)

        glBegin(GL_QUAD_STRIP)
        for j in range(slices + 1):
            lon = 2 * math.pi * j / slices
            x = math.cos(lon)
            y = math.sin(lon)

            glNormal3f(x * r0, y * r0, z0)
            glVertex3f(x * r0 * radius, y * r0 * radius, z0 * radius)

            glNormal3f(x * r1, y * r1, z1)
            glVertex3f(x * r1 * radius, y * r1 * radius, z1 * radius)
        glEnd()


def draw_orbit(radius):
    """绘制轨道圆环"""
    glColor3f(0.4, 0.4, 0.5)
    glBegin(GL_LINE_LOOP)
    for i in range(128):
        angle = 2 * math.pi * i / 128
        glVertex3f(radius * math.cos(angle), 0, radius * math.sin(angle))
    glEnd()


def draw_saturn_ring(inner_radius, outer_radius):
    """绘制土星环"""
    glColor3f(0.8, 0.7, 0.5)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.8, 0.7, 0.5, 1.0])

    segments = 64
    glBegin(GL_QUAD_STRIP)
    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        x = math.cos(angle)
        z = math.sin(angle)
        glVertex3f(x * inner_radius, 0, z * inner_radius)
        glVertex3f(x * outer_radius, 0, z * outer_radius)
    glEnd()


def draw_sun():
    """绘制太阳（带发光效果）"""
    glDisable(GL_LIGHTING)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glColor4f(1.0, 0.6, 0.0, 0.15)
    draw_sphere_raw(4.0, 24, 24)

    glColor4f(1.0, 0.8, 0.0, 0.3)
    draw_sphere_raw(3.2, 24, 24)

    glColor4f(1.0, 0.95, 0.2, 0.5)
    draw_sphere_raw(2.5, 24, 24)

    glColor3f(1.0, 1.0, 0.0)
    draw_sphere_raw(2.0, 32, 32)

    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)


def draw_sphere_raw(radius, slices, stacks):
    """绘制球体（无材质设置）"""
    for i in range(stacks):
        lat0 = math.pi * (-0.5 + i / stacks)
        lat1 = math.pi * (-0.5 + (i + 1) / stacks)

        z0 = math.sin(lat0)
        z1 = math.sin(lat1)
        r0 = math.cos(lat0)
        r1 = math.cos(lat1)

        glBegin(GL_QUAD_STRIP)
        for j in range(slices + 1):
            lon = 2 * math.pi * j / slices
            x = math.cos(lon)
            y = math.sin(lon)

            glVertex3f(x * r0 * radius, y * r0 * radius, z0 * radius)
            glVertex3f(x * r1 * radius, y * r1 * radius, z1 * radius)
        glEnd()


def draw_stars():
    """绘制星空背景"""
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_POINTS)
    for i in range(500):
        seed = i * 127.1 + 311.7
        x = math.sin(seed) * 150
        seed = i * 269.5 + 183.3
        y = math.cos(seed) * 100
        seed = i * 419.2 + 117.3
        z = math.sin(seed) * 150
        glVertex3f(x, y, z)
    glEnd()
    glEnable(GL_LIGHTING)


# ========== 2D UI 绘制 ==========

HELP_LINES = [
    "=== 操作说明 ===",
    "",
    "鼠标左键拖动   旋转视角",
    "鼠标滚轮       缩放",
    "W/S            俯仰旋转",
    "A/D            水平旋转",
    "I/J/K/L        相机前后左右移动",
    "U/O            相机上/下移动",
    "+/-            调整模拟速度",
    "空格           暂停/继续",
    "R              重置视角",
    "F              快速视角切换",
    "M              打开菜单",
    "ESC            退出",
    "",
    "--- 触控板手势 ---",
    "单指拖动       旋转视角",
    "双指轻点       暂停/继续",
    "双指拖动       旋转视角",
    "右键/双指轻按  重置视角",
    "捏合           缩放",
]

ABOUT_LINES = [
    f"太阳系 3D 模拟 v{VERSION}",
    "",
    f"作者: {AUTHOR_NAME}",
    f"邮箱: {AUTHOR_EMAIL}",
    f"GitHub: {GITHUB_URL}",
]

FONT_SIZE = 18
LINE_H = 28
MENU_PAD = 18

# 顶部菜单栏
MENUBAR_H = 30
MENUBAR_BG = (40, 40, 65)
MENUBAR_TEXT = (240, 240, 250)
MENUBAR_HOVER = (70, 70, 120)

# 菜单定义
MENU_ITEMS = {
    "文件": [
        ("重置视角", "reset_camera"),
        ("退出", "quit"),
    ],
    "视图": [
        ("默认视角", "view_default"),
        ("俯视", "view_top"),
        ("侧视", "view_side"),
    ],
    "模拟": [
        ("暂停/继续", "toggle_pause"),
        ("加速", "speed_up"),
        ("减速", "speed_down"),
    ],
    "帮助": [
        ("操作说明", "show_help"),
        ("关于", "show_about"),
    ],
}
MENU_BG = (30, 30, 55)
MENU_BORDER = (120, 160, 220)
MENU_TEXT = (255, 255, 255)
MENU_TITLE = (255, 220, 120)
BTN_BG = (45, 45, 90)
BTN_BORDER = (120, 160, 220)
BTN_TEXT = (240, 240, 250)
BTN_HOVER = (70, 70, 140)


def _draw_filled_rect(surf, rect, color):
    pygame.draw.rect(surf, color, rect)


def _draw_rect_border(surf, rect, color, width=2):
    pygame.draw.rect(surf, color, rect, width)


def _render_text(font, text, color):
    """渲染文字 Surface，确保带 alpha 通道"""
    surf = font.render(text, True, color)
    return surf.convert_alpha()


def draw_menubar_overlay(font, mouse_pos, menu_state, game_state):
    """
    用 OpenGL 绘制顶部菜单栏 + 下拉菜单（2D 正交投影覆盖层）。
    """
    width, height = pygame.display.get_surface().get_size()

    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, height, 0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_LIGHTING)

    rects = {}

    # ---- 菜单栏背景 ----
    glColor4f(MENUBAR_BG[0]/255, MENUBAR_BG[1]/255, MENUBAR_BG[2]/255, 1.0)
    _gl_rect(0, 0, width, MENUBAR_H)

    # ---- 计算每个菜单项的位置 ----
    menu_names = list(MENU_ITEMS.keys())
    x = 10
    item_rects = {}
    for name in menu_names:
        txt_surf = _render_text(font, name, MENUBAR_TEXT)
        w = txt_surf.get_width() + 16
        r = pygame.Rect(x, 0, w, MENUBAR_H)
        item_rects[name] = r
        hovered = r.collidepoint(mouse_pos)
        if hovered:
            glColor4f(MENUBAR_HOVER[0]/255, MENUBAR_HOVER[1]/255, MENUBAR_HOVER[2]/255, 1.0)
            _gl_rect(x, 0, w, MENUBAR_H)
        _gl_blit_text(txt_surf, x + 8, 5, width, height)
        x += w + 2

    # ---- 下拉菜单 ----
    open_name = menu_state.get("open_menu")
    if open_name and open_name in item_rects:
        parent_rect = item_rects[open_name]
        items = MENU_ITEMS[open_name]

        max_w = 0
        for label, _ in items:
            tw = font.size(label)[0]
            if tw > max_w:
                max_w = tw
        drop_w = max_w + 30
        drop_h = len(items) * 28 + 8
        drop_x = parent_rect.x
        drop_y = MENUBAR_H
        drop_rect = pygame.Rect(drop_x, drop_y, drop_w, drop_h)

        # 面板背景
        glColor4f(MENU_BG[0]/255, MENU_BG[1]/255, MENU_BG[2]/255, 0.95)
        _gl_rect(drop_x, drop_y, drop_w, drop_h)
        # 边框
        glColor4f(MENU_BORDER[0]/255, MENU_BORDER[1]/255, MENU_BORDER[2]/255, 1.0)
        _gl_rect_border(drop_x, drop_y, drop_w, drop_h)

        for idx, (label, action) in enumerate(items):
            iy = drop_y + 4 + idx * 28
            ir = pygame.Rect(drop_x + 4, iy, drop_w - 8, 24)
            rects[f"item_{open_name}_{idx}"] = (action, ir)
            h = ir.collidepoint(mouse_pos)
            if h:
                glColor4f(50/255, 50/255, 100/255, 1.0)
                _gl_rect(drop_x + 4, iy, drop_w - 8, 24)
            txt_surf = _render_text(font, label, (255, 255, 255) if h else MENU_TEXT)
            _gl_blit_text(txt_surf, drop_x + 12, iy + 3, width, height)

    rects["menubar"] = pygame.Rect(0, 0, width, MENUBAR_H)
    rects["menu_items"] = item_rects

    glEnable(GL_LIGHTING)
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

    return rects


def draw_help_about_overlay(font, mouse_pos, mode):
    """用 OpenGL 绘制帮助/关于弹窗覆盖层。"""
    width, height = pygame.display.get_surface().get_size()

    if mode == "help":
        lines = HELP_LINES
    else:
        lines = ABOUT_LINES

    max_char_w = max(font.size(line)[0] for line in lines)
    panel_w = max_char_w + MENU_PAD * 2
    panel_h = len(lines) * LINE_H + MENU_PAD * 2 + 40
    panel_x = (width - panel_w) // 2
    panel_y = MENUBAR_H + 20
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, height, 0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_LIGHTING)

    # 遮罩
    glColor4f(0, 0, 0, 0.45)
    _gl_rect(0, 0, width, height)

    # 面板
    glColor4f(MENU_BG[0]/255, MENU_BG[1]/255, MENU_BG[2]/255, 0.95)
    _gl_rect(panel_x, panel_y, panel_w, panel_h)
    glColor4f(MENU_BORDER[0]/255, MENU_BORDER[1]/255, MENU_BORDER[2]/255, 1.0)
    _gl_rect_border(panel_x, panel_y, panel_w, panel_h)

    title_label = "操作说明" if mode == "help" else f"关于 v{VERSION}"
    txt_surf = _render_text(font, title_label, MENU_TITLE)
    _gl_blit_text(txt_surf, panel_x + MENU_PAD, panel_y + MENU_PAD, width, height)

    y = panel_y + MENU_PAD + LINE_H + 5
    for line in lines:
        if line.startswith("==="):
            c = MENU_TITLE
        elif line.startswith("---"):
            c = (100, 100, 130)
        elif line.startswith("作者") or line.startswith("邮箱") or line.startswith("GitHub"):
            c = (150, 180, 220)
        else:
            c = MENU_TEXT
        txt_surf = _render_text(font, line, c)
        _gl_blit_text(txt_surf, panel_x + MENU_PAD, y, width, height)
        y += LINE_H

    # 关闭按钮
    close_w, close_h = 70, 26
    close_x = panel_x + (panel_w - close_w) // 2
    close_y = panel_y + panel_h - close_h - 10
    close_rect = pygame.Rect(close_x, close_y, close_w, close_h)
    ch = close_rect.collidepoint(mouse_pos)
    c_color = BTN_HOVER if ch else BTN_BG
    glColor4f(c_color[0]/255, c_color[1]/255, c_color[2]/255, 1.0)
    _gl_rect(close_x, close_y, close_w, close_h)
    glColor4f(BTN_BORDER[0]/255, BTN_BORDER[1]/255, BTN_BORDER[2]/255, 1.0)
    _gl_rect_border(close_x, close_y, close_w, close_h)
    txt_surf = _render_text(font, "关闭", BTN_TEXT)
    _gl_blit_text(txt_surf, close_x + close_w//2 - txt_surf.get_width()//2,
                  close_y + close_h//2 - txt_surf.get_height()//2, width, height)

    glEnable(GL_LIGHTING)
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

    return close_rect, panel_rect


def _gl_rect(x, y, w, h):
    """OpenGL 绘制填充矩形"""
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()


def _gl_rect_border(x, y, w, h):
    """OpenGL 绘制矩形边框"""
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()


def _gl_blit_text(txt_surf, x, y, screen_w, screen_h):
    """将 pygame Surface 作为纹理绘制到 OpenGL 矩形上"""
    tw, th = txt_surf.get_width(), txt_surf.get_height()
    data = pygame.image.tostring(txt_surf, 'RGBA', True)
    glEnable(GL_TEXTURE_2D)
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tw, th, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

    glColor4f(1, 1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1); glVertex2f(x, y)
    glTexCoord2f(1, 1); glVertex2f(x + tw, y)
    glTexCoord2f(1, 0); glVertex2f(x + tw, y + th)
    glTexCoord2f(0, 0); glVertex2f(x, y + th)
    glEnd()

    glDeleteTextures([tex])
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)


def _calc_planet_screen_positions(cam, planet_positions, speed, t, width, height):
    """计算所有星球（太阳 + 行星 + 卫星）在当前帧的屏幕位置和点击半径。

    返回字典: {name: (screen_x, screen_y, click_radius)}
    """
    positions = {}

    # 太阳位置 (0, 0, 0)
    sp = _project_3d_to_2d(0, 0, 0, cam, width, height)
    if sp is not None:
        # 太阳的屏幕点击半径根据其在 3D 中的大小估算
        positions["太阳"] = (sp[0], sp[1], 30)  # 增大点击半径

    # 行星
    for name, orbit_radius, radius, period, color, angle in PLANETS_DATA:
        angular_velocity = 2 * math.pi / period
        current_angle = angle + angular_velocity * t * speed
        px = orbit_radius * math.cos(current_angle)
        pz = orbit_radius * math.sin(current_angle)

        sp = _project_3d_to_2d(px, 0, pz, cam, width, height)
        if sp is not None:
            click_radius = max(18, int(radius * 12))  # 增大点击半径
            positions[name] = (sp[0], sp[1], click_radius)

    # 卫星
    for sat_name, parent_name, sat_orbit_radius, sat_radius, sat_period, sat_color, sat_angle in SATELLITES_DATA:
        if parent_name in planet_positions:
            ppx, ppz = planet_positions[parent_name]
            sat_angular_velocity = 2 * math.pi / sat_period
            sat_current_angle = sat_angle + sat_angular_velocity * t * speed
            sx = ppx + sat_orbit_radius * math.cos(sat_current_angle)
            sz = ppz + sat_orbit_radius * math.sin(sat_current_angle)

            sp = _project_3d_to_2d(sx, 0, sz, cam, width, height)
            if sp is not None:
                click_radius = max(12, int(sat_radius * 15))  # 增大卫星点击半径
                positions[sat_name] = (sp[0], sp[1], click_radius)

    return positions


# 信息面板颜色
INFO_BG = (25, 25, 50)
INFO_BORDER = (120, 160, 220)
INFO_TITLE = (255, 220, 120)
INFO_LABEL = (160, 180, 220)
INFO_VALUE = (240, 240, 250)
INFO_LINE = (60, 60, 100)


def draw_planet_info_overlay(font, mouse_pos, planet_name, planet_positions):
    """用 OpenGL 绘制星球科普信息面板。"""
    width, height = pygame.display.get_surface().get_size()

    if planet_name not in PLANET_INFO:
        return None, None

    info = PLANET_INFO[planet_name]
    lines = [
        ("名称", planet_name),
        ("类型", info["type"]),
        ("直径", info["diameter"]),
        ("距太阳", info["distance"]),
        ("公转周期", info["period"]),
        ("温度", info["temperature"]),
        ("简介", info["description"]),
    ]

    # 计算面板尺寸
    label_max_w = max(font.size(label)[0] for label, _ in lines)
    value_max_w = max(font.size(val)[0] for _, val in lines)
    title_w = font.size(planet_name)[0]

    panel_w = max(title_w, label_max_w + value_max_w + 20) + MENU_PAD * 2 + 20
    panel_h = (len(lines) + 1) * LINE_H + MENU_PAD * 2 + 30
    panel_x = (width - panel_w) // 2
    panel_y = (height - panel_h) // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, height, 0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_LIGHTING)

    # 遮罩
    glColor4f(0, 0, 0, 0.35)
    _gl_rect(0, 0, width, height)

    # 面板背景
    glColor4f(INFO_BG[0]/255, INFO_BG[1]/255, INFO_BG[2]/255, 0.95)
    _gl_rect(panel_x, panel_y, panel_w, panel_h)
    # 边框
    glColor4f(INFO_BORDER[0]/255, INFO_BORDER[1]/255, INFO_BORDER[2]/255, 1.0)
    _gl_rect_border(panel_x, panel_y, panel_w, panel_h)

    # 标题
    txt_surf = _render_text(font, planet_name, INFO_TITLE)
    _gl_blit_text(txt_surf, panel_x + MENU_PAD, panel_y + MENU_PAD, width, height)

    # 分隔线
    sep_y = panel_y + MENU_PAD + LINE_H
    glColor4f(INFO_LINE[0]/255, INFO_LINE[1]/255, INFO_LINE[2]/255, 1.0)
    glBegin(GL_LINES)
    glVertex2f(panel_x + MENU_PAD, sep_y)
    glVertex2f(panel_x + panel_w - MENU_PAD, sep_y)
    glEnd()

    # 信息行
    y = sep_y + LINE_H // 2 + 5
    for label, value in lines:
        lbl_surf = _render_text(font, label + ":", INFO_LABEL)
        _gl_blit_text(lbl_surf, panel_x + MENU_PAD, y, width, height)
        val_surf = _render_text(font, value, INFO_VALUE)
        _gl_blit_text(val_surf, panel_x + MENU_PAD + label_max_w + 10, y, width, height)
        y += LINE_H

    # 关闭按钮
    close_w, close_h = 70, 26
    close_x = panel_x + (panel_w - close_w) // 2
    close_y = panel_y + panel_h - close_h - 10
    close_rect = pygame.Rect(close_x, close_y, close_w, close_h)
    ch = close_rect.collidepoint(mouse_pos)
    c_color = BTN_HOVER if ch else BTN_BG
    glColor4f(c_color[0]/255, c_color[1]/255, c_color[2]/255, 1.0)
    _gl_rect(close_x, close_y, close_w, close_h)
    glColor4f(BTN_BORDER[0]/255, BTN_BORDER[1]/255, BTN_BORDER[2]/255, 1.0)
    _gl_rect_border(close_x, close_y, close_w, close_h)
    txt_surf = _render_text(font, "关闭", BTN_TEXT)
    _gl_blit_text(txt_surf, close_x + close_w//2 - txt_surf.get_width()//2,
                  close_y + close_h//2 - txt_surf.get_height()//2, width, height)

    glEnable(GL_LIGHTING)
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

    return close_rect, panel_rect


def draw_satellite_orbit(radius):
    """绘制卫星轨道圆环（相对于已变换的坐标系）"""
    glColor3f(0.5, 0.5, 0.6)
    glBegin(GL_LINE_LOOP)
    for i in range(64):
        angle = 2 * math.pi * i / 64
        glVertex3f(radius * math.cos(angle), 0, radius * math.sin(angle))
    glEnd()


def draw_scene(cam, speed, t, paused):
    """绘制 3D 场景"""
    glClearColor(0.02, 0.02, 0.05, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(-cam['x'], -cam['y'], -cam['z'])
    glTranslatef(0, 0, cam['distance'])
    glRotatef(cam['rot_x'], 1, 0, 0)
    glRotatef(cam['rot_y'], 0, 1, 0)

    glPushMatrix()
    glRotatef(-cam['rot_y'], 0, 1, 0)
    glRotatef(-cam['rot_x'], 1, 0, 0)
    draw_stars()
    glPopMatrix()

    draw_sun()

    # 存储行星位置供卫星使用
    planet_positions = {}

    for name, orbit_radius, radius, period, color, angle in PLANETS_DATA:
        draw_orbit(orbit_radius)
        angular_velocity = 2 * math.pi / period
        current_angle = angle + angular_velocity * t * speed
        px = orbit_radius * math.cos(current_angle)
        pz = orbit_radius * math.sin(current_angle)

        # 存储行星位置
        planet_positions[name] = (px, pz)

        glPushMatrix()
        glTranslatef(px, 0, pz)
        if name == "土星":
            glPushMatrix()
            glRotatef(25, 1, 0, 0)
            draw_saturn_ring(radius * 1.4, radius * 2.3)
            glPopMatrix()
        draw_sphere(radius, color)
        glPopMatrix()

    # 绘制卫星
    for sat_name, parent_name, sat_orbit_radius, sat_radius, sat_period, sat_color, sat_angle in SATELLITES_DATA:
        if parent_name in planet_positions:
            ppx, ppz = planet_positions[parent_name]
            # 计算卫星位置
            sat_angular_velocity = 2 * math.pi / sat_period
            sat_current_angle = sat_angle + sat_angular_velocity * t * speed
            sx = ppx + sat_orbit_radius * math.cos(sat_current_angle)
            sz = ppz + sat_orbit_radius * math.sin(sat_current_angle)

            # 绘制卫星轨道（在父行星位置）
            glPushMatrix()
            glTranslatef(ppx, 0, ppz)
            draw_satellite_orbit(sat_orbit_radius)
            glPopMatrix()

            # 绘制卫星
            glPushMatrix()
            glTranslatef(sx, 0, sz)
            draw_sphere(sat_radius, sat_color)
            glPopMatrix()

    # 返回行星位置信息用于点击检测
    return planet_positions


def process_camera(cam, keys, dragging, velocity, damping):
    """处理相机控制"""
    if not dragging:
        if abs(velocity['x']) > 0.01 or abs(velocity['y']) > 0.01:
            cam['rot_y'] += velocity['x']
            cam['rot_x'] += velocity['y']
            cam['rot_x'] = max(-89, min(89, cam['rot_x']))
            velocity['x'] *= damping
            velocity['y'] *= damping

    if keys[K_UP]:
        cam['distance'] = max(30, cam['distance'] - 1)
    if keys[K_DOWN]:
        cam['distance'] = min(200, cam['distance'] + 1)
    if keys[K_a]:
        cam['rot_y'] -= 1.5
    if keys[K_d]:
        cam['rot_y'] += 1.5
    if keys[K_w]:
        cam['rot_x'] += 1.5
        cam['rot_x'] = max(-89, min(89, cam['rot_x']))
    if keys[K_s]:
        cam['rot_x'] -= 1.5
        cam['rot_x'] = max(-89, min(89, cam['rot_x']))

    move_speed = 1.0
    rot_rad_x = math.radians(cam['rot_x'])
    rot_rad_y = math.radians(cam['rot_y'])
    if keys[K_i]:
        cam['x'] += math.sin(rot_rad_y) * math.cos(rot_rad_x) * move_speed
        cam['y'] -= math.sin(rot_rad_x) * move_speed
        cam['z'] += math.cos(rot_rad_y) * math.cos(rot_rad_x) * move_speed
    if keys[K_k]:
        cam['x'] -= math.sin(rot_rad_y) * math.cos(rot_rad_x) * move_speed
        cam['y'] += math.sin(rot_rad_x) * move_speed
        cam['z'] -= math.cos(rot_rad_y) * math.cos(rot_rad_x) * move_speed
    if keys[K_j]:
        cam['x'] += math.cos(rot_rad_y) * move_speed
        cam['z'] -= math.sin(rot_rad_y) * move_speed
    if keys[K_l]:
        cam['x'] -= math.cos(rot_rad_y) * move_speed
        cam['z'] += math.sin(rot_rad_y) * move_speed
    if keys[K_u]:
        cam['y'] += move_speed
    if keys[K_o]:
        cam['y'] -= move_speed


def main():
    pygame.init()

    width, height = 1200, 800
    screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | RESIZABLE)
    pygame.display.set_caption(f'太阳系 3D 模拟 v{VERSION}')

    # 启用光照
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE)

    glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 0.0, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 0.9, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.2, 1.0])

    glLightfv(GL_LIGHT1, GL_POSITION, [50.0, 50.0, 50.0, 0.0])
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.2, 0.2, 0.3, 1.0])

    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, width / height, 0.1, 500.0)
    glMatrixMode(GL_MODELVIEW)

    # 相机
    cam = {
        'rot_x': -25, 'rot_y': 0, 'distance': 90,
        'x': 0.0, 'y': 0.0, 'z': 0.0,
    }

    clock = pygame.time.Clock()
    running = True
    speed = 1.0
    t = 0
    paused = False

    dragging = False
    last_pos = (0, 0)
    velocity = {'x': 0.0, 'y': 0.0}
    damping = 0.92

    menu_state = {"open_menu": None}  # 顶部菜单状态
    popup_mode = None  # 'help' 或 'about' 弹窗模式
    selected_planet = None  # 当前选中的星球（显示科普面板）
    planet_screen_positions = {}  # 星球屏幕位置: {name: (sx, sy, radius)}
    mouse_pos = (0, 0)
    font = pygame.font.SysFont("arial", FONT_SIZE)

    # 存储每帧的菜单 rect（用于事件检测）
    menu_rects = {}
    popup_close_rect = None
    info_close_rect = None
    info_panel_rect = None

    # 尝试用系统字体，优先用清晰的字体
    available_fonts = pygame.font.get_fonts()
    font_name = None
    for name in ["pingfangsc", "hiraginosansgb", "arialunicodems", "microsoftyahei", "arial"]:
        if name in available_fonts:
            font_name = name
            break
    font = pygame.font.SysFont(font_name if font_name else "arial", FONT_SIZE)

    while running:
        # ---- 先处理事件 ----
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                running = False

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_SPACE:
                    paused = not paused
                elif event.key == K_PLUS or event.key == K_EQUALS:
                    speed = min(10.0, speed + 0.5)
                elif event.key == K_MINUS or event.key == K_UNDERSCORE:
                    speed = max(0.1, speed - 0.5)
                elif event.key == K_r:
                    cam['rot_x'] = -25
                    cam['rot_y'] = 0
                    cam['distance'] = 90
                    cam['x'] = cam['y'] = cam['z'] = 0.0
                elif event.key == K_f:
                    cam['rot_x'] = -45
                    cam['rot_y'] += 45
                    cam['distance'] = 70
                elif event.key == K_m:
                    popup_mode = "help" if popup_mode != "help" else None

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键/触控板点击
                    mx, my = event.pos
                    handled = False

                    # 1) 关闭弹窗按钮
                    if popup_mode and popup_close_rect:
                        if popup_close_rect.collidepoint(mx, my):
                            popup_mode = None
                            handled = True

                    # 2) 关闭星球信息面板按钮
                    if not handled and selected_planet and info_close_rect:
                        if info_close_rect.collidepoint(mx, my):
                            selected_planet = None
                            handled = True

                    if not handled:
                        # 3) 点击菜单区域 → 菜单交互
                        item_rects = menu_rects.get("menu_items", {})

                        # 检查是否点击菜单标题
                        for mname, mrect in item_rects.items():
                            if mrect.collidepoint(mx, my):
                                if menu_state["open_menu"] == mname:
                                    menu_state["open_menu"] = None
                                else:
                                    menu_state["open_menu"] = mname
                                handled = True
                                break

                        # 检查是否点击下拉菜单项
                        if not handled:
                            for key, val in menu_rects.items():
                                if not key.startswith("item_"):
                                    continue
                                action, ir = val
                                if ir.collidepoint(mx, my):
                                    if action == "quit":
                                        running = False
                                    elif action == "reset_camera":
                                        cam['rot_x'] = -25; cam['rot_y'] = 0
                                        cam['distance'] = 90
                                        cam['x'] = cam['y'] = cam['z'] = 0.0
                                    elif action == "view_default":
                                        cam['rot_x'] = -25; cam['rot_y'] = 0
                                        cam['distance'] = 90
                                        cam['x'] = cam['y'] = cam['z'] = 0.0
                                    elif action == "view_top":
                                        cam['rot_x'] = -80; cam['rot_y'] = 0
                                        cam['distance'] = 120
                                        cam['x'] = cam['y'] = cam['z'] = 0.0
                                    elif action == "view_side":
                                        cam['rot_x'] = -5; cam['rot_y'] = 0
                                        cam['distance'] = 100
                                        cam['x'] = cam['y'] = cam['z'] = 0.0
                                    elif action == "toggle_pause":
                                        paused = not paused
                                    elif action == "speed_up":
                                        speed = min(10.0, speed + 0.5)
                                    elif action == "speed_down":
                                        speed = max(0.1, speed - 0.5)
                                    elif action == "show_help":
                                        popup_mode = "help"
                                        menu_state["open_menu"] = None
                                    elif action == "show_about":
                                        popup_mode = "about"
                                        menu_state["open_menu"] = None
                                    handled = True
                                    break

                        # 4) 点击空白关闭菜单 / 点击星球
                        if not handled:
                            menu_state["open_menu"] = None

                            # 检测是否点击了某个星球
                            clicked_planet = None
                            for pname, (sx, sy, cr) in planet_screen_positions.items():
                                dist = math.sqrt((mx - sx) ** 2 + (my - sy) ** 2)
                                if dist < cr:
                                    clicked_planet = pname
                                    break

                            if clicked_planet and not popup_mode:
                                selected_planet = clicked_planet
                                handled = True
                            elif not selected_planet:
                                dragging = True

                    last_pos = event.pos
                    velocity['x'] = velocity['y'] = 0.0

                elif event.button == 2:  # 中键/触控板双指点击
                    # 双指点击：切换暂停状态
                    paused = not paused

                elif event.button == 3:  # 右键/触控板双指轻点
                    # 右键点击：重置视角
                    cam['rot_x'] = -25
                    cam['rot_y'] = 0
                    cam['distance'] = 90
                    cam['x'] = cam['y'] = cam['z'] = 0.0

                elif event.button == 4:  # 滚轮向上
                    cam['distance'] = max(30, cam['distance'] - 3)
                elif event.button == 5:
                    cam['distance'] = min(200, cam['distance'] + 3)

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False

            elif event.type == MOUSEMOTION:
                mouse_pos = event.pos
                if dragging and not popup_mode and not menu_state.get("open_menu"):
                    dx = event.pos[0] - last_pos[0]
                    dy = event.pos[1] - last_pos[1]
                    velocity['x'] = dx * 0.4
                    velocity['y'] = -dy * 0.4
                    cam['rot_y'] += velocity['x']
                    cam['rot_x'] += velocity['y']
                    cam['rot_x'] = max(-89, min(89, cam['rot_x']))
                    last_pos = event.pos

        # 相机控制
        keys = pygame.key.get_pressed()
        process_camera(cam, keys, dragging, velocity, damping)

        # ---- 渲染 ----
        planet_positions = draw_scene(cam, speed, t, paused)

        # 计算星球屏幕位置（用于点击检测和信息面板）
        width, height = pygame.display.get_surface().get_size()
        planet_screen_positions = _calc_planet_screen_positions(cam, planet_positions, speed, t, width, height)

        # ---- 2D overlay ----
        # 顶部菜单栏 + 下拉菜单（保存 rect 供下一帧事件检测用）
        menu_rects = draw_menubar_overlay(font, mouse_pos, menu_state,
                                          {'paused': paused, 'speed': speed})

        # 帮助/关于弹窗
        if popup_mode:
            popup_close_rect, _ = draw_help_about_overlay(font, mouse_pos, popup_mode)
        else:
            popup_close_rect = None

        # 星球科普信息面板
        if selected_planet and not popup_mode:
            info_close_rect, info_panel_rect = draw_planet_info_overlay(
                font, mouse_pos, selected_planet, planet_screen_positions)
        else:
            info_close_rect = None
            info_panel_rect = None

        pygame.display.flip()
        clock.tick(60)

        if not paused:
            t += 0.05

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    import os
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    main()
