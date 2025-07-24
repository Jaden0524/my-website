# YouTube评论抓取器

一个功能强大的YouTube视频评论抓取工具，能够自动抓取YouTube视频下的所有评论，包括回复。支持自动滚动、展开回复，并将结果保存为多种格式的文件。

## 功能特点

- ✅ **完整评论抓取**: 抓取视频下的所有评论和回复
- ✅ **自动滚动**: 自动滚动页面加载所有评论
- ✅ **展开回复**: 自动点击"显示回复"按钮展开所有回复
- ✅ **多种输出格式**: 支持JSON、CSV、TXT格式输出
- ✅ **去重处理**: 自动去除重复评论
- ✅ **详细信息**: 抓取评论者ID、评论时间、评论内容
- ✅ **无头模式**: 支持后台运行，不显示浏览器界面
- ✅ **自动驱动管理**: 使用webdriver-manager自动管理ChromeDriver

## 安装要求

- Python 3.6+
- Chrome浏览器
- 网络连接

## 快速安装

### 方法1: 使用快速安装脚本（推荐）

```bash
python3 quick_setup.py
```

### 方法2: 手动安装

1. 安装Python依赖：
```bash
pip3 install -r requirements.txt
```

2. 安装Chrome浏览器（如果未安装）：
```bash
# Ubuntu/Debian
sudo apt-get install google-chrome-stable

# 或者下载安装包
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

## 使用方法

### 命令行使用

#### 基本使用
```bash
python3 youtube_comment_scraper_improved.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

#### 指定输出格式
```bash
# 只输出JSON格式
python3 youtube_comment_scraper_improved.py "VIDEO_URL" --format json

# 只输出CSV格式
python3 youtube_comment_scraper_improved.py "VIDEO_URL" --format csv

# 只输出TXT格式
python3 youtube_comment_scraper_improved.py "VIDEO_URL" --format txt

# 输出所有格式（默认）
python3 youtube_comment_scraper_improved.py "VIDEO_URL" --format all
```

#### 使用无头模式（后台运行）
```bash
python3 youtube_comment_scraper_improved.py "VIDEO_URL" --headless
```

#### 自定义滚动间隔
```bash
python3 youtube_comment_scraper_improved.py "VIDEO_URL" --scroll-pause 3
```

#### 指定输出文件名
```bash
python3 youtube_comment_scraper_improved.py "VIDEO_URL" --output my_comments
```

### 编程使用

```python
from youtube_comment_scraper_improved import YouTubeCommentScraperImproved

# 创建抓取器实例
scraper = YouTubeCommentScraperImproved(headless=True, scroll_pause_time=2)

try:
    # 抓取评论
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    comments = scraper.scrape_comments(video_url)
    
    # 保存结果
    scraper.save_to_json("comments.json")
    scraper.save_to_csv("comments.csv")
    scraper.save_to_txt("comments.txt")
    
    print(f"成功抓取 {len(comments)} 条评论")
    
finally:
    scraper.close()
```

## 输出格式说明

### JSON格式
```json
{
  "total_comments": 150,
  "extracted_at": "2024-01-01T12:00:00",
  "comments": [
    {
      "author": "用户名",
      "time": "2天前",
      "content": "评论内容",
      "is_reply": false,
      "extracted_at": "2024-01-01T12:00:00"
    }
  ]
}
```

### CSV格式
包含以下字段：
- `author`: 评论者用户名
- `time`: 评论时间
- `content`: 评论内容
- `is_reply`: 是否为回复（true/false）
- `extracted_at`: 抓取时间

### TXT格式
人类可读的文本格式，包含所有评论信息，回复会有缩进标识。

## 命令行参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `url` | YouTube视频URL（必需） | - |
| `--format` | 输出格式：json, csv, txt, all | all |
| `--headless` | 使用无头模式 | False |
| `--scroll-pause` | 滚动间隔时间（秒） | 2 |
| `--output` | 输出文件名（不含扩展名） | 自动生成时间戳 |

## 注意事项

1. **遵守YouTube服务条款**: 请确保您的使用符合YouTube的服务条款和robots.txt规定。

2. **适度使用**: 避免过于频繁的请求，建议在请求之间添加适当的延迟。

3. **网络连接**: 确保网络连接稳定，抓取大量评论可能需要较长时间。

4. **浏览器资源**: 抓取过程会占用一定的系统资源，建议在抓取大量评论时使用无头模式。

5. **评论数量**: 对于评论数量特别多的视频，抓取时间会相应增加。

## 故障排除

### 常见问题

**Q: 提示"Chrome驱动初始化失败"**
A: 确保已安装Chrome浏览器，程序会自动下载对应版本的ChromeDriver。

**Q: 抓取到的评论数量很少**
A: 可能是网络问题或页面加载缓慢，尝试增加`--scroll-pause`参数的值。

**Q: 程序运行很慢**
A: 使用`--headless`参数启用无头模式可以提高性能。

**Q: 某些评论无法抓取**
A: YouTube的页面结构可能发生变化，或者某些评论被限制显示。

### 错误日志

程序运行时会输出详细的日志信息，包括：
- 页面加载状态
- 滚动进度
- 回复展开情况
- 评论提取进度

## 版本说明

- `youtube_comment_scraper.py`: 基础版本
- `youtube_comment_scraper_improved.py`: 改进版本（推荐使用）
  - 使用webdriver-manager自动管理ChromeDriver
  - 更好的错误处理
  - 优化的选择器策略
  - 改进的去重逻辑

## 许可证

本项目仅供学习和研究使用。使用时请遵守相关法律法规和平台服务条款。

## 贡献

欢迎提交Issues和Pull Requests来改进这个项目。

---

**免责声明**: 本工具仅用于学习和研究目的。用户应确保其使用符合YouTube的服务条款和适用的法律法规。作者不对任何不当使用承担责任。