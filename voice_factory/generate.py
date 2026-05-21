"""
Fish Speech 批量声音人格生成器（第一阶段）
功能：
- 自动读取 texts/ 目录下所有文本
- 批量生成 20 个 speaker，每个 30 句
- 自动随机 seed 和采样参数
- 自动创建目录结构和 metadata
- 支持断点续传和错误重试
"""

import os
import json
import random
import time
import requests
from tqdm import tqdm
from datetime import datetime

# =========================
# 配置参数
# =========================
API_URL = "http://127.0.0.1:8080/v1/tts"

# 输入文本目录
TEXT_DIR = "texts"

# 输出目录
OUTPUT_DIR = "outputs"

# metadata 目录
META_DIR = "metadata"

# 生成配置
NUM_SPEAKERS = 20  # 生成多少个 speaker
LINES_PER_SPEAKER = 30  # 每个 speaker 生成多少句

# 重试配置
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 2  # 重试延迟（秒）

# 批量生成新音色参数范围
TEMP_RANGE = (0.75, 0.85)
TOP_P_RANGE = (0.80, 0.90)
REPEAT_PENALTY_RANGE = (1.10, 1.20)

# 创建目录
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)


def load_texts():
    """加载 texts/ 目录下所有文本文件"""
    texts = []
    
    if not os.path.exists(TEXT_DIR):
        print(f"❌ 文本目录不存在: {TEXT_DIR}")
        return texts
    
    for file in sorted(os.listdir(TEXT_DIR)):
        if file.endswith(".txt"):
            path = os.path.join(TEXT_DIR, file)
            
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                
                if content:
                    # 按行分割，过滤空行
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                    texts.extend(lines)
    
    print(f"✅ 加载文本数量: {len(texts)}")
    return texts


def generate_random_params():
    """生成随机采样参数（批量生成新音色模式）"""
    seed = random.randint(1000, 999999)
    temperature = round(random.uniform(*TEMP_RANGE), 2)
    top_p = round(random.uniform(*TOP_P_RANGE), 2)
    repetition_penalty = round(random.uniform(*REPEAT_PENALTY_RANGE), 2)
    
    return {
        "seed": seed,
        "temperature": temperature,
        "top_p": top_p,
        "repetition_penalty": repetition_penalty
    }


def save_metadata(speaker_name, params):
    """保存 speaker 的 metadata"""
    metadata = {
        "speaker": speaker_name,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "params": params
    }
    
    meta_path = os.path.join(META_DIR, f"{speaker_name}.json")
    
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)


def check_api_health():
    """检查 API 服务是否可用"""
    try:
        response = requests.get("http://127.0.0.1:8080/", timeout=5)
        if response.status_code == 200:
            print("✅ Fish Speech API 服务正常")
            return True
        else:
            print(f"⚠️ API 返回状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 Fish Speech API")
        print("💡 请先启动 Fish Speech API 服务器:")
        print("   python tools/api_server.py")
        return False
    except Exception as e:
        print(f"❌ API 健康检查失败: {e}")
        return False


def generate_audio(text, params, retries=0):
    """调用 API 生成单条音频"""
    payload = {
        "text": text,
        "temperature": params["temperature"],
        "top_p": params["top_p"],
        "repetition_penalty": params["repetition_penalty"],
        "seed": params["seed"]
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            return response.content
        else:
            if retries < MAX_RETRIES:
                print(f"\n⚠️ 生成失败 (状态码: {response.status_code})，{retries + 1}/{MAX_RETRIES} 重试中...")
                time.sleep(RETRY_DELAY)
                return generate_audio(text, params, retries + 1)
            else:
                print(f"\n❌ 生成失败，已达最大重试次数: {response.status_code}")
                return None
                
    except requests.exceptions.Timeout:
        if retries < MAX_RETRIES:
            print(f"\n⚠️ 请求超时，{retries + 1}/{MAX_RETRIES} 重试中...")
            time.sleep(RETRY_DELAY)
            return generate_audio(text, params, retries + 1)
        else:
            print("\n❌ 生成超时，已达最大重试次数")
            return None
            
    except Exception as e:
        print(f"\n❌ 生成错误: {e}")
        return None


def main():
    """主函数"""
    print("=" * 60)
    print("🎤 Fish Speech 批量声音人格生成器")
    print("=" * 60)
    
    # 检查 API
    if not check_api_health():
        return
    
    # 加载文本
    texts = load_texts()
    
    if len(texts) == 0:
        print("❌ 没有找到文本，请先在 texts/ 目录下放置 .txt 文件")
        return
    
    if len(texts) < LINES_PER_SPEAKER:
        print(f"⚠️ 文本数量不足：需要 {LINES_PER_SPEAKER} 句，实际只有 {len(texts)} 句")
        print("💡 将使用全部文本进行生成")
    
    # 开始生成
    print(f"\n🚀 开始生成: {NUM_SPEAKERS} 个 speaker，每个 {LINES_PER_SPEAKER} 句")
    print(f"📊 预计总音频数: {NUM_SPEAKERS * LINES_PER_SPEAKER}")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for speaker_id in range(1, NUM_SPEAKERS + 1):
        speaker_name = f"speaker_{speaker_id:04d}"
        speaker_dir = os.path.join(OUTPUT_DIR, speaker_name)
        
        # 创建 speaker 目录
        os.makedirs(speaker_dir, exist_ok=True)
        
        # 检查是否已存在（断点续传）
        existing_files = [f for f in os.listdir(speaker_dir) if f.endswith(".wav")]
        if len(existing_files) >= LINES_PER_SPEAKER:
            print(f"\n⏭️ 跳过 {speaker_name} (已生成 {len(existing_files)} 句)")
            success_count += LINES_PER_SPEAKER
            continue
        
        # 生成随机参数
        params = generate_random_params()
        
        # 保存 metadata
        save_metadata(speaker_name, params)
        
        print(f"\n🎵 开始生成: {speaker_name}")
        print(f"   参数: seed={params['seed']}, temp={params['temperature']}, "
              f"top_p={params['top_p']}, penalty={params['repetition_penalty']}")
        
        # 随机抽取文本
        selected_texts = random.sample(
            texts,
            min(LINES_PER_SPEAKER, len(texts))
        )
        
        # 生成音频
        for idx, text in enumerate(tqdm(selected_texts, desc=f"  {speaker_name}")):
            # 检查是否已生成
            audio_path = os.path.join(speaker_dir, f"{idx:04d}.wav")
            if os.path.exists(audio_path):
                success_count += 1
                continue
            
            # 调用 API
            audio_data = generate_audio(text, params)
            
            if audio_data:
                with open(audio_path, "wb") as f:
                    f.write(audio_data)
                success_count += 1
            else:
                fail_count += 1
                print(f"\n❌ 失败: {speaker_name}/{idx:04d}.wav")
        
        print(f"✅ {speaker_name} 生成完成")
    
    # 生成总结
    print("\n" + "=" * 60)
    print("🎉 全部生成完成！")
    print("=" * 60)
    print(f"✅ 成功: {success_count} 句")
    print(f"❌ 失败: {fail_count} 句")
    print(f"📁 输出目录: {os.path.abspath(OUTPUT_DIR)}")
    print(f"📄 Metadata: {os.path.abspath(META_DIR)}")
    print("=" * 60)
    print("\n💡 下一步: 运行质量筛选器")
    print("   python quality_filter.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
