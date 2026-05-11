#!/bin/bash
# 耄耋Official - 一键启动脚本

echo "🐱 耄耋Official 全自动运营Bot"
echo "================================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装"
    exit 1
fi

# 检查Playwright
if ! python3 -c "import playwright" 2>/dev/null; then
    echo "📦 安装依赖..."
    pip3 install -r requirements.txt --break-system-packages
    echo "📦 安装浏览器..."
    python3 -m playwright install chromium
fi

# 创建图片目录
mkdir -p images/maodie

if [ ! "$(ls -A images/maodie 2>/dev/null)" ]; then
    echo "⚠️  images/maodie/ 文件夹为空"
    echo "   请把圆头耄耋表情包图片放进去"
    echo "   支持格式: jpg, png, gif, webp"
fi

# 启动
echo ""
echo "🚀 启动Bot..."
python3 maodie_bot.py "$@"
