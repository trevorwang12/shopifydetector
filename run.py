#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本 - Shopify主题检测器
这个脚本用于启动Shopify主题检测Web应用
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("❌ 错误: 需要Python 3.7或更高版本")
        print(f"当前版本: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python版本检查通过: {sys.version.split()[0]}")

def install_requirements():
    """安装依赖包"""
    requirements_file = Path(__file__).parent / 'requirements.txt'
    
    if not requirements_file.exists():
        print("❌ 错误: 找不到requirements.txt文件")
        sys.exit(1)
    
    print("📦 正在安装依赖包...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
        ])
        print("✅ 依赖包安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        print("请手动运行: pip install -r requirements.txt")
        sys.exit(1)

def check_dependencies():
    """检查依赖包是否已安装"""
    required_packages = [
        'flask',
        'requests',
        'beautifulsoup4',
        'lxml',
        'user_agents',
        'flask_cors'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("正在自动安装...")
        install_requirements()
    else:
        print("✅ 所有依赖包已安装")

def start_application():
    """启动应用"""
    print("🚀 正在启动Shopify主题检测器...")
    print("📍 应用将在以下地址运行:")
    print("   - 本地访问: http://localhost:5000")
    print("   - 网络访问: http://0.0.0.0:5000")
    print("")
    print("💡 使用说明:")
    print("   1. 在浏览器中打开上述地址")
    print("   2. 输入Shopify网站的URL")
    print("   3. 点击'检测主题'按钮")
    print("   4. 查看检测结果")
    print("")
    print("⚠️  按 Ctrl+C 停止应用")
    print("" + "="*50)
    
    try:
        # 导入并运行Flask应用
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    print("🔍 Shopify主题检测器 - 启动程序")
    print("" + "="*50)
    
    # 检查Python版本
    check_python_version()
    
    # 检查依赖包
    check_dependencies()
    
    # 启动应用
    start_application()

if __name__ == '__main__':
    main()