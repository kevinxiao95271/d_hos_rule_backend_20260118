#!/usr/bin/env python3
import requests
import time

def check_service():
    """快速检查服务状态"""
    try:
        response = requests.get("http://localhost:4101/api/health", timeout=2)
        if response.status_code == 200:
            print("✅ 服务已启动!")
            return True
        else:
            print(f"⚠️ 服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 服务未启动 (连接被拒绝)")
        return False
    except requests.exceptions.Timeout:
        print("⏳ 服务响应超时")
        return False
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

if __name__ == "__main__":
    print("🔍 快速检查服务状态...")
    if check_service():
        print("\n🎯 可以开始测试API了!")
    else:
        print("\n⏳ 服务可能还在启动中，请稍等...")