# 音频文件匹配机制详解

## 🎯 核心原理

HTML 文件和音频文件通过**相同的时间戳**进行匹配。

## 📋 匹配流程

### 1. 生成 HTML 文件

```python
# main.py 第 1689 行
if is_daily_summary:
    filename = "当前榜单汇总.html"  # 或 "当日汇总.html" / "当日增量.html"
else:
    filename = f"{format_time_filename()}.html"  # 例如: "20时09分.html"
```

**生成的文件名**：`20时09分.html`

### 2. 提取时间标识

```python
# main.py 第 1704 行
# 从filename中提取时间（如 "20时09分.html" -> "20时09分"）
time_filename = filename.replace(".html", "")
```

**提取结果**：`20时09分`

### 3. 构建音频文件路径

```python
# main.py 第 1705-1706 行
date_folder = format_date_folder()  # 例如: "2025年11月25日"
audio_path = Path("output") / date_folder / "audio" / f"{time_filename}.mp3"
```

**构建路径**：`output/2025年11月25日/audio/20时09分.mp3`

### 4. 检查文件是否存在

```python
# main.py 第 1708-1713 行
if audio_path.exists():
    # 使用相对路径（从 html 目录到 audio 目录）
    audio_file = f"../audio/{time_filename}.mp3"
    print(f"找到对应的音频文件: {audio_path}")
else:
    print(f"未找到音频文件: {audio_path}")
```

**相对路径**：`../audio/20时09分.mp3`

### 5. 在 HTML 中引用

```html
<!-- 如果音频文件存在 -->
<audio controls class="audio-player">
    <source src="../audio/20时09分.mp3" type="audio/mpeg">
    您的浏览器不支持音频播放。
</audio>
```

## 🗂️ 文件结构示例

```
output/
└── 2025年11月25日/
    ├── html/
    │   ├── 18时05分.html  ←── 引用 ../audio/18时05分.mp3
    │   ├── 20时09分.html  ←── 引用 ../audio/20时09分.mp3
    │   ├── 21时55分.html  ←── 引用 ../audio/21时55分.mp3
    │   └── 当日汇总.html   ←── 汇总文件，不包含音频
    │
    └── audio/
        ├── 18时05分.mp3   ←── 对应 18时05分.html
        ├── 20时09分.mp3   ←── 对应 20时09分.html
        └── 21时55分.mp3   ←── 对应 21时55分.html
```

## ✅ 匹配保证机制

### 1. **时间戳一致性**

两个文件使用**完全相同**的时间生成函数：

```python
def format_time_filename():
    """格式化时间文件名"""
    return get_beijing_time().strftime("%H时%M分")
```

只要在同一分钟内生成，文件名就会一致。

### 2. **原子性操作**

匹配检查发生在 HTML 生成的**同一时刻**：

```python
# 步骤1: 确定 HTML 文件名
filename = f"{format_time_filename()}.html"  # "20时09分.html"

# 步骤2: 从文件名提取时间标识
time_filename = filename.replace(".html", "")  # "20时09分"

# 步骤3: 查找对应的音频文件
audio_path = Path("output") / date_folder / "audio" / f"{time_filename}.mp3"
```

这样确保了 HTML 和音频使用**相同的时间标识**。

### 3. **日期文件夹隔离**

按日期组织文件，避免跨天混淆：

```python
date_folder = format_date_folder()  # "2025年11月25日"
```

同一天的所有文件都在同一个日期文件夹下。

## 🔍 关键代码位置

| 功能 | 文件位置 | 说明 |
|------|----------|------|
| HTML 文件名生成 | main.py:1689 | 生成带时间戳的文件名 |
| 时间标识提取 | main.py:1704 | 从文件名提取时间 |
| 音频路径构建 | main.py:1706 | 构建音频文件完整路径 |
| 存在性检查 | main.py:1708 | 检查音频文件是否存在 |
| HTML 引用 | main.py:2252 | 在 HTML 中插入 audio 标签 |

## 🎬 完整示例

假设当前时间是 **2025年11月25日 20:09**

### 步骤 1: 运行爬虫

```bash
python main.py
```

生成文件：
- `output/2025年11月25日/txt/20时09分.txt`
- `output/2025年11月25日/html/20时09分.html`（暂无音频）

### 步骤 2: 生成播客

```bash
python generate_podcast_auto.py
```

生成文件：
- `output/2025年11月25日/audio/20时09分.mp3` ✅
- `output/2025年11月25日/audio/20时09分_script.txt`

**关键**：脚本读取最新的 txt 文件（`20时09分.txt`），提取其文件名作为时间标识。

```python
# generate_podcast_auto.py 第 47 行
txt_files = sorted([f for f in txt_dir.iterdir() if f.suffix == ".txt"])
latest_file = txt_files[-1]  # 20时09分.txt

# 第 58 行
return content, latest_file.stem  # 返回 "20时09分"
```

### 步骤 3: 重新生成 HTML

```bash
python main.py
```

在 HTML 生成时：

```python
# 当前时间可能已经是 20:10 或更晚
filename = f"{format_time_filename()}.html"  # 可能是 "20时10分.html"

# ❌ 错误做法（已修复前）
time_filename = format_time_filename()  # 会得到 "20时10分"
audio_path = f"output/.../audio/20时10分.mp3"  # 找不到！

# ✅ 正确做法（修复后）
time_filename = filename.replace(".html", "")  # 从文件名提取，得到 "20时10分"
audio_path = f"output/.../audio/20时10分.mp3"  # 正确匹配！
```

## ⚠️ 特殊情况处理

### 1. 汇总文件

汇总文件（如 `当日汇总.html`）**不会**匹配音频：

```python
# main.py 第 1699-1701 行
if is_daily_summary:
    # 汇总文件不需要音频（因为是汇总多个时间段的）
    audio_file = None
```

原因：汇总文件包含多个时间段的新闻，没有单一对应的音频。

### 2. 跨分钟边界

如果 txt 文件在 20:09 生成，但 HTML 在 20:10 重新生成：

**修复前**：会查找 `20时10分.mp3`（不存在）❌
**修复后**：会查找 `20时09分.mp3`（存在）✅

### 3. 音频文件缺失

如果音频文件不存在，HTML 正常生成，只是**不显示**播放器：

```python
if audio_path.exists():
    audio_file = f"../audio/{time_filename}.mp3"
else:
    audio_file = None  # HTML 不会包含播放器
```

## 🛡️ 可靠性保证

1. **使用文件名而非当前时间**：确保跨时间重新生成时匹配正确
2. **相对路径引用**：`../audio/` 保证 HTML 移动后仍能找到音频
3. **存在性检查**：只有音频存在才添加播放器，避免404错误
4. **日志输出**：打印找到/未找到信息，便于调试

## 🧪 验证方法

运行测试脚本：

```bash
python test_audio_integration.py
```

测试会：
1. 创建测试音频文件
2. 生成对应的 HTML
3. 验证 HTML 中的音频引用
4. 确认时间戳匹配

## 📝 总结

匹配机制的核心是：

```
HTML 文件名 → 提取时间标识 → 查找同名音频文件
   ↓              ↓                ↓
20时09分.html → 20时09分 → 20时09分.mp3
```

通过这种方式，确保了：
- ✅ 时间戳精确匹配
- ✅ 不受重新生成时间影响
- ✅ 文件对应关系清晰
- ✅ 易于调试和维护
