"""
RVC 全自动批量训练脚本
直接调用 RVC 的 train1key 函数，无需 WebUI！
"""

import os
import sys

# 设置 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 RVC 到路径
RVC_DIR = r"W:\rvc"
sys.path.insert(0, RVC_DIR)
os.chdir(RVC_DIR)

print("=" * 70)
print("🚀 RVC 全自动批量训练")
print("=" * 70)
print()

# 导入 RVC 模块
print("📥 加载 RVC 模块...")
try:
    import importlib
    infer_web = importlib.import_module('infer-web')
    train1key = infer_web.train1key
    print("✅ RVC 模块加载成功")
except Exception as e:
    print(f"❌ 加载失败: {e}")
    print("请确保 RVC 环境正确")
    sys.exit(1)

print()

# 训练配置
TRAIN_CONFIG = {
    "sr2": "40k",              # 采样率
    "if_f0_3": 1,              # 使用 F0 (音高)
    "spk_id5": 1,              # Speaker ID
    "np7": 8,                  # CPU 线程数
    "f0method8": "rmvpe",      # F0 提取方法
    "save_epoch10": 10,        # 保存频率
    "total_epoch11": 200,      # 总训练轮数
    "batch_size12": 8,         # Batch Size
    "if_save_latest13": 1,     # 保存最新模型
    "pretrained_G14": os.path.join(RVC_DIR, "pretrained", "f0G40k.pth"),
    "pretrained_D15": os.path.join(RVC_DIR, "pretrained", "f0D40k.pth"),
    "gpus16": "0",             # GPU ID (如果有 GPU)
    "if_cache_gpu17": 1,       # 缓存到 GPU
    "if_save_every_weights18": 0,  # 不保存每个权重
    "version19": "v2",         # RVC 版本
    "gpus_rmvpe": "0",         # RMVPE GPU
}

def train_single_speaker(speaker_name):
    """训练单个 speaker"""
    print(f"\n{'='*70}")
    print(f"🎓 训练: {speaker_name}")
    print(f"{'='*70}")
    
    exp_dir = speaker_name
    trainset_dir = os.path.join(RVC_DIR, "logs", speaker_name)
    
    # 检查训练数据
    if not os.path.exists(trainset_dir):
        print(f"❌ 训练数据不存在: {trainset_dir}")
        return False
    
    audio_count = len([f for f in os.listdir(trainset_dir) if f.endswith(".wav")])
    if audio_count == 0:
        print(f"❌ 没有音频文件")
        return False
    
    print(f"📊 训练数据: {audio_count} 个音频")
    print(f"📁 实验目录: {exp_dir}")
    print(f"⚙️  训练参数:")
    print(f"   - Epoch: {TRAIN_CONFIG['total_epoch11']}")
    print(f"   - Batch Size: {TRAIN_CONFIG['batch_size12']}")
    print(f"   - Sample Rate: {TRAIN_CONFIG['sr2']}")
    print()
    
    # 调用训练函数
    try:
        # train1key 是生成器，需要迭代获取进度
        for progress in train1key(
            exp_dir,
            TRAIN_CONFIG["sr2"],
            TRAIN_CONFIG["if_f0_3"],
            trainset_dir,
            TRAIN_CONFIG["spk_id5"],
            TRAIN_CONFIG["np7"],
            TRAIN_CONFIG["f0method8"],
            TRAIN_CONFIG["save_epoch10"],
            TRAIN_CONFIG["total_epoch11"],
            TRAIN_CONFIG["batch_size12"],
            TRAIN_CONFIG["if_save_latest13"],
            TRAIN_CONFIG["pretrained_G14"],
            TRAIN_CONFIG["pretrained_D15"],
            TRAIN_CONFIG["gpus16"],
            TRAIN_CONFIG["if_cache_gpu17"],
            TRAIN_CONFIG["if_save_every_weights18"],
            TRAIN_CONFIG["version19"],
            TRAIN_CONFIG["gpus_rmvpe"],
        ):
            print(f"  📝 {progress}")
        
        print(f"\n✅ {speaker_name} 训练完成！")
        print(f"📁 模型保存位置:")
        print(f"   W:\\rvc\\logs\\{speaker_name}\\G_{TRAIN_CONFIG['total_epoch11']}.pth")
        print(f"   W:\\rvc\\logs\\{speaker_name}\\added_{TRAIN_CONFIG['total_epoch11']}.index")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 训练失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    # 获取所有 speaker
    logs_dir = os.path.join(RVC_DIR, "logs")
    speakers = sorted([d for d in os.listdir(logs_dir) 
                       if os.path.isdir(os.path.join(logs_dir, d)) and d.startswith('speaker_')])
    
    if len(speakers) == 0:
        print("❌ 没有找到训练数据")
        print("请先运行: python complete_pipeline.py")
        return
    
    print(f"✅ 找到 {len(speakers)} 个 Speaker")
    print()
    
    # 询问训练模式
    print("训练模式:")
    print("1. 测试训练 (speaker_0001)")
    print("2. 批量训练所有 (20 个)")
    print("3. 自定义选择")
    print()
    
    choice = input("请选择 (1/2/3): ").strip()
    
    if choice == "1":
        # 测试训练
        speakers_to_train = [speakers[0]]
    elif choice == "2":
        # 批量训练
        speakers_to_train = speakers
    elif choice == "3":
        # 自定义
        print("\n可用的 Speaker:")
        for i, spk in enumerate(speakers, 1):
            print(f"  {i}. {spk}")
        print()
        
        indices = input("输入要训练的编号 (用逗号分隔，如 1,2,3): ").strip()
        indices = [int(x.strip()) for x in indices.split(",")]
        speakers_to_train = [speakers[i-1] for i in indices]
    else:
        print("无效选择")
        return
    
    print(f"\n将训练 {len(speakers_to_train)} 个 Speaker:")
    for spk in speakers_to_train:
        print(f"  - {spk}")
    print()
    
    confirm = input("确认开始训练？(y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    # 开始训练
    success_count = 0
    fail_count = 0
    
    for speaker in speakers_to_train:
        success = train_single_speaker(speaker)
        if success:
            success_count += 1
        else:
            fail_count += 1
        
        # 显示统计
        print(f"\n进度: {success_count + fail_count}/{len(speakers_to_train)}")
        print(f"  成功: {success_count}")
        print(f"  失败: {fail_count}")
    
    # 最终统计
    print(f"\n{'='*70}")
    print("🎉 训练完成！")
    print(f"{'='*70}")
    print(f"  总计: {len(speakers_to_train)}")
    print(f"  成功: {success_count}")
    print(f"  失败: {fail_count}")
    print()
    print("📁 模型文件位置:")
    print(f"  W:\\rvc\\logs\\speaker_XXXX\\")
    print(f"  - G_200.pth (声模模型)")
    print(f"  - added_200.index (特征索引)")
    print()


if __name__ == "__main__":
    main()
