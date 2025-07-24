#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube评论抓取器使用示例
"""

from youtube_comment_scraper import YouTubeCommentScraper

def simple_usage_example():
    """简单使用示例"""
    # YouTube视频URL示例
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # 请替换为实际的视频URL
    
    # 创建抓取器实例
    scraper = YouTubeCommentScraper(headless=True, scroll_pause_time=2)
    
    try:
        print("开始抓取评论...")
        comments = scraper.scrape_comments(video_url)
        
        if comments:
            print(f"成功抓取到 {len(comments)} 条评论")
            
            # 保存为不同格式
            scraper.save_to_json("my_comments.json")
            scraper.save_to_csv("my_comments.csv")
            scraper.save_to_txt("my_comments.txt")
            
            # 打印前几条评论作为示例
            print("\n前5条评论:")
            for i, comment in enumerate(comments[:5], 1):
                reply_prefix = "    ↳ " if comment["is_reply"] else ""
                print(f"{reply_prefix}{i}. {comment['author']}")
                print(f"{reply_prefix}   时间: {comment['time']}")
                print(f"{reply_prefix}   内容: {comment['content'][:100]}...")
                print()
        else:
            print("未找到任何评论")
            
    except Exception as e:
        print(f"发生错误: {e}")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    simple_usage_example()