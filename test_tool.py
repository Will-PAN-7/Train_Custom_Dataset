#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据集标注工具测试脚本
"""

import sys
import os
import json

def test_imports():
    """测试必要的模块导入"""
    print("测试模块导入...")
    
    try:
        import json
        print("✓ json 模块导入成功")
    except ImportError as e:
        print(f"✗ json 模块导入失败: {e}")
        return False
    
    try:
        import datetime
        print("✓ datetime 模块导入成功")
    except ImportError as e:
        print(f"✗ datetime 模块导入失败: {e}")
        return False
    
    try:
        import os
        print("✓ os 模块导入成功")
    except ImportError as e:
        print(f"✗ os 模块导入失败: {e}")
        return False
    
    # 测试可选模块
    optional_modules = {
        'flask': 'Flask',
        'cv2': 'OpenCV',
        'PIL': 'Pillow',
        'numpy': 'NumPy'
    }
    
    for module, name in optional_modules.items():
        try:
            __import__(module)
            print(f"✓ {name} 模块导入成功")
        except ImportError:
            print(f"⚠ {name} 模块未安装（需要安装: pip install {module}）")
    
    return True

def test_file_structure():
    """测试文件结构"""
    print("\n测试文件结构...")
    
    required_files = [
        'annotation_tool.py',
        'requirements.txt',
        '标注工具使用说明.md',
        'templates/index.html',
        'templates/project.html', 
        'templates/annotate.html'
    ]
    
    all_exists = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} 存在")
        else:
            print(f"✗ {file_path} 不存在")
            all_exists = False
    
    return all_exists

def test_directories():
    """测试目录创建"""
    print("\n测试目录创建...")
    
    required_dirs = ['uploads', 'annotations']
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name)
                print(f"✓ 创建目录: {dir_name}")
            except Exception as e:
                print(f"✗ 创建目录失败 {dir_name}: {e}")
                return False
        else:
            print(f"✓ 目录已存在: {dir_name}")
    
    return True

def test_json_operations():
    """测试JSON操作"""
    print("\n测试JSON操作...")
    
    # 测试创建项目配置
    test_project = {
        'name': '测试项目',
        'task_type': 'classification',
        'classes': ['类别1', '类别2'],
        'created_at': '2024-01-01T00:00:00',
        'images': [],
        'annotations': {}
    }
    
    try:
        # 测试JSON序列化
        json_str = json.dumps(test_project, ensure_ascii=False, indent=2)
        print("✓ JSON序列化成功")
        
        # 测试JSON反序列化
        parsed_project = json.loads(json_str)
        print("✓ JSON反序列化成功")
        
        # 测试写入文件
        if not os.path.exists('annotations'):
            os.makedirs('annotations')
        
        test_file = 'annotations/test_project.json'
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_project, f, ensure_ascii=False, indent=2)
        print("✓ JSON文件写入成功")
        
        # 测试读取文件
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_project = json.load(f)
        print("✓ JSON文件读取成功")
        
        # 清理测试文件
        os.remove(test_file)
        print("✓ 测试文件清理完成")
        
        return True
        
    except Exception as e:
        print(f"✗ JSON操作测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("数据集标注工具 - 基础功能测试")
    print("作者：同济子豪兄")
    print("=" * 50)
    
    tests = [
        ("模块导入测试", test_imports),
        ("文件结构测试", test_file_structure),
        ("目录创建测试", test_directories),
        ("JSON操作测试", test_json_operations)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
            print(f"✓ {test_name} 通过")
        else:
            print(f"✗ {test_name} 失败")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有基础功能测试通过！")
        print("\n下一步:")
        print("1. 安装Python依赖: pip install -r requirements.txt")
        print("2. 启动应用: python annotation_tool.py")
        print("3. 在浏览器中访问: http://localhost:5000")
        return True
    else:
        print("❌ 部分测试失败，请检查环境配置")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)