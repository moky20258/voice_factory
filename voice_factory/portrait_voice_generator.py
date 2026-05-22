#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
人物画像声音生成器
根据人物画像调用 Fish Speech TTS API 生成训练音频
"""

import os
import json
import time
import requests
from typing import Dict, List, Optional
from tqdm import tqdm
from datetime import datetime

from portrait_to_tts_config import generate_tts_params
from portrait_text_generator import get_texts_for_portrait


# API 配置
API_URL = "http://127.0.0.1:8080/v1/tts"
MAX_RETRIES = 3
RETRY_DELAY = 2


def check_api_health() -> bool:
    """检查 Fish Speech API 服务是否可用"""
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


def generate_single_audio(text: str, params: Dict, retries: int = 0) -> Optional[bytes]:
    """
    调用 API 生成单条音频
    
    Args:
        text: 文本内容
        params: TTS 参数
        retries: 当前重试次数
    
    Returns:
        bytes or None: 音频数据
    """
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
                return generate_single_audio(text, params, retries + 1)
            else:
                print(f"\n❌ 生成失败，已达最大重试次数: {response.status_code}")
                return None
                
    except requests.exceptions.Timeout:
        if retries < MAX_RETRIES:
            print(f"\n⚠️ 请求超时，{retries + 1}/{MAX_RETRIES} 重试中...")
            time.sleep(RETRY_DELAY)
            return generate_single_audio(text, params, retries + 1)
        else:
            print("\n❌ 生成超时，已达最大重试次数")
            return None
            
    except Exception as e:
        print(f"\n❌ 生成错误: {e}")
        return None


def generate_voice_from_portrait(
    portrait: str,
    output_dir: str,
    num_sentences: int = 30,
    fixed_seed: Optional[int] = None
) -> Dict:
    """
    根据人物画像生成声音
    
    Args:
        portrait: 人物画像描述
        output_dir: 输出目录
        num_sentences: 生成句子数
        fixed_seed: 固定种子（可选）
    
    Returns:
        dict: 生成结果统计
    """
    print("\n" + "="*70)
    print(f"🎤 开始生成 {portrait} 的声音")
    print("="*70)
    
    # 检查 API
    if not check_api_health():
        return {"success": 0, "failed": 0, "error": "API不可用"}
    
    # 生成 TTS 参数
    tts_params = generate_tts_params(portrait, fixed_seed)
    print(f"\n📊 TTS 参数:")
    print(f"   temperature: {tts_params['temperature']}")
    print(f"   top_p: {tts_params['top_p']}")
    print(f"   repetition_penalty: {tts_params['repetition_penalty']}")
    print(f"   seed: {tts_params['seed']}")
    print(f"   描述: {tts_params['description']}")
    
    # 获取训练文本
    print(f"\n📝 加载训练文本...")
    texts = get_texts_for_portrait(portrait, num_sentences)
    print(f"   文本数量: {len(texts)}")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成音频
    success_count = 0
    fail_count = 0
    
    print(f"\n🎵 开始生成音频...")
    for idx, text in enumerate(tqdm(texts, desc="生成进度")):
        audio_path = os.path.join(output_dir, f"{idx:04d}.wav")
        
        # 检查是否已生成（断点续传）
        if os.path.exists(audio_path):
            success_count += 1
            continue
        
        # 调用 API
        audio_data = generate_single_audio(text, tts_params)
        
        if audio_data:
            with open(audio_path, "wb") as f:
                f.write(audio_data)
            success_count += 1
        else:
            fail_count += 1
            print(f"\n❌ 失败: {idx:04d}.wav")
    
    # 生成 metadata
    metadata = {
        "portrait": portrait,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "params": tts_params,
        "total_sentences": len(texts),
        "success_count": success_count,
        "fail_count": fail_count
    }
    
    meta_path = os.path.join(output_dir, "metadata.json")
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    # 打印总结
    print("\n" + "="*70)
    print("🎉 声音生成完成！")
    print("="*70)
    print(f"✅ 成功: {success_count} 句")
    print(f"❌ 失败: {fail_count} 句")
    print(f"📁 输出目录: {os.path.abspath(output_dir)}")
    print(f"📄 Metadata: {meta_path}")
    print("="*70)
    
    return {
        "success": success_count,
        "failed": fail_count,
        "output_dir": output_dir,
        "metadata": metadata
    }


# 测试代码
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="人物画像声音生成器")
    parser.add_argument("portrait", help="人物画像描述")
    parser.add_argument("-o", "--output", help="输出目录", default=None)
    parser.add_argument("-n", "--num-sentences", type=int, default=5, help="生成句子数")
    parser.add_argument("--seed", type=int, default=None, help="固定种子")
    
    args = parser.parse_args()
    
    # 默认输出目录
    if args.output is None:
        safe_name = args.portrait.replace(" ", "_").replace("/", "_")
        args.output = f"outputs/test_{safe_name}"
    
    # 生成声音
    result = generate_voice_from_portrait(
        args.portrait,
        args.output,
        args.num_sentences,
        args.seed
    )
    
    if result["success"] > 0:
        print("\n✅ 测试成功！可以开始生成完整数据集。")
    else:
        print("\n❌ 测试失败，请检查 API 服务和参数配置。")
