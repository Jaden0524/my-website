#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube评论抓取器测试脚本
"""

import sys
from youtube_comment_scraper_improved import YouTubeCommentScraperImproved

def test_basic_functionality():
    """测试基本功能"""
    print("YouTube评论抓取器测试")
    print("=" * 30)
    
    # 测试URL（使用一个有评论的短视频）
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - 经典测试视频
    
    print(f"测试URL: {test_url}")
    print("注意：这是一个测试，将使用无头模式运行")
    
    try:
        # 创建抓取器实例（使用无头模式进行测试）
        scraper = YouTubeCommentScraperImproved(headless=True, scroll_pause_time=1)
        
        print("✓ 抓取器初始化成功")
        
        # 测试URL验证
        try:
            video_id = scraper.extract_video_id(test_url)
            print(f"✓ URL解析成功，视频ID: {video_id}")
        except Exception as e:
            print(f"✗ URL解析失败: {e}")
            return False
        
        print("\n开始测试评论抓取...")
        print("注意：这可能需要几分钟时间")
        
        # 抓取评论（限制滚动次数以加快测试）
        comments = scraper.scrape_comments(test_url)
        
        if comments:
            print(f"✓ 成功抓取到 {len(comments)} 条评论")
            
            # 显示前几条评论作为示例
            print("\n前3条评论示例:")
            for i, comment in enumerate(comments[:3], 1):
                prefix = "    ↳ " if comment["is_reply"] else ""
                print(f"{prefix}{i}. 作者: {comment['author']}")
                print(f"{prefix}   时间: {comment['time']}")
                print(f"{prefix}   内容: {comment['content'][:100]}...")
                print()
            
            # 测试保存功能
            print("测试文件保存功能...")
            try:
                json_file = scraper.save_to_json("test_comments.json")
                csv_file = scraper.save_to_csv("test_comments.csv")
                txt_file = scraper.save_to_txt("test_comments.txt")
                
                print(f"✓ JSON文件保存成功: {json_file}")
                print(f"✓ CSV文件保存成功: {csv_file}")
                print(f"✓ TXT文件保存成功: {txt_file}")
                
            except Exception as e:
                print(f"✗ 文件保存失败: {e}")
                return False
            
            print("\n✓ 所有测试通过！")
            return True
            
        else:
            print("✗ 未能抓取到任何评论")
            print("可能的原因:")
            print("- 网络连接问题")
            print("- YouTube页面结构变化")
            print("- 该视频没有评论或评论被禁用")
            return False
            
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 清理资源
        try:
            scraper.close()
            print("✓ 资源清理完成")
        except:
            pass

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)