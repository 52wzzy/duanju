import re
import jieba
from typing import List, Dict, Tuple
from config import FORBIDDEN_WORDS

class TextProcessor:
    """文本处理类，负责违禁词检测、关键词提取等功能"""
    
    def __init__(self):
        self.forbidden_words = set(FORBIDDEN_WORDS)
        # 初始化jieba分词
        jieba.initialize()
    
    def check_forbidden_words(self, text: str) -> Dict[str, List[str]]:
        """
        检测文本中的违禁词
        
        Args:
            text: 待检测的文本
            
        Returns:
            包含违禁词信息的字典
        """
        found_words = []
        text_lower = text.lower()
        
        for word in self.forbidden_words:
            if word.lower() in text_lower:
                found_words.append(word)
        
        return {
            "has_forbidden": len(found_words) > 0,
            "forbidden_words": found_words,
            "suggestion": self._get_replacement_suggestions(found_words)
        }
    
    def _get_replacement_suggestions(self, forbidden_words: List[str]) -> Dict[str, str]:
        """为违禁词提供替换建议"""
        suggestions = {
            "最好": "优质",
            "最佳": "优秀", 
            "第一": "领先",
            "唯一": "独特",
            "包治": "改善",
            "根治": "缓解",
            "100%有效": "效果显著",
            "绝对": "相对",
            "保证": "力求",
            "限时": "特惠",
            "秒杀": "优惠",
            "暴富": "增收",
            "躺赚": "收益"
        }
        
        result = {}
        for word in forbidden_words:
            if word in suggestions:
                result[word] = suggestions[word]
            else:
                result[word] = "请修改此词汇"
        
        return result
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        从文本中提取关键词
        
        Args:
            text: 输入文本
            top_k: 返回前k个关键词
            
        Returns:
            关键词列表
        """
        # 使用jieba进行分词
        words = jieba.cut(text)
        
        # 过滤停用词和标点符号
        stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', 
            '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
            '你', '会', '着', '没有', '看', '好', '自己', '这', '那',
            '，', '。', '！', '？', '；', '：', '"', '"', ''', '''
        }
        
        filtered_words = [word for word in words 
                         if len(word) > 1 and word not in stop_words]
        
        # 统计词频
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_words[:top_k]]
    
    def generate_title_variants(self, original_title: str) -> List[str]:
        """
        根据原标题生成多个变体，用于主图设计
        
        Args:
            original_title: 原始标题
            
        Returns:
            标题变体列表
        """
        variants = [original_title]
        
        # 提取关键词
        keywords = self.extract_keywords(original_title, 3)
        
        if len(keywords) >= 2:
            # 生成简化版本
            simplified = " + ".join(keywords[:2])
            variants.append(simplified)
            
            # 生成问号版本
            question = f"如何{keywords[0]}？"
            variants.append(question)
            
            # 生成数字版本
            numbered = f"3步掌握{keywords[0]}"
            variants.append(numbered)
        
        return variants
    
    def optimize_for_image_text(self, text: str, max_length: int = 20) -> str:
        """
        优化文本用于图片显示
        
        Args:
            text: 原始文本
            max_length: 最大长度
            
        Returns:
            优化后的文本
        """
        # 移除违禁词
        check_result = self.check_forbidden_words(text)
        if check_result["has_forbidden"]:
            for word, replacement in check_result["suggestion"].items():
                text = text.replace(word, replacement)
        
        # 控制长度
        if len(text) > max_length:
            # 保留关键部分
            keywords = self.extract_keywords(text, 2)
            if keywords:
                text = " ".join(keywords[:2])
            else:
                text = text[:max_length] + "..."
        
        return text
    
    def extract_selling_points(self, content: str) -> List[str]:
        """
        从文章内容中提取卖点
        
        Args:
            content: 文章内容
            
        Returns:
            卖点列表
        """
        selling_points = []
        
        # 查找包含数字的句子（通常是数据支撑）
        number_pattern = r'[0-9]+[%万千百十元天小时分钟]'
        sentences = re.split(r'[。！？\n]', content)
        
        for sentence in sentences:
            if re.search(number_pattern, sentence) and len(sentence) < 50:
                selling_points.append(sentence.strip())
        
        # 查找包含效果词汇的句子
        effect_words = ['提升', '增加', '减少', '改善', '优化', '节省', '获得']
        for sentence in sentences:
            for word in effect_words:
                if word in sentence and len(sentence) < 50:
                    selling_points.append(sentence.strip())
                    break
        
        # 去重并限制数量
        selling_points = list(set(selling_points))[:5]
        
        return selling_points