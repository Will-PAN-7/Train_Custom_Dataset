#!/bin/bash

echo "数据集标注工具 - 同济子豪兄"
echo "================================"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.7+"
    exit 1
fi

# 检查pip是否安装
if ! command -v pip3 &> /dev/null; then
    echo "错误: 未找到pip3，请先安装pip"
    exit 1
fi

echo "正在检查依赖..."

# 安装依赖
pip3 install -r requirements.txt

echo "依赖安装完成！"
echo "启动标注工具..."

# 启动应用
python3 annotation_tool.py