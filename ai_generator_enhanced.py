import requests
import base64
import json
import time
import os
import re
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from typing import Dict, Optional, List

class EnhancedAIImageGenerator:
    """增强版AI图片生成器，支持多种国内外模型"""
    
    def __init__(self):
        self.api_configs = {}
        self.supported_models = {
            # 国外模型
            'dalle3': {
                'name': 'DALL-E 3',
                'provider': 'OpenAI',
                'free': False,
                'api_url': 'https://api.openai.com/v1/images/generations',
                'requires': ['api_key']
            },
            'stable_diffusion': {
                'name': 'Stable Diffusion',
                'provider': 'Stability AI',
                'free': False,
                'api_url': 'https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image',
                'requires': ['api_key']
            },
            # 国内免费模型
            'baidu_wenxin': {
                'name': '文心一格',
                'provider': '百度',
                'free': True,
                'api_url': 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/text2image/sd_xl',
                'requires': ['api_key', 'secret_key']
            },
            'ali_tongyi': {
                'name': '通义万相',
                'provider': '阿里云',
                'free': True,
                'api_url': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis',
                'requires': ['api_key']
            },
            'tencent_hunyuan': {
                'name': '混元AI绘画',
                'provider': '腾讯云',
                'free': True,
                'api_url': 'https://hunyuan.tencentcloudapi.com/',
                'requires': ['secret_id', 'secret_key']
            },
            'zhipu_cogview': {
                'name': 'CogView',
                'provider': '智谱AI',
                'free': True,
                'api_url': 'https://open.bigmodel.cn/api/paas/v4/images/generations',
                'requires': ['api_key']
            },
            'minimax_text2image': {
                'name': 'MiniMax文生图',
                'provider': 'MiniMax',
                'free': True,
                'api_url': 'https://api.minimax.chat/v1/text_to_image',
                'requires': ['api_key']
            },
            'yitu_wonder': {
                'name': '奇妙文生图',
                'provider': '依图科技',
                'free': True,
                'api_url': 'https://api.yitutech.com/text2image',
                'requires': ['api_key']
            },
            # 开源免费模型
            'replicate_sdxl': {
                'name': 'SDXL (Replicate)',
                'provider': 'Replicate',
                'free': True,
                'api_url': 'https://api.replicate.com/v1/predictions',
                'requires': ['api_key']
            },
            'huggingface_diffusion': {
                'name': 'Hugging Face Diffusion',
                'provider': 'Hugging Face',
                'free': True,
                'api_url': 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0',
                'requires': ['api_key']
            }
        }
        
    def get_supported_models(self) -> List[Dict]:
        """获取支持的模型列表"""
        return [
            {
                'id': model_id,
                'name': info['name'],
                'provider': info['provider'],
                'free': info['free'],
                'requires': info['requires']
            }
            for model_id, info in self.supported_models.items()
        ]
    
    def set_api_config(self, model_id: str, config: Dict[str, str]):
        """设置API配置"""
        if model_id in self.supported_models:
            self.api_configs[model_id] = config
            return True
        return False
    
    def generate_image_prompt(self, title: str, content: str, style: str = 'commercial') -> str:
        """生成图片提示词"""
        keywords = self._extract_keywords(content)
        
        # 中英文提示词模板
        if style == 'commercial':
            prompt_cn = f"电商主图设计：{title}，专业商务风格，现代简洁布局，吸引人的排版设计"
            prompt_en = f"Professional e-commerce main image for '{title}', modern clean business style, attractive typography, commercial appeal"
            keywords_text = "，".join(keywords[:5]) if keywords else ""
            if keywords_text:
                prompt_cn += f"，关键词：{keywords_text}"
                prompt_en += f", keywords: {', '.join(keywords[:5])}"
        elif style == 'tutorial':
            prompt_cn = f"教程封面图：{title}，教育类设计，清晰易懂，步骤指导风格"
            prompt_en = f"Educational tutorial cover for '{title}', instructional design, clear and easy to understand"
        else:
            prompt_cn = f"创意图片：{title}，专业美观"
            prompt_en = f"Creative image for '{title}', professional and appealing"
            
        return {
            'chinese': prompt_cn,
            'english': prompt_en,
            'keywords': keywords[:5]
        }
    
    def _extract_keywords(self, content: str) -> List[str]:
        """从内容中提取关键词"""
        common_words = ['的', '是', '在', '有', '和', '与', '或', '但', '就', '这', '那', '及', '以', '为', '了', '到', '等']
        words = []
        
        text_words = re.findall(r'[\u4e00-\u9fff]+', content)
        
        for word in text_words:
            if len(word) >= 2 and word not in common_words:
                words.append(word)
                
        return list(set(words))[:10]
    
    def generate_image(self, model_id: str, prompt_data: Dict, **kwargs) -> Optional[str]:
        """生成图片"""
        if model_id not in self.supported_models:
            raise ValueError(f"不支持的模型: {model_id}")
            
        if model_id not in self.api_configs:
            raise ValueError(f"模型 {model_id} 未配置API信息")
        
        config = self.api_configs[model_id]
        
        # 根据不同模型调用相应的生成方法
        try:
            if model_id == 'dalle3':
                return self._generate_dalle3(prompt_data, config, **kwargs)
            elif model_id == 'stable_diffusion':
                return self._generate_stability_ai(prompt_data, config, **kwargs)
            elif model_id == 'baidu_wenxin':
                return self._generate_baidu_wenxin(prompt_data, config, **kwargs)
            elif model_id == 'ali_tongyi':
                return self._generate_ali_tongyi(prompt_data, config, **kwargs)
            elif model_id == 'tencent_hunyuan':
                return self._generate_tencent_hunyuan(prompt_data, config, **kwargs)
            elif model_id == 'zhipu_cogview':
                return self._generate_zhipu_cogview(prompt_data, config, **kwargs)
            elif model_id == 'minimax_text2image':
                return self._generate_minimax(prompt_data, config, **kwargs)
            elif model_id == 'replicate_sdxl':
                return self._generate_replicate_sdxl(prompt_data, config, **kwargs)
            elif model_id == 'huggingface_diffusion':
                return self._generate_huggingface(prompt_data, config, **kwargs)
            else:
                return self._generate_generic(model_id, prompt_data, config, **kwargs)
        except Exception as e:
            print(f"生成图片失败 ({model_id}): {e}")
            return None
    
    def _generate_dalle3(self, prompt_data: Dict, config: Dict, **kwargs) -> Optional[str]:
        """DALL-E 3生成"""
        try:
            import openai
            openai.api_key = config['api_key']
            
            response = openai.Image.create(
                model="dall-e-3",
                prompt=prompt_data['english'],
                size=kwargs.get('size', "1024x1024"),
                quality=kwargs.get('quality', "standard"),
                n=1,
            )
            
            return response.data[0].url
        except Exception as e:
            print(f"DALL-E 3生成失败: {e}")
            return None
    
    def _generate_stability_ai(self, prompt_data: Dict, config: Dict, **kwargs) -> Optional[str]:
        """Stability AI生成"""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}"
        }
        
        body = {
            "text_prompts": [{"text": prompt_data['english'], "weight": 1}],
            "cfg_scale": kwargs.get('cfg_scale', 7),
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": kwargs.get('steps', 30),
        }
        
        response = requests.post(
            self.supported_models['stable_diffusion']['api_url'],
            headers=headers,
            json=body
        )
        
        if response.status_code == 200:
            data = response.json()
            for artifact in data["artifacts"]:
                image_data = base64.b64decode(artifact["base64"])
                filename = f"stability_ai_{int(time.time())}.png"
                filepath = os.path.join("generated", filename)
                with open(filepath, "wb") as f:
                    f.write(image_data)
                return f"/generated/{filename}"
        
        return None
    
    def _generate_baidu_wenxin(self, prompt_data: Dict, config: Dict, **kwargs) -> Optional[str]:
        """百度文心一格生成"""
        # 获取access_token
        token_url = "https://aip.baidubce.com/oauth/2.0/token"
        token_params = {
            "grant_type": "client_credentials",
            "client_id": config['api_key'],
            "client_secret": config['secret_key']
        }
        
        token_response = requests.post(token_url, params=token_params)
        if token_response.status_code != 200:
            return None
            
        access_token = token_response.json().get("access_token")
        if not access_token:
            return None
        
        # 生成图片
        headers = {"Content-Type": "application/json"}
        body = {
            "prompt": prompt_data['chinese'],
            "width": kwargs.get('width', 1024),
            "height": kwargs.get('height', 1024),
            "image_num": 1
        }
        
        url = f"{self.supported_models['baidu_wenxin']['api_url']}?access_token={access_token}"
        response = requests.post(url, headers=headers, json=body)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and data["data"].get("sub_task_result_list"):
                img_url = data["data"]["sub_task_result_list"][0].get("final_image_list", [{}])[0].get("img_url")
                if img_url:
                    return self._download_and_save_image(img_url, "baidu_wenxin")
        
        return None
    
    def _generate_ali_tongyi(self, prompt_data: Dict, config: Dict, **kwargs) -> Optional[str]:
        """阿里通义万相生成"""
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        body = {
            "model": "wanx-v1",
            "input": {
                "prompt": prompt_data['chinese']
            },
            "parameters": {
                "style": kwargs.get('style', '<auto>'),
                "size": kwargs.get('size', '1024*1024'),
                "n": 1
            }
        }
        
        response = requests.post(
            self.supported_models['ali_tongyi']['api_url'],
            headers=headers,
            json=body
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("output") and data["output"].get("results"):
                img_url = data["output"]["results"][0].get("url")
                if img_url:
                    return self._download_and_save_image(img_url, "ali_tongyi")
        
        return None
    
    def _generate_zhipu_cogview(self, prompt_data: Dict, config: Dict, **kwargs) -> Optional[str]:
        """智谱CogView生成"""
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        body = {
            "model": "cogview-3",
            "prompt": prompt_data['chinese'],
            "size": kwargs.get('size', '1024x1024')
        }
        
        response = requests.post(
            self.supported_models['zhipu_cogview']['api_url'],
            headers=headers,
            json=body
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and len(data["data"]) > 0:
                img_url = data["data"][0].get("url")
                if img_url:
                    return self._download_and_save_image(img_url, "zhipu_cogview")
        
        return None
    
    def _generate_minimax(self, prompt_data: Dict, config: Dict, **kwargs) -> Optional[str]:
        """MiniMax生成"""
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        body = {
            "model": "text_to_image_01",
            "prompt": prompt_data['chinese'],
            "image_size": kwargs.get('size', '1024x1024')
        }
        
        response = requests.post(
            self.supported_models['minimax_text2image']['api_url'],
            headers=headers,
            json=body
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and data["data"].get("images"):
                img_url = data["data"]["images"][0].get("url")
                if img_url:
                    return self._download_and_save_image(img_url, "minimax")
        
        return None
    
    def _generate_replicate_sdxl(self, prompt_data: Dict, config: Dict, **kwargs) -> Optional[str]:
        """Replicate SDXL生成"""
        headers = {
            "Authorization": f"Token {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        body = {
            "version": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            "input": {
                "prompt": prompt_data['english'],
                "width": 1024,
                "height": 1024,
                "num_inference_steps": kwargs.get('steps', 25)
            }
        }
        
        response = requests.post(
            self.supported_models['replicate_sdxl']['api_url'],
            headers=headers,
            json=body
        )
        
        if response.status_code == 201:
            data = response.json()
            prediction_url = data.get("urls", {}).get("get")
            
            # 轮询结果
            for _ in range(60):  # 最多等待5分钟
                time.sleep(5)
                result_response = requests.get(prediction_url, headers=headers)
                if result_response.status_code == 200:
                    result_data = result_response.json()
                    if result_data.get("status") == "succeeded":
                        img_url = result_data.get("output", [None])[0]
                        if img_url:
                            return self._download_and_save_image(img_url, "replicate")
                    elif result_data.get("status") == "failed":
                        break
        
        return None
    
    def _generate_huggingface(self, prompt_data: Dict, config: Dict, **kwargs) -> Optional[str]:
        """Hugging Face生成"""
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        body = {
            "inputs": prompt_data['english'],
            "parameters": {
                "num_inference_steps": kwargs.get('steps', 20),
                "guidance_scale": kwargs.get('guidance_scale', 7.5)
            }
        }
        
        response = requests.post(
            self.supported_models['huggingface_diffusion']['api_url'],
            headers=headers,
            json=body
        )
        
        if response.status_code == 200:
            filename = f"huggingface_{int(time.time())}.png"
            filepath = os.path.join("generated", filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            return f"/generated/{filename}"
        
        return None
    
    def _generate_tencent_hunyuan(self, prompt_data: Dict, config: Dict, **kwargs) -> Optional[str]:
        """腾讯混元生成（需要特殊的签名算法）"""
        # 腾讯云API需要复杂的签名过程，这里提供简化版本
        # 实际使用时需要安装腾讯云SDK: pip install tencentcloud-sdk-python
        try:
            from tencentcloud.common import credential
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.common.profile.http_profile import HttpProfile
            from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
            
            cred = credential.Credential(config['secret_id'], config['secret_key'])
            httpProfile = HttpProfile()
            httpProfile.endpoint = "hunyuan.tencentcloudapi.com"
            
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = hunyuan_client.HunyuanClient(cred, "ap-beijing", clientProfile)
            
            req = models.TextToImageProRequest()
            req.Prompt = prompt_data['chinese']
            req.Resolution = kwargs.get('resolution', '1024:1024')
            
            resp = client.TextToImagePro(req)
            if resp.ResultImage:
                filename = f"tencent_hunyuan_{int(time.time())}.png"
                filepath = os.path.join("generated", filename)
                image_data = base64.b64decode(resp.ResultImage)
                with open(filepath, "wb") as f:
                    f.write(image_data)
                return f"/generated/{filename}"
        except ImportError:
            print("腾讯云SDK未安装，请运行: pip install tencentcloud-sdk-python")
        except Exception as e:
            print(f"腾讯混元生成失败: {e}")
        
        return None
    
    def _generate_generic(self, model_id: str, prompt_data: Dict, config: Dict, **kwargs) -> Optional[str]:
        """通用生成方法"""
        model_info = self.supported_models[model_id]
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        body = {
            "prompt": prompt_data.get('chinese', prompt_data.get('english', '')),
            "size": kwargs.get('size', '1024x1024')
        }
        
        response = requests.post(model_info['api_url'], headers=headers, json=body)
        
        if response.status_code == 200:
            data = response.json()
            # 尝试从常见的响应格式中提取图片URL
            img_url = None
            if 'url' in data:
                img_url = data['url']
            elif 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
                img_url = data['data'][0].get('url')
            elif 'images' in data and len(data['images']) > 0:
                img_url = data['images'][0]
            
            if img_url:
                return self._download_and_save_image(img_url, model_id)
        
        return None
    
    def _download_and_save_image(self, img_url: str, model_name: str) -> str:
        """下载并保存图片"""
        try:
            response = requests.get(img_url)
            if response.status_code == 200:
                filename = f"{model_name}_{int(time.time())}.png"
                filepath = os.path.join("generated", filename)
                with open(filepath, "wb") as f:
                    f.write(response.content)
                return f"/generated/{filename}"
        except Exception as e:
            print(f"下载图片失败: {e}")
        
        return img_url  # 如果下载失败，返回原URL

# 为了兼容性，提供别名
AIImageGenerator = EnhancedAIImageGenerator