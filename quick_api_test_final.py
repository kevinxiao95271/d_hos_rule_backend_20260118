#!/usr/bin/env python3
import requests
import json

def test_api(name, url):
    """测试API端点"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name}: 正常 (返回 {len(data.get('data', []))} 条记录)")
            return True
        else:
            print(f"⚠️ {name}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: {e}")
        return False

def main():
    print("🚀 医疗质控系统 - 快速API测试")
    print("=" * 50)
    
    base_url = "http://localhost:4101"
    
    # 测试主要API
    tests = [
        ("服务状态", f"{base_url}/api/qc/status"),
        ("规则列表", f"{base_url}/api/qc/rules"),
        ("字典类型", f"{base_url}/api/dict/types"),
        ("民族字典", f"{base_url}/api/dict/type/ethnicity"),
    ]
    
    success_count = 0
    for name, url in tests:
        if test_api(name, url):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 测试完成: {success_count}/{len(tests)} 个API正常")
    
    if success_count == len(tests):
        print("✅ 系统已就绪，可以开始使用!")
    else:
        print("⚠️ 部分API异常，请检查日志")

if __name__ == "__main__":
    main()