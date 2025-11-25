# GitHub Workflow 简化方案 - 带播客的 index.html

## 🎯 目标

在 GitHub Actions 中自动生成一个**带播客音频**的 `index.html`，部署到 GitHub Pages。

**特点**：
- ✅ 精简内容：每个平台取10条新闻
- ✅ 自动生成播客音频
- ✅ 音频播放器集成在 index.html 中
- ✅ 一次运行完成所有步骤

## 🚀 快速开始

### 1. 配置 GitHub Secrets

在你的 GitHub 仓库中：

```
Settings → Secrets and variables → Actions → New repository secret
```

添加：
- **Name**: `OPENROUTER_API_KEY`
- **Value**: `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`

### 2. 修改 workflow 文件

编辑 `.github/workflows/crawler.yml`（或你的 workflow 文件），将原来的步骤替换为：

```yaml
name: Generate News with Podcast

on:
  schedule:
    - cron: '0 */2 * * *'  # 每2小时运行
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Fetch news
        run: python main.py

      - name: Generate podcast and index.html
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: python generate_index_with_podcast.py

      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add output/ index.html
          git commit -m "Auto update $(date)" || exit 0
          git push
```

### 3. 完成！

提交 workflow 文件后，GitHub Actions 会自动运行，生成带播客的 index.html。

## 📋 脚本说明

### `generate_index_with_podcast.py`

这个脚本做了以下事情：

```
1. 读取最新的新闻数据
   ↓
2. 简化内容（每个平台取10条新闻）
   ↓
3. 调用 DeepSeek V3 生成播客脚本
   ↓
4. 使用 Edge TTS 生成音频 (podcast.mp3)
   ↓
5. 生成 index.html（自动包含音频播放器）
```

### 关键参数

```python
# 每个平台取多少条新闻
max_items_per_platform=10

# 音频文件名（固定）
audio_filename = "podcast.mp3"

# 音频位置
output/2025年11月25日/audio/podcast.mp3
```

## 📂 生成的文件结构

```
TrendRadar/
├── index.html                      ← 带播客播放器的首页
└── output/
    └── 2025年11月25日/
        ├── txt/
        │   └── 22时09分.txt        ← 原始新闻数据
        └── audio/
            ├── podcast.mp3          ← 播客音频
            └── podcast_script.txt   ← 播客脚本
```

## 🎨 index.html 效果

```
┌────────────────────────────────────────────┐
│         热点新闻分析                        │
│  ┌──────────────────────────────────────┐  │
│  │ 🎧 播客音频                           │  │
│  │ [====○────] 01:23 / 03:45  ⏯       │  │ ← 播放器
│  └──────────────────────────────────────┘  │
│  报告类型: 定时报告                        │
│  新闻总数: 50 条                          │
└────────────────────────────────────────────┘
   新闻内容（精简版，每个平台10条）...
```

## 🔧 本地测试

```bash
# 1. 设置 API Key
export OPENROUTER_API_KEY="your-key"

# 2. 运行爬虫
python main.py

# 3. 生成带播客的 index.html
python generate_index_with_podcast.py

# 4. 打开查看
open index.html
```

## ⚙️ 自定义配置

### 修改每个平台的新闻数量

编辑 `generate_index_with_podcast.py` 第 155 行：

```python
news_data = parse_and_simplify_news(news_content, max_items_per_platform=10)
#                                                                      ^^^
#                                                                      改为你想要的数量
```

### 修改播客风格

编辑 `generate_index_with_podcast.py` 第 100 行的 prompt：

```python
prompt = f"""你是一位专业的播客主播...
要求：
1. 语言风格轻松、口语化  ← 修改这里
2. ...
```

### 修改语音

编辑 `generate_index_with_podcast.py` 第 182 行：

```python
communicate = edge_tts.Communicate(script, "zh-CN-YunyangNeural")
#                                          ^^^^^^^^^^^^^^^^^^^
#                                          改为其他语音
```

可用语音：
- `zh-CN-XiaoxiaoNeural` - 女声，温柔
- `zh-CN-YunxiNeural` - 男声，沉稳
- `zh-CN-YunyangNeural` - 男声，新闻播报（默认）

## 💰 成本估算

- DeepSeek V3 API: ~$0.001/次
- Edge TTS: 免费
- **总计**: ~$0.001/次（约 0.007 元人民币）

每2小时运行一次，每天12次，月成本约 **$0.36**（约 2.5 元人民币）

## 🐛 故障排除

### 问题1: index.html 没有播放器

**检查**：
```bash
# 检查音频文件是否生成
ls -lh output/*/audio/podcast.mp3

# 检查 HTML 中是否有 audio 标签
grep "audio controls" index.html
```

### 问题2: 音频生成失败

**可能原因**：
1. edge-tts 未安装：在 requirements.txt 中已包含
2. 网络问题：检查 GitHub Actions 日志
3. API Key 错误：检查 Secrets 配置

### 问题3: GitHub Actions 失败

**查看日志**：
```
Actions → 最近的运行 → 点击查看详细日志
```

常见错误：
- `OPENROUTER_API_KEY not found` → 检查 Secrets 配置
- `ModuleNotFoundError: edge_tts` → 检查 requirements.txt

## 📚 完整流程图

```
GitHub Actions 触发（定时或手动）
          ↓
安装 Python 和依赖
          ↓
运行 main.py（爬取新闻）
          ↓
output/2025年11月25日/txt/22时09分.txt
          ↓
运行 generate_index_with_podcast.py
          ↓
    ┌─────┴─────┐
    ↓           ↓
读取新闻    调用 AI
简化内容    生成脚本
    ↓           ↓
    └─────┬─────┘
          ↓
    生成音频 (Edge TTS)
          ↓
output/2025年11月25日/audio/podcast.mp3
          ↓
    生成 index.html
    （包含播放器）
          ↓
    index.html
          ↓
Git commit & push
          ↓
GitHub Pages 自动部署
          ↓
    ✅ 完成！
```

## ✨ 优势

1. **简化流程**：只需运行一个脚本，自动生成带播客的 index.html
2. **固定文件名**：音频文件名固定为 `podcast.mp3`，便于引用
3. **精简内容**：每个平台10条新闻，减少 API 调用和音频长度
4. **GitHub Actions 友好**：环境变量管理，错误处理完善
5. **即时部署**：生成的 index.html 可直接用于 GitHub Pages

## 🎉 总结

这个方案实现了：
- ✅ 一个脚本完成所有步骤
- ✅ index.html 直接包含播放器
- ✅ 内容精简（每平台10条）
- ✅ GitHub Actions 集成简单
- ✅ 成本低廉（~$0.001/次）

现在你的 GitHub workflow 只需要两个步骤：
1. `python main.py` - 爬取新闻
2. `python generate_index_with_podcast.py` - 生成带播客的 index.html

就这么简单！🚀
