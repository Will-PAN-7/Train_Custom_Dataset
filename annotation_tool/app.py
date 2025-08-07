#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据集标注工具后端服务
支持图像分类、目标检测等多种标注任务
"""

import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from PIL import Image
import numpy as np

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = 'uploads'
ANNOTATIONS_FOLDER = 'annotations'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# 创建必要的文件夹
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ANNOTATIONS_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_info(filepath):
    """获取图像基本信息"""
    try:
        with Image.open(filepath) as img:
            width, height = img.size
            return {
                'width': width,
                'height': height,
                'format': img.format,
                'mode': img.mode
            }
    except Exception as e:
        return None

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传图像文件"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件被上传'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # 获取图像信息
        image_info = get_image_info(filepath)
        if not image_info:
            os.remove(filepath)
            return jsonify({'error': '无效的图像文件'}), 400
        
        # 创建图像记录
        image_data = {
            'id': file_id,
            'filename': filename,
            'original_name': file.filename,
            'upload_time': datetime.now().isoformat(),
            'image_info': image_info,
            'annotations': []
        }
        
        return jsonify({
            'success': True,
            'image_data': image_data
        })
    
    return jsonify({'error': '不支持的文件格式'}), 400

@app.route('/api/images')
def list_images():
    """获取所有已上传的图像列表"""
    images = []
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            if allowed_file(filename):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file_id = filename.split('_')[0]
                image_info = get_image_info(filepath)
                
                if image_info:
                    images.append({
                        'id': file_id,
                        'filename': filename,
                        'image_info': image_info
                    })
    
    return jsonify({'images': images})

@app.route('/api/images/<image_id>')
def get_image(image_id):
    """获取特定图像"""
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.startswith(f"{image_id}_"):
            return send_from_directory(UPLOAD_FOLDER, filename)
    
    return jsonify({'error': '图像不存在'}), 404

@app.route('/api/annotations/<image_id>', methods=['GET'])
def get_annotations(image_id):
    """获取图像的标注数据"""
    annotation_file = os.path.join(ANNOTATIONS_FOLDER, f"{image_id}.json")
    
    if os.path.exists(annotation_file):
        with open(annotation_file, 'r', encoding='utf-8') as f:
            annotations = json.load(f)
        return jsonify(annotations)
    
    return jsonify({'annotations': []})

@app.route('/api/annotations/<image_id>', methods=['POST'])
def save_annotations(image_id):
    """保存图像的标注数据"""
    try:
        annotation_data = request.get_json()
        
        # 添加元数据
        annotation_data['image_id'] = image_id
        annotation_data['last_modified'] = datetime.now().isoformat()
        
        # 保存到文件
        annotation_file = os.path.join(ANNOTATIONS_FOLDER, f"{image_id}.json")
        with open(annotation_file, 'w', encoding='utf-8') as f:
            json.dump(annotation_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '标注保存成功'})
    
    except Exception as e:
        return jsonify({'error': f'保存失败: {str(e)}'}), 500

@app.route('/api/export/<format>')
def export_annotations(format):
    """导出标注数据"""
    try:
        all_annotations = []
        
        # 收集所有标注文件
        if os.path.exists(ANNOTATIONS_FOLDER):
            for filename in os.listdir(ANNOTATIONS_FOLDER):
                if filename.endswith('.json'):
                    filepath = os.path.join(ANNOTATIONS_FOLDER, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        annotation = json.load(f)
                        all_annotations.append(annotation)
        
        if format.lower() == 'json':
            return jsonify(all_annotations)
        elif format.lower() == 'coco':
            # 转换为COCO格式
            coco_data = convert_to_coco_format(all_annotations)
            return jsonify(coco_data)
        elif format.lower() == 'yolo':
            # 转换为YOLO格式
            yolo_data = convert_to_yolo_format(all_annotations)
            return jsonify(yolo_data)
        else:
            return jsonify({'error': '不支持的导出格式'}), 400
    
    except Exception as e:
        return jsonify({'error': f'导出失败: {str(e)}'}), 500

def convert_to_coco_format(annotations):
    """转换为COCO格式"""
    coco_data = {
        "info": {
            "description": "Custom Dataset",
            "version": "1.0",
            "year": datetime.now().year,
            "contributor": "Annotation Tool",
            "date_created": datetime.now().isoformat()
        },
        "licenses": [],
        "images": [],
        "annotations": [],
        "categories": []
    }
    
    category_map = {}
    category_id = 1
    annotation_id = 1
    
    for ann in annotations:
        image_id = ann.get('image_id', '')
        
        # 添加图像信息
        if 'image_info' in ann:
            coco_data['images'].append({
                "id": len(coco_data['images']) + 1,
                "file_name": f"{image_id}.jpg",
                "width": ann['image_info'].get('width', 0),
                "height": ann['image_info'].get('height', 0)
            })
        
        # 处理标注
        for annotation in ann.get('annotations', []):
            if annotation['type'] == 'classification':
                # 图像分类转为整图标注
                category_name = annotation['label']
                if category_name not in category_map:
                    category_map[category_name] = category_id
                    coco_data['categories'].append({
                        "id": category_id,
                        "name": category_name,
                        "supercategory": ""
                    })
                    category_id += 1
                
            elif annotation['type'] == 'detection':
                # 目标检测
                category_name = annotation['label']
                if category_name not in category_map:
                    category_map[category_name] = category_id
                    coco_data['categories'].append({
                        "id": category_id,
                        "name": category_name,
                        "supercategory": ""
                    })
                    category_id += 1
                
                bbox = annotation['bbox']
                coco_data['annotations'].append({
                    "id": annotation_id,
                    "image_id": len(coco_data['images']),
                    "category_id": category_map[category_name],
                    "bbox": [bbox['x'], bbox['y'], bbox['width'], bbox['height']],
                    "area": bbox['width'] * bbox['height'],
                    "iscrowd": 0
                })
                annotation_id += 1
    
    return coco_data

def convert_to_yolo_format(annotations):
    """转换为YOLO格式"""
    yolo_data = {
        "classes": [],
        "annotations": {}
    }
    
    class_names = set()
    
    # 收集所有类别名称
    for ann in annotations:
        for annotation in ann.get('annotations', []):
            if 'label' in annotation:
                class_names.add(annotation['label'])
    
    yolo_data['classes'] = sorted(list(class_names))
    class_to_id = {name: idx for idx, name in enumerate(yolo_data['classes'])}
    
    # 转换标注
    for ann in annotations:
        image_id = ann.get('image_id', '')
        image_annotations = []
        
        image_width = ann.get('image_info', {}).get('width', 1)
        image_height = ann.get('image_info', {}).get('height', 1)
        
        for annotation in ann.get('annotations', []):
            if annotation['type'] == 'detection':
                bbox = annotation['bbox']
                class_id = class_to_id[annotation['label']]
                
                # 转换为YOLO格式 (中心点坐标 + 相对宽高)
                center_x = (bbox['x'] + bbox['width'] / 2) / image_width
                center_y = (bbox['y'] + bbox['height'] / 2) / image_height
                width = bbox['width'] / image_width
                height = bbox['height'] / image_height
                
                image_annotations.append(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}")
        
        yolo_data['annotations'][image_id] = image_annotations
    
    return yolo_data

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)