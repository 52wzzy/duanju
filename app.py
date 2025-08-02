import streamlit as st
import pandas as pd
from PIL import Image
import base64
import io
import json
import os
import requests
from typing import Dict, List, Optional

# 导入自定义工具类
from utils.text_processor import TextProcessor
from utils.image_processor import ImageProcessor
from utils.ai_generator import AIGenerator
from config import DEFAULT_FONT_CONFIG, IMAGE_SIZES, AI_MODELS

# 页面配置
st.set_page_config(
    page_title="智能电商主图与详情页生成器",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态
if 'text_processor' not in st.session_state:
    st.session_state.text_processor = TextProcessor()

if 'image_processor' not in st.session_state:
    st.session_state.image_processor = ImageProcessor()

if 'ai_generator' not in st.session_state:
    st.session_state.ai_generator = AIGenerator()

if 'generated_images' not in st.session_state:
    st.session_state.generated_images = {}

if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

def main():
    """主函数"""
    st.title("🎨 智能电商主图与详情页生成器")
    st.markdown("---")
    
    # 侧边栏 - AI配置
    setup_sidebar()
    
    # 主界面标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 文章输入与分析", 
        "🖼️ 模板上传与分析", 
        "🎯 主图生成", 
        "📄 详情页生成"
    ])
    
    with tab1:
        article_input_section()
    
    with tab2:
        template_upload_section()
    
    with tab3:
        main_image_generation_section()
    
    with tab4:
        detail_page_generation_section()

def setup_sidebar():
    """设置侧边栏 - AI配置"""
    st.sidebar.header("🔧 AI模型配置")
    
    # 获取所有可用模型
    available_models = st.session_state.ai_generator.get_available_models()
    
    # 模型选择
    st.sidebar.subheader("🤖 选择AI模型")
    
    # 构建模型选项
    model_options = []
    model_details = {}
    
    for provider, models in available_models.items():
        for model_key, model_info in models.items():
            display_name = f"{model_info['name']} ({model_info['provider']})"
            if model_info.get('cost') == '免费额度' or model_info.get('cost') == '免费（本地）':
                display_name += " 🆓"
            elif model_info.get('cost') == '付费':
                display_name += " 💰"
            
            model_options.append(display_name)
            model_details[display_name] = {
                "provider": provider,
                "model_key": model_key,
                "info": model_info
            }
    
    selected_model_name = st.sidebar.selectbox(
        "选择生图模型",
        options=model_options,
        index=0,
        help="选择用于生成图片的AI模型"
    )
    
    # 显示选中模型的详细信息
    if selected_model_name in model_details:
        model_detail = model_details[selected_model_name]
        model_info = model_detail["info"]
        
        st.sidebar.info(f"""
        **模型信息:**
        - 提供商: {model_info['provider']}
        - 费用: {model_info['cost']}
        - 质量: {model_info['quality']}
        - 速度: {model_info['speed']}
        - 最大分辨率: {model_info['max_resolution']}
        """ + (f"\n- 免费额度: {model_info['free_quota']}" if 'free_quota' in model_info else ""))
        
        # 设置当前模型
        st.session_state.ai_generator.set_current_model(
            model_detail["provider"], 
            model_detail["model_key"]
        )
    
    # API配置部分
    st.sidebar.subheader("🔑 API密钥配置")
    
    # 根据选择的模型显示对应的API配置
    if selected_model_name in model_details:
        provider = model_details[selected_model_name]["provider"]
        
        if provider == "openai":
            openai_key = st.sidebar.text_input(
                "OpenAI API Key",
                type="password",
                help="输入您的OpenAI API密钥"
            )
            if openai_key:
                st.session_state.ai_generator.set_api_key("openai", openai_key)
                st.sidebar.success("✅ OpenAI API已配置")
        
        elif provider == "智谱AI":
            zhipu_key = st.sidebar.text_input(
                "智谱AI API Key",
                type="password",
                help="输入您的智谱AI API密钥"
            )
            if zhipu_key:
                st.session_state.ai_generator.set_api_key("zhipu", zhipu_key)
                st.sidebar.success("✅ 智谱AI API已配置")
                st.sidebar.info("💡 免费用户每日可生成100次")
        
        elif provider == "百度":
            col1, col2 = st.sidebar.columns(2)
            with col1:
                baidu_api_key = st.text_input(
                    "API Key",
                    type="password",
                    help="百度API Key"
                )
            with col2:
                baidu_secret_key = st.text_input(
                    "Secret Key", 
                    type="password",
                    help="百度Secret Key"
                )
            
            if baidu_api_key and baidu_secret_key:
                st.session_state.ai_generator.set_api_key("baidu", baidu_api_key, secret_key=baidu_secret_key)
                st.sidebar.success("✅ 百度文心一格已配置")
                st.sidebar.info("💡 免费用户每日可生成50次")
        
        elif provider == "阿里云":
            alibaba_key = st.sidebar.text_input(
                "阿里云API Key",
                type="password",
                help="输入您的阿里云API密钥"
            )
            if alibaba_key:
                st.session_state.ai_generator.set_api_key("alibaba", alibaba_key)
                st.sidebar.success("✅ 阿里云通义万相已配置")
                st.sidebar.info("💡 免费用户每月可生成500次")
        
        elif provider == "腾讯云":
            col1, col2 = st.sidebar.columns(2)
            with col1:
                tencent_id = st.text_input(
                    "Secret ID",
                    type="password",
                    help="腾讯云Secret ID"
                )
            with col2:
                tencent_key = st.text_input(
                    "Secret Key",
                    type="password", 
                    help="腾讯云Secret Key"
                )
            
            if tencent_id and tencent_key:
                st.session_state.ai_generator.set_api_key("tencent", "", secret_id=tencent_id, secret_key=tencent_key)
                st.sidebar.success("✅ 腾讯云混元DiT已配置")
                st.sidebar.info("💡 免费用户每日可生成100次")
        
        elif provider == "科大讯飞":
            iflytek_key = st.sidebar.text_input(
                "科大讯飞API Key",
                type="password",
                help="输入您的科大讯飞API密钥"
            )
            if iflytek_key:
                st.session_state.ai_generator.set_api_key("iflytek", iflytek_key)
                st.sidebar.success("✅ 科大讯飞星火绘画已配置")
                st.sidebar.info("💡 免费用户每日可生成20次")
        
        elif provider == "Stability AI":
            st.sidebar.info("🖥️ 本地Stable Diffusion")
            sd_url = st.sidebar.text_input(
                "API地址",
                value="http://localhost:7860",
                help="Stable Diffusion Web UI的API地址"
            )
            
            if st.sidebar.button("测试连接"):
                try:
                    response = requests.get(f"{sd_url}/api/v1/options", timeout=5)
                    if response.status_code == 200:
                        st.sidebar.success("✅ Stable Diffusion连接成功")
                    else:
                        st.sidebar.error("❌ 连接失败")
                except:
                    st.sidebar.error("❌ 无法连接到Stable Diffusion")
        
        elif provider == "Midjourney":
            st.sidebar.warning("⚠️ Midjourney需要第三方API服务")
            mj_key = st.sidebar.text_input(
                "Midjourney API Key",
                type="password",
                help="输入第三方Midjourney API密钥"
            )
            if mj_key:
                st.session_state.ai_generator.set_api_key("midjourney", mj_key)
                st.sidebar.success("✅ Midjourney API已配置")
    
    # 高级设置
    st.sidebar.subheader("⚙️ 高级设置")
    
    # 图片参数配置
    image_size = st.sidebar.selectbox(
        "图片尺寸",
        options=["1024x1024", "1024x1792", "1792x1024"],
        index=0,
        help="选择生成图片的尺寸"
    )
    st.session_state.image_size = image_size
    
    image_quality = st.sidebar.selectbox(
        "图片质量",
        options=["standard", "hd"],
        index=0,
        help="选择图片质量（部分模型支持）"
    )
    st.session_state.image_quality = image_quality
    
    # 样式偏好设置
    st.sidebar.subheader("🎨 样式偏好")
    color_scheme = st.sidebar.selectbox(
        "配色方案",
        options=["现代商务", "活力橙色", "简约黑白", "温暖渐变", "自定义"],
        index=1
    )
    
    style_preference = st.sidebar.selectbox(
        "设计风格",
        options=["现代简约", "商务专业", "活力时尚", "温馨友好", "科技感"],
        index=0
    )
    
    st.session_state.style_preferences = {
        "color_scheme": color_scheme,
        "style": style_preference
    }
    
    # 显示当前配置状态
    st.sidebar.subheader("📊 配置状态")
    current_model = st.session_state.ai_generator.current_model
    if current_model:
        st.sidebar.success(f"当前模型: {current_model['config']['name']}")
    else:
        st.sidebar.warning("请选择AI模型")

def article_input_section():
    """文章输入与分析部分"""
    st.header("📝 文章信息输入")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 文章标题输入
        article_title = st.text_input(
            "文章标题",
            placeholder="输入您的文章标题...",
            help="请输入吸引人的文章标题"
        )
        
        # 文章内容输入
        article_content = st.text_area(
            "文章内容",
            placeholder="输入您的文章内容...",
            height=300,
            help="请输入完整的文章内容，系统将自动提取关键信息"
        )
        
        # 保存到会话状态
        st.session_state.article_title = article_title
        st.session_state.article_content = article_content
    
    with col2:
        st.subheader("📊 实时分析")
        
        if article_title and article_content:
            # 违禁词检测
            forbidden_check = st.session_state.text_processor.check_forbidden_words(
                article_title + " " + article_content
            )
            
            if forbidden_check["has_forbidden"]:
                st.error("⚠️ 检测到违禁词")
                for word in forbidden_check["forbidden_words"]:
                    suggestion = forbidden_check["suggestion"].get(word, "请修改")
                    st.write(f"- `{word}` → `{suggestion}`")
            else:
                st.success("✅ 文本合规")
            
            # 关键词提取
            keywords = st.session_state.text_processor.extract_keywords(
                article_content, 8
            )
            st.subheader("🔑 关键词")
            for i, keyword in enumerate(keywords[:5], 1):
                st.write(f"{i}. {keyword}")
            
            # 卖点提取
            selling_points = st.session_state.text_processor.extract_selling_points(
                article_content
            )
            if selling_points:
                st.subheader("💡 核心卖点")
                for point in selling_points[:3]:
                    st.write(f"• {point}")
        else:
            st.info("请输入文章标题和内容以开始分析")

def template_upload_section():
    """模板上传与分析部分"""
    st.header("🖼️ 模板图片上传")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 模板框架")
        template_file = st.file_uploader(
            "上传主图模板框架",
            type=['png', 'jpg', 'jpeg', 'webp'],
            help="上传您的主图模板框架图片"
        )
        
        if template_file:
            template_image = Image.open(template_file)
            st.image(template_image, caption="模板框架", use_column_width=True)
            st.session_state.template_image = template_image
    
    with col2:
        st.subheader("🎯 参考成品")
        reference_file = st.file_uploader(
            "上传参考成品图片",
            type=['png', 'jpg', 'jpeg', 'webp'],
            help="上传您设计的成品图片作为样式参考"
        )
        
        if reference_file:
            reference_image = Image.open(reference_file)
            st.image(reference_image, caption="参考成品", use_column_width=True)
            st.session_state.reference_image = reference_image
    
    # 模板分析
    if st.button("🔍 分析模板", type="primary"):
        if 'template_image' in st.session_state:
            with st.spinner("正在分析模板..."):
                reference_img = st.session_state.get('reference_image', None)
                analysis = st.session_state.image_processor.analyze_template(
                    st.session_state.template_image,
                    reference_img
                )
                st.session_state.template_analysis = analysis
                
                st.success("✅ 模板分析完成")
                
                # 显示分析结果
                st.subheader("📊 分析结果")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("图片尺寸", f"{analysis['width']}×{analysis['height']}")
                
                with col2:
                    st.metric("宽高比", f"{analysis['aspect_ratio']:.2f}")
                
                with col3:
                    st.metric("文本区域", len(analysis['text_regions']))
                
                # 显示颜色调色板
                if analysis['color_palette']:
                    st.subheader("🎨 主要颜色")
                    colors_html = ""
                    for color in analysis['color_palette'][:6]:
                        colors_html += f'<div style="display:inline-block; width:50px; height:30px; background-color:{color}; margin:5px; border:1px solid #ccc;"></div>'
                    st.markdown(colors_html, unsafe_allow_html=True)
        else:
            st.error("请先上传模板图片")

def main_image_generation_section():
    """主图生成部分"""
    st.header("🎯 主图生成")
    
    if not all(key in st.session_state for key in ['article_title', 'article_content']):
        st.warning("⚠️ 请先在第一个标签页输入文章信息")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("⚙️ 生成设置")
        
        # 标题变体选择
        title_variants = st.session_state.text_processor.generate_title_variants(
            st.session_state.article_title
        )
        
        selected_title = st.selectbox(
            "选择标题变体",
            options=title_variants,
            help="选择最适合的标题变体用于主图"
        )
        
        # 自定义副标题
        custom_subtitle = st.text_input(
            "自定义副标题",
            placeholder="输入副标题（可选）",
            help="为主图添加副标题"
        )
        
        # 生成方式选择
        generation_method = st.radio(
            "生成方式",
            options=["模板渲染", "AI生成", "模板+AI结合"],
            index=1,  # 默认选择AI生成
            help="选择主图生成方式"
        )
        
        # 字体样式配置
        st.subheader("🔤 字体样式")
        font_size_title = st.slider("标题字体大小", 20, 60, 36)
        font_size_subtitle = st.slider("副标题字体大小", 14, 40, 24)
        
        title_color = st.color_picker("标题颜色", "#FF6B35")
        subtitle_color = st.color_picker("副标题颜色", "#333333")
    
    with col2:
        st.subheader("🖼️ 生成结果")
        
        if st.button("🚀 开始生成主图", type="primary"):
            # 检查是否已配置AI模型
            current_model = st.session_state.ai_generator.current_model
            if not current_model and generation_method == "AI生成":
                st.error("请先在侧边栏选择并配置AI模型")
                return
            
            if generation_method == "模板渲染" and 'template_image' in st.session_state:
                # 模板渲染方式
                with st.spinner("正在渲染主图..."):
                    style_config = {
                        "title": {
                            "size": font_size_title,
                            "color": title_color,
                            "weight": "bold"
                        },
                        "subtitle": {
                            "size": font_size_subtitle,
                            "color": subtitle_color,
                            "weight": "normal"
                        }
                    }
                    
                    texts = {"title": selected_title}
                    if custom_subtitle:
                        texts["subtitle"] = custom_subtitle
                    
                    # 添加卖点
                    selling_points = st.session_state.text_processor.extract_selling_points(
                        st.session_state.article_content
                    )
                    if selling_points:
                        texts["selling_points"] = selling_points[:3]
                    
                    generated_image = st.session_state.image_processor.render_text_on_template(
                        st.session_state.template_image,
                        texts,
                        style_config
                    )
                    
                    st.session_state.generated_main_image = generated_image
                    st.image(generated_image, caption="生成的主图", use_column_width=True)
                    
                    # 提供下载按钮
                    img_buffer = io.BytesIO()
                    generated_image.save(img_buffer, format='PNG')
                    st.download_button(
                        label="💾 下载主图",
                        data=img_buffer.getvalue(),
                        file_name="main_image.png",
                        mime="image/png"
                    )
            
            elif generation_method == "AI生成":
                # AI生成方式
                with st.spinner("正在使用AI生成主图..."):
                    # 生成提示词
                    prompt = st.session_state.ai_generator.generate_image_prompt(
                        selected_title,
                        st.session_state.article_content,
                        st.session_state.style_preferences
                    )
                    
                    st.write("🤖 生成提示词:", prompt)
                    
                    # 调用AI生成
                    try:
                        ai_image = st.session_state.ai_generator.generate_image(prompt)
                        
                        if ai_image:
                            st.session_state.generated_main_image = ai_image
                            st.image(ai_image, caption="AI生成的主图", use_column_width=True)
                            
                            # 提供下载按钮
                            img_buffer = io.BytesIO()
                            ai_image.save(img_buffer, format='PNG')
                            st.download_button(
                                label="💾 下载主图",
                                data=img_buffer.getvalue(),
                                file_name="ai_main_image.png",
                                mime="image/png"
                            )
                        else:
                            st.error("AI生成失败，请检查API配置或稍后重试")
                    except Exception as e:
                        st.error(f"生成失败: {str(e)}")
            
            else:
                st.info("结合生成功能正在开发中...")

def detail_page_generation_section():
    """详情页生成部分"""
    st.header("📄 详情页生成")
    
    if not all(key in st.session_state for key in ['article_title', 'article_content']):
        st.warning("⚠️ 请先在第一个标签页输入文章信息")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚙️ 详情页配置")
        
        # 页面风格选择
        page_style = st.selectbox(
            "页面风格",
            options=["现代商务", "简约清新", "活力时尚", "专业权威"],
            index=0
        )
        
        # 章节选择
        st.subheader("📋 包含章节")
        include_hero = st.checkbox("产品亮点", value=True)
        include_features = st.checkbox("核心特色", value=True)
        include_benefits = st.checkbox("用户收益", value=True)
        include_process = st.checkbox("使用流程", value=True)
        include_guarantee = st.checkbox("品质承诺", value=True)
        
        # 生成按钮
        if st.button("🚀 生成详情页", type="primary"):
            with st.spinner("正在生成详情页布局..."):
                # 生成详情页布局
                layout = st.session_state.ai_generator.generate_detail_page_layout(
                    st.session_state.article_content
                )
                
                # 根据选择过滤章节
                selected_sections = []
                section_map = {
                    "hero": include_hero,
                    "features": include_features,
                    "benefits": include_benefits,
                    "process": include_process,
                    "guarantee": include_guarantee
                }
                
                for section in layout["sections"]:
                    if section_map.get(section["type"], True):
                        selected_sections.append(section)
                
                layout["sections"] = selected_sections
                st.session_state.detail_layout = layout
                
                st.success("✅ 详情页布局生成完成")
    
    with col2:
        st.subheader("📄 详情页预览")
        
        if 'detail_layout' in st.session_state:
            layout = st.session_state.detail_layout
            
            # 显示每个章节
            for section in layout["sections"]:
                st.markdown(f"### {section['title']}")
                
                if section["type"] == "hero":
                    # 产品亮点 - 大标题样式
                    for content in section["content"]:
                        st.markdown(f"#### 🌟 {content}")
                
                elif section["type"] == "features":
                    # 核心特色 - 图标样式
                    cols = st.columns(min(len(section["content"]), 3))
                    for i, content in enumerate(section["content"]):
                        with cols[i % 3]:
                            st.markdown(f"🔥 **{content}**")
                
                elif section["type"] == "benefits":
                    # 用户收益 - 编号列表
                    for i, content in enumerate(section["content"], 1):
                        st.markdown(f"{i}. ✅ {content}")
                
                elif section["type"] == "process":
                    # 使用流程 - 步骤样式
                    process_cols = st.columns(len(section["content"]))
                    for i, (col, content) in enumerate(zip(process_cols, section["content"])):
                        with col:
                            st.markdown(f"**步骤{i+1}**")
                            st.markdown(f"🔄 {content}")
                
                elif section["type"] == "guarantee":
                    # 品质承诺 - 徽章样式
                    guarantee_cols = st.columns(len(section["content"]))
                    for col, content in zip(guarantee_cols, section["content"]):
                        with col:
                            st.markdown(f"🏆 **{content}**")
                
                st.markdown("---")
            
            # 导出选项
            st.subheader("📤 导出选项")
            export_col1, export_col2 = st.columns(2)
            
            with export_col1:
                if st.button("📄 导出为HTML"):
                    html_content = generate_html_detail_page(layout)
                    st.download_button(
                        label="💾 下载HTML文件",
                        data=html_content,
                        file_name="detail_page.html",
                        mime="text/html"
                    )
            
            with export_col2:
                if st.button("📊 导出配置JSON"):
                    json_content = json.dumps(layout, ensure_ascii=False, indent=2)
                    st.download_button(
                        label="💾 下载配置文件",
                        data=json_content,
                        file_name="layout_config.json",
                        mime="application/json"
                    )

def generate_html_detail_page(layout: Dict) -> str:
    """生成HTML详情页"""
    html_template = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>产品详情页</title>
        <style>
            body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 750px; margin: 0 auto; background: white; }}
            .section {{ padding: 20px; margin-bottom: 10px; }}
            .hero {{ background: linear-gradient(135deg, {primary}, {secondary}); color: white; text-align: center; }}
            .features {{ display: flex; flex-wrap: wrap; gap: 15px; }}
            .feature-item {{ flex: 1; min-width: 200px; text-align: center; padding: 15px; background: #f9f9f9; border-radius: 8px; }}
            .benefits {{ padding-left: 20px; }}
            .process {{ display: flex; justify-content: space-between; }}
            .process-step {{ text-align: center; flex: 1; }}
            .guarantee {{ display: flex; justify-content: center; gap: 20px; }}
            .guarantee-badge {{ padding: 10px 20px; background: {primary}; color: white; border-radius: 20px; }}
            h2 {{ color: {primary}; border-bottom: 2px solid {primary}; padding-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            {sections_html}
        </div>
    </body>
    </html>
    """
    
    sections_html = ""
    colors = layout["color_scheme"]
    
    for section in layout["sections"]:
        section_html = f'<div class="section {section["type"]}">'
        section_html += f'<h2>{section["title"]}</h2>'
        
        if section["type"] == "hero":
            for content in section["content"]:
                section_html += f'<h3>🌟 {content}</h3>'
        
        elif section["type"] == "features":
            section_html += '<div class="features">'
            for content in section["content"]:
                section_html += f'<div class="feature-item">🔥 <strong>{content}</strong></div>'
            section_html += '</div>'
        
        elif section["type"] == "benefits":
            section_html += '<ol class="benefits">'
            for content in section["content"]:
                section_html += f'<li>✅ {content}</li>'
            section_html += '</ol>'
        
        elif section["type"] == "process":
            section_html += '<div class="process">'
            for i, content in enumerate(section["content"], 1):
                section_html += f'<div class="process-step"><strong>步骤{i}</strong><br>🔄 {content}</div>'
            section_html += '</div>'
        
        elif section["type"] == "guarantee":
            section_html += '<div class="guarantee">'
            for content in section["content"]:
                section_html += f'<div class="guarantee-badge">🏆 {content}</div>'
            section_html += '</div>'
        
        section_html += '</div>'
        sections_html += section_html
    
    return html_template.format(
        primary=colors["primary"],
        secondary=colors["secondary"],
        sections_html=sections_html
    )

if __name__ == "__main__":
    main()