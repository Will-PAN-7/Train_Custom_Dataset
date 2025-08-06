# 🏷️ 数据集标注工具

一个基于Web的现代化数据集标注工具，支持图像分类、目标检测等多种标注任务，具有直观的用户界面和强大的数据导出功能。

## ✨ 功能特色

### 🎯 多种标注模式
- **图像分类**: 为整张图像添加类别标签
- **目标检测**: 通过拖拽绘制边界框进行目标标注
- **实时预览**: 标注结果实时显示在图像上

### 📁 文件管理
- **拖拽上传**: 支持拖拽多个图像文件上传
- **格式支持**: JPG、PNG、GIF、BMP等常见图像格式
- **批量处理**: 一次上传多个文件，快速切换标注

### 💾 数据导出
- **JSON格式**: 原始标注数据导出
- **COCO格式**: 兼容COCO数据集格式
- **YOLO格式**: 支持YOLO训练格式导出

### 🎨 用户体验
- **现代化UI**: 渐变背景、圆角设计、流畅动画
- **响应式设计**: 适配不同屏幕尺寸
- **实时反馈**: 操作提示、进度显示、通知消息
- **键盘快捷键**: Delete/Backspace删除标注

## 🚀 快速开始

### 环境要求
- Python 3.7+
- 现代浏览器（Chrome、Firefox、Safari、Edge）

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd annotation_tool
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动服务**
```bash
python app.py
```

4. **打开浏览器**
访问 `http://localhost:5000` 开始使用

### Docker 部署（可选）

```bash
# 构建镜像
docker build -t annotation-tool .

# 运行容器
docker run -p 5000:5000 -v $(pwd)/uploads:/app/uploads -v $(pwd)/annotations:/app/annotations annotation-tool
```

## 📖 使用指南

### 1. 上传图像
- 点击左侧"文件管理"区域的上传框
- 或直接拖拽图像文件到上传区域
- 支持同时上传多个文件

### 2. 图像分类标注
1. 选择"图像分类"模式
2. 在右侧输入类别标签
3. 点击"添加分类标注"按钮
4. 每张图像只能有一个分类标注

### 3. 目标检测标注
1. 选择"目标检测"模式
2. 在右侧输入目标标签
3. 在图像上拖拽鼠标绘制边界框
4. 可以添加多个检测框
5. 右键点击边界框可删除标注

### 4. 保存和导出
- 点击"保存标注"保存当前图像的标注
- 使用导出按钮将所有标注数据导出为不同格式
- 支持JSON、COCO、YOLO三种格式

### 5. 快捷键操作
- `Delete` 或 `Backspace`: 删除最后一个标注
- `右键`: 删除点击位置的检测框

## 🔧 API 文档

### 图像管理

#### 上传图像
```http
POST /api/upload
Content-Type: multipart/form-data

参数:
- file: 图像文件

返回:
{
  "success": true,
  "image_data": {
    "id": "图像ID",
    "filename": "文件名",
    "original_name": "原始文件名",
    "upload_time": "上传时间",
    "image_info": {
      "width": 图像宽度,
      "height": 图像高度,
      "format": "图像格式",
      "mode": "颜色模式"
    }
  }
}
```

#### 获取图像列表
```http
GET /api/images

返回:
{
  "images": [
    {
      "id": "图像ID",
      "filename": "文件名",
      "image_info": {...}
    }
  ]
}
```

#### 获取图像文件
```http
GET /api/images/<image_id>

返回: 图像文件数据
```

### 标注管理

#### 获取标注数据
```http
GET /api/annotations/<image_id>

返回:
{
  "annotations": [
    {
      "id": "标注ID",
      "type": "classification|detection",
      "label": "标签",
      "bbox": {...}, // 仅检测标注
      "timestamp": "时间戳"
    }
  ]
}
```

#### 保存标注数据
```http
POST /api/annotations/<image_id>
Content-Type: application/json

参数:
{
  "annotations": [...],
  "image_info": {
    "width": 图像宽度,
    "height": 图像高度
  }
}

返回:
{
  "success": true,
  "message": "标注保存成功"
}
```

### 数据导出

#### 导出标注数据
```http
GET /api/export/<format>

format: json|coco|yolo

返回: 对应格式的标注数据
```

## 📁 项目结构

```
annotation_tool/
├── app.py                 # Flask后端服务器
├── requirements.txt       # Python依赖
├── README.md             # 项目文档
├── templates/
│   └── index.html        # 前端界面
├── uploads/              # 上传的图像文件
├── annotations/          # 标注数据文件
└── static/              # 静态资源（如有）
```

## 🎨 界面预览

### 主界面
- **左侧边栏**: 文件管理、图片列表、统计信息
- **中间区域**: 图像显示和标注画布
- **右侧边栏**: 标注工具、标注列表、数据管理

### 标注模式
- **分类模式**: 简单的标签输入界面
- **检测模式**: 可视化边界框绘制

### 数据导出格式

#### JSON格式
```json
{
  "image_id": "图像ID",
  "annotations": [
    {
      "id": "标注ID",
      "type": "detection",
      "label": "cat",
      "bbox": {
        "x": 100,
        "y": 50,
        "width": 200,
        "height": 150
      },
      "timestamp": "2024-01-01T12:00:00Z"
    }
  ]
}
```

#### COCO格式
```json
{
  "info": {...},
  "images": [...],
  "annotations": [...],
  "categories": [...]
}
```

#### YOLO格式
```json
{
  "classes": ["cat", "dog", "bird"],
  "annotations": {
    "image_id": [
      "0 0.5 0.3 0.4 0.2"
    ]
  }
}
```

## 🔧 自定义配置

### 修改上传限制
在 `app.py` 中修改 `ALLOWED_EXTENSIONS` 变量：
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
```

### 修改存储路径
```python
UPLOAD_FOLDER = 'custom_uploads'
ANNOTATIONS_FOLDER = 'custom_annotations'
```

### 添加新的导出格式
在 `app.py` 中添加新的转换函数：
```python
def convert_to_custom_format(annotations):
    # 自定义转换逻辑
    return custom_data
```

## 🐛 常见问题

### Q: 上传失败怎么办？
A: 检查文件格式是否支持，文件大小是否过大，网络连接是否正常。

### Q: 标注数据丢失了？
A: 确保在切换图像前点击"保存标注"按钮。数据保存在 `annotations/` 文件夹中。

### Q: 如何批量处理图像？
A: 可以一次上传多个图像，然后逐个进行标注。未来版本将支持批量操作。

### Q: 支持哪些图像格式？
A: 目前支持 PNG、JPG、JPEG、GIF、BMP 格式。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

---

**快速链接**:
- [🐛 报告Bug](../../issues)
- [💡 功能建议](../../issues)
- [📖 文档](README.md)
- [🔧 API文档](#-api-文档)