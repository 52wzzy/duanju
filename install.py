#!/usr/bin/env python3
"""
电商主图生成工具安装脚本
"""

import subprocess
import sys
import os

def install_package(package):
    """安装单个包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        print(f"警告: 安装 {package} 失败")
        return False

def main():
    print("=== 电商主图生成工具安装程序 ===")
    print("正在安装必需的依赖包...")
    
    # 基础必需包
    basic_packages = [
        "flask==2.3.3",
        "flask-cors==4.0.0", 
        "pillow==10.0.1",
        "numpy==1.24.3",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "werkzeug==2.3.7"
    ]
    
    # 可选包
    optional_packages = [
        "opencv-python==4.8.1.78",
        "openai==0.28.0"
    ]
    
    # 安装基础包
    failed_basic = []
    for package in basic_packages:
        print(f"安装 {package}...")
        if not install_package(package):
            failed_basic.append(package)
    
    # 安装可选包
    failed_optional = []
    for package in optional_packages:
        print(f"安装可选包 {package}...")
        if not install_package(package):
            failed_optional.append(package)
    
    # 创建必要目录
    directories = ['uploads', 'generated', 'static', 'templates', 'static/fonts']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"创建目录: {directory}")
    
    # 安装结果
    print("\n=== 安装结果 ===")
    if not failed_basic:
        print("✅ 所有基础依赖安装成功")
    else:
        print("❌ 以下基础依赖安装失败:")
        for pkg in failed_basic:
            print(f"   - {pkg}")
    
    if not failed_optional:
        print("✅ 所有可选依赖安装成功")
    else:
        print("⚠️ 以下可选依赖安装失败（不影响基本功能）:")
        for pkg in failed_optional:
            print(f"   - {pkg}")
    
    print("\n=== 下一步 ===")
    print("1. 将字体文件放置到 static/fonts/ 目录（可选）")
    print("2. 复制 .env.example 为 .env 并配置API密钥（可选）")
    print("3. 运行命令: python app.py")
    print("4. 访问浏览器: http://localhost:5000")
    
    print("\n✨ 安装完成！")

if __name__ == "__main__":
    main()