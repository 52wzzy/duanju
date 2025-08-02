#!/usr/bin/env python3
"""
电商主图生成工具启动脚本
"""

import os
import sys
import webbrowser
import time
from threading import Timer

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)  # 等待2秒让服务器启动
    webbrowser.open('http://localhost:5000')

def main():
    print("🚀 启动电商主图生成工具...")
    print("📂 检查必要目录...")
    
    # 检查并创建必要目录
    directories = ['uploads', 'generated', 'static', 'templates', 'static/fonts']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"   创建目录: {directory}")
    
    print("✅ 目录检查完成")
    print("🌐 启动Web服务器...")
    print("📱 服务地址: http://localhost:5000")
    print("🔄 按 Ctrl+C 停止服务")
    print("-" * 50)
    
    # 延迟打开浏览器
    Timer(2.0, open_browser).start()
    
    # 导入并启动Flask应用
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("💡 请先运行: python install.py")

if __name__ == "__main__":
    main()