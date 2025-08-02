# 配置文件
import os
from typing import Dict, List

# AI模型配置
AI_MODELS = {
    # OpenAI模型（付费）
    "openai": {
        "dalle-3": {
            "name": "DALL-E 3",
            "provider": "OpenAI",
            "max_resolution": "1024x1792",
            "supports_text": True,
            "cost": "付费",
            "quality": "极高",
            "speed": "中等",
            "api_endpoint": "https://api.openai.com/v1/images/generations"
        },
        "dalle-2": {
            "name": "DALL-E 2", 
            "provider": "OpenAI",
            "max_resolution": "1024x1024",
            "supports_text": False,
            "cost": "付费",
            "quality": "高",
            "speed": "快",
            "api_endpoint": "https://api.openai.com/v1/images/generations"
        }
    },
    
    # 国内免费模型
    "zhipu": {
        "cogview-3": {
            "name": "CogView-3",
            "provider": "智谱AI",
            "max_resolution": "1024x1024",
            "supports_text": True,
            "cost": "免费额度",
            "quality": "高",
            "speed": "快",
            "api_endpoint": "https://open.bigmodel.cn/api/paas/v4/images/generations",
            "free_quota": "每日100次"
        }
    },
    
    "baidu": {
        "ernie-vilg": {
            "name": "文心一格",
            "provider": "百度",
            "max_resolution": "1024x1024",
            "supports_text": True,
            "cost": "免费额度",
            "quality": "高",
            "speed": "快",
            "api_endpoint": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/text2image",
            "free_quota": "每日50次"
        }
    },
    
    "alibaba": {
        "tongyi-wanxiang": {
            "name": "通义万相",
            "provider": "阿里云",
            "max_resolution": "1024x1024", 
            "supports_text": True,
            "cost": "免费额度",
            "quality": "高",
            "speed": "快",
            "api_endpoint": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis",
            "free_quota": "每月500次"
        }
    },
    
    "tencent": {
        "hunyuan-dit": {
            "name": "混元DiT",
            "provider": "腾讯云",
            "max_resolution": "1024x1024",
            "supports_text": True,
            "cost": "免费额度",
            "quality": "高", 
            "speed": "快",
            "api_endpoint": "https://hunyuan.tencentcloudapi.com",
            "free_quota": "每日100次"
        }
    },
    
    "iflytek": {
        "spark-image": {
            "name": "讯飞星火绘画",
            "provider": "科大讯飞",
            "max_resolution": "1024x1024",
            "supports_text": True,
            "cost": "免费额度",
            "quality": "中等",
            "speed": "快",
            "api_endpoint": "https://spark-api-open.xf-yun.com/v1/images/generations",
            "free_quota": "每日20次"
        }
    },
    
    # 开源模型（需要本地部署或免费API）
    "stable_diffusion": {
        "sd-xl": {
            "name": "Stable Diffusion XL",
            "provider": "Stability AI",
            "max_resolution": "1024x1024",
            "supports_text": True,
            "cost": "免费（本地）",
            "quality": "高",
            "speed": "慢",
            "api_endpoint": "http://localhost:7860/api/v1/txt2img",
            "free_quota": "无限制（本地部署）"
        }
    },
    
    "midjourney": {
        "mj-v6": {
            "name": "Midjourney V6",
            "provider": "Midjourney",
            "max_resolution": "1024x1024",
            "supports_text": True,
            "cost": "付费",
            "quality": "极高",
            "speed": "慢",
            "api_endpoint": "https://api.midjourney.com/v1/imagine",
            "free_quota": "25次试用"
        }
    }
}

# 违禁词列表 - 电商平台常见违禁词
FORBIDDEN_WORDS = [
    # 绝对性词汇
    "最好", "最佳", "最优", "第一", "唯一", "独家", "全球领先", "世界第一",
    "国家级", "最高级", "最低价", "史上最低", "前无古人", "绝无仅有",
    
    # 虚假宣传
    "包治", "根治", "药到病除", "立竿见影", "一次见效", "永久有效",
    "100%有效", "绝对", "肯定", "保证", "承诺", "无效退款",
    
    # 时间限制虚假宣传
    "限时", "秒杀", "今日特价", "最后一天", "仅此一次", "错过不再",
    
    # 功效夸大
    "神奇", "奇迹", "秘方", "祖传", "御用", "宫廷", "太医",
    "名医", "专家推荐", "医生推荐", "权威认证",
    
    # 投资理财相关
    "暴富", "一夜暴富", "轻松赚钱", "躺赚", "日赚", "月入",
    "稳赚不赔", "零风险", "高收益", "包赚", "必赚"
]

# 默认字体配置
DEFAULT_FONT_CONFIG = {
    "title": {
        "size": 36,
        "color": "#FF6B35",
        "weight": "bold",
        "family": "Microsoft YaHei"
    },
    "subtitle": {
        "size": 24,
        "color": "#333333", 
        "weight": "normal",
        "family": "Microsoft YaHei"
    },
    "content": {
        "size": 18,
        "color": "#666666",
        "weight": "normal", 
        "family": "Microsoft YaHei"
    }
}

# 图片尺寸配置
IMAGE_SIZES = {
    "main_image": (800, 800),
    "detail_banner": (750, 1334),
    "thumbnail": (300, 300)
}