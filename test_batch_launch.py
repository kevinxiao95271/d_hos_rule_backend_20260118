#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试批量任务启动 - 只检查启动时返回的病案数
"""

import requests

BASE_URL = "http://localhost:4101"

print("="*80)
print("测试批量任务启动")
print("="*80)

# 测试1: 2023年1月 (应该是94条)
print("\n测试1: 2023年1月")
try:
    response = requests.post(
        f"{BASE_URL}/api/qc/check/batch",
        json={"periodType": "month", "year": 2023, "month": 1},
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['code'] == 200:
            result = data['data']
            case_count = result.get('caseCount', 0)
            batch_key = result.get('batchKey', '')
            
            print(f"  批次键: {batch_key}")
            print(f"  病案数: {case_count}")
            
            if case_count == 94:
                print(f"  ✅ 正确！")
            else:
                print(f"  ❌ 错误！应该是94条")
        else:
            print(f"  ✗ API错误: {data.get('message', 'Unknown')}")
    else:
        print(f"  ✗ HTTP错误: {response.status_code}")
except Exception as e:
    print(f"  ✗ 异常: {str(e)}")

# 测试2: 2020年1月 (应该是6095条)
print("\n测试2: 2020年1月")
try:
    response = requests.post(
        f"{BASE_URL}/api/qc/check/batch",
        json={"periodType": "month", "year": 2020, "month": 1},
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['code'] == 200:
            result = data['data']
            case_count = result.get('caseCount', 0)
            batch_key = result.get('batchKey', '')
            
            print(f"  批次键: {batch_key}")
            print(f"  病案数: {case_count}")
            
            if case_count == 6095:
                print(f"  ✅ 正确！")
            else:
                print(f"  ❌ 错误！应该是6095条")
        else:
            print(f"  ✗ API错误: {data.get('message', 'Unknown')}")
    else:
        print(f"  ✗ HTTP错误: {response.status_code}")
except Exception as e:
    print(f"  ✗ 异常: {str(e)}")

# 测试3: 2023年全年 (应该是96条)
print("\n测试3: 2023年全年")
try:
    response = requests.post(
        f"{BASE_URL}/api/qc/check/batch",
        json={"periodType": "year", "year": 2023},
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['code'] == 200:
            result = data['data']
            case_count = result.get('caseCount', 0)
            batch_key = result.get('batchKey', '')
            
            print(f"  批次键: {batch_key}")
            print(f"  病案数: {case_count}")
            
            if case_count == 96:
                print(f"  ✅ 正确！")
            else:
                print(f"  ❌ 错误！应该是96条")
        else:
            print(f"  ✗ API错误: {data.get('message', 'Unknown')}")
    else:
        print(f"  ✗ HTTP错误: {response.status_code}")
except Exception as e:
    print(f"  ✗ 异常: {str(e)}")

print("\n" + "="*80)
print("测试完成！")
print("="*80)
