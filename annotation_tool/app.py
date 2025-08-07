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
IMU_FOLDER = 'imu_data'  # 新增IMU数据文件夹
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
ALLOWED_IMU_EXTENSIONS = {'csv', 'txt', 'json'}  # 新增IMU文件格式支持

# 创建必要的文件夹
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ANNOTATIONS_FOLDER, exist_ok=True)
os.makedirs(IMU_FOLDER, exist_ok=True)  # 创建IMU数据文件夹

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_imu_file(filename):
    """检查是否为允许的IMU文件格式"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMU_EXTENSIONS

def parse_imu_data(filepath):
    """解析IMU数据文件"""
    try:
        file_ext = filepath.rsplit('.', 1)[1].lower()
        
        if file_ext == 'csv':
            import pandas as pd
            df = pd.read_csv(filepath)
            # 假设CSV格式包含如下字段：
            # timestamp: 消息发送的时间戳，单位为秒（s），用于标识每一帧IMU数据的采集时刻
            # acc_x, acc_y, acc_z: 三轴线性加速度，单位为米每二次方秒（m/s^2），分别对应X、Y、Z轴
            # gyro_x, gyro_y, gyro_z: 三轴角速度，单位为弧度每秒（rad/s），分别对应X、Y、Z轴
            #
            # 说明：如需扩展IMU消息头部（如frame_id坐标系ID）、空间姿态（orientation四元数）、协方差矩阵（covariance）等字段，可参考ROS标准IMU消息格式sensor_msgs/Imu。
            # 当前实现仅支持常见的加速度计和陀螺仪数据。
            return {
                'format': 'csv',
                'columns': list(df.columns),
                'length': len(df),
                'sample_data': df.head(5).to_dict('records'),
                'data': df.to_dict('records')
            }
        
        elif file_ext == 'json':
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    'format': 'json',
                    'length': len(data) if isinstance(data, list) else 1,
                    'sample_data': data[:5] if isinstance(data, list) else data,
                    'data': data
                }
        
        elif file_ext == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # 简单的文本解析，假设每行是以空格或逗号分隔的数值
                data = []
                for line in lines[:100]:  # 只处理前100行作为示例
                    line = line.strip()
                    if line:
                        values = line.replace(',', ' ').split()
                        try:
                            numeric_values = [float(v) for v in values]
                            data.append(numeric_values)
                        except ValueError:
                            continue
                
                return {
                    'format': 'txt',
                    'length': len(lines),
                    'sample_data': data[:5],
                    'data': data
                }
        
        return None
    except Exception as e:
        print(f"解析IMU数据时出错: {e}")
        return None

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

# IMU数据相关API
@app.route('/api/imu/upload', methods=['POST'])
def upload_imu():
    """上传IMU数据文件"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_imu_file(file.filename):
        # 生成唯一的文件ID
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        filepath = os.path.join(IMU_FOLDER, filename)
        
        file.save(filepath)
        
        # 解析IMU数据
        imu_info = parse_imu_data(filepath)
        if not imu_info:
            return jsonify({'error': '无法解析IMU数据文件'}), 400
        
        # 保存文件信息
        file_info = {
            'id': file_id,
            'filename': file.filename,
            'filepath': filepath,
            'upload_time': datetime.now().isoformat(),
            'imu_info': imu_info
        }
        
        return jsonify({
            'success': True,
            'file_info': file_info
        })
    
    return jsonify({'error': '不支持的文件格式'}), 400

@app.route('/api/imu/list', methods=['GET'])
def list_imu_files():
    """获取IMU文件列表"""
    files = []
    
    for filename in os.listdir(IMU_FOLDER):
        if allowed_imu_file(filename):
            filepath = os.path.join(IMU_FOLDER, filename)
            file_id = filename.split('_')[0]
            original_name = '_'.join(filename.split('_')[1:])
            
            # 获取文件基本信息
            stat = os.stat(filepath)
            
            files.append({
                'id': file_id,
                'filename': original_name,
                'size': stat.st_size,
                'upload_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
    
    return jsonify({'files': files})

@app.route('/api/imu/<file_id>', methods=['GET'])
def get_imu_data(file_id):
    """获取特定IMU文件的数据"""
    # 查找文件
    target_file = None
    for filename in os.listdir(IMU_FOLDER):
        if filename.startswith(file_id + '_'):
            target_file = os.path.join(IMU_FOLDER, filename)
            break
    
    if not target_file or not os.path.exists(target_file):
        return jsonify({'error': '文件不存在'}), 404
    
    # 解析数据
    imu_data = parse_imu_data(target_file)
    if not imu_data:
        return jsonify({'error': '无法解析文件'}), 500
    
    return jsonify(imu_data)

@app.route('/api/imu/annotations/<file_id>', methods=['GET', 'POST'])
def imu_annotations(file_id):
    """获取或保存IMU数据标注"""
    annotation_file = os.path.join(ANNOTATIONS_FOLDER, f'imu_{file_id}.json')
    
    if request.method == 'GET':
        # 获取标注数据
        if os.path.exists(annotation_file):
            with open(annotation_file, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        else:
            return jsonify({'annotations': []})
    
    elif request.method == 'POST':
        # 保存标注数据
        data = request.get_json()
        
        annotation_data = {
            'file_id': file_id,
            'annotations': data.get('annotations', []),
            'last_updated': datetime.now().isoformat()
        }
        
        with open(annotation_file, 'w', encoding='utf-8') as f:
            json.dump(annotation_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '标注已保存'})

@app.route('/api/imu/export/<format_type>', methods=['GET'])
def export_imu_annotations(format_type):
    """导出IMU标注数据"""
    # 获取所有IMU标注文件
    annotations = []
    
    for filename in os.listdir(ANNOTATIONS_FOLDER):
        if filename.startswith('imu_') and filename.endswith('.json'):
            filepath = os.path.join(ANNOTATIONS_FOLDER, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                annotations.append(json.load(f))
    
    if format_type == 'json':
        return jsonify({
            'export_time': datetime.now().isoformat(),
            'total_files': len(annotations),
            'annotations': annotations
        })
    
    elif format_type == 'csv':
        # 将标注数据转换为CSV格式
        import pandas as pd
        
        rows = []
        for ann_file in annotations:
            file_id = ann_file.get('file_id', '')
            for annotation in ann_file.get('annotations', []):
                row = {
                    'file_id': file_id,
                    'start_time': annotation.get('start_time', ''),
                    'end_time': annotation.get('end_time', ''),
                    'label': annotation.get('label', ''),
                    'description': annotation.get('description', ''),
                    'timestamp': annotation.get('timestamp', '')
                }
                rows.append(row)
        
        df = pd.DataFrame(rows)
        csv_content = df.to_csv(index=False)
        
        return jsonify({
            'format': 'csv',
            'content': csv_content,
            'filename': f'imu_annotations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        })
    
    return jsonify({'error': '不支持的导出格式'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)