#!/bin/bash
# 打包太阳系模拟器为 macOS 应用程序
set -e

cd "$(dirname "$0")"

echo "=== 安装依赖 ==="
.venv/bin/pip install -q pyinstaller 2>/dev/null

echo "=== 开始打包 ==="
.venv/bin/pyinstaller \
  --name "太阳系模拟器" \
  --onedir \
  --windowed \
  solar_system.py

echo ""
echo "=== 打包完成 ==="
echo "应用程序: dist/太阳系模拟器.app"
echo "大小: $(du -sh dist/太阳系模拟器.app | cut -f1)"
echo ""
echo "你可以将 太阳系模拟器.app 拖入 /Applications 文件夹运行"
