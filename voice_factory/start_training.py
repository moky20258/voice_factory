#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""启动5个声模的训练流程"""
import requests
import sys

def check_api():
    """检查API状态"""
    try:
        response = requests.get("http://127.0.0.1:8080/", timeout=5)
        if response.status_code == 200:
            print("✅ Fish Speech API 服务正常")
            return True
        else:
            print(f"⚠️ API 返回状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到 Fish Speech API: {e}")
        print("\n💡 请先启动 Fish Speech API 服务器:")
        print("   cd w:\\fish-speech-1.5.1")
        print("   python tools/api_server.py")
        return False

if __name__ == "__main__":
    if not check_api():
        sys.exit(1)
    
    print("\n✅ API 检查通过，准备开始训练...\n")
    
    # 导入并运行批量训练
    sys.path.insert(0, "w:\\fish-speech-1.5.1\\voice_factory")
    from batch_train_5_speakers import main as train_main
    train_main()
