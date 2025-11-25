# TrendRadar 播客音频功能

## 功能概述

这个功能可以将 TrendRadar 抓取的新闻热点自动转换成播客音频，并在生成的 HTML 报告中添加音频播放器。

## 工作流程

```
新闻爬取 (main.py)
    ↓
生成播客脚本和音频 (generate_podcast_auto.py)
    ↓
生成HTML报告 (main.py 会自动检测并嵌入音频播放器)
```

## 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

主要新增依赖：
- `edge-tts` - 免费的微软 TTS（推荐）
- `gTTS` - Google TTS（备选）
- `openai` - OpenAI TTS（可选，需要 API Key）

### 2. 配置 API Key

#### 本地开发

```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

或创建 `.env` 文件（基于 `.env.example`）：

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

#### GitHub Actions

在 GitHub 仓库的 Settings → Secrets and variables → Actions 中添加：

- `OPENROUTER_API_KEY`: OpenRouter API Key (用于生成播客脚本)

### 3. 运行脚本

#### 交互式模式（本地开发）

```bash
python generate_podcast.py
```

这个脚本会：
1. 读取最新的新闻文件
2. 使用 DeepSeek V3 生成播客脚本
3. 让你选择 TTS 引擎生成音频

#### 自动化模式（GitHub Actions）

```bash
export OPENROUTER_API_KEY="your-key"
python generate_podcast_auto.py
```

这个脚本会：
1. 自动从环境变量读取 API Key
2. 生成播客脚本
3. 使用 Edge TTS 自动生成音频

### 4. 生成包含音频播放器的 HTML

运行主程序生成 HTML：

```bash
python main.py
```

如果对应的音频文件存在，HTML 报告会自动在页面顶部添加音频播放器。

## 文件结构

```
output/
└── 2025年11月25日/
    ├── txt/
    │   └── 20时09分.txt          # 新闻原始数据
    ├── html/
    │   └── 20时09分.html         # HTML报告（包含音频播放器）
    └── audio/
        ├── 20时09分.mp3          # 播客音频
        └── 20时09分_script.txt   # 播客脚本
```

## GitHub Actions 集成

在你的 `.github/workflows/` 中添加播客生成步骤：

```yaml
name: Generate News and Podcast

on:
  schedule:
    - cron: '0 */2 * * *'  # 每2小时运行一次
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
        run: |
          pip install -r requirements.txt

      - name: Run crawler
        run: python main.py

      - name: Generate podcast
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: python generate_podcast_auto.py

      - name: Commit and push
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add output/
          git add index.html
          git commit -m "Auto update: $(date '+%Y-%m-%d %H:%M:%S')" || exit 0
          git push
```

## TTS 引擎对比

| 引擎 | 优点 | 缺点 | 费用 |
|------|------|------|------|
| Edge TTS | 音质好，免费，支持多种语音 | 需要网络 | 免费 |
| gTTS | 简单易用，免费 | 音质一般 | 免费 |
| OpenAI TTS | 音质最好，自然度高 | 需要 API Key | 付费 |

## 语音选项

Edge TTS 支持多种中文语音：

- `zh-CN-XiaoxiaoNeural` - 女声，温柔
- `zh-CN-YunxiNeural` - 男声，沉稳
- `zh-CN-YunyangNeural` - 男声，新闻播报风格（默认）
- `zh-CN-XiaoyiNeural` - 女声，活泼
- `zh-CN-YunjianNeural` - 男声，专业

可以在 `generate_podcast_auto.py` 中修改语音：

```python
communicate = edge_tts.Communicate(script, "zh-CN-XiaoxiaoNeural")  # 改为女声
```

## 故障排除

### 1. 找不到音频文件

确保：
- 先运行 `main.py` 生成新闻数据
- 然后运行 `generate_podcast_auto.py` 生成音频
- 最后再次运行 `main.py` 生成包含音频的 HTML

### 2. API 调用失败

检查：
- OPENROUTER_API_KEY 是否正确设置
- 网络连接是否正常
- API 额度是否充足

### 3. 音频生成失败

尝试：
- 检查是否安装了 edge-tts: `pip install edge-tts`
- 检查网络连接
- 尝试使用 gTTS: 修改代码调用 `generate_audio_with_gtts()`

## API 费用参考

- OpenRouter (DeepSeek V3): 约 $0.001 per request
- Edge TTS: 免费
- gTTS: 免费

每次生成播客的总成本约为 $0.001（仅脚本生成费用）

## 自定义

### 修改播客风格

编辑 `generate_podcast_auto.py` 中的 prompt：

```python
prompt = f"""你是一位专业的播客主播...
要求：
1. 语言风格轻松、口语化
2. ...（修改为你想要的风格）
"""
```

### 修改生成长度

调整 `max_tokens` 参数：

```python
"max_tokens": 2000,  # 增加此值可生成更长的播客
```

## 许可证

MIT License
