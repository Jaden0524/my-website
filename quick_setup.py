#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube评论抓取器快速安装脚本
"""

import subprocess
import sys
import os

def install_package(package):
    """安装Python包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} 安装成功")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ {package} 安装失败")
        return False

def check_chrome():
    """检查Chrome浏览器是否已安装"""
    try:
        result = subprocess.run(['google-chrome', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Chrome浏览器已安装: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("✗ 未检测到Chrome浏览器")
    return False

def install_chrome_linux():
    """在Linux上安装Chrome浏览器"""
    print("正在安装Chrome浏览器...")
    commands = [
        "wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -",
        "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list",
        "sudo apt-get update",
        "sudo apt-get install -y google-chrome-stable"
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"执行命令失败: {cmd}")
            return False
    
    return check_chrome()

def main():
    print("YouTube评论抓取器快速安装")
    print("=" * 30)
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("✗ 需要Python 3.6或更高版本")
        return
    
    print(f"✓ Python版本: {sys.version}")
    
    # 安装必要的Python包
    packages = ["selenium", "webdriver-manager", "requests"]
    
    print("\n安装Python依赖包...")
    all_installed = True
    for package in packages:
        if not install_package(package):
            all_installed = False
    
    if not all_installed:
        print("某些包安装失败，请手动安装")
        return
    
    # 检查Chrome浏览器
    print("\n检查Chrome浏览器...")
    if not check_chrome():
        if sys.platform.startswith('linux'):
            if input("是否自动安装Chrome浏览器? (y/n): ").lower() == 'y':
                install_chrome_linux()
        else:
            print("请手动安装Chrome浏览器")
            print("下载地址: https://www.google.com/chrome/")
    
    print("\n安装完成！")
    print("\n使用方法:")
    print("1. 基本使用:")
    print("   python3 youtube_comment_scraper_improved.py 'https://www.youtube.com/watch?v=VIDEO_ID'")
    print("\n2. 指定输出格式:")
    print("   python3 youtube_comment_scraper_improved.py 'VIDEO_URL' --format json")
    print("\n3. 使用无头模式:")
    print("   python3 youtube_comment_scraper_improved.py 'VIDEO_URL' --headless")

if __name__ == "__main__":
    main()