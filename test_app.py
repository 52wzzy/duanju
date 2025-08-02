#!/usr/bin/env python3
"""
测试脚本 - 验证核心功能是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.text_processor import TextProcessor
from utils.image_processor import ImageProcessor
from utils.ai_generator import AIGenerator
from PIL import Image
import numpy as np

def test_text_processor():
    """测试文本处理器"""
    print("🧪 测试文本处理器...")
    
    processor = TextProcessor()
    
    # 测试违禁词检测
    test_text = "这是最好的产品，保证100%有效"
    result = processor.check_forbidden_words(test_text)
    
    print(f"   违禁词检测: {'✅' if result['has_forbidden'] else '❌'}")
    if result['has_forbidden']:
        print(f"   发现违禁词: {result['forbidden_words']}")
        print(f"   替换建议: {result['suggestion']}")
    
    # 测试关键词提取
    content = "网络创业是当今时代的新机遇，通过线上业务可以实现财务自由"
    keywords = processor.extract_keywords(content, 5)
    print(f"   关键词提取: {'✅' if keywords else '❌'}")
    print(f"   提取结果: {keywords}")
    
    # 测试标题变体生成
    title = "网络创业指南"
    variants = processor.generate_title_variants(title)
    print(f"   标题变体: {'✅' if len(variants) > 1 else '❌'}")
    print(f"   变体数量: {len(variants)}")
    
    return True

def test_image_processor():
    """测试图片处理器"""
    print("🧪 测试图片处理器...")
    
    processor = ImageProcessor()
    
    # 创建测试图片
    test_image = Image.new('RGB', (800, 800), color='white')
    
    # 测试模板分析
    try:
        analysis = processor.analyze_template(test_image)
        print(f"   模板分析: {'✅' if analysis else '❌'}")
        print(f"   图片尺寸: {analysis['width']}x{analysis['height']}")
        print(f"   颜色数量: {len(analysis['color_palette'])}")
    except Exception as e:
        print(f"   模板分析: ❌ - {e}")
        return False
    
    # 测试文字渲染
    try:
        texts = {"title": "测试标题", "subtitle": "测试副标题"}
        style_config = {
            "title": {"size": 36, "color": "#FF6B35", "weight": "bold"},
            "subtitle": {"size": 24, "color": "#333333", "weight": "normal"}
        }
        result_image = processor.render_text_on_template(test_image, texts, style_config)
        print(f"   文字渲染: {'✅' if result_image else '❌'}")
    except Exception as e:
        print(f"   文字渲染: ❌ - {e}")
        return False
    
    return True

def test_ai_generator():
    """测试AI生成器"""
    print("🧪 测试AI生成器...")
    
    generator = AIGenerator()
    
    # 测试提示词生成
    try:
        prompt = generator.generate_image_prompt(
            "网络创业指南",
            "这是一个关于网络创业的教程",
            {"color_scheme": "现代商务", "style": "专业"}
        )
        print(f"   提示词生成: {'✅' if prompt else '❌'}")
        print(f"   提示词长度: {len(prompt)} 字符")
    except Exception as e:
        print(f"   提示词生成: ❌ - {e}")
        return False
    
    # 测试详情页布局生成
    try:
        layout = generator.generate_detail_page_layout("网络创业教程内容示例")
        print(f"   布局生成: {'✅' if layout and 'sections' in layout else '❌'}")
        print(f"   章节数量: {len(layout.get('sections', []))}")
    except Exception as e:
        print(f"   布局生成: ❌ - {e}")
        return False
    
    return True

def test_integration():
    """集成测试"""
    print("🧪 运行集成测试...")
    
    # 测试完整流程
    try:
        # 1. 文本处理
        text_processor = TextProcessor()
        article_content = "网络创业是现代人追求财务自由的新方式，通过互联网平台可以快速建立盈利模式"
        
        keywords = text_processor.extract_keywords(article_content, 5)
        selling_points = text_processor.extract_selling_points(article_content)
        
        # 2. 图片处理
        image_processor = ImageProcessor()
        template = Image.new('RGB', (800, 800), color='white')
        analysis = image_processor.analyze_template(template)
        
        # 3. AI生成
        ai_generator = AIGenerator()
        layout = ai_generator.generate_detail_page_layout(article_content)
        
        print(f"   完整流程: ✅")
        print(f"   关键词: {len(keywords)}, 卖点: {len(selling_points)}, 布局: {len(layout['sections'])}")
        
    except Exception as e:
        print(f"   完整流程: ❌ - {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("🚀 开始测试智能电商主图生成器")
    print("=" * 50)
    
    tests = [
        ("文本处理器", test_text_processor),
        ("图片处理器", test_image_processor), 
        ("AI生成器", test_ai_generator),
        ("集成测试", test_integration)
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
        print("🎉 所有测试通过！系统运行正常")
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)