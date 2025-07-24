#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube评论抓取器 - 改进版
使用webdriver-manager自动管理ChromeDriver
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
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
import argparse
import os

class YouTubeCommentScraperImproved:
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
        """设置Chrome浏览器驱动 - 使用webdriver-manager自动管理"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        try:
            # 使用webdriver-manager自动下载和管理ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 执行脚本来隐藏webdriver属性
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(30)
            
            print("Chrome驱动初始化成功")
        except Exception as e:
            print(f"Chrome驱动初始化失败: {e}")
            raise
    
    def load_video_page(self, video_url):
        """加载YouTube视频页面"""
        print(f"正在加载视频页面: {video_url}")
        self.driver.get(video_url)
        
        # 等待页面加载
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "primary"))
            )
            print("页面加载完成")
            time.sleep(3)  # 额外等待时间确保页面完全加载
        except TimeoutException:
            print("页面加载超时")
            return False
        
        return True
    
    def scroll_to_comments(self):
        """滚动到评论区域"""
        print("正在滚动到评论区域...")
        
        # 滚动到页面底部几次，确保评论区域加载
        for i in range(5):
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)
            print(f"滚动进度: {i+1}/5")
        
        # 查找评论区域
        try:
            comments_section = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "comments"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView();", comments_section)
            time.sleep(3)
            print("已滚动到评论区域")
            return True
        except TimeoutException:
            print("未找到评论区域，可能该视频没有开启评论功能")
            return False
    
    def expand_replies(self):
        """展开所有回复"""
        expanded_count = 0
        
        # 查找并点击所有"显示回复"按钮
        reply_selectors = [
            "//tp-yt-paper-button[contains(@aria-label, 'replies') or contains(@aria-label, '回复')]",
            "//tp-yt-paper-button[@id='more-replies']",
            "//tp-yt-paper-button[contains(text(), 'replies') or contains(text(), '回复')]",
            "//button[contains(@aria-label, 'replies') or contains(@aria-label, '回复')]"
        ]
        
        for selector in reply_selectors:
            try:
                buttons = self.driver.find_elements(By.XPATH, selector)
                for button in buttons:
                    try:
                        if button.is_displayed() and button.is_enabled():
                            self.driver.execute_script("arguments[0].click();", button)
                            expanded_count += 1
                            time.sleep(1)  # 等待回复加载
                    except (StaleElementReferenceException, Exception):
                        continue
            except Exception:
                continue
        
        if expanded_count > 0:
            print(f"展开了 {expanded_count} 个回复")
        
        return expanded_count
    
    def scroll_and_load_comments(self):
        """滚动页面并加载所有评论"""
        print("开始滚动加载评论...")
        
        last_height = self.driver.execute_script("return document.documentElement.scrollHeight")
        scroll_attempts = 0
        max_scroll_attempts = 30  # 减少最大滚动次数
        no_change_count = 0
        
        while scroll_attempts < max_scroll_attempts and no_change_count < 5:
            # 滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            
            # 等待新内容加载
            time.sleep(self.scroll_pause_time)
            
            # 展开当前可见的回复
            self.expand_replies()
            
            # 检查是否有新内容加载
            new_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            
            if new_height == last_height:
                no_change_count += 1
                print(f"页面高度未变化，连续次数: {no_change_count}/5")
            else:
                no_change_count = 0
                print(f"页面高度从 {last_height} 变化到 {new_height}")
            
            last_height = new_height
            scroll_attempts += 1
        
        print("滚动加载完成")
    
    def extract_comment_info(self, comment_element):
        """提取单个评论的信息"""
        try:
            comment_data = {}
            
            # 评论者用户名
            try:
                author_element = comment_element.find_element(By.CSS_SELECTOR, "#author-text span")
                comment_data["author"] = author_element.text.strip()
            except:
                try:
                    author_element = comment_element.find_element(By.ID, "author-text")
                    comment_data["author"] = author_element.text.strip()
                except:
                    comment_data["author"] = "未知用户"
            
            # 评论时间
            try:
                time_element = comment_element.find_element(By.CSS_SELECTOR, ".published-time-text a")
                comment_data["time"] = time_element.get_attribute("title") or time_element.text.strip()
            except:
                try:
                    time_element = comment_element.find_element(By.CLASS_NAME, "published-time-text")
                    comment_data["time"] = time_element.text.strip()
                except:
                    comment_data["time"] = "未知时间"
            
            # 评论内容
            try:
                content_element = comment_element.find_element(By.ID, "content-text")
                comment_data["content"] = content_element.text.strip()
            except:
                try:
                    content_element = comment_element.find_element(By.CSS_SELECTOR, "#content-text span")
                    comment_data["content"] = content_element.text.strip()
                except:
                    comment_data["content"] = "无法获取内容"
            
            # 判断是否为回复
            comment_data["is_reply"] = "ytd-comment-reply-renderer" in comment_element.get_attribute("outerHTML")
            
            # 添加抓取时间
            comment_data["extracted_at"] = datetime.now().isoformat()
            
            return comment_data if comment_data["content"] != "无法获取内容" else None
            
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
        
        all_comments = []
        
        # 查找所有评论容器
        comment_containers = self.driver.find_elements(By.CSS_SELECTOR, "ytd-comment-thread-renderer")
        print(f"找到 {len(comment_containers)} 个评论线程")
        
        for container in comment_containers:
            try:
                # 主评论
                main_comment = container.find_element(By.CSS_SELECTOR, "ytd-comment-renderer")
                comment_info = self.extract_comment_info(main_comment)
                if comment_info:
                    all_comments.append(comment_info)
                
                # 回复评论
                reply_comments = container.find_elements(By.CSS_SELECTOR, "ytd-comment-reply-renderer")
                for reply in reply_comments:
                    reply_info = self.extract_comment_info(reply)
                    if reply_info:
                        all_comments.append(reply_info)
                        
            except Exception as e:
                print(f"处理评论容器时出错: {e}")
                continue
        
        # 去重
        unique_comments = []
        seen = set()
        
        for comment in all_comments:
            key = (comment["author"], comment["time"], comment["content"][:50])  # 使用内容前50字符作为去重依据
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
            json.dump({
                "total_comments": len(self.comments),
                "extracted_at": datetime.now().isoformat(),
                "comments": self.comments
            }, f, ensure_ascii=False, indent=2)
        
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
    parser = argparse.ArgumentParser(description='YouTube评论抓取器 - 改进版')
    parser.add_argument('url', help='YouTube视频URL')
    parser.add_argument('--format', choices=['json', 'csv', 'txt', 'all'], default='all',
                       help='输出格式 (默认: all)')
    parser.add_argument('--headless', action='store_true', help='使用无头模式')
    parser.add_argument('--scroll-pause', type=int, default=2, help='滚动间隔时间（秒）')
    parser.add_argument('--output', help='输出文件名（不含扩展名）')
    
    args = parser.parse_args()
    
    scraper = YouTubeCommentScraperImproved(headless=args.headless, scroll_pause_time=args.scroll_pause)
    
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
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.close()

if __name__ == "__main__":
    main()