#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试count API
"""

import requests

BASE_URL = "http://localhost:4101"

print("="*80)
print("测试病案数量统计API")
print("="*80)

# 测试1: 2023年1月
print("\n测试1: 2023年1月")
try:
    response = requests.get(
        f"{BASE_URL}/api/qc/records/count",
        params={"year": 2023, "month": 1},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['code'] == 200:
            count = data['data']
            print(f"  结果: {count} 条")
            if count == 94:
                print(f"  ✅ 正确！")
            else:
                print(f"  ❌ 错误！应该是94条")
        else:
            print(f"  ✗ API错误: {data.get('message', 'Unknown')}")
    else:
        print(f"  ✗ HTTP错误: {response.status_code}")
        print(f"    响应: {response.text[:200]}")
except Exception as e:
    print(f"  ✗ 异常: {str(e)}")

# 测试2: 2020年1月
print("\n测试2: 2020年1月")
try:
    response = requests.get(
        f"{BASE_URL}/api/qc/records/count",
        params={"year": 2020, "month": 1},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['code'] == 200:
            count = data['data']
            print(f"  结果: {count} 条")
            if count == 6095:
                print(f"  ✅ 正确！")
            else:
                print(f"  ❌ 错误！应该是6095条")
        else:
            print(f"  ✗ API错误: {data.get('message', 'Unknown')}")
    else:
        print(f"  ✗ HTTP错误: {response.status_code}")
        print(f"    响应: {response.text[:200]}")
except Exception as e:
    print(f"  ✗ 异常: {str(e)}")

# 测试3: 2023年全年
print("\n测试3: 2023年全年")
try:
    response = requests.get(
        f"{BASE_URL}/api/qc/records/count",
        params={"year": 2023},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['code'] == 200:
            count = data['data']
            print(f"  结果: {count} 条")
            if count == 96:
                print(f"  ✅ 正确！")
            else:
                print(f"  ❌ 错误！应该是96条")
        else:
            print(f"  ✗ API错误: {data.get('message', 'Unknown')}")
    else:
        print(f"  ✗ HTTP错误: {response.status_code}")
        print(f"    响应: {response.text[:200]}")
except Exception as e:
    print(f"  ✗ 异常: {str(e)}")

print("\n" + "="*80)
