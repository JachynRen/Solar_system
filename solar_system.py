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
AUTHOR_EMAIL = "jachynren@example.com"
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
]

ABOUT_LINES = [
    f"太阳系 3D 模拟 v{VERSION}",
    "",
    f"作者: {AUTHOR_NAME}",
    f"邮箱: {AUTHOR_EMAIL}",
    f"GitHub: {GITHUB_URL}",
]

FONT_SIZE = 16
LINE_H = 24
MENU_PAD = 15

# 顶部菜单栏
MENUBAR_H = 26
MENUBAR_BG = (50, 50, 70)
MENUBAR_TEXT = (220, 220, 230)
MENUBAR_HOVER = (80, 80, 130)

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
MENU_BG = (25, 25, 45)
MENU_BORDER = (80, 120, 180)
MENU_TEXT = (220, 220, 230)
MENU_TITLE = (255, 200, 80)
BTN_BG = (40, 40, 80)
BTN_BORDER = (100, 150, 200)
BTN_TEXT = (220, 220, 220)
BTN_HOVER = (60, 60, 120)


def _draw_filled_rect(surf, rect, color):
    pygame.draw.rect(surf, color, rect)


def _draw_rect_border(surf, rect, color, width=2):
    pygame.draw.rect(surf, color, rect, width)


def _render_text(font, text, color):
    return font.render(text, True, color)


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
    # 将 pygame surface 转为像素数据
    data = pygame.image.tostring(txt_surf, 'RGBA', True)
    glEnable(GL_TEXTURE_2D)
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tw, th, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

    glColor4f(1, 1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x, y)
    glTexCoord2f(1, 0); glVertex2f(x + tw, y)
    glTexCoord2f(1, 1); glVertex2f(x + tw, y + th)
    glTexCoord2f(0, 1); glVertex2f(x, y + th)
    glEnd()

    glDeleteTextures([tex])
    glDisable(GL_TEXTURE_2D)


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

    for name, orbit_radius, radius, period, color, angle in PLANETS_DATA:
        draw_orbit(orbit_radius)
        angular_velocity = 2 * math.pi / period
        current_angle = angle + angular_velocity * t * speed
        px = orbit_radius * math.cos(current_angle)
        pz = orbit_radius * math.sin(current_angle)

        glPushMatrix()
        glTranslatef(px, 0, pz)
        if name == "土星":
            glPushMatrix()
            glRotatef(25, 1, 0, 0)
            draw_saturn_ring(radius * 1.4, radius * 2.3)
            glPopMatrix()
        draw_sphere(radius, color)
        glPopMatrix()


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
    mouse_pos = (0, 0)
    font = pygame.font.SysFont("arial", FONT_SIZE)

    # 存储每帧的菜单 rect（用于事件检测）
    menu_rects = {}
    popup_close_rect = None

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
                if event.button == 1:
                    mx, my = event.pos
                    handled = False

                    # 1) 关闭弹窗按钮
                    if popup_mode and popup_close_rect:
                        if popup_close_rect.collidepoint(mx, my):
                            popup_mode = None
                            handled = True

                    if not handled:
                        # 2) 菜单栏点击
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

                        # 3) 点击空白关闭菜单
                        if not handled:
                            menu_state["open_menu"] = None
                            dragging = True

                    last_pos = event.pos
                    velocity['x'] = velocity['y'] = 0.0
                elif event.button == 4:
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
        draw_scene(cam, speed, t, paused)

        # ---- 2D overlay ----
        # 顶部菜单栏 + 下拉菜单（保存 rect 供下一帧事件检测用）
        menu_rects = draw_menubar_overlay(font, mouse_pos, menu_state,
                                          {'paused': paused, 'speed': speed})

        # 帮助/关于弹窗
        if popup_mode:
            popup_close_rect, _ = draw_help_about_overlay(font, mouse_pos, popup_mode)
        else:
            popup_close_rect = None

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
