# 🚀 快速使用指南

## 立即开始

### 1. 启动服务器
```bash
cd annotation_tool
python3 app.py
```

### 2. 打开浏览器
访问: http://localhost:5000

### 3. 开始标注
1. **上传图片**: 点击或拖拽图片到上传区域
2. **选择模式**: 
   - 图像分类: 为整张图片添加标签
   - 目标检测: 在图片上绘制边界框
3. **添加标注**: 根据选择的模式进行标注
4. **保存数据**: 点击"保存标注"按钮
5. **导出数据**: 选择JSON、COCO或YOLO格式导出

## 🎯 标注模式详解

### 图像分类
- 用途: 为整张图片分配一个类别
- 操作: 输入类别名称，点击"添加分类标注"
- 示例: 将一张猫的照片标注为"cat"

### 目标检测
- 用途: 标记图片中的具体目标位置
- 操作: 在图片上拖拽鼠标绘制边界框
- 功能: 
  - 左键拖拽: 绘制边界框
  - 右键点击: 删除边界框
  - Delete键: 删除最后一个标注

## 📊 数据格式

### JSON格式 (原始数据)
```json
{
  "image_id": "12345",
  "annotations": [
    {
      "type": "classification",
      "label": "cat"
    },
    {
      "type": "detection", 
      "label": "dog",
      "bbox": {"x": 100, "y": 50, "width": 200, "height": 150}
    }
  ]
}
```

### COCO格式 (目标检测标准)
- 兼容COCO数据集格式
- 适用于训练目标检测模型
- 包含图片信息、标注信息、类别信息

### YOLO格式 (深度学习训练)
- 适用于YOLO系列模型训练
- 边界框使用相对坐标
- 每行格式: `class_id x_center y_center width height`

## 🛠️ 快捷键

- `Delete` / `Backspace`: 删除最后一个标注
- `右键`: 删除点击位置的检测框
- `拖拽`: 上传文件或绘制边界框

## 📁 文件结构

```
annotation_tool/
├── uploads/          # 上传的图片
├── annotations/      # 标注数据(JSON)
├── app.py           # 服务器程序  
├── templates/       # 网页模板
└── demo_images/     # 演示图片
```

## 🔧 自定义配置

### 修改端口
在 `app.py` 最后一行:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # 改为8080端口
```

### 添加支持的图片格式
在 `app.py` 中修改:
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'tiff'}
```

### 修改存储路径
```python
UPLOAD_FOLDER = 'my_uploads'
ANNOTATIONS_FOLDER = 'my_annotations'
```

## 🐛 故障排除

### 问题: 无法上传图片
- 检查文件格式是否支持
- 确认文件大小不超过限制
- 查看浏览器控制台错误信息

### 问题: 标注数据丢失
- 确保点击"保存标注"按钮
- 检查 `annotations/` 文件夹权限
- 查看服务器控制台错误信息

### 问题: 页面无法访问
- 确认服务器正在运行
- 检查端口是否被占用
- 尝试使用 `http://127.0.0.1:5000`

## 📞 获取帮助

- 查看完整文档: [README.md](README.md)
- 运行演示脚本: `python3 demo.py`
- 检查服务器日志获取错误信息

---

**提示**: 首次使用建议先用 `demo_images/` 中的示例图片进行测试！