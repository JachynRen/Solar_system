# 太阳系 3D 模拟器 v1.0.0

> 使用 Python + Pygame + OpenGL 实现的太阳系八大行星运动 3D 可视化程序

<p align="center">
  <b>作者</b>: JachynRen &nbsp;|&nbsp;
  <b>邮箱</b>: jachynren@example.com &nbsp;|&nbsp;
  <b>GitHub</b>: <a href="https://github.com/JachynRen/Solar_system">Solar_system</a>
</p>

---

## ✨ 功能特性

- 🌞 **太阳**：位于中心，带多层光晕发光效果和点光源照明
- 🪐 **八大行星**：水星、金星、地球、火星、木星、土星、天王星、海王星
- ⭕ **轨道线**：每个行星的轨道路径可视化
- 💫 **土星环**：土星特有的倾斜光环效果
- 🌌 **星空背景**：500 颗随机生成的星星
- 🎥 **自由相机**：支持旋转、缩放、前后左右移动、上下升降
- 📋 **菜单栏**：顶部原生风格菜单，支持文件、视图、模拟、帮助操作

---

## 📸 截图

![截图](screenshots/solar_system.png)

---

## 🖥️ 运行方式

### 方式一：从源码运行

```bash
# 1. 克隆仓库
git clone https://github.com/JachynRen/Solar_system.git
cd Solar_system

# 2. 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行
python solar_system.py
```

### 方式二：直接运行打包应用（macOS）

```bash
# 下载 Release 中的 太阳系模拟器.app，双击即可运行
```

---

## 🎮 操作方式

### 鼠标 / 触控板

| 操作 | 功能 |
|------|------|
| 左键拖动 / 单指拖动 | 旋转视角 |
| 滚轮 / 双指捏合 | 缩放 |

### 键盘

| 按键 | 功能 |
|------|------|
| W / S | 俯仰旋转（上/下看） |
| A / D | 水平旋转（左/右转） |
| I / J / K / L | 相机前后左右移动 |
| U / O | 相机上/下移动 |
| ↑ / ↓ | 缩放 |
| + / - | 调整模拟速度 |
| 空格 | 暂停/继续 |
| R | 重置视角 |
| F | 快速视角切换 |
| M | 打开帮助说明 |
| ESC | 退出 |

### 顶部菜单栏

| 菜单 | 功能项 |
|------|--------|
| **文件** | 重置视角、退出 |
| **视图** | 默认视角、俯视、侧视 |
| **模拟** | 暂停/继续、加速、减速 |
| **帮助** | 操作说明、关于 |

---

## 📦 打包

### macOS 打包为 .app 应用

```bash
# 一键打包
./build.sh

# 或手动执行
.venv/bin/pip install pyinstaller
.venv/bin/pyinstaller --name "太阳系模拟器" --onedir --windowed solar_system.py
```

打包产物位于 `dist/太阳系模拟器.app`，可直接复制到 `/Applications` 运行。

### 其他平台

```bash
# Windows
pyinstaller --name "太阳系模拟器" --onedir --windowed solar_system.py

# Linux
pyinstaller --name "solar_system" --onedir --windowed solar_system.py
```

---

## 🪐 行星数据

程序中的行星参数基于真实天文数据（轨道半径和大小经过非线性缩放以适应可视化效果）：

| 行星 | 公转周期（天） | 轨道半径 | 相对大小 | 颜色 |
|------|---------------|---------|---------|------|
| 水星 | 88 | 8 | 0.35 | 灰色 |
| 金星 | 225 | 11 | 0.55 | 橙黄色 |
| 地球 | 365 | 15 | 0.55 | 蓝色 |
| 火星 | 687 | 20 | 0.4 | 红色 |
| 木星 | 4,333 | 30 | 1.8 | 棕黄色 |
| 土星 | 10,759 | 42 | 1.5 | 金黄色（带光环） |
| 天王星 | 30,687 | 55 | 0.9 | 青蓝色 |
| 海王星 | 60,190 | 68 | 0.85 | 深蓝色 |

---

## 🔧 技术栈

| 组件 | 用途 |
|------|------|
| **Pygame** | 窗口管理、事件处理、帧率控制 |
| **PyOpenGL** | OpenGL 3D 渲染 API |
| **OpenGL 固定管线** | 光照、材质、深度测试、混合模式 |
| **PyInstaller** | 打包为独立应用程序 |

### 渲染特性

- 太阳：多层半透明光晕 + 中心点光源（`GL_LIGHT0`）
- 行星：使用 `GL_QUAD_STRIP` 手动绘制的球体，带环境光和漫反射材质
- 轨道：`GL_LINE_LOOP` 绘制的圆环
- 土星环：倾斜 25° 的双半径圆环
- 星空：500 个随机分布的 `GL_POINTS`
- 菜单：OpenGL 正交投影 + 文字纹理 overlay

---

## 📁 项目结构

```
Solar_system/
├── solar_system.py      # 主程序
├── requirements.txt     # Python 依赖
├── build.sh             # macOS 一键打包脚本
├── .gitignore           # Git 忽略规则
└── README.md            # 项目说明文档
```

---

## ❓ 常见问题

### 窗口打开但显示黑屏

确保你的系统支持 OpenGL 图形加速。

```bash
# macOS 检查 OpenGL 版本
system_profiler SPDisplaysDataType | grep OpenGL
```

### 运行卡顿

程序默认运行在 60 FPS，如果卡顿可以尝试：
1. 缩小窗口
2. 减少球体绘制的 `slices/stacks` 数量

---

## 🚀 扩展方向

- [ ] 添加行星名称标签（OpenGL 文字渲染）
- [ ] 添加小行星带
- [ ] 添加行星卫星（如月球）
- [ ] 实时显示行星信息面板
- [ ] 支持保存/加载模拟状态
- [ ] 更真实的椭圆轨道（开普勒方程）

---

## 📄 许可证

MIT License
