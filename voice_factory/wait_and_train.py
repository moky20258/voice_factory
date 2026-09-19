#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""等待API就绪并开始训练"""
import requests
import time
import sys

def wait_for_api(timeout=120):
    """等待API就绪"""
    print("[WAIT] 等待 Fish Speech API 启动...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get("http://127.0.0.1:8080/", timeout=5)
            if response.status_code == 200:
                print("[OK] Fish Speech API 已就绪!")
                return True
        except:
            pass
        
        elapsed = int(time.time() - start_time)
        if elapsed % 10 == 0:
            print(f"   已等待 {elapsed} 秒...")
        time.sleep(2)
    
    print(f"[ERROR] 等待超时 ({timeout}秒)")
    return False

if __name__ == "__main__":
    if wait_for_api(120):
        print()
        print("[OK] API 检查通过，准备开始训练...")
        print()
        
        # 导入并运行批量训练（自动确认模式）
        sys.path.insert(0, "w:\\fish-speech-1.5.1\\voice_factory")
        from batch_train_5_speakers import main as train_main
        train_main(auto_confirm=True)
    else:
        print()
        print("[ERROR] API 未能启动，请检查:")
        print("   1. Python 3.12 是否正确安装")
        print("   2. 依赖是否完整 (pip install -e .)")
        print("   3. 模型文件是否存在")
        sys.exit(1)
