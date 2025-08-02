import requests
import base64
import json
import time
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import io
import os
import re
from typing import Dict, Optional, Tuple

class SimpleAIImageGenerator:
    """简化版AI图片生成器类"""
    
    def __init__(self):
        self.api_key = None
        self.model_type = None
        
    def set_api_key(self, api_key: str, model_type: str = 'dalle3'):
        """设置API密钥"""
        self.api_key = api_key
        self.model_type = model_type
            
    def generate_image_prompt(self, title: str, content: str, style: str = 'commercial') -> str:
        """生成图片提示词"""
        # 提取关键词
        keywords = self._extract_keywords(content)
        
        # 根据风格生成提示词
        if style == 'commercial':
            prompt = f"""
            Create a professional e-commerce main image for: "{title}"
            Style: Modern, clean, business-oriented
            Elements: Professional layout, attractive typography, commercial appeal
            Keywords: {', '.join(keywords[:5])}
            Requirements: High quality, suitable for product listing, eye-catching design
            Color scheme: Professional blues and whites with accent colors
            Layout: Centered title, supporting text, clean background
            """
        elif style == 'tutorial':
            prompt = f"""
            Create an educational tutorial image for: "{title}"
            Style: Educational, informative, step-by-step
            Elements: Clear instructions, visual guides, professional presentation
            Keywords: {', '.join(keywords[:5])}
            Requirements: Easy to understand, instructional design, engaging visuals
            Color scheme: Friendly blues and greens with clear contrast
            Layout: Title at top, key points below, organized structure
            """
        else:
            prompt = f"""
            Create an attractive image for: "{title}"
            Keywords: {', '.join(keywords[:5])}
            Style: Professional and appealing
            """
            
        return prompt.strip()
    
    def _extract_keywords(self, content: str) -> list:
        """从内容中提取关键词"""
        # 简单的关键词提取
        common_words = ['的', '是', '在', '有', '和', '与', '或', '但', '就', '这', '那', '及', '以', '为', '了', '到', '等']
        words = []
        
        # 分割文本并过滤
        text_words = re.findall(r'[\u4e00-\u9fff]+', content)
        
        for word in text_words:
            if len(word) >= 2 and word not in common_words:
                words.append(word)
                
        return list(set(words))[:10]  # 返回前10个唯一关键词

class SimpleImageProcessor:
    """简化版图片处理器"""
    
    def __init__(self):
        self.default_fonts = {
            'title': 48,
            'subtitle': 28,
            'content': 24,
            'small': 18
        }
        
    def create_enhanced_main_image(self, template_path: str, text_data: dict, 
                                 reference_path: str = None, 
                                 style_config: dict = None) -> str:
        """创建增强版主图"""
        try:
            # 加载模板
            template = Image.open(template_path)
            if template.mode != 'RGB':
                template = template.convert('RGB')
                
            # 增强图片质量
            template = self._enhance_image_quality(template)
            
            # 添加文字内容
            template = self._add_advanced_text(template, text_data)
            
            # 添加装饰元素
            template = self._add_decorative_elements(template, text_data)
            
            # 最终优化
            template = self._final_optimization(template)
            
            # 保存结果
            output_filename = f"enhanced_main_image_{int(time.time())}.png"
            output_path = os.path.join("generated", output_filename)
            template.save(output_path, quality=95, optimize=True)
            
            return output_path
            
        except Exception as e:
            print(f"创建增强主图失败: {e}")
            return None
    
    def _enhance_image_quality(self, image: Image.Image) -> Image.Image:
        """增强图片质量"""
        # 提高对比度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        
        # 提高饱和度
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.05)
        
        return image
    
    def _add_advanced_text(self, image: Image.Image, text_data: dict) -> Image.Image:
        """添加高级文字效果"""
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # 颜色方案
        title_color = (255, 68, 68)  # 红色
        subtitle_color = (46, 134, 171)  # 蓝色
        
        # 加载字体
        fonts = self._load_fonts()
        
        # 绘制主标题（带阴影效果）
        title = text_data.get('main_title', '')
        if title:
            title_font = fonts['title']
            
            # 计算位置
            try:
                title_bbox = draw.textbbox((0, 0), title, font=title_font)
                title_width = title_bbox[2] - title_bbox[0]
            except:
                # 降级方案
                title_width = len(title) * 30
                
            title_x = (width - title_width) // 2
            title_y = height // 4
            
            # 绘制阴影
            shadow_offset = 2
            draw.text((title_x + shadow_offset, title_y + shadow_offset), 
                     title, fill=(0, 0, 0, 100), font=title_font)
            
            # 绘制主文字
            draw.text((title_x, title_y), title, fill=title_color, font=title_font)
        
        # 绘制副标题
        subtitle = text_data.get('subtitle', '')
        if subtitle:
            subtitle_font = fonts['subtitle']
            try:
                subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
                subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            except:
                subtitle_width = len(subtitle) * 20
                
            subtitle_x = (width - subtitle_width) // 2
            subtitle_y = title_y + 80
            
            # 绘制文字
            draw.text((subtitle_x, subtitle_y), subtitle, fill=subtitle_color, font=subtitle_font)
        
        # 绘制关键点
        key_points = text_data.get('key_points', [])
        if key_points:
            point_font = fonts['content']
            start_y = subtitle_y + 100
            
            for i, point in enumerate(key_points[:3]):
                point_y = start_y + i * 40
                
                # 绘制项目符号
                draw.ellipse([30, point_y + 5, 40, point_y + 15], fill=subtitle_color)
                
                # 绘制文字
                draw.text((50, point_y), f"{point}", fill=(51, 51, 51), font=point_font)
        
        return image
    
    def _add_decorative_elements(self, image: Image.Image, text_data: dict) -> Image.Image:
        """添加装饰元素"""
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # 添加边框装饰
        border_color = (102, 126, 234)
        border_width = 3
        
        # 顶部装饰线
        draw.rectangle([0, 0, width, border_width], fill=border_color)
        
        # 底部装饰线
        draw.rectangle([0, height - border_width, width, height], fill=border_color)
        
        return image
    
    def _final_optimization(self, image: Image.Image) -> Image.Image:
        """最终优化"""
        # 最终对比度调整
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.02)
        
        return image
    
    def _load_fonts(self) -> dict:
        """加载字体"""
        fonts = {}
        
        # 尝试系统字体路径
        font_paths = [
            "static/fonts/PingFang-Bold.ttf",
            "static/fonts/PingFang-Regular.ttf",
            "/System/Library/Fonts/PingFang.ttc",
            "/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/msyh.ttc",
            "/System/Library/Fonts/Arial.ttf",
            "C:/Windows/Fonts/arial.ttf"
        ]
        
        for size_name, size in self.default_fonts.items():
            font_loaded = False
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        fonts[size_name] = ImageFont.truetype(font_path, size)
                        font_loaded = True
                        break
                except Exception as e:
                    continue
            
            if not font_loaded:
                try:
                    # 使用默认字体
                    fonts[size_name] = ImageFont.load_default()
                except:
                    # 最后降级方案
                    fonts[size_name] = None
        
        return fonts

# 为了兼容性，提供相同的接口
AIImageGenerator = SimpleAIImageGenerator
AdvancedImageProcessor = SimpleImageProcessor