# 配置文件
import os
from typing import Dict, List

# AI模型配置
AI_MODELS = {
    "openai": {
        "dalle-3": {
            "name": "DALL-E 3",
            "max_resolution": "1024x1792",
            "supports_text": True
        },
        "dalle-2": {
            "name": "DALL-E 2", 
            "max_resolution": "1024x1024",
            "supports_text": False
        }
    },
    "midjourney": {
        "name": "Midjourney",
        "max_resolution": "1024x1024",
        "supports_text": True
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