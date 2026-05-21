"""
RVC 实际训练脚本 - 使用 RVC 的训练模块
注意：RVC 的训练通常需要 WebUI，这里提供命令行训练方式
"""

import os
import sys
import subprocess
import argparse

# 设置 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

RVC_DIR = r"W:\rvc"
VOICE_FACTORY_DIR = r"W:\fish-speech-1.5.1\voice_factory"

def check_rvc_environment():
    """检查 RVC 环境"""
    print("=" * 70)
    print("检查 RVC 环境...")
    print("=" * 70)
    
    # 检查 RVC 目录
    if not os.path.exists(RVC_DIR):
        print(f"错误: RVC 目录不存在: {RVC_DIR}")
        return False
    
    # 检查关键文件
    required_files = [
        "infer-web.py",
        "configs",
        "pretrained",
    ]
    
    for file in required_files:
        path = os.path.join(RVC_DIR, file)
        if not os.path.exists(path):
            print(f"警告: 缺少 {file}")
    
    # 检查预训练模型
    pretrained_dir = os.path.join(RVC_DIR, "pretrained")
    if os.path.exists(pretrained_dir):
        models = os.listdir(pretrained_dir)
        print(f"预训练模型: {len(models)} 个")
    else:
        print("警告: 预训练模型目录不存在")
    
    print()
    return True


def train_with_rvc_cli(speaker_name, epochs=200, batch_size=8):
    """
    使用 RVC 的命令行接口训练
    
    注意：RVC 主要通过 WebUI 训练，命令行训练需要调用其内部模块
    """
    print(f"\n训练 {speaker_name}...")
    print("-" * 70)
    
    # RVC 的训练数据目录
    experiment_dir = os.path.join(RVC_DIR, "logs", speaker_name)
    
    if not os.path.exists(experiment_dir):
        print(f"  错误: 训练数据不存在: {experiment_dir}")
        return False
    
    # 检查音频文件
    audio_files = [f for f in os.listdir(experiment_dir) if f.endswith(".wav")]
    if len(audio_files) == 0:
        print(f"  错误: 没有音频文件")
        return False
    
    print(f"  音频文件: {len(audio_files)} 个")
    print(f"  训练轮数: {epochs}")
    print(f"  Batch Size: {batch_size}")
    print()
    
    # 方法 1: 使用 RVC 的训练脚本（如果存在）
    train_script = os.path.join(RVC_DIR, "tools", "train", "train.py")
    
    if os.path.exists(train_script):
        print("  使用 RVC 训练脚本...")
        cmd = [
            sys.executable, train_script,
            "--exp_dir", experiment_dir,
            "--total_epoch", str(epochs),
            "--batch_size", str(batch_size),
        ]
        
        try:
            result = subprocess.run(cmd, cwd=RVC_DIR)
            return result.returncode == 0
        except Exception as e:
            print(f"  训练失败: {e}")
            return False
    else:
        print("  RVC 训练脚本不存在")
        print()
        print("=" * 70)
        print("建议使用 RVC WebUI 进行训练：")
        print("=" * 70)
        print()
        print(f"1. 打开新终端，运行:")
        print(f"   cd {RVC_DIR}")
        print(f"   go-web.bat")
        print()
        print(f"2. 在浏览器打开: http://localhost:7897")
        print()
        print(f"3. 选择'训练'标签页，填写:")
        print(f"   - 实验名称: {speaker_name}")
        print(f"   - 目标音频目录: {experiment_dir}")
        print(f"   - 训练轮数: {epochs}")
        print(f"   - Batch Size: {batch_size}")
        print()
        print(f"4. 点击'一键训练'")
        print()
        print(f"5. 训练完成后，模型保存在:")
        print(f"   {experiment_dir}")
        print()
        return False


def batch_train(speakers, epochs=200, batch_size=8):
    """批量训练多个 speaker"""
    print("=" * 70)
    print("RVC 批量训练")
    print("=" * 70)
    print()
    
    if not check_rvc_environment():
        print("环境检查失败")
        return
    
    success_count = 0
    fail_count = 0
    
    for speaker in speakers:
        success = train_with_rvc_cli(speaker, epochs, batch_size)
        if success:
            success_count += 1
        else:
            fail_count += 1
    
    print()
    print("=" * 70)
    print("训练完成统计")
    print("=" * 70)
    print(f"  成功: {success_count}")
    print(f"  失败: {fail_count}")
    print()


def main():
    parser = argparse.ArgumentParser(description="RVC 批量训练脚本")
    parser.add_argument("--speakers", nargs="+", help="要训练的 speaker 列表")
    parser.add_argument("--all", action="store_true", help="训练所有 speaker")
    parser.add_argument("--epochs", type=int, default=200, help="训练轮数 (默认: 200)")
    parser.add_argument("--batch-size", type=int, default=8, help="Batch Size (默认: 8)")
    
    args = parser.parse_args()
    
    # 获取 speaker 列表
    if args.all:
        logs_dir = os.path.join(RVC_DIR, "logs")
        if not os.path.exists(logs_dir):
            print(f"错误: RVC logs 目录不存在: {logs_dir}")
            print("请先运行: python complete_pipeline.py")
            return
        
        speakers = sorted([d for d in os.listdir(logs_dir) 
                          if os.path.isdir(os.path.join(logs_dir, d))])
        
        if len(speakers) == 0:
            print("错误: 没有找到 speaker 训练数据")
            print("请先运行: python complete_pipeline.py")
            return
        
        print(f"找到 {len(speakers)} 个 speaker")
    elif args.speakers:
        speakers = args.speakers
    else:
        print("请指定 --all 或 --speakers")
        return
    
    # 开始训练
    batch_train(speakers, args.epochs, args.batch_size)


if __name__ == "__main__":
    main()
