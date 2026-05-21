# RVC 训练完整指南

## 音频数据评估结果

### 数据统计
- **总音频数**: 3,250 个
- **平均时长**: 3.55 秒
- **时长范围**: 0.43 - 6.88 秒
- **总时长**: 约 192 分钟
- **每个 speaker**: ~162 个音频

### 训练有效性

⚠️ **音频时长偏短，但可以训练**

**说明**:
- RVC 推荐音频时长 5-10 秒
- 当前 3.55 秒可以训练，但效果可能一般
- 优势：音频数量充足（162 个/speaker）
- 劣势：单条音频较短，特征提取可能不充分

**建议**:
1. ✅ 可以直接开始训练
2. ⏱️ 先用 1-2 个 speaker 测试效果
3. 🔄 如果效果不好，需要重新生成更长音频

---

## 训练方法

### 方法 1: 使用 RVC WebUI（推荐）

这是最稳定、最可控的方法。

#### 步骤：

**1. 启动 RVC WebUI**
```bash
cd W:\rvc
go-web.bat
```

等待启动完成，看到类似输出：
```
Running on local URL:  http://127.0.0.1:7897
```

**2. 打开浏览器**
访问：http://localhost:7897

**3. 切换到"训练"标签页**

**4. 填写训练参数**

对每个 speaker 重复以下步骤：

```
实验名称: speaker_0001
目标音频目录: 留空（自动从 logs/speaker_0001 读取）

预训练模型:
  - 底模: pretrained/f0G40k.pth (默认)
  
训练参数:
  - 保存频率: 10
  - 总训练轮数: 200
  - 批处理大小: 8
  - GPU: 0 (如果有 GPU，否则留空用 CPU)
  
其他选项:
  - 是否缓存训练集: 是
  - 是否使用 fp16: 是 (如果有 GPU)
```

**5. 点击"一键训练"**

训练过程：
- 阶段 1: 预处理音频（提取特征）
- 阶段 2: 训练模型
- 阶段 3: 生成索引文件

**6. 等待训练完成**

预计时间：
- **GPU (RTX 3060+)**: 30-60 分钟/speaker
- **CPU**: 2-4 小时/speaker

**7. 检查输出文件**

训练完成后，在 `W:\rvc\logs\speaker_0001\` 会生成：
```
speaker_0001/
├── G_200.pth          ← 声模转换模型（可用）
├── D_200.pth          ← 判别器模型（训练用）
├── added_200.index    ← 特征索引文件（可用）
└── ...
```

**8. 测试模型**

在 WebUI 的"推理"标签页：
- 上传测试音频
- 选择模型: `logs/speaker_0001/G_200.pth`
- 选择索引: `logs/speaker_0001/added_200.index`
- 点击"转换"

---

### 方法 2: 半自动批量训练

由于 RVC 没有命令行训练接口，我创建了一个辅助脚本来简化流程。

#### 使用训练检查脚本

```bash
# 检查训练数据
cd W:\fish-speech-1.5.1\voice_factory
C:\Users\moqi\AppData\Local\Programs\Python\Python312\python.exe check_audio_duration.py
```

#### 生成训练清单

```bash
# 生成所有 speaker 的训练清单
python -c "
import os
logs_dir = r'W:\rvc\logs'
speakers = sorted([d for d in os.listdir(logs_dir) if os.path.isdir(os.path.join(logs_dir, d))])
for i, spk in enumerate(speakers, 1):
    audio_count = len([f for f in os.listdir(os.path.join(logs_dir, spk)) if f.endswith('.wav')])
    print(f'{i}. {spk} ({audio_count} 个音频)')
"
```

---

### 方法 3: 使用 RVC 的推理 API（如果只需要测试）

如果你只是想测试声音转换效果，不需要训练，可以使用预训练模型。

```bash
cd W:\rvc

# 使用命令行推理
python tools/infer_cli.py --input input.wav --output output.wav --model_path model.pth --index_path index.index
```

---

## 训练参数建议

### 对于短音频（3-4 秒）

由于你的音频较短，建议调整参数：

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| Total Epoch | **300** | 增加训练轮数补偿短音频 |
| Batch Size | **4-8** | 较小 batch 更适合短音频 |
| Sample Rate | **40k** | 与预训练模型匹配 |
| Save Every | **10** | 每 10 epoch 保存 |
| Cache Data | **是** | 加速训练 |

### 训练质量检查点

训练过程中关注：

1. **Epoch 50**: 
   - Loss 应该明显下降
   - 如果 Loss 不降，可能需要调整学习率

2. **Epoch 100**:
   - 可以测试一次推理
   - 检查声音相似度

3. **Epoch 200**:
   - 标准训练完成点
   - 测试效果

4. **Epoch 300**:
   - 如果 200 epoch 效果不够，继续训练
   - 注意是否过拟合

---

## 批量训练 20 个 Speaker 的策略

### 方案 A: 逐步训练（推荐）

```
第 1 天: 训练 speaker_0001 ~ speaker_0005 (5 个)
第 2 天: 训练 speaker_0006 ~ speaker_0010 (5 个)
第 3 天: 训练 speaker_0011 ~ speaker_0015 (5 个)
第 4 天: 训练 speaker_0016 ~ speaker_0020 (5 个)
```

**优点**:
- 可以检查每个模型质量
- 发现问题及时调整
- 不会一次性占用太多资源

**预计时间**（GPU）:
- 每天: 2.5-5 小时
- 总计: 10-20 小时

### 方案 B: 批量自动训练

创建一个批处理文件 `train_all.bat`：

```batch
@echo off
cd W:\rvc

echo ========================================
echo 开始批量训练 20 个 Speaker
echo ========================================

REM 这里需要使用 RVC 的 API，但 RVC 主要依赖 WebUI
REM 建议使用方法 A：手动在 WebUI 中训练

echo 请使用 RVC WebUI 进行训练
echo 1. 运行: go-web.bat
echo 2. 打开浏览器: http://localhost:7897
echo 3. 在"训练"标签页逐个训练

pause
```

---

## 训练后处理

### 1. 整理模型文件

创建统一存放目录：

```bash
mkdir W:\rvc\trained_models
```

复制训练好的模型：

```batch
@echo off
set SPEAKER=speaker_0001
set EPOCH=200

mkdir W:\rvc\trained_models\%SPEAKER%
copy W:\rvc\logs\%SPEAKER%\G_%EPOCH%.pth W:\rvc\trained_models\%SPEAKER%\
copy W:\rvc\logs\%SPEAKER%\added_%EPOCH%.index W:\rvc\trained_models\%SPEAKER%\

echo 模型已保存到: W:\rvc\trained_models\%SPEAKER%\
```

### 2. 测试模型质量

对每个模型：

```bash
cd W:\rvc

# 使用测试音频
python tools/infer_cli.py ^
  --input test_audio.wav ^
  --output test_output.wav ^
  --model_path logs/speaker_0001/G_200.pth ^
  --index_path logs/speaker_0001/added_200.index ^
  --f0up_key 0 ^
  --f0method rmvpe ^
  --index_rate 0.7
```

### 3. 评估标准

好的模型应该：
- ✅ 音色相似度高（与原始 speaker 一致）
- ✅ 无明显的电子音/机械音
- ✅ 发音清晰
- ✅ 无明显噪音

---

## 常见问题

### Q1: 训练时 Loss 不下降

**原因**:
- 学习率过高/过低
- 音频质量差
- 音频时长太短

**解决**:
- 检查音频质量
- 尝试降低学习率
- 增加训练 epoch

### Q2: 训练完成后声音不像

**原因**:
- 训练数据不足
- 音频时长太短
- Epoch 不够

**解决**:
- 增加到 300 epoch
- 重新生成更长的音频（5-10 秒）
- 增加音频数量

### Q3: CPU 训练太慢

**解决**:
- 减少 Epoch 到 150
- 减少 Batch Size 到 4
- 使用 GPU 训练（推荐）
- 只训练几个最重要的 speaker

### Q4: 显存不足

**解决**:
- 减少 Batch Size: 8 → 4 → 2
- 使用 `--fp16` 选项
- 关闭其他程序

---

## 总结

### 当前状况
- ✅ 数据已准备好（3,250 个音频）
- ⚠️ 音频偏短（3.55 秒），但可以训练
- ✅ 每个 speaker 有 162 个音频（数量充足）

### 建议流程
1. **先测试 1-2 个 speaker**
2. **检查训练效果**
3. **如果满意，批量训练剩余 speaker**
4. **如果不满意，重新生成更长音频**

### 下一步
```bash
# 1. 启动 RVC
cd W:\rvc
go-web.bat

# 2. 在浏览器训练 speaker_0001
# http://localhost:7897 → 训练标签页

# 3. 等待完成，检查效果

# 4. 决定继续或调整
```

---

**准备好了吗？开始训练吧！** 🚀
