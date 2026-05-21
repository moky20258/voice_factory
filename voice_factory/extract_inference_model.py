#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
提取 RVC 推理小模型
将完整训练的 checkpoint 转换为可用于推理的轻量级模型
"""

import os
import sys
import torch
import argparse


def extract_small_model(
    checkpoint_path,
    output_path,
    device="cpu"
):
    """
    提取推理小模型
    
    Args:
        checkpoint_path: 完整训练模型路径 (G_XXX.pth)
        output_path: 输出推理模型路径
        device: 设备 (cpu/cuda)
    """
    print(f"📦 加载完整模型: {checkpoint_path}")
    
    # 加载 checkpoint
    cpt = torch.load(checkpoint_path, map_location=device)
    
    print(f"   模型键: {list(cpt.keys())}")
    
    # 检查格式
    if "weight" not in cpt:
        print("❌ 模型格式错误：缺少 'weight' 键")
        print("   这可能是训练中间文件，请使用 G_XXX.pth 或 D_XXX.pth")
        return False
    
    # 提取必要信息
    config = cpt["config"]
    weight = cpt["weight"]
    
    print(f"   配置: {config[:5]}...")
    print(f"   权重数量: {len(weight)}")
    
    # 更新 n_spk
    if "emb_g.weight" in weight:
        n_spk = weight["emb_g.weight"].shape[0]
        config[-3] = n_spk
        print(f"   n_spk: {n_spk}")
    
    # 创建新的精简 checkpoint
    small_cpt = {
        "config": config,
        "weight": weight,
        "info": cpt.get("info", "")
    }
    
    # 保存
    print(f"💾 保存推理模型: {output_path}")
    torch.save(small_cpt, output_path)
    
    # 显示文件大小
    original_size = os.path.getsize(checkpoint_path)
    new_size = os.path.getsize(output_path)
    
    print(f"\n📊 模型大小:")
    print(f"   原始: {original_size / 1024 / 1024:.2f} MB")
    print(f"   精简: {new_size / 1024 / 1024:.2f} MB")
    print(f"   压缩率: {(1 - new_size / original_size) * 100:.1f}%")
    
    return True


def process_directory(log_dir, epochs, output_dir=None):
    """
    处理目录中的所有模型
    
    Args:
        log_dir: RVC logs 目录下的 speaker 目录
        epochs: epoch 数
        output_dir: 输出目录（默认与 log_dir 相同）
    """
    if output_dir is None:
        output_dir = log_dir
    
    # 查找模型文件
    g_model = os.path.join(log_dir, f"G_{epochs}.pth")
    
    if not os.path.exists(g_model):
        # 尝试查找其他格式
        import glob
        g_files = glob.glob(os.path.join(log_dir, "G_*.pth"))
        if g_files:
            # 使用最新的
            g_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
            g_model = g_files[-1]
            print(f"⚠️  未找到 G_{epochs}.pth，使用: {os.path.basename(g_model)}")
        else:
            print(f"❌ 未找到模型文件: {g_model}")
            return False
    
    # 输出路径
    output_name = f"small_{os.path.basename(g_model)}"
    output_path = os.path.join(output_dir, output_name)
    
    # 提取
    return extract_small_model(g_model, output_path)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="提取 RVC 推理小模型")
    parser.add_argument("model_path", help="模型文件路径 (G_XXX.pth)")
    parser.add_argument("-o", "--output", help="输出路径（默认: small_G_XXX.pth）")
    parser.add_argument("--device", default="cpu", help="设备 (cpu/cuda)")
    
    args = parser.parse_args()
    
    # 检查文件
    if not os.path.exists(args.model_path):
        print(f"❌ 文件不存在: {args.model_path}")
        return
    
    # 确定输出路径
    if args.output:
        output_path = args.output
    else:
        dir_name = os.path.dirname(args.model_path)
        base_name = os.path.basename(args.model_path)
        output_path = os.path.join(dir_name, f"small_{base_name}")
    
    # 提取
    success = extract_small_model(args.model_path, output_path, args.device)
    
    if success:
        print(f"\n✅ 推理模型提取成功!")
        print(f"   路径: {output_path}")
        print(f"\n💡 现在可以在 RVC GUI 中使用此模型进行变声")


if __name__ == "__main__":
    main()
