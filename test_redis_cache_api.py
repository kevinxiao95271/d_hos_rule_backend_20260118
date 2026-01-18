#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

BASE_URL = "http://localhost:4101/api"

def test_redis_cache():
    """测试Redis缓存API"""
    print("=== 测试Redis缓存API ===")
    
    try:
        # 1. 测试缓存统计
        print("1. 测试缓存统计...")
        response = requests.get(f"{BASE_URL}/dict/cache/stats", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 缓存统计成功")
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            data = result.get('data', {})
            dict_count = data.get('dictCacheCount', 0)
            set_count = data.get('setCacheCount', 0)
            
            print(f"字典缓存数量: {dict_count}")
            print(f"Set缓存数量: {set_count}")
            
            if dict_count > 0:
                print("✅ Redis缓存正常工作")
                return True
            else:
                print("⚠️  缓存为空，尝试重新加载...")
                return reload_cache()
        else:
            print(f"❌ 缓存统计失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 缓存统计异常: {e}")
        return False

def reload_cache():
    """重新加载缓存"""
    print("\n2. 重新加载缓存...")
    
    try:
        response = requests.post(f"{BASE_URL}/dict/cache/reload", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 缓存重新加载成功")
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 再次检查缓存统计
            print("\n3. 检查重新加载后的缓存...")
            response = requests.get(f"{BASE_URL}/dict/cache/stats", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                data = result.get('data', {})
                dict_count = data.get('dictCacheCount', 0)
                set_count = data.get('setCacheCount', 0)
                
                print(f"字典缓存数量: {dict_count}")
                print(f"Set缓存数量: {set_count}")
                
                if dict_count > 0:
                    print("✅ 缓存重新加载成功")
                    return True
                else:
                    print("❌ 缓存重新加载后仍为空")
                    return False
            else:
                print(f"❌ 重新检查缓存失败: {response.status_code}")
                return False
        else:
            print(f"❌ 缓存重新加载失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 缓存重新加载异常: {e}")
        return False

def test_dict_validation():
    """测试字典验证"""
    print("\n=== 测试字典验证 ===")
    
    # 测试一些已知的字典值
    test_cases = [
        ("RCJBBM", "A00.000"),  # 疾病编码
        ("operation_dict_v3", "00.01"),  # 手术编码
        ("RC001", "1"),  # 性别
        ("RC002", "汉族"),  # 民族
    ]
    
    for dict_type, test_value in test_cases:
        try:
            response = requests.post(f"{BASE_URL}/dict/validate", 
                                   json={
                                       'dictTypeCode': dict_type,
                                       'value': test_value
                                   }, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                is_valid = result.get('data', False)
                print(f"字典验证 {dict_type}:{test_value} = {is_valid}")
            else:
                print(f"字典验证失败 {dict_type}:{test_value} - {response.status_code}")
                print(f"响应: {response.text}")
                
        except Exception as e:
            print(f"字典验证异常 {dict_type}:{test_value} - {e}")

if __name__ == "__main__":
    print("Redis缓存API测试")
    print("=" * 40)
    
    # 测试Redis缓存
    cache_ok = test_redis_cache()
    
    if cache_ok:
        # 测试字典验证
        test_dict_validation()
        print("\n✅ Redis缓存系统正常工作")
    else:
        print("\n❌ Redis缓存系统存在问题")