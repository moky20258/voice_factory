"""生成训练清单"""
import os

logs_dir = r"W:\rvc\logs"
speakers = sorted([d for d in os.listdir(logs_dir) 
                   if os.path.isdir(os.path.join(logs_dir, d)) and d.startswith('speaker_')])

print("\nSpeaker 训练清单\n")
print("=" * 70)

for i, spk in enumerate(speakers, 1):
    audio_count = len([f for f in os.listdir(os.path.join(logs_dir, spk)) if f.endswith(".wav")])
    status = "待训练"
    print(f"  {i:2d}. {spk}  ({audio_count:4d} 个音频)  [{status}]")

print("=" * 70)
print(f"\n总计: {len(speakers)} 个 Speaker")
print(f"预计训练时间 (GPU): {len(speakers) * 0.75:.1f} - {len(speakers) * 1.5:.1f} 小时")
print(f"预计训练时间 (CPU): {len(speakers) * 3:.1f} - {len(speakers) * 4:.1f} 小时")
print()
