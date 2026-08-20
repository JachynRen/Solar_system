"""
太阳系 3D 模拟程序
使用 Pygame + OpenGL 展示太阳系八大行星的运动轨迹
使用 pygame-menu 提供原生风格的菜单 UI

操作方式：
- 触控板单指拖动 / 鼠标左键拖动：旋转视角
- 触控板双指捏合 / 鼠标滚轮 / 上下方向键：缩放
- I/J/K/L 键：相机前后左右移动（基于当前朝向）
- U/O 键：相机上/下移动
- 空格键：暂停/继续
- +/- 键：调整速度
- A/D 键：水平旋转
- W/S 键：垂直旋转
- R 键：重置视角
- M 键：打开菜单
- ESC：退出
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import sys
import pygame_menu

# 作者信息
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


def create_help_menu(menu_theme, width, height):
    """创建帮助菜单"""
    help_text = (
        "=== 操作说明 ===\n\n"
        "鼠标 / 触控板：\n"
        "  左键拖动 / 单指拖动 - 旋转视角\n"
        "  滚轮 / 双指捏合     - 缩放\n\n"
        "键盘：\n"
        "  W/S        - 俯仰旋转（上/下看）\n"
        "  A/D        - 水平旋转（左/右转）\n"
        "  I/J/K/L    - 相机前后左右移动\n"
        "  U/O        - 相机上/下移动\n"
        "  ↑/↓        - 缩放\n"
        "  +/-        - 调整模拟速度\n"
        "  空格       - 暂停/继续\n"
        "  R          - 重置视角\n"
        "  F          - 快速视角切换\n"
        "  M          - 打开菜单\n"
        "  ESC        - 退出\n"
    )

    menu = pygame_menu.Menu('操作说明', width, height, theme=menu_theme)
    menu.add.label(help_text, max_char=60, font_size=16, align=pygame_menu.locals.ALIGN_LEFT)
    menu.add.button('关闭', pygame_menu.events.BACK)
    return menu


def create_about_menu(menu_theme, width, height):
    """创建关于菜单"""
    menu = pygame_menu.Menu('关于', width, height, theme=menu_theme)
    menu.add.label(f'太阳系 3D 模拟程序', font_size=20)
    menu.add.label('')
    menu.add.label(f'作者: {AUTHOR_NAME}', font_size=16)
    menu.add.label(f'邮箱: {AUTHOR_EMAIL}', font_size=14)
    menu.add.label(f'GitHub:', font_size=14)
    menu.add.label(GITHUB_URL, font_size=12, font_color=(100, 180, 255))
    menu.add.label('')
    menu.add.button('关闭', pygame_menu.events.BACK)
    return menu


def create_main_menu(menu_theme, width, height, help_menu, about_menu, game_state):
    """创建主菜单"""
    menu = pygame_menu.Menu('菜单', width, height, theme=menu_theme)
    menu.add.button('操作说明', help_menu)
    menu.add.button('关于', about_menu)

    # 暂停/继续按钮
    def toggle_pause():
        game_state['paused'] = not game_state['paused']

    def update_pause_label():
        return '继续' if game_state['paused'] else '暂停'

    menu.add.selector('速度:', [(f'{s:.1f}x', s) for s in [0.5, 1.0, 2.0, 3.0, 5.0, 10.0]],
                      onchange=lambda _, val: game_state.__setitem__('speed', val))
    menu.add.button(update_pause_label, toggle_pause)
    menu.add.button('返回模拟', pygame_menu.events.BACK)
    return menu


def main():
    pygame.init()

    width, height = 1200, 800
    screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | RESIZABLE)
    pygame.display.set_caption('太阳系 3D 模拟')

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

    # 相机参数
    cam_rot_x = -25
    cam_rot_y = 0
    cam_distance = 90
    cam_x = 0.0
    cam_y = 0.0
    cam_z = 0.0

    clock = pygame.time.Clock()
    running = True
    speed = 1.0
    t = 0
    paused = False

    # 拖动状态
    dragging = False
    last_pos = (0, 0)

    # 惯性滑动参数
    velocity_x = 0.0
    velocity_y = 0.0
    damping = 0.92

    # 游戏状态（供菜单引用）
    game_state = {'paused': False, 'speed': 1.0}

    # pygame-menu 主题
    theme = pygame_menu.themes.THEME_BLUE.copy()
    theme.title_background_color = (30, 30, 50)
    theme.widget_alignment = pygame_menu.locals.ALIGN_CENTER

    # 创建菜单
    help_menu = create_help_menu(theme, 500, 600)
    about_menu = create_about_menu(theme, 450, 400)
    main_menu = create_main_menu(theme, 400, 500, help_menu, about_menu, game_state)

    # 菜单按钮栏位置
    menu_btn_rect = pygame.Rect(10, 10, 60, 30)

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                running = False

            elif main_menu.is_enabled():
                # 菜单打开时处理菜单事件
                if main_menu.update(events):
                    pass
                # 同步游戏状态
                paused = game_state['paused']
                speed = game_state['speed']

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_SPACE:
                    paused = not paused
                    game_state['paused'] = paused
                elif event.key == K_PLUS or event.key == K_EQUALS:
                    speed = min(10.0, speed + 0.5)
                    game_state['speed'] = speed
                elif event.key == K_MINUS or event.key == K_UNDERSCORE:
                    speed = max(0.1, speed - 0.5)
                    game_state['speed'] = speed
                elif event.key == K_r:
                    cam_rot_x = -25
                    cam_rot_y = 0
                    cam_distance = 90
                    cam_x = 0.0
                    cam_y = 0.0
                    cam_z = 0.0
                elif event.key == K_f:
                    cam_rot_x = -45
                    cam_rot_y = cam_rot_y + 45
                    cam_distance = 70
                elif event.key == K_m:
                    main_menu.enable()

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    # 检查菜单按钮点击
                    if menu_btn_rect.collidepoint(event.pos):
                        main_menu.enable()
                    else:
                        dragging = True
                        last_pos = event.pos
                        velocity_x = 0.0
                        velocity_y = 0.0
                elif event.button == 4:
                    cam_distance = max(30, cam_distance - 3)
                elif event.button == 5:
                    cam_distance = min(200, cam_distance + 3)

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False

            elif event.type == MOUSEMOTION:
                if dragging:
                    dx = event.pos[0] - last_pos[0]
                    dy = event.pos[1] - last_pos[1]
                    velocity_x = dx * 0.4
                    velocity_y = -dy * 0.4
                    cam_rot_y += velocity_x
                    cam_rot_x += velocity_y
                    cam_rot_x = max(-89, min(89, cam_rot_x))
                    last_pos = event.pos

        # 如果菜单打开，只绘制菜单
        if main_menu.is_enabled() or help_menu.is_enabled() or about_menu.is_enabled():
            # 先渲染 3D 场景作为背景
            glClearColor(0.02, 0.02, 0.05, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glLoadIdentity()
            glTranslatef(-cam_x, -cam_y, -cam_z)
            glTranslatef(0, 0, cam_distance)
            glRotatef(cam_rot_x, 1, 0, 0)
            glRotatef(cam_rot_y, 0, 1, 0)

            glPushMatrix()
            glRotatef(-cam_rot_y, 0, 1, 0)
            glRotatef(-cam_rot_x, 1, 0, 0)
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

            # 绘制菜单覆盖层
            if main_menu.is_enabled():
                main_menu.draw(screen)
            elif help_menu.is_enabled():
                help_menu.draw(screen)
            elif about_menu.is_enabled():
                about_menu.draw(screen)

            pygame.display.flip()
            clock.tick(60)
            continue

        # 惯性滑动
        if not dragging:
            if abs(velocity_x) > 0.01 or abs(velocity_y) > 0.01:
                cam_rot_y += velocity_x
                cam_rot_x += velocity_y
                cam_rot_x = max(-89, min(89, cam_rot_x))
                velocity_x *= damping
                velocity_y *= damping

        # 键盘控制
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            cam_distance = max(30, cam_distance - 1)
        if keys[K_DOWN]:
            cam_distance = min(200, cam_distance + 1)
        if keys[K_a]:
            cam_rot_y -= 1.5
        if keys[K_d]:
            cam_rot_y += 1.5
        if keys[K_w]:
            cam_rot_x += 1.5
            cam_rot_x = max(-89, min(89, cam_rot_x))
        if keys[K_s]:
            cam_rot_x -= 1.5
            cam_rot_x = max(-89, min(89, cam_rot_x))

        # 相机位置移动
        move_speed = 1.0
        rot_rad_x = math.radians(cam_rot_x)
        rot_rad_y = math.radians(cam_rot_y)
        if keys[K_i]:
            cam_x += math.sin(rot_rad_y) * math.cos(rot_rad_x) * move_speed
            cam_y -= math.sin(rot_rad_x) * move_speed
            cam_z += math.cos(rot_rad_y) * math.cos(rot_rad_x) * move_speed
        if keys[K_k]:
            cam_x -= math.sin(rot_rad_y) * math.cos(rot_rad_x) * move_speed
            cam_y += math.sin(rot_rad_x) * move_speed
            cam_z -= math.cos(rot_rad_y) * math.cos(rot_rad_x) * move_speed
        if keys[K_j]:
            cam_x += math.cos(rot_rad_y) * move_speed
            cam_z -= math.sin(rot_rad_y) * move_speed
        if keys[K_l]:
            cam_x -= math.cos(rot_rad_y) * move_speed
            cam_z += math.sin(rot_rad_y) * move_speed
        if keys[K_u]:
            cam_y += move_speed
        if keys[K_o]:
            cam_y -= move_speed

        glClearColor(0.02, 0.02, 0.05, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        glTranslatef(-cam_x, -cam_y, -cam_z)
        glTranslatef(0, 0, cam_distance)
        glRotatef(cam_rot_x, 1, 0, 0)
        glRotatef(cam_rot_y, 0, 1, 0)

        glPushMatrix()
        glRotatef(-cam_rot_y, 0, 1, 0)
        glRotatef(-cam_rot_x, 1, 0, 0)
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

        # 绘制顶部菜单按钮
        status = "暂停" if paused else "运行中"
        pygame.display.set_caption(
            f'太阳系 3D 模拟 - {status} | 速度: {speed:.1f}x | '
            f'拖动旋转 | 滚轮缩放 | A/D旋转 | W/S俯仰 | I/J/K/L移动 | U/O升降 | R重置 | M菜单 | 空格暂停 | ESC退出'
        )

        # 菜单按钮
        btn_surf = pygame.Surface((menu_btn_rect.w, menu_btn_rect.h))
        btn_surf.fill((40, 40, 80))
        pygame.draw.rect(btn_surf, (100, 150, 200), btn_surf.get_rect(), 2)
        font = pygame.font.SysFont("arial", 16)
        text_surf = font.render("☰ 菜单", True, (220, 220, 220))
        text_rect = text_surf.get_rect(center=menu_btn_rect.center)
        screen.blit(btn_surf, menu_btn_rect.topleft)
        screen.blit(text_surf, text_rect)

        pygame.display.flip()
        clock.tick(60)

        if not paused:
            t += 0.05

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
