# 电商主图生成工具

一个基于AI的电商主图和详情页生成工具，专为网络创业项目教程设计。

## 功能特性

### 核心功能
- 📝 **文章内容处理**: 智能提取文章标题和内容中的关键信息
- 🚫 **违禁词检测**: 自动检测和替换电商平台违禁词汇
- 🖼️ **主图生成**: 基于模板和参考图生成专业的电商主图
- 🤖 **AI图片生成**: 支持DALL-E 3、Stable Diffusion等AI模型
- 📄 **详情页生成**: 自动生成结构化的产品详情页内容
- 💾 **草稿保存**: 自动保存和恢复编辑内容

### 高级特性
- 🎨 **样式分析**: 分析参考图的颜色和布局风格
- ✨ **图片增强**: 自动优化图片质量、对比度和饱和度
- 🎯 **精准文字**: 智能控制字体大小、颜色和位置
- 🎪 **装饰元素**: 自动添加边框、阴影等装饰效果

## 技术栈

### 后端
- **Flask**: Python Web框架
- **PIL/Pillow**: 图片处理库
- **OpenCV**: 计算机视觉库
- **OpenAI API**: AI图片生成

### 前端
- **Bootstrap 5**: 响应式UI框架
- **Vanilla JavaScript**: 原生JavaScript
- **Bootstrap Icons**: 图标库

## 安装部署

### 环境要求
- Python 3.8+
- pip包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd ecommerce-image-generator
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
创建`.env`文件：
```env
OPENAI_API_KEY=your_openai_api_key_here
STABILITY_API_KEY=your_stability_api_key_here
```

4. **启动应用**
```bash
python app.py
```

5. **访问应用**
打开浏览器访问: http://localhost:5000

## 使用指南

### 1. 文章信息输入
- **标题**: 输入文章标题（建议50字符以内）
- **内容**: 输入文章主要内容（至少50字符）
- **违禁词检查**: 点击检查按钮自动识别和替换违禁词

### 2. 图片上传
- **主图模板**: 上传作为基础的图片模板（必需）
- **参考图**: 上传参考的成品图片（可选，用于样式分析）

### 3. AI生成设置
- **模型选择**: 支持DALL-E 3、Midjourney、Stable Diffusion
- **API密钥**: 输入对应AI服务的API密钥

### 4. 生成操作
- **生成主图**: 基于模板和文章内容生成主图
- **AI生成图片**: 使用AI模型生成全新图片
- **生成详情页**: 自动生成产品详情页内容

## 项目结构

```
ecommerce-image-generator/
├── app.py                 # Flask应用主文件
├── ai_generator.py        # AI图片生成模块
├── requirements.txt       # Python依赖包
├── README.md             # 项目说明文档
├── .env                  # 环境变量配置
├── static/               # 静态资源目录
│   ├── css/
│   │   └── style.css     # 样式文件
│   ├── js/
│   │   └── main.js       # JavaScript文件
│   └── fonts/            # 字体文件目录
├── templates/            # HTML模板目录
│   └── index.html        # 主页模板
├── uploads/              # 用户上传文件目录
└── generated/            # 生成文件目录
```

## API接口

### 文件上传
```
POST /api/upload
Content-Type: multipart/form-data

参数:
- file: 图片文件
- type: 文件类型 (template/reference)
```

### 违禁词检查
```
POST /api/check-words
Content-Type: application/json

参数:
{
  "text": "要检查的文本内容"
}
```

### 生成主图
```
POST /api/generate-main-image
Content-Type: application/json

参数:
{
  "title": "文章标题",
  "content": "文章内容",
  "template": "模板文件名",
  "reference": "参考图文件名",
  "use_enhanced": true
}
```

### AI生成图片
```
POST /api/generate-ai-image
Content-Type: application/json

参数:
{
  "title": "文章标题",
  "content": "文章内容",
  "api_key": "API密钥",
  "model_type": "dalle3",
  "style": "commercial"
}
```

### 生成详情页
```
POST /api/generate-detail
Content-Type: application/json

参数:
{
  "title": "文章标题",
  "content": "文章内容"
}
```

## 配置说明

### 违禁词配置
在`app.py`中的`FORBIDDEN_WORDS`列表中配置需要检测的违禁词：

```python
FORBIDDEN_WORDS = [
    '暴利', '躺赚', '日赚', '月入', '轻松赚钱', 
    '不劳而获', '一夜暴富', '包赚', '稳赚', '零风险'
    # 添加更多违禁词...
]
```

### 字体配置
将字体文件放置在`static/fonts/`目录下：
- PingFang-Bold.ttf (粗体)
- PingFang-Regular.ttf (常规)

### AI模型配置
支持的AI模型：
- **DALL-E 3**: 需要OpenAI API密钥
- **Stable Diffusion**: 需要Stability AI API密钥
- **Midjourney**: 需要相应的API接入

## 开发指南

### 添加新的AI模型
1. 在`ai_generator.py`中的`AIImageGenerator`类添加新方法
2. 在前端`main.js`中添加对应的调用逻辑
3. 更新HTML模板中的模型选择选项

### 自定义违禁词规则
1. 修改`app.py`中的`FORBIDDEN_WORDS`列表
2. 更新`replace_forbidden_words`函数的替换规则
3. 可以添加更复杂的正则表达式匹配

### 扩展图片处理功能
1. 在`ai_generator.py`中的`AdvancedImageProcessor`类添加新方法
2. 支持更多图片格式和处理效果
3. 添加批量处理功能

## 故障排除

### 常见问题

**1. 字体显示异常**
- 确保字体文件已正确放置在`static/fonts/`目录
- 检查字体文件权限和格式

**2. AI生成失败**
- 验证API密钥是否正确
- 检查网络连接和API服务状态
- 确认API配额和使用限制

**3. 图片上传失败**
- 检查文件大小是否超过16MB限制
- 确认文件格式是否支持 (png, jpg, jpeg, gif)
- 验证上传目录权限

**4. 主图生成异常**
- 确认模板图片格式正确
- 检查PIL/Pillow库是否正确安装
- 验证生成目录写入权限

### 日志调试
启用调试模式：
```python
app.run(debug=True)
```

查看详细错误信息：
```bash
tail -f app.log
```

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。

### 开发环境设置
1. Fork项目到你的GitHub账户
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -am 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 创建Pull Request

## 更新日志

### v1.0.0 (2024-01-XX)
- ✨ 初始版本发布
- 🎨 基础主图生成功能
- 🤖 AI图片生成集成
- 🚫 违禁词检测和过滤
- 📄 详情页自动生成
- 💾 草稿自动保存功能

## 支持

如果你觉得这个项目有用，请给它一个 ⭐️ Star！

有问题或建议？请创建 [Issue](https://github.com/your-repo/issues) 或联系开发者。
