#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
声音特征分析工具
用于提取说话人的声音特征，为声模匹配提供依据
"""

import os
import sys
import json
import argparse
import numpy as np
import librosa
from scipy import signal


def extract_voice_features(audio_path, sr=40000):
    """
    提取声音特征
    
    Args:
        audio_path: 音频文件路径
        sr: 采样率（默认 40kHz）
    
    Returns:
        dict: 声音特征字典
    """
    print(f"📊 分析音频: {os.path.basename(audio_path)}")
    
    # 加载音频
    y, audio_sr = librosa.load(audio_path, sr=sr)
    duration = len(y) / sr
    
    print(f"   时长: {duration:.2f} 秒")
    print(f"   采样率: {audio_sr} Hz")
    
    # 1. 基频 (F0) 分析
    print("   提取基频特征...")
    f0 = librosa.pyin(y, fmin=50, fmax=800, sr=sr)[0]
    f0 = f0[~np.isnan(f0)]  # 去除 NaN
    
    if len(f0) == 0:
        print("   ⚠️  无法检测到基频")
        f0_stats = {
            'f0_mean': 150.0,
            'f0_std': 30.0,
            'f0_min': 80.0,
            'f0_max': 300.0,
            'f0_median': 150.0
        }
    else:
        f0_stats = {
            'f0_mean': float(np.mean(f0)),
            'f0_std': float(np.std(f0)),
            'f0_min': float(np.min(f0)),
            'f0_max': float(np.max(f0)),
            'f0_median': float(np.median(f0)),
            'f0_percentile_25': float(np.percentile(f0, 25)),
            'f0_percentile_75': float(np.percentile(f0, 75))
        }
    
    # 2. 音域分析
    pitch_range = f0_stats['f0_max'] - f0_stats['f0_min']
    
    # 3. 推测性别
    if f0_stats['f0_mean'] < 165:
        estimated_gender = 'male'
        gender_confidence = min(0.95, 0.5 + (165 - f0_stats['f0_mean']) / 200)
    else:
        estimated_gender = 'female'
        gender_confidence = min(0.95, 0.5 + (f0_stats['f0_mean'] - 165) / 200)
    
    # 4. 推测年龄范围
    if f0_stats['f0_mean'] < 120:
        age_range = 'adult_deep'  # 成年男低音
    elif f0_stats['f0_mean'] < 165:
        age_range = 'adult_normal'  # 成年男中音
    elif f0_stats['f0_mean'] < 200:
        age_range = 'adult_high'  # 成年男高音/女低音
    elif f0_stats['f0_mean'] < 250:
        age_range = 'female_normal'  # 成年女中音
    else:
        age_range = 'female_high'  # 成年女高音
    
    # 5. 频谱特征（音色）
    print("   提取频谱特征...")
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.85)[0]
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    
    spectral_features = {
        'spectral_centroid_mean': float(np.mean(spectral_centroids)),
        'spectral_centroid_std': float(np.std(spectral_centroids)),
        'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
        'mfcc_mean': [float(np.mean(mfccs[i])) for i in range(13)],
        'mfcc_std': [float(np.std(mfccs[i])) for i in range(13)]
    }
    
    # 6. 共振峰特征（Formants）
    print("   提取共振峰特征...")
    formants = extract_formants(y, sr)
    
    # 7. 响度特征
    rms = librosa.feature.rms(y=y)[0]
    loudness_features = {
        'loudness_mean': float(np.mean(rms)),
        'loudness_std': float(np.std(rms)),
        'loudness_max': float(np.max(rms))
    }
    
    # 8. 音质评估
    # 信噪比估计（简单版）
    noise_floor = np.percentile(np.abs(y), 10)
    signal_level = np.percentile(np.abs(y), 90)
    snr_estimate = 20 * np.log10(signal_level / max(noise_floor, 1e-10))
    
    # 剪辑检测
    clipping_ratio = np.sum(np.abs(y) > 0.99) / len(y)
    
    quality_features = {
        'snr_estimate_db': float(snr_estimate),
        'clipping_ratio': float(clipping_ratio),
        'quality_score': calculate_quality_score(snr_estimate, clipping_ratio)
    }
    
    # 整合所有特征
    features = {
        'audio_file': os.path.basename(audio_path),
        'duration': duration,
        'sample_rate': int(audio_sr),
        'f0': f0_stats,
        'pitch_range': float(pitch_range),
        'estimated_gender': estimated_gender,
        'gender_confidence': float(gender_confidence),
        'age_range': age_range,
        'spectral': spectral_features,
        'formants': formants,
        'loudness': loudness_features,
        'quality': quality_features
    }
    
    return features


def extract_formants(y, sr, max_formants=3):
    """
    提取共振峰频率
    
    Args:
        y: 音频信号
        sr: 采样率
        max_formants: 最大共振峰数量
    
    Returns:
        dict: 共振峰特征
    """
    try:
        # 使用简化的频谱峰值方法（不依赖 lpc）
        # 分帧处理
        frame_length = int(0.025 * sr)  # 25ms 帧
        hop_length = int(0.010 * sr)    # 10ms 跳帧
        
        formant_freqs = []
        
        # 只分析前 5 帧（提速）
        frame_count = 0
        for start in range(0, min(len(y) - frame_length, 5 * hop_length + frame_length), hop_length):
            frame = y[start:start + frame_length]
            frame = frame * np.hamming(len(frame))  # 加窗
            
            try:
                # 简化的共振峰检测
                spectrum = np.abs(np.fft.rfft(frame, n=1024))
                peaks = find_spectral_peaks(spectrum, sr, max_peaks=max_formants)
                formant_freqs.extend(peaks[:max_formants])
                frame_count += 1
                if frame_count >= 5:
                    break
            except:
                continue
        
        if len(formant_freqs) == 0:
            return {f'F{i+1}_mean': 500 * (i + 1) for i in range(max_formants)}
        
        # 统计共振峰
        formants = {}
        for i in range(max_formants):
            freqs = [f[i] for f in formant_freqs if len(f) > i]
            if freqs:
                formants[f'F{i+1}_mean'] = float(np.mean(freqs))
                formants[f'F{i+1}_std'] = float(np.std(freqs))
            else:
                formants[f'F{i+1}_mean'] = 500 * (i + 1)
                formants[f'F{i+1}_std'] = 100.0
        
        return formants
    except Exception as e:
        print(f"   ⚠️  共振峰提取失败: {e}")
        return {f'F{i+1}_mean': 500 * (i + 1) for i in range(max_formants)}


def find_spectral_peaks(spectrum, sr, max_peaks=3):
    """
    查找频谱峰值（共振峰候选）
    
    Args:
        spectrum: 频谱
        sr: 采样率
        max_peaks: 最大峰值数
    
    Returns:
        list: 峰值频率列表
    """
    from scipy.signal import find_peaks
    
    # 只在 300-4000 Hz 范围内查找（共振峰典型范围）
    freq_resolution = sr / len(spectrum)
    start_bin = int(300 / freq_resolution)
    end_bin = int(4000 / freq_resolution)
    
    spectrum_region = spectrum[start_bin:end_bin]
    
    # 查找峰值
    peaks, _ = find_peaks(spectrum_region, height=np.max(spectrum_region) * 0.1)
    
    # 转换为频率
    peak_freqs = [(start_bin + p) * freq_resolution for p in peaks[:max_peaks]]
    
    return [peak_freqs]


def calculate_quality_score(snr, clipping_ratio):
    """
    计算音质评分（0-100）
    
    Args:
        snr: 信噪比（dB）
        clipping_ratio: 剪辑比例
    
    Returns:
        float: 质量评分
    """
    # SNR 评分（0-50 分）
    snr_score = min(50, max(0, snr / 40 * 50))
    
    # 剪辑评分（0-30 分）
    clipping_score = max(0, 30 - clipping_ratio * 3000)
    
    # 基础分（20 分）
    base_score = 20
    
    total_score = base_score + snr_score + clipping_score
    
    return round(min(100, max(0, total_score)), 2)


def analyze_directory(audio_dir, output_file=None, max_samples=10):
    """
    分析目录下所有音频文件
    
    Args:
        audio_dir: 音频目录
        output_file: 输出 JSON 文件路径
        max_samples: 最大采样文件数（默认 10 个，提速）
    
    Returns:
        dict: 所有音频的特征
    """
    print(f"\n📁 分析目录: {audio_dir}\n")
    
    # 找到所有 wav 文件
    wav_files = sorted([f for f in os.listdir(audio_dir) if f.endswith('.wav')])
    
    if not wav_files:
        print("❌ 未找到 wav 文件")
        return {}
    
    # 采样分析（提速）
    if len(wav_files) > max_samples:
        import random
        random.seed(42)  # 固定种子，保证可重复
        sample_files = random.sample(wav_files, max_samples)
        sample_files.sort()  # 保持顺序
        print(f"找到 {len(wav_files)} 个音频文件，采样分析 {max_samples} 个\n")
    else:
        sample_files = wav_files
        print(f"找到 {len(wav_files)} 个音频文件\n")
    
    all_features = {}
    
    for i, wav_file in enumerate(sample_files, 1):
        audio_path = os.path.join(audio_dir, wav_file)
        print(f"\n[{i}/{len(sample_files)}] 处理: {wav_file}")
        
        try:
            features = extract_voice_features(audio_path)
            all_features[wav_file] = features
        except Exception as e:
            print(f"   ❌ 处理失败: {e}")
            continue
    
    # 计算平均特征
    print("\n📊 计算平均特征...")
    avg_features = calculate_average_features(all_features)
    
    # 保存结果
    result = {
        'directory': audio_dir,
        'total_audio_count': len(wav_files),
        'analyzed_count': len(all_features),
        'individual_features': all_features,
        'average_features': avg_features
    }
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 结果已保存: {output_file}")
    
    return result


def calculate_average_features(all_features):
    """
    计算平均特征
    
    Args:
        all_features: 所有音频的特征字典
    
    Returns:
        dict: 平均特征
    """
    if not all_features:
        return {}
    
    # 收集所有 F0 均值
    f0_means = [f['f0']['f0_mean'] for f in all_features.values()]
    f0_stds = [f['f0']['f0_std'] for f in all_features.values()]
    pitch_ranges = [f['pitch_range'] for f in all_features.values()]
    
    # 统计性别
    genders = [f['estimated_gender'] for f in all_features.values()]
    male_count = genders.count('male')
    female_count = genders.count('female')
    
    avg = {
        'f0_mean': float(np.mean(f0_means)),
        'f0_std': float(np.mean(f0_stds)),
        'pitch_range_mean': float(np.mean(pitch_ranges)),
        'estimated_gender': 'male' if male_count > female_count else 'female',
        'gender_distribution': {
            'male': male_count,
            'female': female_count
        },
        'audio_count': len(all_features)
    }
    
    return avg


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="声音特征分析工具")
    parser.add_argument("audio_path", help="音频文件路径或目录")
    parser.add_argument("-o", "--output", help="输出 JSON 文件路径")
    parser.add_argument("--single", action="store_true", help="强制作为单个文件处理")
    
    args = parser.parse_args()
    
    if args.single or os.path.isfile(args.audio_path):
        # 分析单个文件
        features = extract_voice_features(args.audio_path)
        
        # 打印结果
        print("\n" + "="*60)
        print("📊 声音特征分析结果")
        print("="*60)
        print(f"文件: {features['audio_file']}")
        print(f"时长: {features['duration']:.2f} 秒")
        print(f"\n基频特征:")
        print(f"  均值: {features['f0']['f0_mean']:.2f} Hz")
        print(f"  标准差: {features['f0']['f0_std']:.2f} Hz")
        print(f"  范围: {features['f0']['f0_min']:.2f} - {features['f0']['f0_max']:.2f} Hz")
        print(f"\n音域: {features['pitch_range']:.2f} Hz")
        print(f"\n推测性别: {features['estimated_gender']} (置信度: {features['gender_confidence']:.2f})")
        print(f"年龄范围: {features['age_range']}")
        print(f"\n音质评分: {features['quality']['quality_score']:.1f}/100")
        print(f"  信噪比: {features['quality']['snr_estimate_db']:.2f} dB")
        print(f"  剪辑率: {features['quality']['clipping_ratio']:.4f}")
        
        # 保存
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(features, f, indent=2, ensure_ascii=False)
            print(f"\n✅ 结果已保存: {args.output}")
    else:
        # 分析目录
        analyze_directory(args.audio_path, args.output)
        
        # 打印摘要
        if args.output and os.path.exists(args.output):
            with open(args.output, 'r', encoding='utf-8') as f:
                result = json.load(f)
            
            avg = result['average_features']
            print("\n" + "="*60)
            print("📊 目录分析摘要")
            print("="*60)
            print(f"音频数量: {result['audio_count']}")
            print(f"平均 F0: {avg['f0_mean']:.2f} Hz")
            print(f"平均音域: {avg['pitch_range_mean']:.2f} Hz")
            print(f"推测性别: {avg['estimated_gender']} (男:{avg['gender_distribution']['male']}, 女:{avg['gender_distribution']['female']})")


if __name__ == "__main__":
    main()
