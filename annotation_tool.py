#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据集标注工具
支持图像分类、目标检测、语义分割等多种标注任务
作者：同济子豪兄
"""

import os
import json
import shutil
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'annotation_tool_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ANNOTATIONS_FOLDER'] = 'annotations'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 支持的图像格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

# 创建必要的目录
for folder in [app.config['UPLOAD_FOLDER'], app.config['ANNOTATIONS_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def allowed_file(filename):
    """检查文件扩展名是否被允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class AnnotationManager:
    """标注管理器"""
    
    def __init__(self):
        self.projects = {}
        self.load_projects()
    
    def load_projects(self):
        """加载现有项目"""
        projects_file = os.path.join(app.config['ANNOTATIONS_FOLDER'], 'projects.json')
        if os.path.exists(projects_file):
            with open(projects_file, 'r', encoding='utf-8') as f:
                self.projects = json.load(f)
    
    def save_projects(self):
        """保存项目配置"""
        projects_file = os.path.join(app.config['ANNOTATIONS_FOLDER'], 'projects.json')
        with open(projects_file, 'w', encoding='utf-8') as f:
            json.dump(self.projects, f, ensure_ascii=False, indent=2)
    
    def create_project(self, project_name, task_type, classes):
        """创建新项目"""
        project_id = f"{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.projects[project_id] = {
            'name': project_name,
            'task_type': task_type,  # classification, detection, segmentation
            'classes': classes,
            'created_at': datetime.now().isoformat(),
            'images': [],
            'annotations': {}
        }
        
        # 创建项目目录
        project_dir = os.path.join(app.config['ANNOTATIONS_FOLDER'], project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        self.save_projects()
        return project_id
    
    def add_image(self, project_id, image_filename):
        """向项目添加图像"""
        if project_id in self.projects:
            if image_filename not in self.projects[project_id]['images']:
                self.projects[project_id]['images'].append(image_filename)
                self.save_projects()
            return True
        return False
    
    def save_annotation(self, project_id, image_filename, annotation_data):
        """保存标注数据"""
        if project_id in self.projects:
            self.projects[project_id]['annotations'][image_filename] = annotation_data
            
            # 保存到单独的标注文件
            project_dir = os.path.join(app.config['ANNOTATIONS_FOLDER'], project_id)
            annotation_file = os.path.join(project_dir, f"{image_filename}.json")
            
            with open(annotation_file, 'w', encoding='utf-8') as f:
                json.dump(annotation_data, f, ensure_ascii=False, indent=2)
            
            self.save_projects()
            return True
        return False
    
    def get_annotation(self, project_id, image_filename):
        """获取标注数据"""
        if project_id in self.projects:
            return self.projects[project_id]['annotations'].get(image_filename, {})
        return {}
    
    def export_annotations(self, project_id, export_format='coco'):
        """导出标注数据"""
        if project_id not in self.projects:
            return None
        
        project = self.projects[project_id]
        
        if export_format == 'coco' and project['task_type'] == 'detection':
            return self._export_coco_format(project_id)
        elif export_format == 'yolo' and project['task_type'] == 'detection':
            return self._export_yolo_format(project_id)
        elif project['task_type'] == 'classification':
            return self._export_classification_format(project_id)
        
        return None
    
    def _export_coco_format(self, project_id):
        """导出COCO格式"""
        project = self.projects[project_id]
        
        coco_data = {
            "info": {
                "description": f"Dataset exported from annotation tool - {project['name']}",
                "version": "1.0",
                "year": datetime.now().year,
                "date_created": datetime.now().isoformat()
            },
            "licenses": [{"id": 1, "name": "Unknown", "url": ""}],
            "images": [],
            "annotations": [],
            "categories": []
        }
        
        # 添加类别
        for idx, class_name in enumerate(project['classes']):
            coco_data['categories'].append({
                "id": idx + 1,
                "name": class_name,
                "supercategory": ""
            })
        
        annotation_id = 1
        
        # 处理每张图像
        for idx, image_filename in enumerate(project['images']):
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            if os.path.exists(image_path):
                img = cv2.imread(image_path)
                height, width = img.shape[:2]
                
                coco_data['images'].append({
                    "id": idx + 1,
                    "width": width,
                    "height": height,
                    "file_name": image_filename,
                    "license": 1,
                    "date_captured": ""
                })
                
                # 添加标注
                annotation_data = self.get_annotation(project_id, image_filename)
                if 'objects' in annotation_data:
                    for obj in annotation_data['objects']:
                        bbox = obj['bbox']  # [x, y, width, height]
                        category_id = project['classes'].index(obj['class']) + 1
                        
                        coco_data['annotations'].append({
                            "id": annotation_id,
                            "image_id": idx + 1,
                            "category_id": category_id,
                            "bbox": bbox,
                            "area": bbox[2] * bbox[3],
                            "iscrowd": 0
                        })
                        annotation_id += 1
        
        return coco_data
    
    def _export_yolo_format(self, project_id):
        """导出YOLO格式"""
        project = self.projects[project_id]
        yolo_data = {}
        
        for image_filename in project['images']:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            if os.path.exists(image_path):
                img = cv2.imread(image_path)
                height, width = img.shape[:2]
                
                yolo_annotations = []
                annotation_data = self.get_annotation(project_id, image_filename)
                
                if 'objects' in annotation_data:
                    for obj in annotation_data['objects']:
                        bbox = obj['bbox']  # [x, y, width, height]
                        class_id = project['classes'].index(obj['class'])
                        
                        # 转换为YOLO格式 (归一化的中心点坐标和宽高)
                        x_center = (bbox[0] + bbox[2] / 2) / width
                        y_center = (bbox[1] + bbox[3] / 2) / height
                        norm_width = bbox[2] / width
                        norm_height = bbox[3] / height
                        
                        yolo_annotations.append(f"{class_id} {x_center} {y_center} {norm_width} {norm_height}")
                
                yolo_data[image_filename] = yolo_annotations
        
        return yolo_data
    
    def _export_classification_format(self, project_id):
        """导出分类格式"""
        project = self.projects[project_id]
        classification_data = {}
        
        for image_filename in project['images']:
            annotation_data = self.get_annotation(project_id, image_filename)
            if 'class' in annotation_data:
                classification_data[image_filename] = annotation_data['class']
        
        return classification_data

# 全局标注管理器实例
annotation_manager = AnnotationManager()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html', projects=annotation_manager.projects)

@app.route('/create_project', methods=['POST'])
def create_project():
    """创建新项目"""
    data = request.json
    project_name = data.get('project_name')
    task_type = data.get('task_type')
    classes = data.get('classes', [])
    
    if not project_name or not task_type:
        return jsonify({'success': False, 'message': '项目名称和任务类型不能为空'})
    
    project_id = annotation_manager.create_project(project_name, task_type, classes)
    return jsonify({'success': True, 'project_id': project_id})

@app.route('/upload_images/<project_id>', methods=['POST'])
def upload_images(project_id):
    """上传图像到项目"""
    if 'files' not in request.files:
        return jsonify({'success': False, 'message': '没有选择文件'})
    
    files = request.files.getlist('files')
    uploaded_files = []
    
    for file in files:
        if file.filename == '':
            continue
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 添加时间戳避免重名
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # 添加到项目
            if annotation_manager.add_image(project_id, filename):
                uploaded_files.append(filename)
    
    return jsonify({'success': True, 'uploaded_files': uploaded_files})

@app.route('/project/<project_id>')
def project_page(project_id):
    """项目页面"""
    if project_id not in annotation_manager.projects:
        return "项目不存在", 404
    
    project = annotation_manager.projects[project_id]
    return render_template('project.html', project=project, project_id=project_id)

@app.route('/annotate/<project_id>/<image_filename>')
def annotate_image(project_id, image_filename):
    """标注页面"""
    if project_id not in annotation_manager.projects:
        return "项目不存在", 404
    
    project = annotation_manager.projects[project_id]
    annotation_data = annotation_manager.get_annotation(project_id, image_filename)
    
    return render_template('annotate.html', 
                         project=project, 
                         project_id=project_id,
                         image_filename=image_filename,
                         annotation_data=annotation_data)

@app.route('/save_annotation/<project_id>/<image_filename>', methods=['POST'])
def save_annotation(project_id, image_filename):
    """保存标注数据"""
    annotation_data = request.json
    
    if annotation_manager.save_annotation(project_id, image_filename, annotation_data):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': '保存失败'})

@app.route('/get_annotation/<project_id>/<image_filename>')
def get_annotation(project_id, image_filename):
    """获取标注数据"""
    annotation_data = annotation_manager.get_annotation(project_id, image_filename)
    return jsonify(annotation_data)

@app.route('/export/<project_id>/<export_format>')
def export_annotations(project_id, export_format):
    """导出标注数据"""
    data = annotation_manager.export_annotations(project_id, export_format)
    
    if data is None:
        return jsonify({'success': False, 'message': '导出失败'})
    
    # 保存导出文件
    export_filename = f"{project_id}_{export_format}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    export_path = os.path.join(app.config['ANNOTATIONS_FOLDER'], export_filename)
    
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return send_from_directory(app.config['ANNOTATIONS_FOLDER'], export_filename, as_attachment=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传的文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete_project/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """删除项目"""
    if project_id in annotation_manager.projects:
        # 删除项目目录
        project_dir = os.path.join(app.config['ANNOTATIONS_FOLDER'], project_id)
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
        
        # 删除项目配置
        del annotation_manager.projects[project_id]
        annotation_manager.save_projects()
        
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': '项目不存在'})

if __name__ == '__main__':
    print("数据集标注工具启动中...")
    print("访问地址: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)