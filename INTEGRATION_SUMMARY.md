# TrendRadar 播客功能集成总结

## ✅ 已完成的功能

### 1. HTML 音频播放器集成

已成功修改 `main.py` 的以下函数：

- `render_html_content()` - 添加了 `audio_file` 参数
- `generate_html_report()` - 添加了音频文件检测逻辑
- HTML 样式 - 添加了美观的音频播放器样式

**功能特点：**
- 自动检测对应时间的音频文件
- 在 HTML 页面顶部 header 区域显示播放器
- 使用相对路径引用音频文件 (`../audio/时间.mp3`)
- 玻璃态设计，与页面风格统一
- 带有 🎧 图标和"播客音频"标签

### 2. AI 播客脚本生成

创建了两个脚本：

#### `generate_podcast.py` - 交互式版本
- 支持手动选择 TTS 引擎
- 适合本地开发和测试
- 可以预览生成的脚本

#### `generate_podcast_auto.py` - 自动化版本
- 从环境变量读取 API Key
- 自动使用 Edge TTS 生成音频
- 适合 GitHub Actions 集成

**AI 功能：**
- 使用 OpenRouter 的 DeepSeek V3 模型
- 自动将新闻转换成口语化播客脚本
- 支持自定义播客风格和长度

### 3. TTS 音频生成

支持三种 TTS 引擎：

| 引擎 | 特点 | 推荐度 |
|------|------|--------|
| Edge TTS | 免费、音质好、支持多种中文语音 | ⭐⭐⭐⭐⭐ |
| gTTS | 免费、简单易用、音质一般 | ⭐⭐⭐ |
| OpenAI TTS | 音质最好、需要 API Key、付费 | ⭐⭐⭐⭐ |

### 4. 文件组织结构

```
output/
└── 2025年11月25日/
    ├── txt/
    │   └── 20时09分.txt          # 原始新闻数据
    ├── html/
    │   └── 20时09分.html         # HTML报告（包含音频播放器）
    └── audio/
        ├── 20时09分.mp3          # 播客音频
        └── 20时09分_script.txt   # 播客脚本
```

### 5. 依赖更新

更新了 `requirements.txt`，添加：
- `edge-tts>=6.1.0` - 推荐的 TTS 引擎
- `gTTS>=2.5.0` - 备选 TTS
- `openai>=1.0.0` - 可选的 OpenAI TTS

## 🎯 使用流程

### 本地开发流程

```bash
# 1. 运行爬虫获取新闻
python main.py

# 2. 设置 API Key
export OPENROUTER_API_KEY="your-api-key"

# 3. 生成播客（交互式）
python generate_podcast.py
# 选择 TTS 引擎（推荐选择 1 - Edge TTS）

# 4. 重新生成 HTML（会自动检测音频文件）
python main.py
```

### GitHub Actions 自动化流程

```yaml
- name: Run crawler
  run: python main.py

- name: Generate podcast
  env:
    OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
  run: python generate_podcast_auto.py

- name: Regenerate HTML with audio
  run: python main.py
```

## 📝 配置说明

### 环境变量

**本地开发：**
```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

**GitHub Actions：**
在仓库 Settings → Secrets 中添加：
- `OPENROUTER_API_KEY`

### 语音选项

可在 `generate_podcast_auto.py` 中修改语音：

```python
# 第 221 行
communicate = edge_tts.Communicate(script, "zh-CN-YunyangNeural")
```

可用语音：
- `zh-CN-XiaoxiaoNeural` - 女声，温柔
- `zh-CN-YunxiNeural` - 男声，沉稳
- `zh-CN-YunyangNeural` - 男声，新闻播报风格（默认）

### 脚本风格

可在 `generate_podcast_auto.py` 的 prompt 中自定义：

```python
# 第 124 行开始
prompt = f"""你是一位专业的播客主播...
要求：
1. 语言风格轻松、口语化
2. 每条新闻要简洁精炼
3. ...（自定义你的要求）
"""
```

## 🧪 测试结果

### AI 脚本生成测试

✅ 成功调用 OpenRouter DeepSeek V3
✅ 生成的脚本质量高，口语化自然
✅ 脚本结构完整（开场-正文-结尾）

示例脚本片段：
```
主持人：哈喽大家好！欢迎收听今天的《热点五分钟》，我是你们的老朋友小林...
```

### HTML 集成测试

✅ 音频播放器样式正常
✅ 自动检测音频文件机制工作正常
✅ 相对路径引用正确
✅ 播放器在 header 区域正确显示

### 文件生成测试

✅ 脚本文件正确生成 (`*_script.txt`)
✅ 音频文件路径正确 (`output/日期/audio/*.mp3`)
✅ HTML 文件正确引用音频

## 💡 使用建议

1. **首次使用**：建议先用交互式版本（`generate_podcast.py`）测试，熟悉后再配置自动化

2. **API 费用**：DeepSeek V3 非常便宜（约 $0.001/次），Edge TTS 完全免费

3. **音质选择**：
   - 日常使用：Edge TTS 足够
   - 高质量需求：可考虑 OpenAI TTS
   - 快速测试：gTTS

4. **调试技巧**：
   - 播客脚本会保存为 `*_script.txt`，可以查看和调整
   - 如果音频生成失败，脚本仍会保存，可手动用其他工具生成音频

## 📚 相关文档

- [README_PODCAST.md](./README_PODCAST.md) - 详细使用文档
- [.env.example](./.env.example) - 环境变量配置示例

## 🔧 故障排除

### 问题：HTML 中没有音频播放器

**原因**：生成 HTML 时没有找到对应的音频文件

**解决**：
1. 确保音频文件存在于 `output/日期/audio/时间.mp3`
2. 文件名必须与 HTML 文件名匹配（如 `20时09分.html` 对应 `20时09分.mp3`）
3. 重新运行 `python main.py` 生成 HTML

### 问题：音频生成失败

**可能原因**：
1. edge-tts 未安装：`pip install edge-tts`
2. 网络问题：检查网络连接
3. 脚本为空：检查 API Key 是否正确

### 问题：GitHub Actions 中 API 调用失败

**检查**：
1. Secret `OPENROUTER_API_KEY` 是否正确配置
2. workflow 文件中环境变量传递是否正确
3. 查看 Actions 日志中的详细错误信息

## 🚀 后续优化建议

1. **性能优化**：可以缓存相同新闻的播客脚本，避免重复生成

2. **多语言支持**：可以扩展支持英文播客

3. **自定义模板**：允许用户自定义播客开场和结尾

4. **分段播放**：对于特别长的新闻，可以分段生成多个音频

5. **音频质量**：可以添加背景音乐、音效等后期处理

## ✨ 总结

该集成已经完整实现了从新闻爬取 → AI 脚本生成 → TTS 音频合成 → HTML 展示的完整链路。

主要特点：
- 🤖 AI 驱动，自动化程度高
- 💰 成本低（主要使用免费服务）
- 🎨 界面美观，用户体验好
- 🔧 易于配置和扩展
- 📦 代码结构清晰，易于维护

现在你可以愉快地生成带有音频播放功能的新闻热点播客了！🎉
