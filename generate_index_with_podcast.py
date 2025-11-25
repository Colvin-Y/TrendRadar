#!/usr/bin/env python3
# coding=utf-8
"""
为 GitHub Pages 生成带播客的 index.html
- 精简版：每个主题取10条新闻
- 生成播客音频
- 在 index.html 中集成播放器
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import pytz
import requests
from typing import Optional
import asyncio


def get_beijing_time():
    """获取北京时间"""
    return datetime.now(pytz.timezone("Asia/Shanghai"))


def format_date_folder():
    """格式化日期文件夹"""
    return get_beijing_time().strftime("%Y年%m月%d日")


def ensure_directory_exists(directory: str):
    """确保目录存在"""
    Path(directory).mkdir(parents=True, exist_ok=True)


def read_latest_news_for_summary() -> Optional[str]:
    """读取最新的新闻文件用于生成摘要"""
    date_folder = format_date_folder()
    txt_dir = Path("output") / date_folder / "txt"

    if not txt_dir.exists():
        print(f"❌ 目录不存在: {txt_dir}")
        return None

    txt_files = sorted([f for f in txt_dir.iterdir() if f.suffix == ".txt"])
    if not txt_files:
        print(f"❌ 没有找到txt文件")
        return None

    latest_file = txt_files[-1]
    print(f"✅ 读取新闻文件: {latest_file.name}")

    with open(latest_file, "r", encoding="utf-8") as f:
        content = f.read()

    return content


def parse_and_simplify_news(news_content: str, max_items_per_platform: int = 10) -> list:
    """解析并简化新闻内容"""
    lines = news_content.strip().split("\n")

    news_data = []
    current_platform = ""
    current_platform_news = []

    for line in lines:
        line = line.strip()
        if not line or "==== 以下ID请求失败 ====" in line:
            continue

        # 检测平台名称行
        if not line[0].isdigit() and ("|" in line or "[" not in line):
            # 保存上一个平台的数据
            if current_platform_news and current_platform:
                news_data.append({
                    "platform": current_platform,
                    "items": current_platform_news[:max_items_per_platform]
                })
                current_platform_news = []

            # 解析新平台
            if "|" in line:
                parts = line.split("|")
                current_platform = parts[1].strip() if len(parts) > 1 else parts[0].strip()
            else:
                current_platform = line

        elif line[0].isdigit() and ". " in line:
            # 新闻条目行
            title = line.split(". ", 1)[1]
            # 移除URL链接部分
            if "[URL:" in title:
                title = title.split("[URL:")[0].strip()
            if "[MOBILE:" in title:
                title = title.split("[MOBILE:")[0].strip()

            current_platform_news.append(title)

    # 处理最后一个平台
    if current_platform_news and current_platform:
        news_data.append({
            "platform": current_platform,
            "items": current_platform_news[:max_items_per_platform]
        })

    return news_data


def generate_podcast_script_with_ai(news_data: list, api_key: str) -> Optional[str]:
    """使用 OpenRouter qwen-2.5-72b-instruct 生成播客脚本"""

    # 构建提示词, 平台都取，当然用户可以调整 news_data 的数据来减少内容
    news_summary = ""
    for platform_data in news_data:
        platform = platform_data["platform"]
        items = platform_data["items"]
        news_summary += f"\n【{platform}】\n"
        for i, item in enumerate(items, 1):
            news_summary += f"{i}. {item}\n"

    prompt = f"""你是一位专业的播客主播，名字叫小严新闻联播，需要将以下新闻热点改编成一篇自然、流畅的播客稿。

要求：
1. 语言风格专业，像在听新闻联播
2. 每条新闻要简洁精炼，突出关键信息
3. 平台之间的过渡要自然
4. 开头要有欢迎语，结尾要有总结
5. 总时长控制在5-10分钟（约1200-2400字）
6. 避免使用过度专业的术语确保播客内容对一般听众也有价值


新闻内容：
{news_summary}

请直接输出播客稿，不要有其他说明文字，不要用Markdown格式以保证tts友好"""

    print("🤖 正在调用 qwen-2.5-72b-instruct 生成播客脚本...")

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "qwen/qwen-2.5-72b-instruct",  # 使用 Qwen 2.5 72B
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,  # 提高温度让内容更有创意
                "max_tokens": 3500,  # 增加 token 限制以支持更长内容
            },
            timeout=90  # 增加超时时间
        )

        if response.status_code == 200:
            result = response.json()
            script = result["choices"][0]["message"]["content"]
            print("✅ AI 脚本生成成功")
            return script
        else:
            print(f"❌ API 调用失败: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ 生成脚本时出错: {e}")
        return None


def generate_audio_with_edge_tts(script: str, output_path: Path) -> bool:
    """使用 Edge TTS 生成音频"""
    try:
        print("🎙️  使用 Edge TTS 生成音频...")

        import edge_tts

        async def generate():
            communicate = edge_tts.Communicate(script, "zh-CN-YunyangNeural")
            await communicate.save(str(output_path))

        asyncio.run(generate())
        print(f"✅ 音频生成成功: {output_path}")
        return True

    except ImportError:
        print("⚠️  edge-tts 未安装，跳过音频生成")
        return False
    except Exception as e:
        print(f"❌ 生成音频时出错: {e}")
        return False


def generate_index_html_with_podcast(news_data: list, audio_filename: str):
    """生成带播客的 index.html"""
    from main import render_html_content, prepare_report_data

    # 将简化的新闻数据转换为 stats 格式
    stats = []
    for platform_data in news_data:
        for idx, title in enumerate(platform_data["items"]):
            stats.append({
                'word': title[:20],  # 取标题前20字作为关键词
                'count': 1,
                'position': idx,
                'percentage': 100.0,
                'titles': [{
                    'title': title,
                    'source_name': platform_data["platform"],
                    'first_time': get_beijing_time().strftime("%H时%M分"),
                    'last_time': get_beijing_time().strftime("%H时%M分"),
                    'time_display': get_beijing_time().strftime("%H时%M分"),
                    'count': 1,
                    'ranks': [idx + 1],
                    'rank_threshold': 10,
                    'url': '',
                    'mobileUrl': '',
                    'is_new': False
                }]
            })

    total_titles = sum(len(p["items"]) for p in news_data)

    report_data = prepare_report_data(stats, None, None, None, "daily")

    # 设置音频文件路径（相对于 index.html）
    date_folder = format_date_folder()
    audio_file = f"output/{date_folder}/audio/{audio_filename}"

    html_content = render_html_content(
        report_data,
        total_titles,
        is_daily_summary=False,  # 改为 False，这样会显示播放器
        mode="daily",
        update_info=None,
        audio_file=audio_file
    )

    # 写入 index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ index.html 已生成（包含音频播放器）")


def main():
    """主函数"""
    print("=" * 60)
    print("🎙️  生成带播客的 index.html for GitHub Pages")
    print("=" * 60)

    # 1. 检查 API Key
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print("❌ 错误: 未找到 OPENROUTER_API_KEY 环境变量")
        return 1

    # 2. 读取最新新闻
    news_content = read_latest_news_for_summary()
    if not news_content:
        print("❌ 无法读取新闻内容")
        return 1

    # 3. 解析并简化新闻（每个平台取10条）
    print("📝 解析新闻内容（每个平台取10条）...")
    news_data = parse_and_simplify_news(news_content, max_items_per_platform=10)
    print(f"✅ 解析到 {len(news_data)} 个平台的新闻")

    # 4. 准备音频文件路径
    date_folder = format_date_folder()
    audio_dir = Path("output") / date_folder / "audio"
    ensure_directory_exists(str(audio_dir))

    audio_filename = "podcast.mp3"  # 固定文件名
    audio_path = audio_dir / audio_filename
    script_path = audio_dir / "podcast_script.txt"

    # 5. 生成播客脚本
    script = generate_podcast_script_with_ai(news_data, api_key)
    if not script:
        print("❌ 脚本生成失败")
        return 1

    # 保存脚本
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)
    print(f"✅ 播客脚本已保存: {script_path}")

    # 6. 生成音频
    audio_generated = generate_audio_with_edge_tts(script, audio_path)

    if not audio_generated:
        print("⚠️  音频生成失败，但会继续生成 HTML")
        # 创建一个空文件占位
        audio_path.touch()

    # 7. 生成 index.html
    print("📄 生成 index.html...")
    generate_index_html_with_podcast(news_data, audio_filename)

    # 8. 完成
    print("\n" + "=" * 60)
    print("✅ 完成！")
    print("=" * 60)
    print(f"📝 播客脚本: {script_path}")
    if audio_path.exists():
        print(f"🎵 音频文件: {audio_path} ({audio_path.stat().st_size / 1024:.1f} KB)")
    print(f"📄 首页: index.html")
    print("\n💡 index.html 已包含音频播放器，可直接部署到 GitHub Pages")

    return 0


if __name__ == "__main__":
    sys.exit(main())
