import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from typing import Dict, List, Tuple, Optional
import base64
import io

class ImageProcessor:
    """图片处理类，负责模板分析、样式提取、文字渲染等功能"""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
    
    def analyze_template(self, template_image: Image.Image, reference_image: Image.Image = None) -> Dict:
        """
        分析模板图片的布局和样式
        
        Args:
            template_image: 模板图片
            reference_image: 参考成品图片（可选）
            
        Returns:
            包含布局信息的字典
        """
        # 转换为numpy数组进行分析
        template_array = np.array(template_image)
        
        # 基础信息
        height, width = template_array.shape[:2]
        analysis_result = {
            "width": width,
            "height": height,
            "aspect_ratio": width / height,
            "text_regions": [],
            "color_palette": [],
            "layout_zones": {}
        }
        
        # 检测可能的文字区域
        text_regions = self._detect_text_regions(template_array)
        analysis_result["text_regions"] = text_regions
        
        # 提取主要颜色
        color_palette = self._extract_color_palette(template_array)
        analysis_result["color_palette"] = color_palette
        
        # 分析布局区域
        layout_zones = self._analyze_layout_zones(template_array)
        analysis_result["layout_zones"] = layout_zones
        
        # 如果有参考图片，进行样式匹配
        if reference_image:
            style_info = self._extract_style_from_reference(reference_image)
            analysis_result["reference_style"] = style_info
        
        return analysis_result
    
    def _detect_text_regions(self, image_array: np.ndarray) -> List[Dict]:
        """检测图片中可能的文字区域"""
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        
        # 使用形态学操作检测文字区域
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        grad = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
        
        # 二值化
        _, binary = cv2.threshold(grad, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 连接组件分析
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))
        connected = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 查找轮廓
        contours, _ = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # 过滤太小的区域
            if w > 50 and h > 20:
                text_regions.append({
                    "x": int(x),
                    "y": int(y), 
                    "width": int(w),
                    "height": int(h),
                    "area": w * h,
                    "aspect_ratio": w / h
                })
        
        # 按面积排序
        text_regions.sort(key=lambda x: x["area"], reverse=True)
        
        return text_regions[:5]  # 返回最大的5个区域
    
    def _extract_color_palette(self, image_array: np.ndarray, n_colors: int = 8) -> List[str]:
        """提取图片的主要颜色"""
        # 重塑数组
        data = image_array.reshape((-1, 3))
        data = np.float32(data)
        
        # 使用K-means聚类
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(data, n_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # 转换为十六进制颜色
        colors = []
        for center in centers:
            rgb = [int(c) for c in center]
            hex_color = "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
            colors.append(hex_color)
        
        return colors
    
    def _analyze_layout_zones(self, image_array: np.ndarray) -> Dict:
        """分析图片的布局区域"""
        height, width = image_array.shape[:2]
        
        # 定义标准布局区域
        zones = {
            "header": {
                "x": 0, "y": 0, 
                "width": width, "height": height // 4,
                "purpose": "标题区域"
            },
            "main": {
                "x": 0, "y": height // 4,
                "width": width, "height": height // 2,
                "purpose": "主要内容区域"
            },
            "footer": {
                "x": 0, "y": 3 * height // 4,
                "width": width, "height": height // 4,
                "purpose": "底部信息区域"
            }
        }
        
        return zones
    
    def _extract_style_from_reference(self, reference_image: Image.Image) -> Dict:
        """从参考图片中提取样式信息"""
        # 这里应该使用OCR技术提取文字样式
        # 简化版本，返回基础样式信息
        return {
            "title_style": {
                "color": "#FF6B35",
                "size": 36,
                "weight": "bold",
                "position": "top_center"
            },
            "subtitle_style": {
                "color": "#333333",
                "size": 24,
                "weight": "normal",
                "position": "center"
            },
            "highlight_color": "#FF6B35",
            "background_style": "gradient"
        }
    
    def render_text_on_template(self, template: Image.Image, texts: Dict, style_config: Dict) -> Image.Image:
        """
        在模板上渲染文字
        
        Args:
            template: 模板图片
            texts: 文字内容字典
            style_config: 样式配置
            
        Returns:
            渲染后的图片
        """
        # 创建副本
        result_image = template.copy()
        draw = ImageDraw.Draw(result_image)
        
        width, height = result_image.size
        
        # 渲染标题
        if "title" in texts:
            title_style = style_config.get("title", {})
            font_size = title_style.get("size", 36)
            font_color = title_style.get("color", "#FF6B35")
            
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # 计算文字位置（居中）
            text = texts["title"]
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = height // 6  # 标题放在上方1/6处
            
            # 添加文字阴影效果
            shadow_offset = 2
            draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill="#000000")
            draw.text((x, y), text, font=font, fill=font_color)
        
        # 渲染副标题
        if "subtitle" in texts:
            subtitle_style = style_config.get("subtitle", {})
            font_size = subtitle_style.get("size", 24)
            font_color = subtitle_style.get("color", "#333333")
            
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            text = texts["subtitle"]
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            
            x = (width - text_width) // 2
            y = height // 2  # 副标题放在中间
            
            draw.text((x, y), text, font=font, fill=font_color)
        
        # 渲染卖点列表
        if "selling_points" in texts and isinstance(texts["selling_points"], list):
            point_style = style_config.get("content", {})
            font_size = point_style.get("size", 18)
            font_color = point_style.get("color", "#666666")
            
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            y_start = 2 * height // 3
            for i, point in enumerate(texts["selling_points"][:3]):  # 最多显示3个卖点
                text = f"• {point}"
                x = width // 10
                y = y_start + i * (font_size + 10)
                
                draw.text((x, y), text, font=font, fill=font_color)
        
        return result_image
    
    def apply_filters_and_effects(self, image: Image.Image, effects: Dict) -> Image.Image:
        """应用滤镜和视觉效果"""
        result = image.copy()
        
        # 亮度调整
        if "brightness" in effects:
            enhancer = ImageEnhance.Brightness(result)
            result = enhancer.enhance(effects["brightness"])
        
        # 对比度调整
        if "contrast" in effects:
            enhancer = ImageEnhance.Contrast(result)
            result = enhancer.enhance(effects["contrast"])
        
        # 饱和度调整
        if "saturation" in effects:
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(effects["saturation"])
        
        # 锐度调整
        if "sharpness" in effects:
            enhancer = ImageEnhance.Sharpness(result)
            result = enhancer.enhance(effects["sharpness"])
        
        return result
    
    def image_to_base64(self, image: Image.Image) -> str:
        """将PIL图片转换为base64字符串"""
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    
    def base64_to_image(self, base64_str: str) -> Image.Image:
        """将base64字符串转换为PIL图片"""
        img_data = base64.b64decode(base64_str)
        img = Image.open(io.BytesIO(img_data))
        return img