import openai
import requests
import base64
import json
import time
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import io
import os
from typing import Dict, Optional, Tuple

class AIImageGenerator:
    """AI图片生成器类"""
    
    def __init__(self):
        self.openai_client = None
        
    def set_api_key(self, api_key: str, model_type: str = 'dalle3'):
        """设置API密钥"""
        if model_type == 'dalle3':
            openai.api_key = api_key
            self.openai_client = openai
            
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
        import re
        text_words = re.findall(r'[\u4e00-\u9fff]+', content)
        
        for word in text_words:
            if len(word) >= 2 and word not in common_words:
                words.append(word)
                
        return list(set(words))[:10]  # 返回前10个唯一关键词
    
    def generate_with_dalle3(self, prompt: str, size: str = "1024x1024") -> Optional[str]:
        """使用DALL-E 3生成图片"""
        try:
            if not self.openai_client:
                raise Exception("OpenAI API未初始化")
                
            response = self.openai_client.Image.create(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="standard",
                n=1,
            )
            
            return response.data[0].url
            
        except Exception as e:
            print(f"DALL-E 3生成失败: {e}")
            return None
    
    def generate_with_stable_diffusion(self, prompt: str, api_key: str) -> Optional[str]:
        """使用Stable Diffusion生成图片"""
        try:
            # 这里可以集成Stability AI的API
            # 由于需要具体的API实现，这里提供框架
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
            
            body = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1
                    }
                ],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 50,
            }
            
            response = requests.post(url, headers=headers, json=body)
            
            if response.status_code == 200:
                data = response.json()
                # 处理返回的图片数据
                for artifact in data["artifacts"]:
                    image_data = base64.b64decode(artifact["base64"])
                    # 保存图片并返回URL
                    filename = f"sd_generated_{int(time.time())}.png"
                    filepath = os.path.join("generated", filename)
                    with open(filepath, "wb") as f:
                        f.write(image_data)
                    return f"/generated/{filename}"
            else:
                print(f"Stable Diffusion API错误: {response.text}")
                return None
                
        except Exception as e:
            print(f"Stable Diffusion生成失败: {e}")
            return None

class AdvancedImageProcessor:
    """高级图片处理器"""
    
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
                
            # 如果有参考图，分析其样式
            style_analysis = None
            if reference_path and os.path.exists(reference_path):
                style_analysis = self._analyze_reference_style(reference_path)
                
            # 应用样式配置
            if style_config:
                self._apply_style_config(template, style_config)
                
            # 增强图片质量
            template = self._enhance_image_quality(template)
            
            # 添加文字内容
            template = self._add_advanced_text(template, text_data, style_analysis)
            
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
    
    def _analyze_reference_style(self, reference_path: str) -> dict:
        """分析参考图样式"""
        try:
            ref_img = Image.open(reference_path)
            
            # 分析主要颜色
            colors = self._extract_dominant_colors(ref_img)
            
            # 分析布局（简化版）
            layout = self._analyze_layout(ref_img)
            
            return {
                'colors': colors,
                'layout': layout,
                'size': ref_img.size
            }
            
        except Exception as e:
            print(f"分析参考图失败: {e}")
            return {}
    
    def _extract_dominant_colors(self, image: Image.Image, num_colors: int = 5) -> list:
        """提取主要颜色"""
        try:
            # 缩小图片以提高处理速度
            small_img = image.resize((150, 150))
            
            # 转换为RGB
            if small_img.mode != 'RGB':
                small_img = small_img.convert('RGB')
                
            # 量化颜色
            quantized = small_img.quantize(colors=num_colors)
            palette = quantized.getpalette()
            
            # 提取主要颜色
            colors = []
            for i in range(num_colors):
                r = palette[i*3]
                g = palette[i*3+1] 
                b = palette[i*3+2]
                colors.append((r, g, b))
                
            return colors
            
        except Exception as e:
            print(f"提取颜色失败: {e}")
            return [(255, 255, 255)]  # 默认白色
    
    def _analyze_layout(self, image: Image.Image) -> dict:
        """分析布局"""
        width, height = image.size
        
        return {
            'width': width,
            'height': height,
            'aspect_ratio': width / height,
            'title_area': (0, 0, width, height // 3),
            'content_area': (0, height // 3, width, height * 2 // 3),
            'footer_area': (0, height * 2 // 3, width, height)
        }
    
    def _enhance_image_quality(self, image: Image.Image) -> Image.Image:
        """增强图片质量"""
        # 提高对比度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        # 提高饱和度
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.1)
        
        # 轻微锐化
        image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=2))
        
        return image
    
    def _add_advanced_text(self, image: Image.Image, text_data: dict, 
                          style_analysis: dict = None) -> Image.Image:
        """添加高级文字效果"""
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # 确定颜色方案
        if style_analysis and 'colors' in style_analysis:
            colors = style_analysis['colors']
            title_color = colors[0] if colors else (255, 0, 0)
            subtitle_color = colors[1] if len(colors) > 1 else (0, 100, 200)
        else:
            title_color = (255, 68, 68)  # 红色
            subtitle_color = (46, 134, 171)  # 蓝色
        
        # 加载字体
        fonts = self._load_fonts()
        
        # 绘制主标题（带阴影效果）
        title = text_data.get('main_title', '')
        if title:
            title_font = fonts['title']
            
            # 计算位置
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (width - title_width) // 2
            title_y = height // 4
            
            # 绘制阴影
            shadow_offset = 3
            draw.text((title_x + shadow_offset, title_y + shadow_offset), 
                     title, fill=(0, 0, 0, 128), font=title_font)
            
            # 绘制主文字
            draw.text((title_x, title_y), title, fill=title_color, font=title_font)
        
        # 绘制副标题（带背景）
        subtitle = text_data.get('subtitle', '')
        if subtitle:
            subtitle_font = fonts['subtitle']
            subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]
            
            subtitle_x = (width - subtitle_width) // 2
            subtitle_y = title_y + 80
            
            # 绘制背景框
            padding = 10
            draw.rounded_rectangle([
                subtitle_x - padding, subtitle_y - padding,
                subtitle_x + subtitle_width + padding, subtitle_y + subtitle_height + padding
            ], radius=8, fill=(255, 255, 255, 200))
            
            # 绘制文字
            draw.text((subtitle_x, subtitle_y), subtitle, fill=subtitle_color, font=subtitle_font)
        
        # 绘制关键点（美化版）
        key_points = text_data.get('key_points', [])
        if key_points:
            point_font = fonts['content']
            start_y = subtitle_y + 100
            
            for i, point in enumerate(key_points[:3]):
                point_y = start_y + i * 45
                
                # 绘制项目符号
                draw.ellipse([30, point_y + 5, 45, point_y + 20], fill=subtitle_color)
                
                # 绘制文字
                draw.text((60, point_y), f"{point}", fill=(51, 51, 51), font=point_font)
        
        return image
    
    def _add_decorative_elements(self, image: Image.Image, text_data: dict) -> Image.Image:
        """添加装饰元素"""
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # 添加边框装饰
        border_color = (102, 126, 234, 100)
        border_width = 5
        
        # 顶部装饰线
        draw.rectangle([0, 0, width, border_width], fill=border_color)
        
        # 底部装饰线
        draw.rectangle([0, height - border_width, width, height], fill=border_color)
        
        # 添加角落装饰
        corner_size = 30
        for corner in [(0, 0), (width - corner_size, 0), 
                      (0, height - corner_size), (width - corner_size, height - corner_size)]:
            draw.rectangle([corner[0], corner[1], 
                          corner[0] + corner_size, corner[1] + corner_size], 
                         fill=(255, 255, 255, 50))
        
        return image
    
    def _final_optimization(self, image: Image.Image) -> Image.Image:
        """最终优化"""
        # 轻微模糊处理以平滑边缘
        image = image.filter(ImageFilter.SMOOTH_MORE)
        
        # 最终对比度调整
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.05)
        
        return image
    
    def _load_fonts(self) -> dict:
        """加载字体"""
        fonts = {}
        font_paths = [
            "static/fonts/PingFang-Bold.ttf",
            "static/fonts/PingFang-Regular.ttf",
            "/System/Library/Fonts/PingFang.ttc",
            "/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/msyh.ttc"
        ]
        
        for size_name, size in self.default_fonts.items():
            font_loaded = False
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        fonts[size_name] = ImageFont.truetype(font_path, size)
                        font_loaded = True
                        break
                except:
                    continue
            
            if not font_loaded:
                try:
                    fonts[size_name] = ImageFont.load_default()
                except:
                    fonts[size_name] = ImageFont.load_default()
        
        return fonts
    
    def _apply_style_config(self, image: Image.Image, config: dict):
        """应用样式配置"""
        if 'brightness' in config:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(config['brightness'])
        
        if 'contrast' in config:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(config['contrast'])
        
        return image