#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
转换 PyTorch Lightning checkpoint 为 RVC 原生格式
"""

import os
import sys
import io

# 修复 Windows GBK 编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import torch
import argparse


def convert_lightning_to_rvc(checkpoint_path, output_path, device="cpu"):
    """
    转换 Lightning checkpoint 为 RVC 格式
    
    Args:
        checkpoint_path: Lightning checkpoint 路径
        output_path: 输出 RVC 格式路径
        device: 设备
    """
    print(f"🔄 转换模型: {os.path.basename(checkpoint_path)}")
    
    # 加载 checkpoint
    cpt = torch.load(checkpoint_path, map_location=device)
    
    print(f"   原始键: {list(cpt.keys())}")
    
    # 检查是否是 Lightning 格式
    if "state_dict" in cpt:
        # Lightning 格式
        state_dict = cpt["state_dict"]
        print(f"   检测到 Lightning 格式")
        
        # 提取 generator 权重
        weight = {}
        for key, value in state_dict.items():
            # 移除模块前缀
            if key.startswith("generator."):
                new_key = key[len("generator."):]
                weight[new_key] = value
            elif key.startswith("module.generator."):
                new_key = key[len("module.generator."):]
                weight[new_key] = value
            else:
                weight[key] = value
        
        print(f"   权重数量: {len(weight)}")
        
        # 创建 RVC 格式
        # 注意：需要从配置文件中获取 config
        # 这里使用默认的 v2 40k 配置
        config = [
            40,  # sample_rate
            12800,  # segment_size
            2048,  # filter_length
            400,  # hop_length
            512,  # upsample_initial_channel
            [[1, 3, 5], [1, 3, 5], [1, 3, 5]],  # resblock_dilation_sizes
            [3, 7, 11],  # resblock_kernel_sizes
            [10, 10, 2, 2],  # upsample_rates
            [16, 16, 4, 4],  # upsample_kernel_sizes
            1,  # if_f0
            1,  # spk_embed_dim (will be updated)
            192,  # inter_channels
            192,  # hidden_channels
            6,  # n_layers
            2,  # n_heads
            3,  # kernel_size
            0,  # p_dropout
            "1",  # resblock
            109,  # gin_channels
            False,  # use_spectral_norm
        ]
        
        # 更新 n_spk
        if "emb_g.weight" in weight:
            config[11] = weight["emb_g.weight"].shape[0]
            print(f"   n_spk: {config[11]}")
        
        rvc_cpt = {
            "config": config,
            "weight": weight,
            "info": "Converted from Lightning checkpoint"
        }
        
    elif "model" in cpt:
        # 另一种格式：model 键直接包含权重
        print(f"   检测到 model 格式")
        weight = cpt["model"]
        
        if isinstance(weight, dict):
            print(f"   权重数量: {len(weight)}")
            
            # 使用默认配置（v2 40k，18 个参数）
            # 参考: infer/lib/train/process_ckpt.py 的 extract_small_model 函数
            config = [
                1025,  # filter_length // 2 + 1
                32,  # 未知参数
                192,  # inter_channels
                192,  # hidden_channels
                768,  # filter_channels
                2,  # n_heads
                6,  # n_layers
                3,  # kernel_size
                0,  # p_dropout
                "1",  # resblock
                [3, 7, 11],  # resblock_kernel_sizes
                [[1, 3, 5], [1, 3, 5], [1, 3, 5]],  # resblock_dilation_sizes
                [10, 10, 2, 2],  # upsample_rates
                512,  # upsample_initial_channel
                [16, 16, 4, 4],  # upsample_kernel_sizes
                109,  # spk_embed_dim (will be updated)
                256,  # gin_channels
                40000,  # sampling_rate
            ]
            
            if "emb_g.weight" in weight:
                n_spk = weight["emb_g.weight"].shape[0]
                config[15] = n_spk  # spk_embed_dim 在索引 15
                print(f"   n_spk: {n_spk}")
            
            rvc_cpt = {
                'config': config,
                'weight': weight,
                'info': 'Converted from model format',
                'f0': 1,
                'version': 'v2',
                'sr': '40k'
            }
        else:
            print(f"❌ model 键不是字典格式")
            return False
    else:
        print(f"❌ 无法识别的 checkpoint 格式")
        return False
    
    # 保存
    print(f"💾 保存 RVC 格式: {output_path}")
    torch.save(rvc_cpt, output_path)
    
    # 显示大小
    new_size = os.path.getsize(output_path)
    print(f"   文件大小: {new_size / 1024 / 1024:.2f} MB")
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="转换 Lightning checkpoint 为 RVC 格式")
    parser.add_argument("checkpoint", help="Lightning checkpoint 路径")
    parser.add_argument("-o", "--output", help="输出路径")
    parser.add_argument("--device", default="cpu", help="设备")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.checkpoint):
        print(f"❌ 文件不存在: {args.checkpoint}")
        return
    
    if args.output:
        output = args.output
    else:
        dir_name = os.path.dirname(args.checkpoint)
        base_name = os.path.basename(args.checkpoint)
        output = os.path.join(dir_name, f"rvc_{base_name}")
    
    success = convert_lightning_to_rvc(args.checkpoint, output, args.device)
    
    if success:
        print(f"\n✅ 转换成功!")
        print(f"   路径: {output}")
        print(f"\n💡 现在可以在 RVC GUI 中使用")


if __name__ == "__main__":
    main()
