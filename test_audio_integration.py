#!/usr/bin/env python3
# coding=utf-8
"""
测试音频播放器集成
"""

from pathlib import Path
from main import (
    generate_html_report,
    format_date_folder,
    format_time_filename,
    ensure_directory_exists
)


def test_audio_integration():
    """测试音频播放器集成"""
    print("=" * 60)
    print("🧪 测试音频播放器集成")
    print("=" * 60)

    # 准备测试数据
    date_folder = format_date_folder()
    time_filename = format_time_filename()

    # 创建测试音频文件
    audio_dir = Path("output") / date_folder / "audio"
    ensure_directory_exists(str(audio_dir))

    audio_path = audio_dir / f"{time_filename}.mp3"
    # 创建一个非空的测试文件
    with open(audio_path, 'wb') as f:
        f.write(b'test audio data')

    print(f"✅ 创建测试音频文件: {audio_path}")
    print(f"📂 文件大小: {audio_path.stat().st_size} bytes")

    # 准备测试数据
    stats = [
        {
            'word': '测试热点',
            'count': 3,
            'position': 0,
            'percentage': 100.0,
            'titles': [
                {
                    'title': '这是一条测试新闻标题',
                    'source_name': '测试平台',
                    'first_time': time_filename,
                    'last_time': time_filename,
                    'time_display': time_filename,
                    'count': 1,
                    'ranks': [1],
                    'rank_threshold': 10,
                    'url': 'https://example.com',
                    'mobileUrl': '',
                    'is_new': False
                }
            ]
        }
    ]

    print("\n📝 生成测试 HTML...")
    html_file = generate_html_report(
        stats,
        total_titles=1,
        mode='daily',
        is_daily_summary=False
    )

    print(f"✅ HTML 文件已生成: {html_file}")

    # 验证 HTML 内容
    print("\n🔍 验证 HTML 内容...")
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    tests_passed = 0
    tests_total = 0

    # 测试1: 检查音频播放器容器
    tests_total += 1
    if 'class="audio-player-container"' in content:
        print("✅ 测试1: 音频播放器容器存在")
        tests_passed += 1
    else:
        print("❌ 测试1: 未找到音频播放器容器")

    # 测试2: 检查音频文件引用
    tests_total += 1
    if f'{time_filename}.mp3' in content:
        print(f"✅ 测试2: 音频文件引用正确 ({time_filename}.mp3)")
        tests_passed += 1
    else:
        print(f"❌ 测试2: 未找到音频文件引用")

    # 测试3: 检查音频播放器标签
    tests_total += 1
    if '<audio controls' in content:
        print("✅ 测试3: HTML audio 标签存在")
        tests_passed += 1
    else:
        print("❌ 测试3: 未找到 audio 标签")

    # 测试4: 检查播客图标和标签
    tests_total += 1
    if '🎧' in content and '播客音频' in content:
        print("✅ 测试4: 播客标签和图标存在")
        tests_passed += 1
    else:
        print("❌ 测试4: 未找到播客标签")

    # 测试5: 检查 CSS 样式
    tests_total += 1
    if '.audio-player-container' in content and '.audio-player {' in content:
        print("✅ 测试5: 音频播放器 CSS 样式存在")
        tests_passed += 1
    else:
        print("❌ 测试5: 未找到 CSS 样式")

    # 显示音频播放器代码片段
    print("\n📄 HTML 音频播放器代码片段:")
    print("-" * 60)
    import re
    audio_match = re.search(
        r'<div class="audio-player-container">.*?</div>\s*</div>',
        content,
        re.DOTALL
    )
    if audio_match:
        snippet = audio_match.group(0)
        # 格式化输出
        lines = snippet.split('\n')
        for line in lines[:15]:  # 只显示前15行
            print(line)
        if len(lines) > 15:
            print("    ...")
    else:
        print("未找到音频播放器代码")
    print("-" * 60)

    # 总结
    print("\n" + "=" * 60)
    print(f"测试完成: {tests_passed}/{tests_total} 通过")
    print("=" * 60)

    if tests_passed == tests_total:
        print("🎉 所有测试通过！音频播放器集成成功！")
        print(f"\n💡 打开以下文件查看效果:")
        print(f"   file://{Path(html_file).resolve()}")
        return True
    else:
        print(f"⚠️  {tests_total - tests_passed} 个测试失败")
        return False


if __name__ == "__main__":
    success = test_audio_integration()
    exit(0 if success else 1)
