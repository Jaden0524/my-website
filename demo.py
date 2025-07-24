#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube评论抓取器演示脚本
展示如何使用抓取器的各种功能
"""

from youtube_comment_scraper_improved import YouTubeCommentScraperImproved
import time

def demo_basic_usage():
    """基本使用演示"""
    print("=== YouTube评论抓取器演示 ===")
    print()
    
    # 示例视频URL（请替换为实际的YouTube视频URL）
    demo_url = input("请输入YouTube视频URL (或按回车使用默认测试URL): ").strip()
    
    if not demo_url:
        demo_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        print(f"使用默认测试URL: {demo_url}")
    
    print(f"\n开始抓取视频评论: {demo_url}")
    print("注意：这可能需要几分钟时间，请耐心等待...")
    
    # 创建抓取器实例
    scraper = YouTubeCommentScraperImproved(
        headless=True,           # 使用无头模式，不显示浏览器窗口
        scroll_pause_time=2      # 滚动间隔2秒
    )
    
    try:
        # 抓取评论
        start_time = time.time()
        comments = scraper.scrape_comments(demo_url)
        end_time = time.time()
        
        if comments:
            print(f"\n✅ 抓取成功！")
            print(f"📊 总共抓取到 {len(comments)} 条评论")
            print(f"⏱️ 耗时: {end_time - start_time:.1f} 秒")
            
            # 统计信息
            reply_count = sum(1 for comment in comments if comment['is_reply'])
            main_comment_count = len(comments) - reply_count
            
            print(f"💬 主评论: {main_comment_count} 条")
            print(f"↳ 回复: {reply_count} 条")
            
            # 显示前几条评论作为示例
            print(f"\n📝 前5条评论预览:")
            print("-" * 50)
            
            for i, comment in enumerate(comments[:5], 1):
                prefix = "    ↳ " if comment["is_reply"] else ""
                print(f"{prefix}[{i}] 👤 {comment['author']}")
                print(f"{prefix}    🕐 {comment['time']}")
                
                # 限制显示内容长度
                content = comment['content']
                if len(content) > 100:
                    content = content[:100] + "..."
                print(f"{prefix}    💭 {content}")
                print()
            
            # 保存文件
            print("💾 保存文件...")
            timestamp = int(time.time())
            
            json_file = scraper.save_to_json(f"youtube_comments_{timestamp}.json")
            csv_file = scraper.save_to_csv(f"youtube_comments_{timestamp}.csv")
            txt_file = scraper.save_to_txt(f"youtube_comments_{timestamp}.txt")
            
            print(f"✅ 文件保存完成:")
            print(f"   📄 JSON: {json_file}")
            print(f"   📊 CSV:  {csv_file}")
            print(f"   📝 TXT:  {txt_file}")
            
            # 提供进一步分析建议
            print(f"\n💡 接下来你可以:")
            print(f"   1. 用Excel或其他工具打开CSV文件进行数据分析")
            print(f"   2. 用文本编辑器查看TXT文件")
            print(f"   3. 用编程语言读取JSON文件进行进一步处理")
            
        else:
            print("\n❌ 未能抓取到任何评论")
            print("可能的原因:")
            print("  - 该视频没有评论或评论被禁用")
            print("  - 网络连接问题")
            print("  - YouTube页面结构发生变化")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断了抓取过程")
        
    except Exception as e:
        print(f"\n❌ 抓取过程中发生错误: {e}")
        print("请检查:")
        print("  1. 网络连接是否正常")
        print("  2. YouTube URL是否正确")
        print("  3. Chrome浏览器是否已安装")
        
    finally:
        # 清理资源
        scraper.close()
        print("\n🔄 资源清理完成")

def demo_advanced_usage():
    """高级使用演示"""
    print("\n=== 高级功能演示 ===")
    
    # 演示不同的配置选项
    configurations = [
        {
            "name": "快速模式",
            "headless": True,
            "scroll_pause_time": 1,
            "description": "适合快速抓取，但可能遗漏一些评论"
        },
        {
            "name": "标准模式", 
            "headless": True,
            "scroll_pause_time": 2,
            "description": "平衡速度和完整性"
        },
        {
            "name": "完整模式",
            "headless": True,
            "scroll_pause_time": 3,
            "description": "较慢但更完整"
        }
    ]
    
    print("可用的配置模式:")
    for i, config in enumerate(configurations, 1):
        print(f"  {i}. {config['name']}: {config['description']}")
    
    choice = input("\n选择配置模式 (1-3, 或按回车使用标准模式): ").strip()
    
    if choice in ['1', '2', '3']:
        selected_config = configurations[int(choice) - 1]
    else:
        selected_config = configurations[1]  # 默认使用标准模式
    
    print(f"使用 {selected_config['name']} 配置")

def main():
    """主函数"""
    print("🎬 YouTube评论抓取器 - 演示程序")
    print("=" * 40)
    
    try:
        demo_basic_usage()
        
        # 询问是否进行高级演示
        if input("\n是否查看高级功能演示? (y/n): ").lower() == 'y':
            demo_advanced_usage()
            
    except KeyboardInterrupt:
        print("\n\n👋 演示程序已退出")
    
    print("\n感谢使用YouTube评论抓取器！")
    print("如有问题，请查看README.md或使用指南.md")

if __name__ == "__main__":
    main()