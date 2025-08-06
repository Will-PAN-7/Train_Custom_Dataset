#!/bin/bash

# 数据集标注工具启动脚本

echo "🏷️  数据集标注工具启动脚本"
echo "================================"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查pip是否安装
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip 未安装，请先安装pip"
    exit 1
fi

# 创建虚拟环境（可选）
if [ "$1" = "--venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
fi

# 安装依赖
echo "📦 安装Python依赖包..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败，请检查网络连接和Python环境"
    exit 1
fi

# 创建必要的目录
mkdir -p uploads annotations

echo "✅ 环境准备完成"
echo ""
echo "🚀 启动服务器..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
echo ""

# 启动Flask应用
python3 app.py