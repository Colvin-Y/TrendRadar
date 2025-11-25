#!/bin/bash
# 一键运行爬虫 + 生成播客 + 集成到网页

set -e  # 遇到错误立即退出

echo "════════════════════════════════════════════════════════════"
echo "  TrendRadar - 新闻爬取 + 播客生成 + HTML集成"
echo "════════════════════════════════════════════════════════════"

# 检查 API Key
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ 错误: 未找到 OPENROUTER_API_KEY 环境变量"
    echo "请先设置: export OPENROUTER_API_KEY='your-api-key'"
    exit 1
fi

echo ""
echo "📡 步骤 1/3: 运行爬虫，获取最新新闻..."
echo "──────────────────────────────────────────────────────────"
python main.py

echo ""
echo "🎙️  步骤 2/3: 生成播客音频..."
echo "──────────────────────────────────────────────────────────"
python generate_podcast_auto.py

if [ $? -ne 0 ]; then
    echo "⚠️  播客生成失败，但会继续生成HTML"
fi

echo ""
echo "📄 步骤 3/3: 重新生成HTML（集成音频播放器）..."
echo "──────────────────────────────────────────────────────────"
python main.py

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ 完成！"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📂 生成的文件:"
echo "   - HTML报告: index.html"
echo "   - 音频文件: output/$(date +%Y年%m月%d日)/audio/"
echo ""
echo "💡 打开 index.html 即可看到带播放器的新闻报告"
echo ""
