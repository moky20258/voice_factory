# RVC GUI 模型使用指南

## ❌ 问题原因

训练生成的 `G_50.pth` 是 **PyTorch Lightning 格式**，包含：
- `model`: 模型权重
- `optimizer`: 优化器状态
- `iteration`: 训练轮数
- `learning_rate`: 学习率

但 RVC GUI 需要的是 **RVC 原生格式**，包含：
- `weight`: 模型权重
- `config`: 模型配置
- `info`: 模型信息

---

## ✅ 解决方案

### **方案 1：自动转换（推荐）**

训练脚本已自动转换！训练完成后会生成两个文件：

```
W:\rvc\logs\speaker_0001\
├── G_50.pth                    ← 训练模型（417 MB）
├── speaker_0001_v2.pth         ← RVC GUI 模型（139 MB）✅ 使用这个
└── added_50.index              ← 索引文件
```

**在 RVC GUI 中：**
- 模型文件：选择 `speaker_0001_v2.pth`
- 索引文件：选择 `added_50.index`

---

### **方案 2：手动转换**

如果已有训练模型，可以手动转换：

```bash
cd W:\fish-speech-1.5.1\voice_factory

# 转换模型
python convert_to_rvc_format.py W:\rvc\logs\speaker_0001\G_50.pth -o W:\rvc\logs\speaker_0001\speaker_0001_v2.pth
```

---

## 🚀 在 RVC GUI 中使用

### **1. 启动 RVC GUI**

```bash
cd W:\rvc
runtime\python.exe gui_v1.py
```

### **2. 加载模型**

1. 点击 **"模型推理"** 选项卡
2. 在 **"音源模型"** 中选择：
   - 点击文件夹图标
   - 导航到 `W:\rvc\logs\speaker_0001\`
   - 选择 `speaker_0001_v2.pth` ✅
3. 在 **"特征检索库"** 中选择：
   - 选择 `added_50.index`

### **3. 配置参数**

推荐参数：
- **变调**: 0（男变男/女变女），+12（女变男），-12（男变女）
- **索引率**: 0.7-0.8（越高越接近训练音色）
- **音色保护**: 0.3-0.5（越高越保留原音色）
- **响应阈值**: 0.5

### **4. 开始变声**

1. 选择输入设备（麦克风）
2. 选择输出设备（虚拟音频设备）
3. 点击 **"开始音频转换"**
4. 对着麦克风说话测试

---

## 📊 模型文件对比

| 文件 | 大小 | 用途 | 格式 |
|------|------|------|------|
| `G_50.pth` | 417 MB | 继续训练 | Lightning |
| `speaker_0001_v2.pth` | 139 MB | RVC GUI 推理 | RVC 原生 ✅ |
| `added_50.index` | 2 MB | 特征检索 | FAISS |

---

## 💡 常见问题

### **Q1: 为什么训练模型不能直接在 GUI 中使用？**

A: RVC 训练使用 PyTorch Lightning 框架，保存的格式包含训练状态（优化器、学习率等），而 GUI 只需要推理权重。

### **Q2: 转换后会损失音质吗？**

A: **不会！** 转换只是提取权重，不修改任何模型参数。音质完全相同。

### **Q3: 可以同时使用多个模型吗？**

A: 可以！RVC GUI 支持热切换模型。只需在推理时选择不同的 `.pth` 文件。

### **Q4: 模型文件太大怎么办？**

A: 
- `speaker_0001_v2.pth` 已经是精简版（139 MB）
- 如需更小，可以使用 ONNX 导出（约 100 MB）

### **Q5: 变声时闪退/报错？**

A: 检查：
1. ✅ 使用的是 `*_v2.pth` 而非 `G_*.pth`
2. ✅ 模型和索引文件匹配（同一次训练）
3. ✅ GPU 显存充足（至少 4 GB）
4. ✅ 采样率匹配（40k 模型配 40k 设置）

---

## 🎯 完整工作流

```
1. 训练模型
   python rvc_full_auto_train.py --test
   
   ↓ 自动生成
   
2. 模型文件
   - speaker_0001_v2.pth ✅
   - added_50.index
   
   ↓ 在 RVC GUI 中加载
   
3. 实时变声
   麦克风 → RVC → 虚拟音频设备 → 目标软件
   
   ↓ 或使用
   
4. 音频文件转换
   选择输入文件 → 转换 → 保存输出文件
```

---

## 📝 示例：测试变声效果

```bash
# Step 1: 训练模型（自动生成 GUI 可用格式）
python rvc_full_auto_train.py --test

# 输出:
# ✅ 已生成 RVC GUI 模型: speaker_0001_v2.pth
#    大小: 139.3 MB

# Step 2: 启动 RVC GUI
cd W:\rvc
runtime\python.exe gui_v1.py

# Step 3: 在 GUI 中加载
# - 模型: W:\rvc\logs\speaker_0001\speaker_0001_v2.pth
# - 索引: W:\rvc\logs\speaker_0001\added_50.index

# Step 4: 测试变声
# 对着麦克风说话，听效果
```

---

## ✅ 检查清单

使用模型前确认：

- [ ] 使用 `*_v2.pth` 文件（不是 `G_*.pth`）
- [ ] 索引文件匹配（同一次训练）
- [ ] 采样率设置正确（40k）
- [ ] GPU 驱动已更新
- [ ] CUDA 可用（`torch.cuda.is_available() == True`）
- [ ] 内存充足（至少 8 GB RAM）

---

**现在你可以在 RVC GUI 中使用训练好的声模了！** 🎉
