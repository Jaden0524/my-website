#!/bin/bash

echo "YouTube评论抓取器安装脚本"
echo "=========================="

# 更新系统包
echo "更新系统包..."
sudo apt-get update

# 安装Chrome浏览器
echo "安装Chrome浏览器..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# 安装ChromeDriver
echo "安装ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
echo "检测到Chrome版本: $CHROME_VERSION"

# 下载对应版本的ChromeDriver
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /tmp/
sudo mv /tmp/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# 安装Python依赖
echo "安装Python依赖..."
pip3 install -r requirements.txt

# 验证安装
echo "验证安装..."
python3 -c "from selenium import webdriver; print('Selenium安装成功')"
chromedriver --version

echo "安装完成！"
echo ""
echo "使用方法："
echo "1. 命令行使用："
echo "   python3 youtube_comment_scraper.py 'https://www.youtube.com/watch?v=VIDEO_ID'"
echo ""
echo "2. 编程使用："
echo "   python3 example_usage.py"
echo ""
echo "支持的输出格式: json, csv, txt, all"