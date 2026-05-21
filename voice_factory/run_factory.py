"""
Fish Speech 声模工厂 - 一键工作流
功能：
- 自动执行完整流水线：生成 → 筛选 → 报告
- 支持分阶段运行
- 自动生成完整的项目结构和使用说明
"""

import os
import sys
import json
import argparse
from datetime import datetime

# =========================
# 配置
# =========================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TEXTS_DIR = os.path.join(PROJECT_ROOT, "texts")
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")
META_DIR = os.path.join(PROJECT_ROOT, "metadata")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
FILTERED_DIR = os.path.join(PROJECT_ROOT, "filtered")


def print_banner():
    """打印欢迎横幅"""
    print("=" * 70)
    print(" " * 15 + "🎤 Fish Speech 声模工厂 🎤")
    print(" " * 10 + "Voice Personality Factory v1.0")
    print("=" * 70)
    print()


def check_environment():
    """检查环境"""
    print("📋 环境检查...")
    
    # 检查 Python 版本
    python_version = sys.version_info
    print(f"  Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major == 3 and python_version.minor < 10:
        print("  ❌ Python 版本过低，需要 3.10+")
        return False
    elif python_version.major == 3 and python_version.minor > 12:
        print("  ⚠️ Python 版本较高，可能存在兼容性问题（推荐 3.10-3.12）")
    
    # 检查目录
    if not os.path.exists(TEXTS_DIR):
        print(f"  ❌ 文本目录不存在: {TEXTS_DIR}")
        return False
    
    text_count = len([f for f in os.listdir(TEXTS_DIR) if f.endswith(".txt")])
    print(f"  ✅ 文本文件: {text_count} 个")
    
    if text_count == 0:
        print("  ❌ 没有找到 .txt 文件")
        return False
    
    # 检查依赖
    try:
        import requests
        print("  ✅ requests 已安装")
    except ImportError:
        print("  ❌ 缺少依赖: requests")
        return False
    
    try:
        import tqdm
        print("  ✅ tqdm 已安装")
    except ImportError:
        print("  ❌ 缺少依赖: tqdm")
        return False
    
    try:
        from faster_whisper import WhisperModel
        print("  ✅ faster-whisper 已安装")
    except ImportError:
        print("  ⚠️ faster-whisper 未安装（质量筛选需要）")
    
    print()
    return True


def run_generation():
    """运行批量生成"""
    print("=" * 70)
    print("🚀 阶段 1: 批量音频生成")
    print("=" * 70)
    print()
    
    # 导入并运行生成器
    sys.path.insert(0, PROJECT_ROOT)
    from generate import main as generate_main
    
    generate_main()
    
    print()


def run_filtering():
    """运行质量筛选"""
    print("=" * 70)
    print("🔍 阶段 2: 音频质量筛选")
    print("=" * 70)
    print()
    
    # 检查是否有音频
    if not os.path.exists(OUTPUTS_DIR):
        print("❌ 没有音频文件，请先运行阶段 1")
        return
    
    audio_count = 0
    for speaker_dir in os.listdir(OUTPUTS_DIR):
        speaker_path = os.path.join(OUTPUTS_DIR, speaker_dir)
        if os.path.isdir(speaker_path):
            audio_count += len([f for f in os.listdir(speaker_path) if f.endswith(".wav")])
    
    if audio_count == 0:
        print("❌ 没有音频文件，请先运行阶段 1")
        return
    
    print(f"✅ 找到 {audio_count} 个音频文件")
    print()
    
    # 导入并运行筛选器
    from quality_filter import main as filter_main
    
    filter_main()
    
    print()


def generate_summary():
    """生成项目总结"""
    print("=" * 70)
    print("📊 项目总结")
    print("=" * 70)
    print()
    
    # 统计生成的音频
    if os.path.exists(OUTPUTS_DIR):
        speaker_count = len([d for d in os.listdir(OUTPUTS_DIR) 
                            if os.path.isdir(os.path.join(OUTPUTS_DIR, d))])
        
        audio_count = 0
        for speaker_dir in os.listdir(OUTPUTS_DIR):
            speaker_path = os.path.join(OUTPUTS_DIR, speaker_dir)
            if os.path.isdir(speaker_path):
                audio_count += len([f for f in os.listdir(speaker_path) if f.endswith(".wav")])
        
        print(f"📁 生成的 Speaker: {speaker_count} 个")
        print(f"🎵 生成的音频: {audio_count} 个")
        print(f"📂 输出目录: {os.path.abspath(OUTPUTS_DIR)}")
        print()
    
    # 统计筛选结果
    if os.path.exists(FILTERED_DIR):
        print("📋 质量分类:")
        for quality_type in ["good", "acceptable", "poor", "repeated", "empty"]:
            type_path = os.path.join(FILTERED_DIR, quality_type)
            if os.path.exists(type_path):
                type_count = 0
                for speaker_dir in os.listdir(type_path):
                    speaker_path = os.path.join(type_path, speaker_dir)
                    if os.path.isdir(speaker_path):
                        type_count += len([f for f in os.listdir(speaker_path) if f.endswith(".wav")])
                
                labels = {
                    "good": "✅ 优质",
                    "acceptable": "⚠️ 可接受",
                    "poor": "❌ 低质量",
                    "repeated": "🔁 重复",
                    "empty": "⭕ 空输出"
                }
                print(f"  {labels.get(quality_type, quality_type)}: {type_count} 个")
        print()
    
    # 统计报告
    if os.path.exists(REPORTS_DIR):
        report_files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".json")]
        if report_files:
            latest_report = sorted(report_files)[-1]
            print(f"📄 最新报告: {os.path.join(REPORTS_DIR, latest_report)}")
            
            with open(os.path.join(REPORTS_DIR, latest_report), "r", encoding="utf-8") as f:
                report = json.load(f)
                print(f"   总音频数: {report.get('total', 0)}")
                
                stats = report.get("quality_stats", {})
                total = sum(stats.values()) if stats else 0
                if total > 0:
                    good_rate = (stats.get("good", 0) + stats.get("acceptable", 0)) / total * 100
                    print(f"   优质率: {good_rate:.1f}%")
            print()
    
    # 给出下一步建议
    print("=" * 70)
    print("💡 下一步建议")
    print("=" * 70)
    print()
    print("1. 检查优质音频:")
    print(f"   目录: {os.path.abspath(os.path.join(FILTERED_DIR, 'good'))}")
    print()
    print("2. 人工试听筛选:")
    print("   从优质音频中挑选最满意的声模")
    print()
    print("3. DSP 增强（可选）:")
    print("   - 变调 (pitch shift)")
    print("   - 共振峰调整 (formant shift)")
    print("   - 均衡器 (EQ)")
    print("   - 速度调整 (rate)")
    print()
    print("4. 训练 RVC 模型（可选）:")
    print("   使用筛选出的优质音频训练 RVC 声模")
    print()
    print("5. 建立声纹数据库:")
    print("   记录每个声模的特征和适用场景")
    print()
    print("=" * 70)
    print("🎉 声模工厂流水线完成！")
    print("=" * 70)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Fish Speech 声模工厂 - 一键工作流",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_factory.py              # 运行完整流水线
  python run_factory.py --generate   # 仅运行生成阶段
  python run_factory.py --filter     # 仅运行筛选阶段
  python run_factory.py --summary    # 仅查看总结
        """
    )
    
    parser.add_argument(
        "--generate",
        action="store_true",
        help="仅运行批量生成阶段"
    )
    
    parser.add_argument(
        "--filter",
        action="store_true",
        help="仅运行质量筛选阶段"
    )
    
    parser.add_argument(
        "--summary",
        action="store_true",
        help="仅查看项目总结"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # 环境检查
    if not check_environment():
        print("❌ 环境检查失败，请修复上述问题后重试")
        sys.exit(1)
    
    # 运行指定阶段
    if args.generate:
        run_generation()
    elif args.filter:
        run_filtering()
    elif args.summary:
        generate_summary()
    else:
        # 默认运行完整流水线
        run_generation()
        
        print("\n" + "=" * 70)
        input("⏸️ 生成完成，按 Enter 继续质量筛选...")
        print()
        
        run_filtering()
        
        print("\n" + "=" * 70)
        input("⏸️ 筛选完成，按 Enter 查看总结...")
        print()
        
        generate_summary()


if __name__ == "__main__":
    main()
