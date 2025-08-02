from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import re
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import requests
from dotenv import load_dotenv
import time

# 可选依赖
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("警告: opencv-python 未安装，某些高级图像处理功能将被禁用")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("警告: openai 未安装，AI图片生成功能将被禁用")

# 尝试导入AI生成器，优先使用简化版本
try:
    from ai_generator_simple import AIImageGenerator, AdvancedImageProcessor
    AI_MODULES_AVAILABLE = True
    print("使用简化版AI模块")
except ImportError:
    try:
        from ai_generator import AIImageGenerator, AdvancedImageProcessor
        AI_MODULES_AVAILABLE = True
        print("使用完整版AI模块")
    except ImportError:
        AI_MODULES_AVAILABLE = False
        print("警告: AI模块导入失败，将使用基础功能")

load_dotenv()

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'generated'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GENERATED_FOLDER'] = GENERATED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 创建必要的目录
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static/fonts', exist_ok=True)

# 初始化AI生成器和图片处理器（如果可用）
if AI_MODULES_AVAILABLE:
    ai_generator = AIImageGenerator()
    image_processor = AdvancedImageProcessor()
else:
    ai_generator = None
    image_processor = None

# 违禁词列表
FORBIDDEN_WORDS = [
    '暴利', '躺赚', '日赚', '月入', '轻松赚钱', '不劳而获', '一夜暴富',
    '包赚', '稳赚', '零风险', '100%', '保证', '必赚', '秒到账',
    '免费领取', '限时免费', '绝密', '内幕', '独家秘诀', '终身受益'
]

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_forbidden_words(text):
    """检查文本中是否包含违禁词"""
    found_words = []
    for word in FORBIDDEN_WORDS:
        if word in text:
            found_words.append(word)
    return found_words

def replace_forbidden_words(text):
    """替换违禁词为更合适的表达"""
    replacements = {
        '暴利': '高收益',
        '躺赚': '轻松获得收入',
        '日赚': '日收入',
        '月入': '月收入',
        '轻松赚钱': '获得收入',
        '不劳而获': '高效获得',
        '一夜暴富': '快速成功',
        '包赚': '高概率盈利',
        '稳赚': '稳定收益',
        '零风险': '低风险',
        '100%': '高比例',
        '保证': '预期',
        '必赚': '可盈利',
        '秒到账': '快速到账',
        '免费领取': '优惠获得',
        '限时免费': '限时优惠',
        '绝密': '专业',
        '内幕': '专业知识',
        '独家秘诀': '专业方法',
        '终身受益': '长期受益'
    }
    
    for word, replacement in replacements.items():
        text = text.replace(word, replacement)
    return text

def extract_key_points(content):
    """从文章内容中提取关键点"""
    # 简单的关键点提取逻辑
    sentences = re.split(r'[。！？\n]', content)
    key_points = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10 and len(sentence) < 100:
            # 优先选择包含关键词的句子
            keywords = ['方法', '技巧', '秘诀', '经验', '步骤', '策略', '收益', '成功']
            if any(keyword in sentence for keyword in keywords):
                key_points.append(sentence)
    
    return key_points[:5]  # 返回前5个关键点

def generate_main_image_text(title, content):
    """生成主图文字内容"""
    # 处理标题
    clean_title = replace_forbidden_words(title)
    
    # 提取关键点
    key_points = extract_key_points(content)
    
    # 生成吸引人的副标题
    subtitles = [
        "实战经验分享",
        "详细教程指导", 
        "专业方法揭秘",
        "成功案例解析",
        "高效操作指南"
    ]
    
    selected_subtitle = subtitles[len(clean_title) % len(subtitles)]
    
    return {
        'main_title': clean_title,
        'subtitle': selected_subtitle,
        'key_points': key_points
    }

def create_main_image(template_path, text_data, output_path):
    """基于模板创建主图"""
    try:
        # 打开模板图片
        template = Image.open(template_path)
        draw = ImageDraw.Draw(template)
        
        # 设置字体（需要准备字体文件）
        try:
            title_font = ImageFont.truetype("static/fonts/PingFang-Bold.ttf", 48)
            subtitle_font = ImageFont.truetype("static/fonts/PingFang-Regular.ttf", 28)
            point_font = ImageFont.truetype("static/fonts/PingFang-Regular.ttf", 24)
        except:
            # 如果字体文件不存在，使用默认字体
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            point_font = ImageFont.load_default()
        
        # 获取图片尺寸
        width, height = template.size
        
        # 绘制主标题（大号红色字体）
        title_text = text_data['main_title']
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        title_y = height // 4
        draw.text((title_x, title_y), title_text, fill='#FF4444', font=title_font)
        
        # 绘制副标题（中号蓝色字体）
        subtitle_text = text_data['subtitle']
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        subtitle_y = title_y + 80
        draw.text((subtitle_x, subtitle_y), subtitle_text, fill='#2E86AB', font=subtitle_font)
        
        # 绘制关键点（小号黑色字体）
        start_y = subtitle_y + 100
        for i, point in enumerate(text_data['key_points'][:3]):  # 最多显示3个关键点
            point_text = f"• {point}"
            point_y = start_y + i * 40
            draw.text((50, point_y), point_text, fill='#333333', font=point_font)
        
        # 保存图片
        template.save(output_path)
        return True
    except Exception as e:
        print(f"生成主图时出错: {e}")
        return False

def generate_detail_page_content(title, content):
    """生成详情页内容"""
    clean_content = replace_forbidden_words(content)
    
    # 提取更多关键信息
    key_points = extract_key_points(clean_content)
    
    # 生成详情页结构
    detail_content = {
        'title': replace_forbidden_words(title),
        'introduction': clean_content[:200] + "...",
        'key_points': key_points,
        'sections': [
            {
                'title': '方法介绍',
                'content': clean_content[:300]
            },
            {
                'title': '详细步骤',
                'content': clean_content[300:600] if len(clean_content) > 300 else clean_content
            },
            {
                'title': '注意事项', 
                'content': '请根据实际情况调整策略，理性对待投资风险。'
            }
        ]
    }
    
    return detail_content

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件被上传'}), 400
        
        file = request.files['file']
        file_type = request.form.get('type', 'template')
        
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 添加时间戳避免文件名冲突
            import time
            timestamp = str(int(time.time()))
            filename = f"{timestamp}_{filename}"
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'url': f'/uploads/{filename}'
            })
        else:
            return jsonify({'error': '不支持的文件类型'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-words', methods=['POST'])
def check_words():
    """检查违禁词接口"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        forbidden_found = check_forbidden_words(text)
        clean_text = replace_forbidden_words(text)
        
        return jsonify({
            'forbidden_words': forbidden_found,
            'clean_text': clean_text,
            'has_forbidden': len(forbidden_found) > 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-main-image', methods=['POST'])
def generate_main_image_api():
    """生成主图接口"""
    try:
        data = request.get_json()
        title = data.get('title', '')
        content = data.get('content', '')
        template_filename = data.get('template', '')
        reference_filename = data.get('reference', '')
        use_enhanced = data.get('use_enhanced', True)
        
        if not all([title, content, template_filename]):
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 生成文字内容
        text_data = generate_main_image_text(title, content)
        
        # 路径设置
        template_path = os.path.join(app.config['UPLOAD_FOLDER'], template_filename)
        reference_path = None
        if reference_filename:
            reference_path = os.path.join(app.config['UPLOAD_FOLDER'], reference_filename)
        
        if use_enhanced and AI_MODULES_AVAILABLE and image_processor:
            # 使用增强版图片生成
            output_path = image_processor.create_enhanced_main_image(
                template_path, text_data, reference_path
            )
            if output_path:
                output_filename = os.path.basename(output_path)
                return jsonify({
                    'success': True,
                    'image_url': f'/generated/{output_filename}',
                    'text_data': text_data,
                    'enhanced': True
                })
            else:
                return jsonify({'error': '增强主图生成失败'}), 500
        else:
            # 使用基础版图片生成
            output_filename = f"main_image_{int(time.time())}.png"
            output_path = os.path.join(app.config['GENERATED_FOLDER'], output_filename)
            
            success = create_main_image(template_path, text_data, output_path)
            
            if success:
                return jsonify({
                    'success': True,
                    'image_url': f'/generated/{output_filename}',
                    'text_data': text_data,
                    'enhanced': False
                })
            else:
                return jsonify({'error': '生成主图失败'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-detail', methods=['POST'])
def generate_detail_api():
    """生成详情页接口"""
    try:
        data = request.get_json()
        title = data.get('title', '')
        content = data.get('content', '')
        
        if not all([title, content]):
            return jsonify({'error': '缺少必要参数'}), 400
        
        detail_content = generate_detail_page_content(title, content)
        
        return jsonify({
            'success': True,
            'detail_content': detail_content
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-ai-image', methods=['POST'])
def generate_ai_image_api():
    """AI生成图片接口"""
    try:
        if not AI_MODULES_AVAILABLE or not ai_generator:
            return jsonify({'error': 'AI功能未启用，请检查依赖安装'}), 400
        
        data = request.get_json()
        title = data.get('title', '')
        content = data.get('content', '')
        api_key = data.get('api_key', '')
        model_type = data.get('model_type', 'dalle3')
        style = data.get('style', 'commercial')
        
        if not all([title, content, api_key]):
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 设置API密钥
        ai_generator.set_api_key(api_key, model_type)
        
        # 生成提示词
        prompt = ai_generator.generate_image_prompt(title, content, style)
        
        # 生成图片
        if model_type == 'dalle3':
            image_url = ai_generator.generate_with_dalle3(prompt)
        elif model_type == 'stable-diffusion':
            image_url = ai_generator.generate_with_stable_diffusion(prompt, api_key)
        else:
            return jsonify({'error': '不支持的模型类型'}), 400
        
        if image_url:
            return jsonify({
                'success': True,
                'image_url': image_url,
                'prompt': prompt,
                'model_type': model_type
            })
        else:
            return jsonify({'error': 'AI生成图片失败'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-ai-image', methods=['POST'])
def save_ai_image_api():
    """保存AI生成的图片到本地"""
    try:
        data = request.get_json()
        image_url = data.get('image_url', '')
        
        if not image_url:
            return jsonify({'error': '缺少图片URL'}), 400
        
        # 下载图片
        response = requests.get(image_url)
        if response.status_code == 200:
            # 保存到本地
            filename = f"ai_generated_{int(time.time())}.png"
            filepath = os.path.join(app.config['GENERATED_FOLDER'], filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return jsonify({
                'success': True,
                'local_url': f'/generated/{filename}',
                'filename': filename
            })
        else:
            return jsonify({'error': '下载图片失败'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """访问上传的文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/generated/<filename>')
def generated_file(filename):
    """访问生成的文件"""
    return send_from_directory(app.config['GENERATED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)