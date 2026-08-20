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


def draw_menu_overlay(surf, font, menu_open, mouse_pos, game_state):
    """绘制菜单覆盖层（pygame 2D 渲染，在 flip 之前）"""
    width, height = surf.get_size()

    # ---- 菜单按钮 ----
    btn_w, btn_h = 80, 32
    btn_rect = pygame.Rect(12, 10, btn_w, btn_h)
    hovered = btn_rect.collidepoint(mouse_pos)
    _draw_filled_rect(surf, btn_rect, BTN_HOVER if hovered else BTN_BG)
    _draw_rect_border(surf, btn_rect, BTN_BORDER)
    txt = _render_text(font, "☰ 菜单", BTN_TEXT)
    surf.blit(txt, txt.get_rect(center=btn_rect.center))

    # ---- 弹窗 ----
    if menu_open:
        # 计算弹窗尺寸
        lines = HELP_LINES + ["", "---"] + ABOUT_LINES
        max_char_w = max(font.size(line)[0] for line in lines)
        panel_w = max_char_w + MENU_PAD * 2
        panel_h = len(lines) * LINE_H + MENU_PAD * 2 + 40  # 额外给关闭按钮留空间
        panel_x = (width - panel_w) // 2
        panel_y = (height - panel_h) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        # 半透明背景遮罩
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surf.blit(overlay, (0, 0))

        # 面板背景
        _draw_filled_rect(surf, panel_rect, MENU_BG)
        _draw_rect_border(surf, panel_rect, MENU_BORDER)

        # 标题
        title = _render_text(font, f"菜单 v{VERSION}", MENU_TITLE)
        surf.blit(title, (panel_x + MENU_PAD, panel_y + MENU_PAD))

        # 内容行
        y = panel_y + MENU_PAD + LINE_H + 5
        for line in lines:
            if line.startswith("===") or line.startswith("太阳系"):
                c = MENU_TITLE
            elif line.startswith("---"):
                c = (100, 100, 130)
            elif line.startswith("作者") or line.startswith("邮箱") or line.startswith("GitHub"):
                c = (150, 180, 220)
            else:
                c = MENU_TEXT
            txt_surf = _render_text(font, line, c)
            surf.blit(txt_surf, (panel_x + MENU_PAD, y))
            y += LINE_H

        # 关闭按钮
        close_w, close_h = 80, 28
        close_rect = pygame.Rect(panel_x + (panel_w - close_w) // 2,
                                 panel_y + panel_h - close_h - 12,
                                 close_w, close_h)
        close_hovered = close_rect.collidepoint(mouse_pos)
        _draw_filled_rect(surf, close_rect, BTN_HOVER if close_hovered else BTN_BG)
        _draw_rect_border(surf, close_rect, BTN_BORDER)
        close_txt = _render_text(font, "关闭", BTN_TEXT)
        surf.blit(close_txt, close_txt.get_rect(center=close_rect.center))

        return btn_rect, close_rect, panel_rect

    return btn_rect, None, None


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

    menu_open = False
    mouse_pos = (0, 0)
    font = pygame.font.SysFont("arial", FONT_SIZE)

    while running:
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
                    menu_open = not menu_open

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    if menu_open:
                        btn_rect, close_rect, panel_rect = draw_menu_overlay(
                            screen, font, menu_open, mouse_pos, None)
                        if close_rect and close_rect.collidepoint(mx, my):
                            menu_open = False
                            continue
                        # 点击面板外关闭
                        if panel_rect and not panel_rect.collidepoint(mx, my):
                            menu_open = False
                            continue
                    else:
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
                if dragging and not menu_open:
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

        # ---- 2D overlay（菜单）----
        # 先绘制 OpenGL 到屏幕，然后用 pygame blit 覆盖
        # 注意：OpenGL 和 pygame 渲染在同一个 surface 上
        glFinish()

        # 菜单覆盖
        btn_rect, close_rect, panel_rect = draw_menu_overlay(
            screen, font, menu_open, mouse_pos, {'paused': paused, 'speed': speed})

        # 状态栏文字（底部）
        status = "暂停" if paused else "运行中"
        status_txt = font.render(
            f'{status} | 速度: {speed:.1f}x | M-菜单 | 空格-暂停 | ESC-退出',
            True, (180, 180, 200))
        sw, sh = screen.get_size()
        screen.blit(status_txt, (sw - status_txt.get_width() - 15, sh - 30))

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
