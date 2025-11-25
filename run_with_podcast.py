#!/usr/bin/env python3
# coding=utf-8
"""
一键运行：爬虫 + 播客生成 + HTML集成
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(description, command, allow_failure=False):
    """运行命令并显示进度"""
    print("\n" + "=" * 60)
    print(f"🔄 {description}")
    print("=" * 60)

    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=False
        )
        print(f"✅ {description} - 完成")
        return True
    except subprocess.CalledProcessError as e:
        if allow_failure:
            print(f"⚠️  {description} - 失败（继续执行）")
            return False
        else:
            print(f"❌ {description} - 失败")
            sys.exit(1)


def main():
    """主函数"""
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║   TrendRadar - 新闻爬取 + 播客生成 + HTML集成           ║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")

    # 检查 API Key
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print("\n❌ 错误: 未找到 OPENROUTER_API_KEY 环境变量")
        print("请先设置: export OPENROUTER_API_KEY='your-api-key'")
        print("\n或者在代码中设置:")
        print("  import os")
        print("  os.environ['OPENROUTER_API_KEY'] = 'your-key'")
        sys.exit(1)

    print(f"\n✅ API Key 已配置: {api_key[:20]}...")

    # 步骤1: 运行爬虫
    run_command(
        "步骤 1/3: 运行爬虫，获取最新新闻",
        "python main.py"
    )

    # 步骤2: 生成播客
    run_command(
        "步骤 2/3: 生成播客音频",
        "python generate_podcast_auto.py",
        allow_failure=True  # 允许失败，继续执行
    )

    # 步骤3: 重新生成HTML
    run_command(
        "步骤 3/3: 重新生成HTML（集成音频播放器）",
        "python main.py"
    )

    # 完成
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║                     ✅ 完成！                            ║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")

    # 显示生成的文件
    print("\n📂 生成的文件:")
    print("   - HTML报告: index.html")

    # 查找最新的音频文件
    from datetime import datetime
    import pytz

    beijing_tz = pytz.timezone("Asia/Shanghai")
    date_str = datetime.now(beijing_tz).strftime("%Y年%m月%d日")
    audio_dir = Path("output") / date_str / "audio"

    if audio_dir.exists():
        audio_files = sorted(audio_dir.glob("*.mp3"))
        if audio_files:
            print(f"   - 音频文件: {audio_dir}/")
            for audio_file in audio_files:
                size_kb = audio_file.stat().st_size / 1024
                print(f"      • {audio_file.name} ({size_kb:.1f} KB)")
        else:
            print(f"   - 音频文件: 未生成")

    print("\n💡 打开 index.html 即可看到带播放器的新闻报告")
    print(f"   file://{Path('index.html').resolve()}")


if __name__ == "__main__":
    main()
