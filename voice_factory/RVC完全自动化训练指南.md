# 🎤 RVC 完全自动化训练 - 使用指南

## ✅ 已完成

完全自动化的 RVC 训练脚本已创建！无需任何 WebUI 操作！

📄 [rvc_full_auto_train.py](file:///w:/fish-speech-1.5.1/voice_factory/rvc_full_auto_train.py)

---

## 🚀 使用方法

### 测试训练（推荐先测试 1 个 speaker）

```bash
cd W:\fish-speech-1.5.1\voice_factory
C:\Users\moqi\AppData\Local\Programs\Python\Python312\python.exe rvc_full_auto_train.py --test --epochs 50
```

**说明**：
- `--test`: 只训练 speaker_0001
- `--epochs 50`: 训练 50 轮（测试用，快速验证）
- 预计时间：5-10 分钟

### 批量训练所有 20 个 Speaker

```bash
C:\Users\moqi\AppData\Local\Programs\Python\Python312\python.exe rvc_full_auto_train.py --all --epochs 200
```

**说明**：
- `--all`: 训练所有 20 个 speaker
- `--epochs 200`: 训练 200 轮（标准配置）
- 预计时间：
  - GPU: 15-30 小时
  - CPU: 60-80 小时

### 训练指定 Speaker

```bash
C:\Users\moqi\AppData\Local\Programs\Python\Python312\python.exe rvc_full_auto_train.py --speakers speaker_0001 speaker_0002 speaker_0003 --epochs 200
```

---

## 📋 训练流程（全自动）

脚本会自动完成以下步骤：

1. ✅ **复制音频** - 从 voice_factory/enhanced 复制到 RVC/logs
2. ✅ **预处理音频** - 重采样、分割、标准化
3. ✅ **提取音高特征** - 使用 RMVPE
4. ✅ **提取声学特征** - 使用 HuBERT
5. ✅ **生成 filelist** - 训练数据列表
6. ✅ **生成配置文件** - config.json
7. ✅ **训练模型** - GAN 训练
8. ✅ **生成索引** - FAISS 向量索引

**无需任何人工干预！**

---

## 📁 输出文件

训练完成后，每个 speaker 会生成：

```
W:\rvc\logs\speaker_XXXX\
├── G_200.pth              ← 声模转换模型（可用）
├── D_200.pth              ← 判别器模型
├── added_200.index        ← 特征索引文件（可用）
├── config.json            ← 训练配置
├── filelist.txt           ← 训练数据列表
└── train.log              ← 训练日志
```

**可用文件**：
- `G_200.pth` - 用于声音转换
- `added_200.index` - 用于提升音质

---

## ⚙️ 训练参数

### 推荐配置

| 参数 | GPU 训练 | CPU 训练 | 说明 |
|------|----------|----------|------|
| Epochs | 200 | 150 | CPU 减少轮数 |
| Batch Size | 8 | 4 | 根据内存调整 |
| Sample Rate | 40k | 40k | 固定值 |

### 自定义参数

```bash
# 自定义训练轮数和 batch size
python rvc_full_auto_train.py --all --epochs 300 --batch-size 4
```

---

## 💡 使用建议

### 1. 先测试

```bash
# 测试 speaker_0001
python rvc_full_auto_train.py --test --epochs 50
```

检查输出文件质量和训练日志。

### 2. 分批训练

如果担心一次性训练 20 个太慢，可以分批：

```bash
# 第一批：speaker_0001 ~ 0010
python rvc_full_auto_train.py --speakers speaker_0001 speaker_0002 speaker_0003 speaker_0004 speaker_0005 speaker_0006 speaker_0007 speaker_0008 speaker_0009 speaker_0010 --epochs 200

# 第二批：speaker_0011 ~ 0020
python rvc_full_auto_train.py --speakers speaker_0011 speaker_0012 speaker_0013 speaker_0014 speaker_0015 speaker_0016 speaker_0017 speaker_0018 speaker_0019 speaker_0020 --epochs 200
```

### 3. 监控训练进度

训练过程中会实时输出：
- 预处理进度
- 特征提取进度
- 训练 epoch 进度
- Loss 值

可以打开 `W:\rvc\logs\speaker_XXXX\train.log` 查看详细日志。

---

## 🔧 故障排除

### 问题 1: 找不到音频文件

**错误**：`❌ 找不到原始音频`

**解决**：
```bash
# 检查 enhanced 目录是否存在
dir W:\fish-speech-1.5.1\voice_factory\enhanced

# 如果不存在，先运行完整流水线
python complete_pipeline.py
```

### 问题 2: 预训练模型不存在

**错误**：`FileNotFoundError: pretrained/f0G40k.pth`

**解决**：
```bash
# 检查预训练模型
dir W:\rvc\pretrained

# 如果缺失，在 RVC WebUI 中下载
cd W:\rvc
go-web.bat
# 在"模型推理"标签页点击"下载模型"
```

### 问题 3: 训练中途失败

**查看日志**：
```bash
# 查看训练日志
type W:\rvc\logs\speaker_0001\train.log

# 查看预处理日志
type W:\rvc\logs\speaker_0001\preprocess.log
```

**常见原因**：
- 显存不足 → 减少 batch size
- 音频格式错误 → 确保是 16-bit WAV
- 路径包含中文 → 使用英文路径

---

## 📊 训练完成后

### 1. 测试模型

在 RVC WebUI 中测试：

```bash
cd W:\rvc
go-web.bat

# 浏览器打开 http://localhost:7897
# 选择"模型推理"标签
# 上传测试音频
# 选择模型: logs/speaker_0001/G_200.pth
# 选择索引: logs/speaker_0001/added_200.index
# 点击"转换"
```

### 2. 整理模型

创建统一存放目录：

```bash
mkdir W:\rvc\trained_models
```

复制训练好的模型（示例）：

```bash
# 使用 Python 脚本批量复制
python -c "
import os, shutil

for i in range(1, 21):
    spk = f'speaker_{i:04d}'
    src_dir = f'W:\\rvc\\logs\\{spk}'
    dst_dir = f'W:\\rvc\\trained_models\\{spk}'
    
    os.makedirs(dst_dir, exist_ok=True)
    
    # 复制模型
    for f in ['G_200.pth', 'added_200.index']:
        src = os.path.join(src_dir, f)
        dst = os.path.join(dst_dir, f)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f'✅ {spk}/{f}')
"
```

### 3. 使用推荐系统

```bash
cd W:\fish-speech-1.5.1\voice_factory
python recommend_voice.py recording.wav
```

---

## 🎉 总结

### 完全自动化流程

```
准备音频 → 一键命令 → 等待完成 → 获得模型
```

**你需要做的**：
1. ✅ 运行一条命令
2. ✅ 等待训练完成
3. ✅ 使用生成的 .pth 和 .index 文件

**我帮你完成的**：
- ✅ 数据准备
- ✅ 质量筛选
- ✅ DSP 增强
- ✅ 声纹数据库
- ✅ 推荐系统
- ✅ 完整自动化训练脚本

---

**准备好了吗？开始训练吧！** 🚀

```bash
# 测试训练
python rvc_full_auto_train.py --test --epochs 50

# 或批量训练
python rvc_full_auto_train.py --all --epochs 200
```
