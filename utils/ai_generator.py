import openai
import requests
import json
import base64
from typing import Dict, List, Optional
from PIL import Image
import io
from config import AI_MODELS

class AIGenerator:
    """AI生成器类，负责调用各种AI API生成图片和优化文本"""
    
    def __init__(self):
        self.openai_client = None
        self.supported_models = AI_MODELS
    
    def set_openai_key(self, api_key: str):
        """设置OpenAI API密钥"""
        openai.api_key = api_key
        self.openai_client = openai.OpenAI(api_key=api_key)
    
    def generate_image_prompt(self, article_title: str, content: str, style_preferences: Dict) -> str:
        """
        根据文章信息生成AI绘图提示词
        
        Args:
            article_title: 文章标题
            content: 文章内容
            style_preferences: 样式偏好
            
        Returns:
            优化后的提示词
        """
        # 提取关键词
        from utils.text_processor import TextProcessor
        processor = TextProcessor()
        keywords = processor.extract_keywords(content, 5)
        
        # 构建基础提示词
        base_prompt = f"Create a professional e-commerce product image for '{article_title}'"
        
        # 添加关键元素
        elements = []
        if keywords:
            elements.append(f"featuring {', '.join(keywords[:3])}")
        
        # 添加样式要求
        style_requirements = [
            "modern design",
            "clean layout", 
            "attractive colors",
            "professional typography",
            "high quality",
            "commercial style"
        ]
        
        # 根据样式偏好调整
        if style_preferences.get("color_scheme"):
            style_requirements.append(f"color scheme: {style_preferences['color_scheme']}")
        
        if style_preferences.get("style"):
            style_requirements.append(f"style: {style_preferences['style']}")
        
        # 组合提示词
        full_prompt = f"{base_prompt}, {', '.join(elements)}, {', '.join(style_requirements)}"
        
        # 添加技术要求
        technical_requirements = [
            "8K resolution",
            "professional photography",
            "studio lighting",
            "commercial product photography style"
        ]
        
        full_prompt += f", {', '.join(technical_requirements)}"
        
        return full_prompt
    
    def generate_image_with_dalle(self, prompt: str, size: str = "1024x1024", quality: str = "standard") -> Optional[Image.Image]:
        """
        使用DALL-E生成图片
        
        Args:
            prompt: 提示词
            size: 图片尺寸
            quality: 图片质量
            
        Returns:
            生成的图片或None
        """
        if not self.openai_client:
            raise ValueError("请先设置OpenAI API密钥")
        
        try:
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )
            
            # 获取图片URL
            image_url = response.data[0].url
            
            # 下载图片
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            
            # 转换为PIL Image
            image = Image.open(io.BytesIO(img_response.content))
            return image
            
        except Exception as e:
            print(f"DALL-E生成图片失败: {str(e)}")
            return None
    
    def optimize_text_with_gpt(self, text: str, optimization_type: str = "title") -> str:
        """
        使用GPT优化文本
        
        Args:
            text: 原始文本
            optimization_type: 优化类型 (title, description, selling_point)
            
        Returns:
            优化后的文本
        """
        if not self.openai_client:
            raise ValueError("请先设置OpenAI API密钥")
        
        prompts = {
            "title": "将以下标题优化为更吸引人的电商产品标题，要求简洁有力，突出卖点，避免违禁词：",
            "description": "将以下描述优化为更具吸引力的产品描述，要求突出优势，避免夸大宣传：",
            "selling_point": "将以下内容提炼为3-5个核心卖点，每个卖点不超过15字："
        }
        
        system_prompt = prompts.get(optimization_type, prompts["title"])
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的电商文案优化专家，擅长创建吸引人且合规的商品文案。"},
                    {"role": "user", "content": f"{system_prompt}\n\n{text}"}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"GPT文本优化失败: {str(e)}")
            return text  # 失败时返回原文本
    
    def generate_detail_page_layout(self, article_content: str) -> Dict:
        """
        生成详情页布局建议
        
        Args:
            article_content: 文章内容
            
        Returns:
            详情页布局配置
        """
        from utils.text_processor import TextProcessor
        processor = TextProcessor()
        
        # 提取关键信息
        keywords = processor.extract_keywords(article_content, 8)
        selling_points = processor.extract_selling_points(article_content)
        
        # 生成布局结构
        layout = {
            "sections": [
                {
                    "type": "hero",
                    "title": "产品亮点",
                    "content": selling_points[:2] if selling_points else ["优质产品", "专业服务"],
                    "style": "large_text_with_background"
                },
                {
                    "type": "features",
                    "title": "核心特色", 
                    "content": selling_points[2:5] if len(selling_points) > 2 else keywords[:3],
                    "style": "icon_with_text"
                },
                {
                    "type": "benefits",
                    "title": "用户收益",
                    "content": self._generate_benefits_from_keywords(keywords),
                    "style": "numbered_list"
                },
                {
                    "type": "process",
                    "title": "使用流程",
                    "content": ["了解产品", "选择方案", "开始使用", "获得收益"],
                    "style": "step_by_step"
                },
                {
                    "type": "guarantee",
                    "title": "品质承诺",
                    "content": ["专业团队", "优质服务", "持续支持"],
                    "style": "badge_style"
                }
            ],
            "color_scheme": {
                "primary": "#FF6B35",
                "secondary": "#333333",
                "accent": "#666666",
                "background": "#FFFFFF"
            },
            "font_config": {
                "title": {"size": 28, "weight": "bold"},
                "subtitle": {"size": 22, "weight": "normal"},
                "content": {"size": 16, "weight": "normal"}
            }
        }
        
        return layout
    
    def _generate_benefits_from_keywords(self, keywords: List[str]) -> List[str]:
        """根据关键词生成用户收益点"""
        benefit_templates = [
            "提升{}效率",
            "掌握{}技巧", 
            "获得{}优势",
            "实现{}目标",
            "学会{}方法"
        ]
        
        benefits = []
        for i, keyword in enumerate(keywords[:5]):
            template = benefit_templates[i % len(benefit_templates)]
            benefits.append(template.format(keyword))
        
        return benefits
    
    def create_detail_page_images(self, layout: Dict, base_prompt: str) -> Dict[str, Image.Image]:
        """
        根据详情页布局生成配套图片
        
        Args:
            layout: 详情页布局配置
            base_prompt: 基础提示词
            
        Returns:
            各个部分的图片字典
        """
        images = {}
        
        for section in layout["sections"]:
            section_type = section["type"]
            section_title = section["title"]
            
            # 为每个部分生成特定的提示词
            section_prompts = {
                "hero": f"{base_prompt}, hero section banner, large title design, professional layout",
                "features": f"{base_prompt}, feature highlights, icon-based design, clean layout", 
                "benefits": f"{base_prompt}, benefits section, numbered list design, modern style",
                "process": f"{base_prompt}, step-by-step process, infographic style, clear flow",
                "guarantee": f"{base_prompt}, quality guarantee badges, trust symbols, professional design"
            }
            
            prompt = section_prompts.get(section_type, base_prompt)
            
            # 生成图片
            image = self.generate_image_with_dalle(prompt, size="1024x1024")
            if image:
                images[section_type] = image
        
        return images
    
    def batch_optimize_texts(self, texts: Dict[str, str]) -> Dict[str, str]:
        """
        批量优化文本内容
        
        Args:
            texts: 文本字典
            
        Returns:
            优化后的文本字典
        """
        optimized = {}
        
        for key, text in texts.items():
            if key == "title":
                optimized[key] = self.optimize_text_with_gpt(text, "title")
            elif key == "description":
                optimized[key] = self.optimize_text_with_gpt(text, "description")
            elif "selling_point" in key:
                optimized[key] = self.optimize_text_with_gpt(text, "selling_point")
            else:
                optimized[key] = text
        
        return optimized