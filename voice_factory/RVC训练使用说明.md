# RVC 完全自动化训练 - 使用说明

## 🎯 问题修复总结

### 已修复的 Bug
1. ✅ **RVC preprocess.py 的 multiprocessing 问题** - Windows 上子进程静默失败
2. ✅ **路径转义问题** - Windows 反斜杠导致的转义错误  
3. ✅ **音频文件重命名** - 去掉特殊字符（+、-等）
4. ✅ **输入目录隔离** - 使用 input_wavs 子目录避免混淆

### 最终方案
使用**修复版预处理脚本**（fixed_preprocess.py），不使用 multiprocessing，单进程顺序处理所有音频。

---

## 🚀 使用方法（在沙箱外运行）

### 测试单个 Speaker

```bash
cd W:\fish-speech-1.5.1\voice_factory
C:\Users\moqi\AppData\Local\Programs\Python\Python312\python.exe rvc_full_auto_train.py --test --epochs 50
```

### 批量训练所有 Speaker

```bash
cd W:\fish-speech-1.5.1\voice_factory
C:\Users\moqi\AppData\Local\Programs\Python\Python312\python.exe rvc_full_auto_train.py --all --epochs 200
```

### 训练指定的 Speaker

```bash
cd W:\fish-speech-1.5.1\voice_factory
C:\Users\moqi\AppData\Local\Programs\Python\Python312\python.exe rvc_full_auto_train.py --speakers speaker_0001 speaker_0002 --epochs 200
```

---

## 📋 训练流程

脚本会自动完成以下步骤：

1. **复制并重命名音频** - 从 enhanced 目录复制，去掉特殊字符
2. **预处理音频** - 使用修复版脚本，重采样到 40k 和 16k
3. **提取音高特征** - 使用 RMVPE
4. **提取声学特征** - 使用 HuBERT
5. **生成 filelist** - 训练数据列表
6. **生成 config** - 训练配置文件
7. **训练模型** - GAN 训练
8. **生成索引** - FAISS 特征索引

---

## ⚙️ 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| --test | 测试模式，只训练第一个 speaker | - |
| --all | 批量训练所有 speaker | - |
| --speakers | 指定要训练的 speaker 列表 | - |
| --epochs | 训练轮数 | 200 |
| --batch_size | 批次大小 | 8 |

---

## 📁 输出文件

训练完成后，模型文件位于：

```
W:\rvc\logs\speaker_XXXX\
├── G_200.pth          # 声模模型（生成器）
├── D_200.pth          # 判别器
├── added_200.index    # FAISS 特征索引
└── ...
```

---

## 🔧 故障排除

### 问题 1: `[WinError 5] 拒绝访问`

**原因**：沙箱环境限制了跨目录访问

**解决**：在沙箱外运行脚本（不使用 Qoder 的 run_in_terminal）

### 问题 2: 预处理后子目录为空

**已修复**：使用 fixed_preprocess.py 替代 RVC 原生的 preprocess.py

### 问题 3: 找不到预训练模型

**检查**：确认 `W:\rvc\pretrained\f0G40k.pth` 和 `f0D40k.pth` 存在

---

## 💡 注意事项

1. **DSP 增强音频会被使用** - 脚本从 enhanced 目录复制音频，保留了之前的 DSP 增强工作成果
2. **音频文件会被重命名** - 去掉 +、- 等特殊字符，避免 RVC 解析失败
3. **训练时间** - 每个 speaker 约需 30-60 分钟（50 epochs）
4. **GPU 要求** - 建议使用 NVIDIA GPU，显存 >= 4GB

---

## 📞 技术支持

如有问题，请检查：
1. RVC 环境是否正常：`W:\rvc\runtime\python.exe`
2. 音频文件是否存在：`W:\fish-speech-1.5.1\voice_factory\enhanced\speaker_XXXX\`
3. 预训练模型是否存在：`W:\rvc\pretrained\`

---

**最后更新**: 2026-05-18
**修复版本**: v2.0 (使用修复版预处理脚本)
