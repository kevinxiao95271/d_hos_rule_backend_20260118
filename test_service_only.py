#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

BASE_URL = "http://localhost:4101/api"

def test_service_status():
    """测试服务状态"""
    print("测试服务状态...")
    try:
        response = requests.get(f"{BASE_URL}/qc/status", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"服务状态测试失败: {e}")
        return False

def test_with_known_case():
    """使用已知的病案测试"""
    print("\n测试已知病案...")
    
    # 根据之前的测试报告，我们知道2023年1月有96个病案
    # 让我们尝试一些可能的病案key格式
    test_cases = [
        "2023001_001",
        "202301_001", 
        "1_001",
        "test_case"
    ]
    
    for mr_key in test_cases:
        print(f"测试病案: {mr_key}")
        try:
            response = requests.post(f"{BASE_URL}/qc/check/single", 
                                   json={"mrKey": mr_key},
                                   timeout=10)
            
            print(f"  状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"  响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return True
            else:
                print(f"  错误响应: {response.text}")
        
        except Exception as e:
            print(f"  测试失败: {e}")
    
    return False

def test_batch_api():
    """测试批量API"""
    print("\n测试批量API...")
    try:
        # 测试启动批量任务
        batch_request = {
            "periodType": "month",
            "year": 2023,
            "month": 1
        }
        
        response = requests.post(f"{BASE_URL}/qc/batch/start", 
                               json=batch_request,
                               timeout=10)
        
        print(f"批量任务启动 - 状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            batch_key = result.get('data', {}).get('batchKey')
            
            if batch_key:
                print(f"批量任务已启动: {batch_key}")
                
                # 等待一会儿检查进度
                time.sleep(2)
                
                progress_response = requests.get(f"{BASE_URL}/qc/batch/progress/{batch_key}", timeout=5)
                print(f"进度查询 - 状态码: {progress_response.status_code}")
                print(f"进度响应: {progress_response.text}")
                
                return True
        
        return False
        
    except Exception as e:
        print(f"批量API测试失败: {e}")
        return False

def main():
    print("Java服务功能测试")
    print("=" * 30)
    
    # 1. 测试服务状态
    if not test_service_status():
        print("❌ 服务状态测试失败")
        return
    
    print("✅ 服务状态正常")
    
    # 2. 测试单个病案质控
    if test_with_known_case():
        print("✅ 单个病案质控测试成功")
    else:
        print("⚠️ 单个病案质控测试失败（可能是病案不存在）")
    
    # 3. 测试批量API
    if test_batch_api():
        print("✅ 批量API测试成功")
    else:
        print("⚠️ 批量API测试失败")
    
    print("\n📋 测试总结:")
    print("- Java服务正在运行")
    print("- API接口可以访问")
    print("- 建议使用实际存在的病案数据进行完整测试")

if __name__ == "__main__":
    main()