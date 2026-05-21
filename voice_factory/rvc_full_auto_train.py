"""
RVC 完全自动化训练脚本
直接调用 RVC 的底层函数，无需 WebUI！

训练流程：
1. preprocess_dataset - 预处理音频
2. extract_f0_feature - 提取音高和特征
3. click_train - 训练模型
4. train_index - 生成索引
"""

import os
import sys
import subprocess
import argparse

# 设置 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# RVC 路径
RVC_DIR = r"W:\rvc"
RVC_PYTHON = os.path.join(RVC_DIR, "runtime", "python.exe")

# 切换到 RVC 目录
os.chdir(RVC_DIR)

def run_rvc_command(cmd, description, cwd=None):
    """运行 RVC 命令"""
    print(f"\n{'='*70}")
    print(f"📝 {description}")
    print(f"{'='*70}")
    print(f"命令: {cmd}\n")
    
    if cwd is None:
        cwd = RVC_DIR
    
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=False
    )
    
    if result.returncode != 0:
        print(f"❌ {description} 失败")
        return False
    
    print(f"✅ {description} 完成")
    return True


def train_speaker(speaker_name, epochs=200, batch_size=8, auto_match=False):
    """训练单个 speaker - 完全自动化"""
    
    print(f"\n{'='*70}")
    print(f"🎓 开始训练: {speaker_name}")
    print(f"{'='*70}")
    
    exp_dir = speaker_name
    # 使用 enhanced 目录的音频（DSP 增强后的）
    trainset_dir = os.path.join(RVC_DIR, "logs", speaker_name)
    input_dir = os.path.join(trainset_dir, "input_wavs")  # 单独的输入目录
    
    # 检查是否有原始音频，没有则从 voice_factory/enhanced 复制并重命名
    if not os.path.exists(input_dir) or len([f for f in os.listdir(input_dir) if f.endswith(".wav")]) == 0:
        src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "enhanced", speaker_name)
        if os.path.exists(src_dir):
            import shutil
            import re
            os.makedirs(input_dir, exist_ok=True)
            # 复制并重命名音频文件（去掉特殊字符）
            count = 0
            for f in os.listdir(src_dir):
                if f.endswith(".wav"):
                    # 重命名：去掉所有特殊字符，只保留字母、数字、下划线、点
                    new_name = re.sub(r'[^a-zA-Z0-9_.]', '_', f)
                    # 确保以数字开头
                    if not new_name[0].isdigit():
                        new_name = f"{count:04d}_{new_name}"
                    
                    src_file = os.path.join(src_dir, f)
                    dst_file = os.path.join(input_dir, new_name)
                    shutil.copy2(src_file, dst_file)
                    count += 1
                    if count <= 3:  # 打印前3个示例
                        print(f"  {f} -> {new_name}")
            print(f"✅ 从 {src_dir} 复制并重命名了 {count} 个音频文件")
        else:
            print(f"❌ 找不到增强音频: {src_dir}")
            return False
    
    # 检查训练数据
    if not os.path.exists(input_dir):
        print(f"❌ 输入数据不存在: {input_dir}")
        return False
    
    audio_files = [f for f in os.listdir(input_dir) if f.endswith(".wav")]
    if len(audio_files) == 0:
        print(f"❌ 没有音频文件")
        return False
    
    # 智能声模匹配
    sr = 40000  # 采样率（数字）
    sr_str = "40k"  # 采样率（字符串）
    if_f0 = 1
    f0method = "rmvpe"
    version = "v2"
    gpus = "0"  # GPU ID，如果没有 GPU 留空
    spk_id = 1
    
    if auto_match:
        # 🎯 智能匹配预训练声模
        print("\n🎯 正在分析声音特征并匹配最佳预训练声模...")
        try:
            from voice_matcher import match_voice
            
            # 使用 input_dir 中的音频进行匹配
            best_match, all_matches = match_voice(input_dir, top_n=3, print_report=True)
            
            if best_match:
                pretrained_G = best_match['model']['pretrained_G']
                pretrained_D = best_match['model']['pretrained_D']
                
                # 如果没有指定 epochs，根据匹配结果推荐
                if epochs == 200:  # 默认值，需要自动计算
                    # 计算音频总时长
                    total_duration = 0
                    for wav_file in audio_files[:10]:  # 采样前10个文件
                        wav_path = os.path.join(input_dir, wav_file)
                        try:
                            import librosa
                            y, sr_temp = librosa.load(wav_path, sr=None)
                            total_duration += len(y) / sr_temp
                        except:
                            total_duration += 10  # 默认 10 秒
                    
                    from voice_matcher import VoiceModelMatcher
                    matcher = VoiceModelMatcher()
                    recommended_epochs = matcher.get_recommended_epochs(best_match, total_duration)
                    epochs = recommended_epochs
                    print(f"\n📊 根据匹配结果推荐训练: {epochs} epochs")
            else:
                # 匹配失败，使用默认模型
                print("\n⚠️  声模匹配失败，使用默认预训练模型")
                pretrained_G = os.path.join(RVC_DIR, "assets", "pretrained_v2", "f0G40k.pth")
                pretrained_D = os.path.join(RVC_DIR, "assets", "pretrained_v2", "f0D40k.pth")
        except Exception as e:
            print(f"\n⚠️  声模匹配失败 ({e})，使用默认预训练模型")
            import traceback
            traceback.print_exc()
            pretrained_G = os.path.join(RVC_DIR, "assets", "pretrained_v2", "f0G40k.pth")
            pretrained_D = os.path.join(RVC_DIR, "assets", "pretrained_v2", "f0D40k.pth")
    else:
        # 使用默认预训练模型
        pretrained_G = os.path.join(RVC_DIR, "assets", "pretrained_v2", "f0G40k.pth")
        pretrained_D = os.path.join(RVC_DIR, "assets", "pretrained_v2", "f0D40k.pth")
    
    print(f"📊 找到 {len(audio_files)} 个音频文件")
    print(f"📁 实验目录: {exp_dir}")
    print(f"⚙️  参数: epochs={epochs}, batch_size={batch_size}")
    print()
    
    # 创建实验目录
    log_dir = os.path.join(RVC_DIR, "logs", exp_dir)
    os.makedirs(log_dir, exist_ok=True)
    print(f"✅ 创建实验目录: {log_dir}")
    print()
    
    # Step 1: 预处理数据集（使用修复版，不用 multiprocessing）
    print("⌛ Step 1/4: 预处理音频...")
        
    # 确保 logs/speaker_XXX 目录存在
    log_exp_dir = os.path.join(RVC_DIR, "logs", exp_dir)
    os.makedirs(log_exp_dir, exist_ok=True)
        
    # 创建临时预处理脚本（避免 multiprocessing 问题）
    temp_script = os.path.join(RVC_DIR, "temp_preprocess.py")
    
    # 使用原始字符串避免转义问题
    rvc_dir_escaped = RVC_DIR.replace('\\', '/')
    input_dir_escaped = input_dir.replace('\\', '/')
    log_exp_dir_escaped = log_exp_dir.replace('\\', '/')
    
    preprocess_code = f'''import sys, io, os
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.chdir("{rvc_dir_escaped}")
sys.path.insert(0, "{rvc_dir_escaped}")
from scipy import signal
import librosa, numpy as np
from scipy.io import wavfile
from infer.lib.audio import load_audio
from infer.lib.slicer2 import Slicer
inp_root = "{input_dir_escaped}"
sr = {sr}
exp_dir = "{log_exp_dir_escaped}"
per = 3.7
gt_wavs_dir = os.path.join(exp_dir, "0_gt_wavs")
wavs16k_dir = os.path.join(exp_dir, "1_16k_wavs")
os.makedirs(gt_wavs_dir, exist_ok=True)
os.makedirs(wavs16k_dir, exist_ok=True)
slicer = Slicer(sr=sr, threshold=-42, min_length=1500, min_interval=400, hop_size=15, max_sil_kept=500)
bh, ah = signal.butter(N=5, Wn=48, btype="high", fs=sr)
overlap, tail, max_val, alpha = 0.3, per + 0.3, 0.9, 0.75
def norm_write(tmp_audio, idx0, idx1):
    tmp_max = np.abs(tmp_audio).max()
    if tmp_max > 2.5: return False
    tmp_audio = (tmp_audio / tmp_max * (max_val * alpha)) + (1 - alpha) * tmp_audio
    wavfile.write(os.path.join(gt_wavs_dir, f"{{idx0}}_{{idx1}}.wav"), sr, tmp_audio.astype(np.float32))
    tmp_audio_16k = librosa.resample(tmp_audio, orig_sr=sr, target_sr=16000)
    wavfile.write(os.path.join(wavs16k_dir, f"{{idx0}}_{{idx1}}.wav"), 16000, tmp_audio_16k.astype(np.float32))
    return True
wav_files = sorted([f for f in os.listdir(inp_root) if f.endswith(".wav")])
print(f"找到 {{len(wav_files)}} 个 wav 文件")
success_count = 0
for idx0, name in enumerate(wav_files):
    path = os.path.join(inp_root, name)
    try:
        audio = load_audio(path, sr)
        audio = signal.lfilter(bh, ah, audio)
        idx1 = 0
        for audio_chunk in slicer.slice(audio):
            i = 0
            while True:
                start = int(sr * (per - overlap) * i)
                i += 1
                if len(audio_chunk[start:]) > int(tail * sr):
                    tmp_audio = audio_chunk[start : start + int(per * sr)]
                    if norm_write(tmp_audio, idx0, idx1): success_count += 1
                    idx1 += 1
                else:
                    tmp_audio = audio_chunk[start:]
                    if norm_write(tmp_audio, idx0, idx1): success_count += 1
                    idx1 += 1
                    break
    except Exception as e:
        print(f"处理失败 {{name}}: {{e}}")
print(f"预处理完成: {{success_count}} 个片段")
print(f"0_gt_wavs: {{len(os.listdir(gt_wavs_dir))}} 个文件")
print(f"1_16k_wavs: {{len(os.listdir(wavs16k_dir))}} 个文件")
'''
    
    with open(temp_script, 'w', encoding='utf-8') as f:
        f.write(preprocess_code)
    
    cmd_preprocess = f'"{RVC_PYTHON}" "{temp_script}"'
        
    if not run_rvc_command(cmd_preprocess, "预处理音频"):
        return False
    
    # Step 2: 提取音高特征
    print("\n⌛ Step 2/4: 提取音高特征...")
    cmd_f0 = (
        f'"{RVC_PYTHON}" infer/modules/train/extract/extract_f0_print.py '
        f'{log_exp_dir} 0 {f0method}'
    )
        
    if not run_rvc_command(cmd_f0, "提取音高特征"):
        return False
        
    # Step 3: 提取特征
    print("\n⌛ Step 3/4: 提取声学特征...")
    cmd_feature = (
        f'"{RVC_PYTHON}" infer/modules/train/extract_feature_print.py '
        f'0 1 0 0 {log_exp_dir} v2 0'
    )
    
    if not run_rvc_command(cmd_feature, "提取声学特征"):
        return False
    
    # 生成 filelist（训练前必须）
    print("\n📝 生成 filelist...")
    
    gt_wavs_dir = os.path.join(log_exp_dir, "0_gt_wavs")
    feature_dir = os.path.join(log_exp_dir, "3_feature768")
    f0_dir = os.path.join(log_exp_dir, "2a_f0")
    f0nsf_dir = os.path.join(log_exp_dir, "2b-f0nsf")
    
    # 获取所有音频名称
    from random import shuffle
    
    if if_f0:
        names = (
            set([name.split(".")[0] for name in os.listdir(gt_wavs_dir)])
            & set([name.split(".")[0] for name in os.listdir(feature_dir)])
            & set([name.split(".")[0] for name in os.listdir(f0_dir)])
            & set([name.split(".")[0] for name in os.listdir(f0nsf_dir)])
        )
    else:
        names = set([name.split(".")[0] for name in os.listdir(gt_wavs_dir)]) & set(
            [name.split(".")[0] for name in os.listdir(feature_dir)]
        )
    
    print(f"  找到 {len(names)} 个有效音频")
    
    # 生成 filelist 内容
    opt = []
    for name in names:
        if if_f0:
            opt.append(
                "%s/%s.wav|%s/%s.npy|%s/%s.wav.npy|%s/%s.wav.npy|%s"
                % (
                    gt_wavs_dir.replace("\\", "\\\\"),
                    name,
                    feature_dir.replace("\\", "\\\\"),
                    name,
                    f0_dir.replace("\\", "\\\\"),
                    name,
                    f0nsf_dir.replace("\\", "\\\\"),
                    name,
                    spk_id,
                )
            )
    
    # 添加静音音频（训练需要）
    mute_dir = os.path.join(RVC_DIR, "logs", "mute")
    if os.path.exists(mute_dir):
        for _ in range(2):
            opt.append(
                "%s/0_gt_wavs/mute%s.wav|%s/3_feature768/mute.npy|%s/2a_f0/mute.wav.npy|%s/2b-f0nsf/mute.wav.npy|%s"
                % (
                    mute_dir.replace("\\", "\\\\"),
                    sr_str,
                    mute_dir.replace("\\", "\\\\"),
                    mute_dir.replace("\\", "\\\\"),
                    mute_dir.replace("\\", "\\\\"),
                    spk_id,
                )
            )
    
    shuffle(opt)
    
    filelist_path = os.path.join(log_exp_dir, "filelist.txt")
    with open(filelist_path, "w", encoding="utf-8") as f:
        f.write("\n".join(opt))
    
    print(f"✅ filelist 已生成: {filelist_path}")
    print()
    
    # Step 4: 训练模型
    print("\n⌛ Step 4/4: 训练模型...")
    
    # 先生成 config.json
    import pathlib
    import json
    
    if version == "v1" or sr_str == "40k":
        config_path = "v1/40k.json"
    else:
        config_path = "v2/40k.json"
    
    config_save_path = os.path.join(log_exp_dir, "config.json")
    
    # 读取 RVC 配置模板
    rvc_config_path = os.path.join(RVC_DIR, "configs", config_path)
    
    if os.path.exists(rvc_config_path):
        with open(rvc_config_path, "r", encoding="utf-8") as f:
            config_template = json.load(f)
        
        with open(config_save_path, "w", encoding="utf-8") as f:
            json.dump(config_template, f, indent=4, sort_keys=True)
        
        print(f"✅ 已生成配置文件: {config_save_path}")
    else:
        print(f"❌ 配置模板不存在: {rvc_config_path}")
        return False
    
    # 直接使用命令行调用训练脚本
    cmd_train = (
        f'"{RVC_PYTHON}" infer/modules/train/train.py '
        f'-e {exp_dir} '
        f'-sr {sr_str} '
        f'-f0 {if_f0} '
        f'-bs {batch_size} '
        f'-g {gpus} '
        f'-te {epochs} '
        f'-se 10 '
        f'-pg "{pretrained_G}" '
        f'-pd "{pretrained_D}" '
        f'-l 1 '
        f'-c 1 '
        f'-sw 0 '
        f'-v {version}'
    )
    
    if not run_rvc_command(cmd_train, "训练模型"):
        return False
    
    # Step 5: 训练索引
    print("\n⌛ Step 5/5: 生成索引文件...")
    
    # 使用 Python 脚本生成索引
    index_script_content = '''import sys
import os
import numpy as np
import faiss

os.chdir(r'{RVC_DIR}')
sys.path.insert(0, r'{RVC_DIR}')

exp_dir = "{exp_dir}"
version = "{version}"

exp_path = os.path.join("logs", exp_dir)
feature_dir = os.path.join(exp_path, "3_feature768")

print(f"加载特征 from {{feature_dir}}")

npys = []
for name in sorted(os.listdir(feature_dir)):
    phone = np.load(os.path.join(feature_dir, name))
    npys.append(phone)

big_npy = np.concatenate(npys, 0)
big_npy_idx = np.arange(big_npy.shape[0])
np.random.shuffle(big_npy_idx)
big_npy = big_npy[big_npy_idx]

print(f"特征 shape: {{big_npy.shape}}")

np.save(os.path.join(exp_path, "total_fea.npy"), big_npy)

n_ivf = min(int(16 * np.sqrt(big_npy.shape[0])), big_npy.shape[0] // 39)
print(f"n_ivf: {{n_ivf}}")

index = faiss.index_factory(768, "IVF{{}},Flat".format(n_ivf))
print("training index...")
index_ivf = faiss.extract_index_ivf(index)
index_ivf.nprobe = 1
index.train(big_npy)

index_path = os.path.join(exp_path, "trained_IVF{{}}_Flat_nprobe_1_{{}}_{{}}.index".format(n_ivf, exp_dir, version))
faiss.write_index(index, index_path)
print(f"索引已保存: {{index_path}}")

# 也创建 added_XXX.index
import shutil
added_path = os.path.join(exp_path, "added_{epochs}.index")
shutil.copy(index_path, added_path)
print(f"已复制: {{added_path}}")
print("索引生成完成！")
'''
    
    index_script_path = os.path.join(RVC_DIR, "temp_index_gen.py")
    
    with open(index_script_path, 'w', encoding='utf-8') as f:
        f.write(index_script_content.format(
            RVC_DIR=RVC_DIR,
            exp_dir=exp_dir,
            version=version,
            epochs=epochs
        ))
    
    cmd_index = f'"{RVC_PYTHON}" "{index_script_path}"'
    
    if not run_rvc_command(cmd_index, "生成索引"):
        return False
    
    # 清理临时文件
    if os.path.exists(index_script_path):
        os.remove(index_script_path)
    
    # 查找并验证模型文件（RVC 使用 step count 而非 epoch number）
    model_files = [f for f in os.listdir(log_exp_dir) if f.startswith("G_") and f.endswith(".pth")]
    if not model_files:
        print(f"\n❌ 未找到模型文件")
        return False
    
    # 按数字排序，取最大的（最新的）
    model_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    actual_G = model_files[-1]
    actual_D = actual_G.replace('G_', 'D_')
    
    # 重命名为标准格式 G_{epochs}.pth
    final_G = f"G_{epochs}.pth"
    final_D = f"D_{epochs}.pth"
    
    if actual_G != final_G:
        import shutil
        src_path = os.path.join(log_exp_dir, actual_G)
        dst_path = os.path.join(log_exp_dir, final_G)
        shutil.copy2(src_path, dst_path)
        print(f"✅ 模型已重命名: {actual_G} -> {final_G}")
        
        if os.path.exists(os.path.join(log_exp_dir, actual_D)):
            shutil.copy2(os.path.join(log_exp_dir, actual_D), 
                        os.path.join(log_exp_dir, final_D))
    
    # 转换为 RVC GUI 可用的格式
    print(f"\n🔄 转换为 RVC GUI 格式...")
    try:
        import torch
        
        # 加载训练模型
        cpt = torch.load(os.path.join(log_exp_dir, final_G), map_location='cpu')
        
        # 检查并转换格式
        if 'weight' not in cpt and 'model' in cpt:
            # 需要转换格式
            weight = cpt['model']
            
            # 使用默认配置（v2 40k，18 个参数）
            # 参考: infer/lib/train/process_ckpt.py 的 extract_small_model 函数
            config = [
                1025,  # filter_length // 2 + 1
                32,    # 未知参数
                192,   # inter_channels
                192,   # hidden_channels
                768,   # filter_channels
                2,     # n_heads
                6,     # n_layers
                3,     # kernel_size
                0,     # p_dropout
                "1",   # resblock (必须是字符串！)
                [3, 7, 11],  # resblock_kernel_sizes
                [[1, 3, 5], [1, 3, 5], [1, 3, 5]],  # resblock_dilation_sizes (必须有！)
                [10, 10, 2, 2],  # upsample_rates
                512,   # upsample_initial_channel
                [16, 16, 4, 4],  # upsample_kernel_sizes
                109,   # spk_embed_dim (will be updated)
                256,   # gin_channels
                40000, # sampling_rate
            ]
            
            if isinstance(weight, dict) and 'emb_g.weight' in weight:
                n_spk = weight['emb_g.weight'].shape[0]
                config[15] = n_spk  # spk_embed_dim 在索引 15，不是 11！
                print(f"   n_spk: {n_spk}")
            
            # 创建 RVC 格式
            rvc_cpt = {
                'config': config,
                'weight': weight,
                'info': 'Auto-converted for RVC GUI',
                'f0': 1,  # 有音高
                'version': 'v2',
                'sr': '40k'
            }
            
            # 保存为推理模型
            inference_model = f"{speaker_name}_v2.pth"
            inference_path = os.path.join(log_exp_dir, inference_model)
            torch.save(rvc_cpt, inference_path)
            
            print(f"✅ 已生成 RVC GUI 模型: {inference_model}")
            print(f"   大小: {os.path.getsize(inference_path)/1024/1024:.1f} MB")
        else:
            print(f"✅ 模型已是 RVC 格式，无需转换")
    except Exception as e:
        print(f"⚠️  模型转换失败 ({e})，但不影响使用")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*70}")
    print(f"🎉 {speaker_name} 训练完成！")
    print(f"{'='*70}")
    print(f"📁 模型文件:")
    print(f"   训练模型: {os.path.join(log_exp_dir, final_G)} ({os.path.getsize(os.path.join(log_exp_dir, final_G))/1024/1024:.1f} MB)")
    print(f"   RVC GUI模型: {os.path.join(log_exp_dir, f'{speaker_name}_v2.pth')} (推荐使用)")
    print(f"   索引文件: {os.path.join(log_exp_dir, f'added_{epochs}.index')}")
    print(f"\n💡 在 RVC GUI 中使用 {speaker_name}_v2.pth 进行变声")
    print()
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="RVC 完全自动化训练（支持智能声模匹配）")
    parser.add_argument("--test", action="store_true", help="测试训练 (speaker_0001)")
    parser.add_argument("--all", action="store_true", help="批量训练所有")
    parser.add_argument("--speakers", nargs="+", help="指定 speaker 列表")
    parser.add_argument("--epochs", type=int, default=200, help="训练轮数（使用智能匹配时会自动推荐）")
    parser.add_argument("--batch-size", type=int, default=8, help="Batch Size")
    parser.add_argument("--no-match", action="store_true", help="禁用智能声模匹配，使用默认预训练模型")
    parser.add_argument("--analyze-only", action="store_true", help="仅分析声音特征，不训练")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🚀 RVC 完全自动化训练系统")
    print("=" * 70)
    print()
    
    # 检查环境
    print("📋 检查环境...")
    if not os.path.exists(RVC_PYTHON):
        print(f"❌ RVC Python 不存在: {RVC_PYTHON}")
        return
    
    if not os.path.exists(os.path.join(RVC_DIR, "infer-web.py")):
        print(f"❌ RVC 主文件不存在")
        return
    
    print("✅ RVC 环境正常")
    print()
    
    # 获取所有 speaker（从 enhanced 目录）
    enhanced_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "enhanced")
    if not os.path.exists(enhanced_dir):
        print(f"❌ enhanced 目录不存在: {enhanced_dir}")
        return
    
    speakers = sorted([d for d in os.listdir(enhanced_dir) 
                       if os.path.isdir(os.path.join(enhanced_dir, d)) and d.startswith('speaker_')])
    
    if len(speakers) == 0:
        print("❌ enhanced 目录中没有找到 speaker 数据")
        print("请先运行: python complete_pipeline.py")
        return
    
    print(f"✅ 找到 {len(speakers)} 个 Speaker")
    print()
    
    # 仅分析模式
    if args.analyze_only:
        print("🔍 声音特征分析模式\n")
        from voice_matcher import match_voice
        
        for speaker in speakers:
            speaker_dir = os.path.join(enhanced_dir, speaker)
            if not os.path.isdir(speaker_dir):
                continue
            
            print(f"\n{'='*70}")
            print(f"📊 分析: {speaker}")
            print(f"{'='*70}")
            
            # 匹配声模（打印报告）
            match_voice(speaker_dir, top_n=3, print_report=True)
        
        return
    
    # 确定训练列表
    if args.test:
        speakers_to_train = [speakers[0]]
    elif args.all:
        speakers_to_train = speakers
    elif args.speakers:
        speakers_to_train = args.speakers
    else:
        # 默认测试模式
        print("📋 训练清单:")
        for i, spk in enumerate(speakers, 1):
            audio_count = len([f for f in os.listdir(os.path.join(enhanced_dir, spk)) if f.endswith(".wav")])
            print(f"  {i:2d}. {spk} ({audio_count} 个音频)")
        print()
        print("💡 使用 --test 测试训练，--all 批量训练，--speakers 指定")
        return
    
    # 开始训练
    success_count = 0
    fail_count = 0
    
    auto_match = not args.no_match  # 默认启用智能匹配
    
    for speaker in speakers_to_train:
        success = train_speaker(speaker, args.epochs, args.batch_size, auto_match=auto_match)
        if success:
            success_count += 1
        else:
            fail_count += 1
        
        print(f"\n{'='*70}")
        print(f"📊 进度: {success_count + fail_count}/{len(speakers_to_train)}")
        print(f"   成功: {success_count}")
        print(f"   失败: {fail_count}")
        print(f"{'='*70}")
    
    # 最终统计
    print(f"\n{'='*70}")
    print("🎉 全部训练完成！")
    print(f"{'='*70}")
    print(f"  总计: {len(speakers_to_train)}")
    print(f"  成功: {success_count}")
    print(f"  失败: {fail_count}")
    print()
    print("📁 模型文件位置:")
    print(f"  W:\\rvc\\logs\\speaker_XXXX\\")
    print(f"  - G_{args.epochs}.pth (声模模型)")
    print(f"  - added_{args.epochs}.index (特征索引)")
    print()


if __name__ == "__main__":
    main()
