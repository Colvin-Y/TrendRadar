#!/usr/bin/env python3
# coding=utf-8
"""
音频生成辅助脚本
使用 OpenRouter (DeepSeek V3) + TTS 为新闻汇总生成播客音频
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import pytz
import requests
from typing import Optional, Tuple


def get_beijing_time():
    """获取北京时间"""
    return datetime.now(pytz.timezone("Asia/Shanghai"))


def format_date_folder():
    """格式化日期文件夹"""
    return get_beijing_time().strftime("%Y年%m月%d日")


def format_time_filename():
    """格式化时间文件名"""
    return get_beijing_time().strftime("%H时%M分")


def ensure_directory_exists(directory: str):
    """确保目录存在"""
    Path(directory).mkdir(parents=True, exist_ok=True)


def read_latest_news_file() -> Tuple[Optional[str], Optional[str]]:
    """读取最新的新闻txt文件"""
    date_folder = format_date_folder()
    txt_dir = Path("output") / date_folder / "txt"

    if not txt_dir.exists():
        print(f"❌ 错误: 目录不存在 {txt_dir}")
        return None, None

    txt_files = sorted([f for f in txt_dir.iterdir() if f.suffix == ".txt"])
    if not txt_files:
        print(f"❌ 错误: 在 {txt_dir} 中没有找到txt文件")
        return None, None

    latest_file = txt_files[-1]
    print(f"✅ 找到最新新闻文件: {latest_file}")

    with open(latest_file, "r", encoding="utf-8") as f:
        content = f.read()

    return content, latest_file.stem


def parse_news_content(news_content: str) -> list:
    """解析新闻内容，提取关键信息"""
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
                    "items": current_platform_news[:5]  # 只取前5条
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
            "items": current_platform_news[:5]
        })

    return news_data


def generate_podcast_script_with_ai(news_data: list, api_key: str) -> Optional[str]:
    """使用 OpenRouter DeepSeek V3 生成播客脚本"""

    # 构建提示词
    news_summary = ""
    for platform_data in news_data[:5]:  # 只取前5个平台
        platform = platform_data["platform"]
        items = platform_data["items"]
        news_summary += f"\n【{platform}】\n"
        for i, item in enumerate(items, 1):
            news_summary += f"{i}. {item}\n"

    prompt = f"""你是一位专业的播客主播，需要将以下新闻热点改编成一篇自然、流畅的播客稿。

要求：
1. 语言风格轻松、口语化，像在和朋友聊天
2. 每条新闻要简洁精炼，突出关键信息
3. 平台之间的过渡要自然
4. 开头要有欢迎语，结尾要有总结
5. 总时长控制在3-5分钟（约800-1200字）
6. 不要使用太多书面语，要像真人在说话

新闻内容：
{news_summary}

请直接输出播客稿，不要有其他说明文字。"""

    print("🤖 正在调用 OpenRouter DeepSeek V3 生成播客脚本...")

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000,
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            script = result["choices"][0]["message"]["content"]
            print("✅ AI 脚本生成成功")
            return script
        else:
            print(f"❌ API 调用失败: {response.status_code}")
            print(f"响应: {response.text}")
            return None

    except Exception as e:
        print(f"❌ 生成脚本时出错: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_audio_with_openai_tts(script: str, output_path: Path, api_key: str) -> bool:
    """使用 OpenAI TTS 生成音频（如果你有 OpenAI API key）"""
    try:
        print("🎙️  使用 OpenAI TTS 生成音频...")

        # 需要 openai 库
        import openai

        client = openai.OpenAI(api_key=api_key)

        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",  # 可选: alloy, echo, fable, onyx, nova, shimmer
            input=script,
            speed=1.0
        )

        response.stream_to_file(str(output_path))
        print(f"✅ 音频生成成功: {output_path}")
        return True

    except ImportError:
        print("⚠️  openai 库未安装，请运行: pip install openai")
        return False
    except Exception as e:
        print(f"❌ 生成音频时出错: {e}")
        return False


def generate_audio_with_edge_tts(script: str, output_path: Path) -> bool:
    """使用 Edge TTS 生成音频（免费方案）"""
    try:
        print("🎙️  使用 Edge TTS 生成音频...")

        import asyncio
        import edge_tts

        async def generate():
            # 中文语音选项
            # zh-CN-XiaoxiaoNeural - 女声，温柔
            # zh-CN-YunxiNeural - 男声，沉稳
            # zh-CN-YunyangNeural - 男声，新闻播报风格
            communicate = edge_tts.Communicate(script, "zh-CN-YunyangNeural")
            await communicate.save(str(output_path))

        asyncio.run(generate())
        print(f"✅ 音频生成成功: {output_path}")
        return True

    except ImportError:
        print("⚠️  edge-tts 未安装，请运行: pip install edge-tts")
        return False
    except Exception as e:
        print(f"❌ 生成音频时出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_audio_with_gtts(script: str, output_path: Path) -> bool:
    """使用 gTTS 生成音频（简单备选方案）"""
    try:
        print("🎙️  使用 gTTS 生成音频...")
        from gtts import gTTS

        tts = gTTS(text=script, lang='zh-CN', slow=False)
        tts.save(str(output_path))

        print(f"✅ 音频生成成功: {output_path}")
        return True

    except ImportError:
        print("⚠️  gTTS 未安装，请运行: pip install gtts")
        return False
    except Exception as e:
        print(f"❌ 生成音频时出错: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("🎙️  TrendRadar 播客音频生成工具")
    print("=" * 60)

    # 获取 API Key
    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not openrouter_key:
        print("⚠️  未找到 OPENROUTER_API_KEY 环境变量")
        print("请设置环境变量或手动输入 API Key")
        openrouter_key = input("OpenRouter API Key: ").strip()

        if not openrouter_key:
            print("❌ API Key 为空，无法继续")
            return 1

    # 读取最新的新闻文件
    news_content, time_filename = read_latest_news_file()

    if not news_content:
        print("❌ 无法读取新闻内容,程序退出")
        return 1

    # 解析新闻数据
    print("📝 正在解析新闻内容...")
    news_data = parse_news_content(news_content)

    if not news_data:
        print("❌ 未能解析出有效的新闻数据")
        return 1

    print(f"✅ 解析到 {len(news_data)} 个平台的新闻")

    # 准备输出路径
    date_folder = format_date_folder()
    audio_dir = Path("output") / date_folder / "audio"
    ensure_directory_exists(str(audio_dir))

    if not time_filename:
        time_filename = format_time_filename()

    output_path = audio_dir / f"{time_filename}.mp3"
    script_path = audio_dir / f"{time_filename}_script.txt"

    print(f"📂 输出路径: {output_path}")

    # 使用 AI 生成播客脚本
    script = generate_podcast_script_with_ai(news_data, openrouter_key)

    if not script:
        print("❌ 脚本生成失败,程序退出")
        return 1

    # 保存脚本
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)
    print(f"✅ 播客脚本已保存: {script_path}")
    print("\n" + "=" * 60)
    print("播客脚本预览:")
    print("=" * 60)
    print(script[:500] + "..." if len(script) > 500 else script)
    print("=" * 60 + "\n")

    # 选择 TTS 引擎
    print("请选择 TTS 引擎:")
    print("1. Edge TTS (免费，推荐，音质好)")
    print("2. gTTS (免费，音质一般)")
    print("3. OpenAI TTS (需要 OpenAI API Key，音质最好)")
    print("4. 跳过音频生成")

    choice = input("\n请输入选项 (1/2/3/4) [默认: 1]: ").strip() or "1"

    success = False
    if choice == "1":
        success = generate_audio_with_edge_tts(script, output_path)
    elif choice == "2":
        success = generate_audio_with_gtts(script, output_path)
    elif choice == "3":
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        if not openai_key:
            openai_key = input("请输入 OpenAI API Key: ").strip()
        if openai_key:
            success = generate_audio_with_openai_tts(script, output_path, openai_key)
        else:
            print("❌ 未提供 OpenAI API Key")
    elif choice == "4":
        print("⏭️  跳过音频生成")
        success = True
    else:
        print("❌ 无效的选项")

    if success:
        print("\n" + "=" * 60)
        print("✅ 处理完成!")
        print("=" * 60)
        print(f"📝 脚本文件: {script_path}")
        if output_path.exists():
            print(f"🎵 音频文件: {output_path}")
            print(f"📊 文件大小: {output_path.stat().st_size / 1024:.2f} KB")
        print("\n💡 下一步: 运行 main.py 生成包含音频播放器的HTML报告")
        print("   python main.py")
        return 0
    else:
        print("\n⚠️  音频生成失败，但脚本已保存")
        print(f"📝 你可以使用其他工具将脚本转换为音频: {script_path}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
