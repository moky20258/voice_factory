# 🎤 Fish Speech 声模工厂

自动化批量生成声音人格 + 智能质量筛选的完整流水线系统。

## 📋 功能特性

### 第一阶段：批量音频生成
- ✅ 自动读取 `texts/` 目录下所有文本
- ✅ 批量生成 20 个 speaker，每个 30 句音频
- ✅ 自动随机 seed 和采样参数（批量生成新音色模式）
- ✅ 自动创建目录结构和 metadata
- ✅ 支持断点续传和错误重试
- ✅ 实时进度显示

### 第二阶段：音频质量筛选
- ✅ 使用 faster-whisper 进行 ASR 反识别
- ✅ 计算 WER (词错误率) 评估发音准确度
- ✅ 检测重复、崩坏音频
- ✅ 自动分类：优质 / 可接受 / 低质量 / 重复 / 空输出
- ✅ 生成详细质量报告
- ✅ 按质量等级自动整理文件

## 📁 目录结构

```
voice_factory/
│
├── texts/                          # 输入文本（已准备）
│   ├── 中文情绪句子.txt
│   ├── 中文疑问句惊讶句.txt
│   ├── 带数字英文时间的句子.txt
│   └── ... (共 10 个文件)
│
├── outputs/                        # 生成的音频（自动生成）
│   ├── speaker_0001/
│   │   ├── 0000.wav
│   │   ├── 0001.wav
│   │   └── ...
│   ├── speaker_0002/
│   └── ...
│
├── metadata/                       # 参数记录（自动生成）
│   ├── speaker_0001.json
│   ├── speaker_0002.json
│   └── ...
│
├── filtered/                       # 质量分类（自动生成）
│   ├── good/                       # ✅ 优质音频
│   ├── acceptable/                 # ⚠️ 可接受音频
│   ├── poor/                       # ❌ 低质量音频
│   ├── repeated/                   # 🔁 重复音频
│   └── empty/                      # ⭕ 空输出
│
├── reports/                        # 质量报告（自动生成）
│   ├── quality_report_*.json
│   └── good_audios_*.txt
│
├── generate.py                     # 批量生成器
├── quality_filter.py               # 质量筛选器
├── run_factory.py                  # 一键工作流
└── README.md                       # 使用说明
```

## 🚀 快速开始

### 前置条件

1. **Python 3.10-3.12**（不兼容 3.14）
2. **Fish Speech** 已部署并可以运行
3. **FFmpeg** 已安装

### 安装依赖

```bash
pip install requests tqdm faster-whisper
```

### 使用方式

#### 方式 1：一键运行完整流水线（推荐）

```bash
cd voice_factory
python run_factory.py
```

这会自动执行：
1. 批量生成 20 个 speaker
2. 质量筛选和分类
3. 生成报告

#### 方式 2：分阶段运行

```bash
# 阶段 1：仅生成音频
python run_factory.py --generate

# 阶段 2：仅质量筛选
python run_factory.py --filter

# 查看总结
python run_factory.py --summary
```

#### 方式 3：独立运行各模块

```bash
# 运行生成器
python generate.py

# 运行筛选器
python quality_filter.py
```

## ⚙️ 配置参数

### 批量生成参数（generate.py）

```python
# 生成规模
NUM_SPEAKERS = 20              # 生成多少个 speaker
LINES_PER_SPEAKER = 30         # 每个 speaker 生成多少句

# 批量生成新音色参数范围
TEMP_RANGE = (0.75, 0.85)      # Temperature 范围
TOP_P_RANGE = (0.80, 0.90)     # Top-P 范围
REPEAT_PENALTY_RANGE = (1.10, 1.20)  # 重复惩罚范围

# 重试配置
MAX_RETRIES = 3                # 最大重试次数
RETRY_DELAY = 2                # 重试延迟（秒）
```

### 质量筛选参数（quality_filter.py）

```python
# Whisper 模型配置
WHISPER_MODEL_SIZE = "base"    # 可选: tiny, base, small, medium, large
WHISPER_DEVICE = "cpu"         # 可选: cpu, cuda
WHISPER_COMPUTE_TYPE = "int8"  # 可选: int8, int16, float16, float32

# 质量阈值
WER_THRESHOLD_GOOD = 0.15      # WER < 15% 为优质
WER_THRESHOLD_ACCEPT = 0.30    # WER < 30% 为可接受
REPETITION_THRESHOLD = 0.5     # 重复度 > 50% 标记为重复
```

## 📊 参数推荐

根据你的文档，不同场景的参数推荐：

### 稳定真人感
```
Temperature: 0.6
Top-P: 0.7
Repeat Penalty: 1.2
Seed: 固定
```

### 批量生成新音色（当前配置）
```
Temperature: 0.75-0.85
Top-P: 0.80-0.90
Repeat Penalty: 1.10-1.20
Seed: 随机
```

### 情绪化生成
```
Temperature: 0.9
Top-P: 0.9
Repeat Penalty: 1.1
```

## 🎯 使用流程

### Step 1: 准备文本

文本文件已放在 `texts/` 目录下，包括：
- 中文情绪句子
- 中文疑问句惊讶句
- 带数字英文时间的句子
- 快速语速朗读的中文句子
- 日常口语句子
- 明显音高变化的句子
- 直播互动句子
- 聊天口头语句子
- 轻声耳语的句子
- 适合 AI 语音训练的长句

### Step 2: 启动 Fish Speech API

```bash
# 在项目根目录运行
python tools/run_webui.py
```

等待 WebUI 启动，确认可以访问 `http://127.0.0.1:7860`

### Step 3: 运行声模工厂

```bash
cd voice_factory
python run_factory.py
```

### Step 4: 检查结果

生成完成后，查看：

1. **生成的音频**：`outputs/` 目录
2. **优质音频**：`filtered/good/` 目录
3. **质量报告**：`reports/quality_report_*.json`
4. **优质列表**：`reports/good_audios_*.txt`

### Step 5: 人工筛选

从 `filtered/good/` 目录中人工试听，挑选最满意的声模。

## 📈 质量评估标准

### WER (Word Error Rate) 词错误率
- **优质**：WER < 15%
- **可接受**：WER < 30%
- **低质量**：WER ≥ 30%

### 重复检测
- 检测连续重复字符（如：啊啊啊啊）
- 检测词组重复比例
- 重复度 > 50% 标记为重复音频

### 空输出检测
- ASR 识别文本 < 3 个字符标记为空输出

## 🔧 高级用法

### 调整生成规模

编辑 `generate.py`：

```python
# 生成 50 个 speaker，每个 50 句
NUM_SPEAKERS = 50
LINES_PER_SPEAKER = 50
```

### 使用 GPU 加速筛选

编辑 `quality_filter.py`：

```python
WHISPER_DEVICE = "cuda"
WHISPER_COMPUTE_TYPE = "float16"
```

### 自定义质量阈值

编辑 `quality_filter.py`：

```python
# 更严格的优质标准
WER_THRESHOLD_GOOD = 0.10  # 从 0.15 改为 0.10
```

## ⚠️ 注意事项

1. **API 服务必须先启动**：运行生成器前确保 Fish Speech WebUI 已启动
2. **文本长度**：建议每句不超过 15 秒朗读时间，最佳 5-10 秒
3. **网络问题**：首次运行 quality_filter.py 会下载 Whisper 模型，需要网络
4. **磁盘空间**：20 个 speaker × 30 句 ≈ 600 个音频文件，约 50-100MB
5. **生成时间**：根据 API 响应速度，可能需要 30-60 分钟

## 🐛 常见问题

### Q: API 连接失败
```
❌ 无法连接到 Fish Speech API
```
**解决**：先启动 Fish Speech WebUI
```bash
python tools/run_webui.py
```

### Q: Whisper 模型下载失败
```
❌ Whisper 模型加载失败
```
**解决**：检查网络连接，或更换较小模型
```python
WHISPER_MODEL_SIZE = "tiny"  # 改为 tiny
```

### Q: 生成速度慢
**解决**：
- 检查 API 服务是否正常
- 减少 NUM_SPEAKERS 或 LINES_PER_SPEAKER
- 使用 GPU 版本的 Fish Speech

### Q: 优质率太低
**解决**：
- 降低 temperature (0.6-0.7)
- 提高 repetition_penalty (1.2-1.3)
- 检查文本质量

## 📝 元数据格式

每个 speaker 的 metadata 文件 (`metadata/speaker_XXXX.json`)：

```json
{
    "speaker": "speaker_0001",
    "created_at": "2026-05-18 14:30:00",
    "params": {
        "seed": 123456,
        "temperature": 0.78,
        "top_p": 0.85,
        "repetition_penalty": 1.15
    }
}
```

## 🎉 下一步

生成优质声模后，可以：

1. **DSP 增强**：
   - 变调 (pitch shift)
   - 共振峰调整 (formant shift)
   - 均衡器 (EQ)
   - 速度调整 (rate)

2. **训练 RVC 模型**：
   使用筛选出的优质音频训练 RVC 声模

3. **建立声纹数据库**：
   记录每个声模的特征和适用场景

## 📄 License

基于 Fish Speech 项目使用。

## 🙏 致谢

- [Fish Speech](https://github.com/fishaudio/fish-speech) - 声音基础模型
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) - 高效语音识别
