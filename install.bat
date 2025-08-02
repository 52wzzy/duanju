@echo off
chcp 65001 >nul
echo =================================
echo     电商主图生成工具安装程序
echo =================================
echo.

echo 🔧 开始安装依赖包...
python -m pip install --upgrade pip

echo.
echo 📦 安装基础依赖...
python -m pip install flask==2.3.3
python -m pip install flask-cors==4.0.0
python -m pip install pillow==10.0.1
python -m pip install numpy==1.24.3
python -m pip install requests==2.31.0
python -m pip install python-dotenv==1.0.0
python -m pip install werkzeug==2.3.7

echo.
echo 📦 尝试安装可选依赖...
python -m pip install opencv-python==4.8.1.78 || echo ⚠️  opencv-python 安装失败，将使用简化版功能
python -m pip install openai==0.28.0 || echo ⚠️  openai 安装失败，AI功能将被禁用

echo.
echo 📁 创建必要目录...
if not exist "uploads" mkdir uploads
if not exist "generated" mkdir generated
if not exist "static" mkdir static
if not exist "templates" mkdir templates
if not exist "static\fonts" mkdir static\fonts

echo.
echo ✅ 安装完成！
echo.
echo 📋 使用说明：
echo 1. 将字体文件放置到 static\fonts\ 目录（可选）
echo 2. 复制 .env.example 为 .env 并配置API密钥（可选）
echo 3. 双击 start.bat 启动程序
echo 4. 或者运行: python start.py
echo.
pause