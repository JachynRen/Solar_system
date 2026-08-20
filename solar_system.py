"""
太阳系 3D 模拟程序
使用 PyQt5 + OpenGL 展示太阳系八大行星的运动轨迹

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
- ESC：退出
"""

import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QOpenGLWidget, QMenuBar,
    QMenu, QAction, QMessageBox, QStatusBar, QLabel
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMouseEvent, QKeyEvent
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective

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


class SolarSystemGLWidget(QOpenGLWidget):
    """OpenGL 渲染窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent

        # 相机参数
        self.cam_rot_x = -25
        self.cam_rot_y = 0
        self.cam_distance = 90
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.cam_z = 0.0

        # 模拟状态
        self.speed = 1.0
        self.t = 0
        self.paused = False

        # 鼠标拖动状态
        self.dragging = False
        self.last_pos = (0, 0)

        # 惯性滑动参数
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.damping = 0.92

        # 按键状态
        self.keys_pressed = set()

        # 定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(16)  # ~60 FPS

    def initializeGL(self):
        """初始化 OpenGL"""
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

        glClearColor(0.02, 0.02, 0.05, 1.0)

    def resizeGL(self, width, height):
        """窗口大小变化时调用"""
        if height == 0:
            height = 1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, width / height, 0.1, 500.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """渲染场景"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        glTranslatef(-self.cam_x, -self.cam_y, -self.cam_z)
        glTranslatef(0, 0, self.cam_distance)
        glRotatef(self.cam_rot_x, 1, 0, 0)
        glRotatef(self.cam_rot_y, 0, 1, 0)

        glPushMatrix()
        glRotatef(-self.cam_rot_y, 0, 1, 0)
        glRotatef(-self.cam_rot_x, 1, 0, 0)
        draw_stars()
        glPopMatrix()

        draw_sun()

        for name, orbit_radius, radius, period, color, angle in PLANETS_DATA:
            draw_orbit(orbit_radius)

            angular_velocity = 2 * math.pi / period
            current_angle = angle + angular_velocity * self.t * self.speed

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

    def update_scene(self):
        """更新模拟状态"""
        # 处理持续按下的按键
        self.process_keys()

        # 惯性滑动
        if not self.dragging:
            if abs(self.velocity_x) > 0.01 or abs(self.velocity_y) > 0.01:
                self.cam_rot_y += self.velocity_x
                self.cam_rot_x += self.velocity_y
                self.cam_rot_x = max(-89, min(89, self.cam_rot_x))
                self.velocity_x *= self.damping
                self.velocity_y *= self.damping

        # 更新状态栏
        if self.parent_window:
            self.parent_window.update_status_bar()

        if not self.paused:
            self.t += 0.05

        self.update()

    def process_keys(self):
        """处理持续按下的按键"""
        move_speed = 1.0
        rot_rad_x = math.radians(self.cam_rot_x)
        rot_rad_y = math.radians(self.cam_rot_y)

        if Qt.Key_Up in self.keys_pressed:
            self.cam_distance = max(30, self.cam_distance - 1)
        if Qt.Key_Down in self.keys_pressed:
            self.cam_distance = min(200, self.cam_distance + 1)
        if Qt.Key_A in self.keys_pressed:
            self.cam_rot_y -= 1.5
        if Qt.Key_D in self.keys_pressed:
            self.cam_rot_y += 1.5
        if Qt.Key_W in self.keys_pressed:
            self.cam_rot_x += 1.5
            self.cam_rot_x = max(-89, min(89, self.cam_rot_x))
        if Qt.Key_S in self.keys_pressed:
            self.cam_rot_x -= 1.5
            self.cam_rot_x = max(-89, min(89, self.cam_rot_x))

        # 相机位置移动（基于当前朝向）
        if Qt.Key_I in self.keys_pressed:  # 前进
            self.cam_x += math.sin(rot_rad_y) * math.cos(rot_rad_x) * move_speed
            self.cam_y -= math.sin(rot_rad_x) * move_speed
            self.cam_z += math.cos(rot_rad_y) * math.cos(rot_rad_x) * move_speed
        if Qt.Key_K in self.keys_pressed:  # 后退
            self.cam_x -= math.sin(rot_rad_y) * math.cos(rot_rad_x) * move_speed
            self.cam_y += math.sin(rot_rad_x) * move_speed
            self.cam_z -= math.cos(rot_rad_y) * math.cos(rot_rad_x) * move_speed
        if Qt.Key_J in self.keys_pressed:  # 左移
            self.cam_x += math.cos(rot_rad_y) * move_speed
            self.cam_z -= math.sin(rot_rad_y) * move_speed
        if Qt.Key_L in self.keys_pressed:  # 右移
            self.cam_x -= math.cos(rot_rad_y) * move_speed
            self.cam_z += math.sin(rot_rad_y) * move_speed
        if Qt.Key_U in self.keys_pressed:  # 上移
            self.cam_y += move_speed
        if Qt.Key_O in self.keys_pressed:  # 下移
            self.cam_y -= move_speed

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_pos = (event.x(), event.y())
            self.velocity_x = 0.0
            self.velocity_y = 0.0
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.dragging:
            dx = event.x() - self.last_pos[0]
            dy = event.y() - self.last_pos[1]
            self.velocity_x = dx * 0.4
            self.velocity_y = -dy * 0.4
            self.cam_rot_y += self.velocity_x
            self.cam_rot_x += self.velocity_y
            self.cam_rot_x = max(-89, min(89, self.cam_rot_x))
            self.last_pos = (event.x(), event.y())
        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        """鼠标滚轮事件"""
        delta = event.angleDelta().y()
        if delta > 0:
            self.cam_distance = max(30, self.cam_distance - 3)
        else:
            self.cam_distance = min(200, self.cam_distance + 3)
        super().wheelEvent(event)

    def keyPressEvent(self, event):
        """键盘按下事件"""
        key = event.key()
        self.keys_pressed.add(key)

        if key == Qt.Key_Escape:
            self.parent_window.close()
        elif key == Qt.Key_Space:
            self.paused = not self.paused
        elif key == Qt.Key_Equal or key == Qt.Key_Plus:
            self.speed = min(10.0, self.speed + 0.5)
        elif key == Qt.Key_Minus or key == Qt.Key_Underscore:
            self.speed = max(0.1, self.speed - 0.5)
        elif key == Qt.Key_R:
            self.reset_camera()
        elif key == Qt.Key_F:
            self.cam_rot_x = -45
            self.cam_rot_y = self.cam_rot_y + 45
            self.cam_distance = 70
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """键盘释放事件"""
        self.keys_pressed.discard(event.key())
        super().keyReleaseEvent(event)

    def reset_camera(self):
        """重置相机位置"""
        self.cam_rot_x = -25
        self.cam_rot_y = 0
        self.cam_distance = 90
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.cam_z = 0.0


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle('太阳系 3D 模拟')
        self.resize(1200, 800)

        # 创建 OpenGL 窗口
        self.gl_widget = SolarSystemGLWidget(self)
        self.setCentralWidget(self.gl_widget)

        # 创建菜单栏
        self.create_menu()

        # 创建状态栏
        self.create_status_bar()

    def create_menu(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 帮助菜单
        help_menu = menubar.addMenu('帮助')

        help_action = QAction('操作说明', self)
        help_action.setShortcut('H')
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        # 关于菜单
        about_menu = menubar.addMenu('关于')

        about_action = QAction('关于程序', self)
        about_action.triggered.connect(self.show_about)
        about_menu.addAction(about_action)

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = self.statusBar()
        self.status_label = QLabel()
        self.status_bar.addWidget(self.status_label)
        self.update_status_bar()

    def update_status_bar(self):
        """更新状态栏"""
        status = "暂停" if self.gl_widget.paused else "运行中"
        self.status_label.setText(
            f'{status} | 速度: {self.gl_widget.speed:.1f}x | '
            f'拖动旋转 | 滚轮缩放 | A/D旋转 | W/S俯仰 | I/J/K/L移动 | U/O升降 | R重置 | 空格暂停 | ESC退出'
        )

    def show_help(self):
        """显示帮助对话框"""
        help_text = """
<h3>操作说明</h3>
<table>
<tr><td><b>鼠标左键拖动</b></td><td>旋转视角</td></tr>
<tr><td><b>鼠标滚轮</b></td><td>缩放</td></tr>
<tr><td><b>W/S</b></td><td>俯仰旋转（上/下看）</td></tr>
<tr><td><b>A/D</b></td><td>水平旋转（左/右转）</td></tr>
<tr><td><b>I/J/K/L</b></td><td>相机前后左右移动</td></tr>
<tr><td><b>U/O</b></td><td>相机上/下移动</td></tr>
<tr><td><b>↑/↓</b></td><td>缩放</td></tr>
<tr><td><b>+/-</b></td><td>调整模拟速度</td></tr>
<tr><td><b>空格</b></td><td>暂停/继续</td></tr>
<tr><td><b>R</b></td><td>重置视角</td></tr>
<tr><td><b>F</b></td><td>快速视角切换</td></tr>
<tr><td><b>ESC</b></td><td>退出</td></tr>
</table>
        """
        QMessageBox.information(self, '操作说明', help_text)

    def show_about(self):
        """显示关于对话框"""
        about_text = f"""
<h3>太阳系 3D 模拟程序</h3>
<p><b>作者:</b> {AUTHOR_NAME}</p>
<p><b>邮箱:</b> {AUTHOR_EMAIL}</p>
<p><b>GitHub:</b> <a href="{GITHUB_URL}">{GITHUB_URL}</a></p>
        """
        QMessageBox.about(self, '关于', about_text)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
