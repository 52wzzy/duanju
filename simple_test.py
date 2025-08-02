#!/usr/bin/env python3
"""
简化测试脚本 - 验证基本结构是否正确
"""

import sys
import os
import importlib.util

def test_file_structure():
    """测试文件结构"""
    print("🧪 测试文件结构...")
    
    required_files = [
        'app.py',
        'config.py', 
        'requirements.txt',
        'run.py',
        'utils/__init__.py',
        'utils/text_processor.py',
        'utils/image_processor.py',
        'utils/ai_generator.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"   ❌ 缺少文件: {missing_files}")
        return False
    else:
        print(f"   ✅ 所有必需文件存在")
        return True

def test_imports():
    """测试基本导入"""
    print("🧪 测试基本导入...")
    
    try:
        # 测试config.py
        spec = importlib.util.spec_from_file_location("config", "config.py")
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        
        # 检查配置项
        required_configs = ['AI_MODELS', 'FORBIDDEN_WORDS', 'DEFAULT_FONT_CONFIG']
        for config_name in required_configs:
            if not hasattr(config, config_name):
                print(f"   ❌ 缺少配置: {config_name}")
                return False
        
        print(f"   ✅ 配置文件导入成功")
        print(f"   - AI模型数量: {len(config.AI_MODELS)}")
        print(f"   - 违禁词数量: {len(config.FORBIDDEN_WORDS)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
        return False

def test_app_structure():
    """测试应用结构"""
    print("🧪 测试应用结构...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # 检查关键函数
        required_functions = [
            'main()',
            'setup_sidebar()',
            'article_input_section()',
            'template_upload_section()',
            'main_image_generation_section()',
            'detail_page_generation_section()'
        ]
        
        missing_functions = []
        for func in required_functions:
            if f"def {func.replace('()', '')}" not in app_content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"   ❌ 缺少函数: {missing_functions}")
            return False
        else:
            print(f"   ✅ 应用结构完整")
            return True
            
    except Exception as e:
        print(f"   ❌ 检查失败: {e}")
        return False

def test_requirements():
    """测试依赖文件"""
    print("🧪 测试依赖文件...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        # 检查关键包
        key_packages = ['streamlit', 'Pillow', 'opencv-python', 'numpy', 'openai']
        found_packages = []
        
        for req in requirements:
            package_name = req.split('==')[0].lower()
            if package_name in [p.lower() for p in key_packages]:
                found_packages.append(package_name)
        
        print(f"   ✅ 找到关键包: {found_packages}")
        print(f"   - 总依赖数量: {len(requirements)}")
        
        return len(found_packages) >= 4
        
    except Exception as e:
        print(f"   ❌ 检查失败: {e}")
        return False

def test_demo_files():
    """测试演示文件"""
    print("🧪 测试演示文件...")
    
    try:
        if os.path.exists('demo/sample_article.txt'):
            with open('demo/sample_article.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content) > 100:
                print(f"   ✅ 演示文章存在 ({len(content)} 字符)")
                return True
            else:
                print(f"   ❌ 演示文章过短")
                return False
        else:
            print(f"   ⚠️ 演示文章不存在，但不影响核心功能")
            return True
            
    except Exception as e:
        print(f"   ❌ 检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始基础功能测试")
    print("=" * 50)
    
    tests = [
        ("文件结构", test_file_structure),
        ("基本导入", test_imports),
        ("应用结构", test_app_structure),
        ("依赖文件", test_requirements),
        ("演示文件", test_demo_files)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"   结果: ✅ 通过")
            else:
                print(f"   结果: ❌ 失败")
        except Exception as e:
            print(f"   结果: ❌ 异常 - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 基础测试全部通过！")
        print("💡 接下来可以:")
        print("   1. 安装依赖: pip install -r requirements.txt")
        print("   2. 运行应用: streamlit run app.py")
        print("   3. 在浏览器中打开: http://localhost:8501")
    else:
        print("⚠️ 部分测试失败，请检查相关文件")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)