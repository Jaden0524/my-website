#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube评论抓取器
能够抓取YouTube视频的所有评论，包括回复
支持自动滚动和点击展开回复
"""

import time
import json
import csv
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import argparse
import os

class YouTubeCommentScraper:
    def __init__(self, headless=True, scroll_pause_time=2):
        """
        初始化YouTube评论抓取器
        
        Args:
            headless (bool): 是否使用无头模式
            scroll_pause_time (int): 滚动间隔时间（秒）
        """
        self.scroll_pause_time = scroll_pause_time
        self.comments = []
        self.driver = None
        self.setup_driver(headless)
    
    def setup_driver(self, headless=True):
        """设置Chrome浏览器驱动"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
        except Exception as e:
            print(f"Chrome驱动初始化失败: {e}")
            print("请确保已安装ChromeDriver")
            raise
    
    def extract_video_id(self, url):
        """从YouTube URL中提取视频ID"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError("无法从URL中提取视频ID")
    
    def load_video_page(self, video_url):
        """加载YouTube视频页面"""
        print(f"正在加载视频页面: {video_url}")
        self.driver.get(video_url)
        
        # 等待页面加载
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "primary"))
            )
            print("页面加载完成")
        except TimeoutException:
            print("页面加载超时")
            return False
        
        return True
    
    def scroll_to_comments(self):
        """滚动到评论区域"""
        print("正在滚动到评论区域...")
        
        # 滚动到页面底部几次，确保评论区域加载
        for i in range(3):
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)
        
        # 查找评论区域
        try:
            comments_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "comments"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView();", comments_section)
            time.sleep(2)
            print("已滚动到评论区域")
            return True
        except TimeoutException:
            print("未找到评论区域")
            return False
    
    def expand_replies(self):
        """展开所有回复"""
        print("正在展开所有回复...")
        
        while True:
            try:
                # 查找所有"显示回复"按钮
                reply_buttons = self.driver.find_elements(
                    By.XPATH, 
                    "//tp-yt-paper-button[@id='more-replies' or contains(@aria-label, '回复') or contains(text(), 'replies') or contains(text(), '回复')]"
                )
                
                if not reply_buttons:
                    break
                
                # 点击所有可见的回复按钮
                buttons_clicked = 0
                for button in reply_buttons:
                    try:
                        if button.is_displayed() and button.is_enabled():
                            self.driver.execute_script("arguments[0].click();", button)
                            buttons_clicked += 1
                            time.sleep(1)  # 等待回复加载
                    except (StaleElementReferenceException, Exception):
                        continue
                
                if buttons_clicked == 0:
                    break
                
                print(f"展开了 {buttons_clicked} 个回复")
                
                # 滚动一下，确保新加载的内容可见
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(1)
                
            except Exception as e:
                print(f"展开回复时出错: {e}")
                break
        
        print("回复展开完成")
    
    def scroll_and_load_comments(self):
        """滚动页面并加载所有评论"""
        print("开始滚动加载评论...")
        
        last_height = self.driver.execute_script("return document.documentElement.scrollHeight")
        scroll_attempts = 0
        max_scroll_attempts = 50  # 最大滚动次数
        
        while scroll_attempts < max_scroll_attempts:
            # 滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            
            # 等待新内容加载
            time.sleep(self.scroll_pause_time)
            
            # 展开当前可见的回复
            self.expand_replies()
            
            # 检查是否有新内容加载
            new_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            
            if new_height == last_height:
                scroll_attempts += 1
                print(f"页面高度未变化，尝试次数: {scroll_attempts}/{max_scroll_attempts}")
            else:
                scroll_attempts = 0  # 重置计数器
                print(f"页面高度从 {last_height} 变化到 {new_height}")
            
            last_height = new_height
        
        print("滚动加载完成")
    
    def extract_comment_info(self, comment_element):
        """提取单个评论的信息"""
        try:
            # 评论者ID/用户名
            author_element = comment_element.find_element(By.ID, "author-text")
            author_name = author_element.text.strip()
            
            # 评论时间
            time_element = comment_element.find_element(By.CLASS_NAME, "published-time-text")
            comment_time = time_element.get_attribute("title") or time_element.text.strip()
            
            # 评论内容
            content_element = comment_element.find_element(By.ID, "content-text")
            comment_content = content_element.text.strip()
            
            # 判断是否为回复（根据元素结构）
            is_reply = "ytd-comment-reply-renderer" in comment_element.get_attribute("class")
            
            return {
                "author": author_name,
                "time": comment_time,
                "content": comment_content,
                "is_reply": is_reply,
                "extracted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"提取评论信息时出错: {e}")
            return None
    
    def scrape_comments(self, video_url):
        """抓取所有评论"""
        if not self.load_video_page(video_url):
            return []
        
        # 滚动到评论区域
        if not self.scroll_to_comments():
            return []
        
        # 滚动并加载所有评论
        self.scroll_and_load_comments()
        
        # 提取所有评论
        print("开始提取评论...")
        
        # 查找所有评论元素（包括主评论和回复）
        comment_selectors = [
            "ytd-comment-thread-renderer",  # 主评论线程
            "ytd-comment-reply-renderer"    # 回复评论
        ]
        
        all_comments = []
        
        for selector in comment_selectors:
            try:
                elements = self.driver.find_elements(By.TAG_NAME, selector)
                print(f"找到 {len(elements)} 个 {selector} 元素")
                
                for element in elements:
                    comment_info = self.extract_comment_info(element)
                    if comment_info:
                        all_comments.append(comment_info)
            
            except Exception as e:
                print(f"查找 {selector} 时出错: {e}")
        
        # 去重（基于作者、时间和内容）
        unique_comments = []
        seen = set()
        
        for comment in all_comments:
            key = (comment["author"], comment["time"], comment["content"])
            if key not in seen:
                seen.add(key)
                unique_comments.append(comment)
        
        print(f"提取到 {len(unique_comments)} 条独特评论")
        self.comments = unique_comments
        return unique_comments
    
    def save_to_json(self, filename=None):
        """保存评论到JSON文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"youtube_comments_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.comments, f, ensure_ascii=False, indent=2)
        
        print(f"评论已保存到: {filename}")
        return filename
    
    def save_to_csv(self, filename=None):
        """保存评论到CSV文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"youtube_comments_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['author', 'time', 'content', 'is_reply', 'extracted_at'])
            writer.writeheader()
            writer.writerows(self.comments)
        
        print(f"评论已保存到: {filename}")
        return filename
    
    def save_to_txt(self, filename=None):
        """保存评论到TXT文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"youtube_comments_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"YouTube评论抓取结果\n")
            f.write(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总评论数: {len(self.comments)}\n")
            f.write("=" * 50 + "\n\n")
            
            for i, comment in enumerate(self.comments, 1):
                prefix = "    ↳ " if comment["is_reply"] else ""
                f.write(f"{prefix}[{i}] {comment['author']}\n")
                f.write(f"{prefix}时间: {comment['time']}\n")
                f.write(f"{prefix}内容: {comment['content']}\n")
                f.write("-" * 30 + "\n")
        
        print(f"评论已保存到: {filename}")
        return filename
    
    def close(self):
        """关闭浏览器驱动"""
        if self.driver:
            self.driver.quit()

def main():
    parser = argparse.ArgumentParser(description='YouTube评论抓取器')
    parser.add_argument('url', help='YouTube视频URL')
    parser.add_argument('--format', choices=['json', 'csv', 'txt', 'all'], default='all',
                       help='输出格式 (默认: all)')
    parser.add_argument('--headless', action='store_true', help='使用无头模式')
    parser.add_argument('--scroll-pause', type=int, default=2, help='滚动间隔时间（秒）')
    parser.add_argument('--output', help='输出文件名（不含扩展名）')
    
    args = parser.parse_args()
    
    scraper = YouTubeCommentScraper(headless=args.headless, scroll_pause_time=args.scroll_pause)
    
    try:
        print(f"开始抓取YouTube视频评论: {args.url}")
        comments = scraper.scrape_comments(args.url)
        
        if not comments:
            print("未找到任何评论")
            return
        
        print(f"成功抓取 {len(comments)} 条评论")
        
        # 保存文件
        if args.format == 'json' or args.format == 'all':
            scraper.save_to_json(f"{args.output}.json" if args.output else None)
        
        if args.format == 'csv' or args.format == 'all':
            scraper.save_to_csv(f"{args.output}.csv" if args.output else None)
        
        if args.format == 'txt' or args.format == 'all':
            scraper.save_to_txt(f"{args.output}.txt" if args.output else None)
        
    except Exception as e:
        print(f"抓取过程中出错: {e}")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    main()