#!/usr/bin/env python3
"""
智能电商主图与详情页生成器 - 启动脚本
"""

import subprocess
import sys
import os

def install_dependencies():
    """安装依赖包"""
    print("🔧 正在安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def check_dependencies():
    """检查依赖包是否已安装"""
    required_packages = [
        'streamlit', 'Pillow', 'opencv-python', 'numpy', 
        'requests', 'openai', 'jieba', 'matplotlib'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def create_directories():
    """创建必要的目录"""
    directories = ['utils', 'temp', 'outputs']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 创建目录: {directory}")

def run_streamlit():
    """运行Streamlit应用"""
    print("🚀 启动智能电商主图生成器...")
    print("🌐 应用将在浏览器中打开: http://localhost:8501")
    print("📖 使用说明:")
    print("   1. 在侧边栏配置OpenAI API密钥")
    print("   2. 输入文章标题和内容")
    print("   3. 上传模板图片和参考成品")
    print("   4. 生成主图和详情页")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 应用已关闭")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print("🎨 智能电商主图与详情页生成器")
    print("=" * 50)
    
    # 创建必要目录
    create_directories()
    
    # 检查依赖
    deps_ok, missing = check_dependencies()
    
    if not deps_ok:
        print(f"⚠️ 缺少依赖包: {', '.join(missing)}")
        print("🔧 尝试自动安装...")
        
        if not install_dependencies():
            print("❌ 请手动安装依赖包: pip install -r requirements.txt")
            return
    
    # 启动应用
    run_streamlit()

if __name__ == "__main__":
    main()