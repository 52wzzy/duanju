import openai
import requests
import json
import base64
from typing import Dict, List, Optional
from PIL import Image
import io
import time
import hashlib
import hmac
from urllib.parse import urlencode
from config import AI_MODELS

class AIGenerator:
    """AI生成器类，负责调用各种AI API生成图片和优化文本"""
    
    def __init__(self):
        self.openai_client = None
        self.supported_models = AI_MODELS
        self.api_keys = {}
        self.current_model = None
    
    def set_api_key(self, provider: str, api_key: str, **kwargs):
        """设置API密钥"""
        self.api_keys[provider] = {
            "api_key": api_key,
            **kwargs
        }
        
        if provider == "openai":
            openai.api_key = api_key
            self.openai_client = openai.OpenAI(api_key=api_key)
    
    def set_current_model(self, provider: str, model_name: str):
        """设置当前使用的模型"""
        if provider in self.supported_models and model_name in self.supported_models[provider]:
            self.current_model = {
                "provider": provider,
                "model": model_name,
                "config": self.supported_models[provider][model_name]
            }
            return True
        return False
    
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
    
    def generate_image_with_openai(self, prompt: str, model: str = "dall-e-3", size: str = "1024x1024", quality: str = "standard") -> Optional[Image.Image]:
        """使用OpenAI DALL-E生成图片"""
        if not self.openai_client:
            raise ValueError("请先设置OpenAI API密钥")
        
        try:
            response = self.openai_client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )
            
            image_url = response.data[0].url
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            
            image = Image.open(io.BytesIO(img_response.content))
            return image
            
        except Exception as e:
            print(f"OpenAI生成图片失败: {str(e)}")
            return None
    
    def generate_image_with_zhipu(self, prompt: str) -> Optional[Image.Image]:
        """使用智谱AI CogView-3生成图片"""
        if "zhipu" not in self.api_keys:
            raise ValueError("请先设置智谱AI API密钥")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_keys['zhipu']['api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "cogview-3",
                "prompt": prompt,
                "size": "1024x1024"
            }
            
            response = requests.post(
                "https://open.bigmodel.cn/api/paas/v4/images/generations",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if "data" in result and len(result["data"]) > 0:
                    image_url = result["data"][0]["url"]
                    img_response = requests.get(image_url)
                    img_response.raise_for_status()
                    
                    image = Image.open(io.BytesIO(img_response.content))
                    return image
            
            print(f"智谱AI生成失败: {response.text}")
            return None
            
        except Exception as e:
            print(f"智谱AI生成图片失败: {str(e)}")
            return None
    
    def generate_image_with_baidu(self, prompt: str) -> Optional[Image.Image]:
        """使用百度文心一格生成图片"""
        if "baidu" not in self.api_keys:
            raise ValueError("请先设置百度API密钥")
        
        try:
            # 获取access_token
            access_token = self._get_baidu_access_token()
            if not access_token:
                return None
            
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "prompt": prompt,
                "width": 1024,
                "height": 1024,
                "image_num": 1
            }
            
            url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/text2image/sd_xl?access_token={access_token}"
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if "data" in result and len(result["data"]) > 0:
                    # 百度返回base64编码的图片
                    image_base64 = result["data"][0]["b64_image"]
                    image_data = base64.b64decode(image_base64)
                    image = Image.open(io.BytesIO(image_data))
                    return image
            
            print(f"百度文心一格生成失败: {response.text}")
            return None
            
        except Exception as e:
            print(f"百度文心一格生成图片失败: {str(e)}")
            return None
    
    def generate_image_with_alibaba(self, prompt: str) -> Optional[Image.Image]:
        """使用阿里云通义万相生成图片"""
        if "alibaba" not in self.api_keys:
            raise ValueError("请先设置阿里云API密钥")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_keys['alibaba']['api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "wanx-v1",
                "input": {
                    "prompt": prompt
                },
                "parameters": {
                    "style": "<auto>",
                    "size": "1024*1024",
                    "n": 1
                }
            }
            
            response = requests.post(
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if "output" in result and "results" in result["output"]:
                    image_url = result["output"]["results"][0]["url"]
                    img_response = requests.get(image_url)
                    img_response.raise_for_status()
                    
                    image = Image.open(io.BytesIO(img_response.content))
                    return image
            
            print(f"阿里云通义万相生成失败: {response.text}")
            return None
            
        except Exception as e:
            print(f"阿里云通义万相生成图片失败: {str(e)}")
            return None
    
    def generate_image_with_tencent(self, prompt: str) -> Optional[Image.Image]:
        """使用腾讯云混元DiT生成图片"""
        if "tencent" not in self.api_keys:
            raise ValueError("请先设置腾讯云API密钥")
        
        try:
            # 腾讯云API需要签名认证
            secret_id = self.api_keys['tencent']['secret_id']
            secret_key = self.api_keys['tencent']['secret_key']
            
            # 构建请求参数
            params = {
                "Action": "TextToImage",
                "Version": "2023-09-01",
                "Region": "ap-beijing",
                "Prompt": prompt,
                "Resolution": "1024:1024",
                "Num": 1
            }
            
            # 生成签名
            signature = self._generate_tencent_signature(params, secret_key)
            
            headers = {
                "Authorization": signature,
                "Content-Type": "application/json; charset=utf-8",
                "Host": "hunyuan.tencentcloudapi.com",
                "X-TC-Action": "TextToImage",
                "X-TC-Version": "2023-09-01",
                "X-TC-Region": "ap-beijing"
            }
            
            response = requests.post(
                "https://hunyuan.tencentcloudapi.com",
                headers=headers,
                json=params,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if "Response" in result and "ResultImage" in result["Response"]:
                    # 腾讯云返回base64编码的图片
                    image_base64 = result["Response"]["ResultImage"]
                    image_data = base64.b64decode(image_base64)
                    image = Image.open(io.BytesIO(image_data))
                    return image
            
            print(f"腾讯云混元DiT生成失败: {response.text}")
            return None
            
        except Exception as e:
            print(f"腾讯云混元DiT生成图片失败: {str(e)}")
            return None
    
    def generate_image_with_iflytek(self, prompt: str) -> Optional[Image.Image]:
        """使用科大讯飞星火绘画生成图片"""
        if "iflytek" not in self.api_keys:
            raise ValueError("请先设置科大讯飞API密钥")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_keys['iflytek']['api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "spark-image-v1",
                "prompt": prompt,
                "size": "1024x1024",
                "quality": "standard",
                "n": 1
            }
            
            response = requests.post(
                "https://spark-api-open.xf-yun.com/v1/images/generations",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if "data" in result and len(result["data"]) > 0:
                    image_url = result["data"][0]["url"]
                    img_response = requests.get(image_url)
                    img_response.raise_for_status()
                    
                    image = Image.open(io.BytesIO(img_response.content))
                    return image
            
            print(f"科大讯飞星火绘画生成失败: {response.text}")
            return None
            
        except Exception as e:
            print(f"科大讯飞星火绘画生成图片失败: {str(e)}")
            return None
    
    def generate_image_with_stable_diffusion(self, prompt: str) -> Optional[Image.Image]:
        """使用本地Stable Diffusion生成图片"""
        try:
            data = {
                "prompt": prompt,
                "negative_prompt": "low quality, blurry, ugly",
                "width": 1024,
                "height": 1024,
                "steps": 20,
                "cfg_scale": 7,
                "sampler_name": "DPM++ 2M Karras"
            }
            
            response = requests.post(
                "http://localhost:7860/api/v1/txt2img",
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                if "images" in result and len(result["images"]) > 0:
                    # Stable Diffusion返回base64编码的图片
                    image_base64 = result["images"][0]
                    image_data = base64.b64decode(image_base64)
                    image = Image.open(io.BytesIO(image_data))
                    return image
            
            print(f"Stable Diffusion生成失败: {response.text}")
            return None
            
        except Exception as e:
            print(f"Stable Diffusion生成图片失败: {str(e)}")
            return None
    
    def generate_image(self, prompt: str, **kwargs) -> Optional[Image.Image]:
        """统一的图片生成接口"""
        if not self.current_model:
            raise ValueError("请先选择AI模型")
        
        provider = self.current_model["provider"]
        model_name = self.current_model["model"]
        
        # 根据提供商调用对应的生成方法
        if provider == "openai":
            return self.generate_image_with_openai(prompt, model_name, **kwargs)
        elif provider == "智谱AI":
            return self.generate_image_with_zhipu(prompt)
        elif provider == "百度":
            return self.generate_image_with_baidu(prompt)
        elif provider == "阿里云":
            return self.generate_image_with_alibaba(prompt)
        elif provider == "腾讯云":
            return self.generate_image_with_tencent(prompt)
        elif provider == "科大讯飞":
            return self.generate_image_with_iflytek(prompt)
        elif provider == "Stability AI":
            return self.generate_image_with_stable_diffusion(prompt)
        else:
            raise ValueError(f"不支持的提供商: {provider}")
    
    def _get_baidu_access_token(self) -> Optional[str]:
        """获取百度API的access_token"""
        try:
            api_key = self.api_keys['baidu']['api_key']
            secret_key = self.api_keys['baidu']['secret_key']
            
            url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
            
            response = requests.post(url)
            if response.status_code == 200:
                result = response.json()
                return result.get("access_token")
            
            print(f"获取百度access_token失败: {response.text}")
            return None
            
        except Exception as e:
            print(f"获取百度access_token异常: {str(e)}")
            return None
    
    def _generate_tencent_signature(self, params: Dict, secret_key: str) -> str:
        """生成腾讯云API签名"""
        # 这里简化了签名过程，实际使用时需要完整的腾讯云签名算法
        # 建议使用腾讯云官方SDK
        timestamp = str(int(time.time()))
        nonce = str(int(time.time() * 1000))
        
        # 构建待签名字符串
        sorted_params = sorted(params.items())
        query_string = urlencode(sorted_params)
        
        string_to_sign = f"POST\nhunyuan.tencentcloudapi.com\n/\n{query_string}"
        
        # 计算签名
        signature = base64.b64encode(
            hmac.new(secret_key.encode(), string_to_sign.encode(), hashlib.sha1).digest()
        ).decode()
        
        return f"TC3-HMAC-SHA256 Credential={self.api_keys['tencent']['secret_id']}/date/service/tc3_request, SignedHeaders=content-type;host, Signature={signature}"
    
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
            image = self.generate_image(prompt)
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
    
    def get_model_info(self, provider: str, model_name: str) -> Dict:
        """获取模型信息"""
        if provider in self.supported_models and model_name in self.supported_models[provider]:
            return self.supported_models[provider][model_name]
        return {}
    
    def get_available_models(self) -> Dict:
        """获取所有可用的模型列表"""
        return self.supported_models