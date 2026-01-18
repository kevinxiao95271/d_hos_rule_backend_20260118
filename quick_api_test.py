#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速API测试
"""

import requests

BASE_URL = "http://localhost:4101"

print("快速API测试")
print("="*80)

# 测试1: 规则搜索
print("\n1. 测试规则搜索:")
try:
    response = requests.get(f"{BASE_URL}/api/qc/rules/search", timeout=5)
    print(f"  状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ 成功，找到{len(data.get('data', []))}条规则")
except Exception as e:
    print(f"  ✗ 失败: {str(e)}")

# 测试2: 单病案质控
print("\n2. 测试单病案质控:")
try:
    response = requests.post(
        f"{BASE_URL}/api/qc/check/single",
        params={"a48": "19079841", "a49": "1"},
        timeout=10
    )
    print(f"  状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ 成功")
except Exception as e:
    print(f"  ✗ 失败: {str(e)}")

print("\n" + "="*80)
