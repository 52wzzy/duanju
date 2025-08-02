# 电商主图生成工具

一个基于AI的电商主图和详情页生成工具，专为网络创业项目教程设计。

## 🌟 功能特性

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

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Windows/Linux/Mac

### 一键安装启动

**Windows 用户:**
1. 双击运行 `install.bat` 自动安装
2. 双击运行 `start.bat` 启动程序
3. 浏览器自动打开 http://localhost:5000

**Linux/Mac 用户:**
```bash
python install.py    # 自动安装依赖
python start.py      # 启动程序
```

### 手动安装

1. **下载项目**
```bash
git clone <repository-url>
cd ecommerce-image-generator
```

2. **安装基础依赖**
```bash
pip install -r requirements_simple.txt
```

3. **可选：安装完整功能**
```bash
pip install opencv-python==4.8.1.78
pip install openai==0.28.0
```

4. **启动应用**
```bash
python app.py
```

## 📖 使用指南

### 1. 基础操作
1. **输入文章信息**: 填写标题和内容
2. **检查违禁词**: 点击按钮自动检测和替换
3. **上传图片模板**: 选择主图框架图片
4. **生成主图**: 一键生成专业主图

### 2. AI功能
1. **配置API密钥**: 在设置中输入OpenAI等API密钥
2. **选择AI模型**: 支持DALL-E 3、Stable Diffusion
3. **生成AI图片**: 基于文章内容生成全新图片
4. **保存使用**: 可将AI图片保存为模板使用

### 3. 高级功能
- **参考图分析**: 上传成品图自动分析样式
- **文字优化**: 自动调整字体大小和位置
- **装饰效果**: 添加阴影、边框等视觉效果
- **详情页生成**: 自动生成产品详情页内容

## 🔧 配置说明

### 违禁词配置
在 `app.py` 中修改违禁词列表：
```python
FORBIDDEN_WORDS = [
    '暴利', '躺赚', '日赚', '月入', 
    # 添加更多违禁词...
]
```

### 字体配置
将字体文件放置到 `static/fonts/` 目录：
- 支持 TTF、OTF、TTC 格式
- 推荐使用 PingFang、微软雅黑等中文字体

### API配置
复制 `.env.example` 为 `.env` 并配置：
```env
OPENAI_API_KEY=your_openai_api_key_here
STABILITY_API_KEY=your_stability_api_key_here
```

## 📁 项目结构

```
ecommerce-image-generator/
├── app.py                      # Flask主应用
├── ai_generator_simple.py      # 简化版AI模块
├── ai_generator.py            # 完整版AI模块
├── start.py                   # 快速启动脚本
├── install.py                 # 安装脚本
├── requirements_simple.txt    # 基础依赖
├── requirements.txt           # 完整依赖
├── static/                    # 前端资源
│   ├── css/style.css         # 样式文件
│   ├── js/main.js            # JavaScript
│   └── fonts/                # 字体目录
├── templates/                 # HTML模板
├── uploads/                   # 上传文件
└── generated/                 # 生成文件
```

## 🛠️ 故障排除

### 常见问题

**1. 依赖安装失败**
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name
```

**2. opencv-python 安装失败**
- 自动降级使用简化版功能
- 或尝试安装：`pip install opencv-python-headless`

**3. 字体显示异常**
- 将 TTF/OTF 字体文件放到 `static/fonts/` 目录
- 确保字体文件权限正确

**4. AI功能无法使用**
- 检查API密钥是否正确配置
- 确认网络连接和API服务状态

### 启动问题
如果遇到启动问题，请尝试：
```bash
# 检查Python版本
python --version

# 重新安装依赖
pip install -r requirements_simple.txt

# 使用调试模式启动
python app.py
```

## 🎯 功能演示

### 主图生成效果
- 自动提取文章关键信息
- 智能排版和配色
- 专业的视觉效果

### 违禁词处理
- 实时检测敏感词汇
- 智能替换为合规表达
- 支持自定义规则

### AI图片生成
- 基于文章内容生成图片
- 支持多种AI模型
- 可保存为模板使用

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发环境
1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 📞 支持

- 🌟 如果项目对你有帮助，请给个 Star！
- 🐛 遇到问题请创建 [Issue](https://github.com/your-repo/issues)
- 📧 技术交流欢迎联系开发者

---

**✨ 让电商主图制作变得简单高效！**