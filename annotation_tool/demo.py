#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据集标注工具 API 使用演示

这个脚本展示了如何通过API接口与标注工具进行交互
"""

import requests
import json
import os
from pathlib import Path

# 配置
BASE_URL = "http://localhost:5000"
DEMO_IMAGE_PATH = "demo_images"  # 演示图片文件夹

def create_demo_images():
    """创建演示图片文件夹和说明"""
    os.makedirs(DEMO_IMAGE_PATH, exist_ok=True)
    
    readme_content = """# 演示图片文件夹

请将一些测试图片放入此文件夹中，支持的格式包括：
- JPG/JPEG
- PNG
- GIF
- BMP

演示脚本会自动上传这些图片并进行标注演示。
"""
    
    with open(os.path.join(DEMO_IMAGE_PATH, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"📁 已创建演示图片文件夹: {DEMO_IMAGE_PATH}")
    print("请将测试图片放入该文件夹中")

def upload_image(image_path):
    """上传图片"""
    print(f"📤 上传图片: {image_path}")
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✅ 上传成功: {data['image_data']['id']}")
            return data['image_data']
        else:
            print(f"❌ 上传失败: {data.get('error', '未知错误')}")
    else:
        print(f"❌ 上传失败: HTTP {response.status_code}")
    
    return None

def get_image_list():
    """获取图片列表"""
    print("📋 获取图片列表...")
    
    response = requests.get(f"{BASE_URL}/api/images")
    if response.status_code == 200:
        data = response.json()
        images = data.get('images', [])
        print(f"📊 共有 {len(images)} 张图片")
        for img in images:
            print(f"  - {img['filename']} ({img['image_info']['width']}×{img['image_info']['height']})")
        return images
    else:
        print(f"❌ 获取失败: HTTP {response.status_code}")
        return []

def add_classification_annotation(image_id, label):
    """添加分类标注"""
    print(f"🏷️ 为图片 {image_id} 添加分类标注: {label}")
    
    annotation_data = {
        "annotations": [
            {
                "id": "demo_classification",
                "type": "classification",
                "label": label,
                "timestamp": "2024-01-01T12:00:00Z"
            }
        ],
        "image_info": {
            "width": 800,
            "height": 600
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/annotations/{image_id}",
        json=annotation_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✅ 分类标注添加成功")
        else:
            print(f"❌ 标注失败: {data.get('error', '未知错误')}")
    else:
        print(f"❌ 标注失败: HTTP {response.status_code}")

def add_detection_annotation(image_id, label, bbox):
    """添加检测标注"""
    print(f"🎯 为图片 {image_id} 添加检测标注: {label}")
    
    annotation_data = {
        "annotations": [
            {
                "id": "demo_detection",
                "type": "detection",
                "label": label,
                "bbox": bbox,
                "timestamp": "2024-01-01T12:00:00Z"
            }
        ],
        "image_info": {
            "width": 800,
            "height": 600
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/annotations/{image_id}",
        json=annotation_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✅ 检测标注添加成功")
        else:
            print(f"❌ 标注失败: {data.get('error', '未知错误')}")
    else:
        print(f"❌ 标注失败: HTTP {response.status_code}")

def get_annotations(image_id):
    """获取标注数据"""
    print(f"📝 获取图片 {image_id} 的标注数据...")
    
    response = requests.get(f"{BASE_URL}/api/annotations/{image_id}")
    if response.status_code == 200:
        data = response.json()
        annotations = data.get('annotations', [])
        print(f"📊 共有 {len(annotations)} 个标注")
        for ann in annotations:
            print(f"  - {ann['type']}: {ann['label']}")
        return annotations
    else:
        print(f"❌ 获取失败: HTTP {response.status_code}")
        return []

def export_data(format_type):
    """导出数据"""
    print(f"💾 导出 {format_type.upper()} 格式数据...")
    
    response = requests.get(f"{BASE_URL}/api/export/{format_type}")
    if response.status_code == 200:
        data = response.json()
        
        # 保存到文件
        filename = f"export_{format_type}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据已导出到: {filename}")
        return data
    else:
        print(f"❌ 导出失败: HTTP {response.status_code}")
        return None

def check_server():
    """检查服务器是否运行"""
    print("🔍 检查服务器状态...")
    
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ 服务器运行正常")
            return True
        else:
            print(f"⚠️ 服务器响应异常: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("请确保标注工具服务器正在运行 (python app.py)")
        return False

def main():
    """主函数"""
    print("🏷️ 数据集标注工具 API 演示")
    print("=" * 40)
    
    # 检查服务器
    if not check_server():
        return
    
    # 创建演示图片文件夹
    create_demo_images()
    
    # 查找演示图片
    demo_images = []
    if os.path.exists(DEMO_IMAGE_PATH):
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']:
            demo_images.extend(Path(DEMO_IMAGE_PATH).glob(ext))
    
    if not demo_images:
        print(f"⚠️ 在 {DEMO_IMAGE_PATH} 文件夹中未找到演示图片")
        print("请添加一些测试图片后重新运行演示")
        return
    
    print(f"📷 找到 {len(demo_images)} 张演示图片")
    
    # 上传图片
    uploaded_images = []
    for img_path in demo_images[:3]:  # 只上传前3张图片
        image_data = upload_image(str(img_path))
        if image_data:
            uploaded_images.append(image_data)
    
    if not uploaded_images:
        print("❌ 没有成功上传的图片，演示结束")
        return
    
    print("\n" + "=" * 40)
    print("📋 演示标注功能")
    
    # 演示分类标注
    if len(uploaded_images) > 0:
        image_id = uploaded_images[0]['id']
        add_classification_annotation(image_id, "演示分类")
        get_annotations(image_id)
    
    # 演示检测标注
    if len(uploaded_images) > 1:
        image_id = uploaded_images[1]['id']
        bbox = {"x": 100, "y": 50, "width": 200, "height": 150}
        add_detection_annotation(image_id, "演示目标", bbox)
        get_annotations(image_id)
    
    print("\n" + "=" * 40)
    print("📊 获取图片列表")
    get_image_list()
    
    print("\n" + "=" * 40)
    print("💾 演示数据导出")
    
    # 导出不同格式的数据
    for format_type in ['json', 'coco', 'yolo']:
        export_data(format_type)
    
    print("\n" + "=" * 40)
    print("✅ 演示完成！")
    print("\n可以通过浏览器访问 http://localhost:5000 查看Web界面")

if __name__ == "__main__":
    main()