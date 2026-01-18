#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试时间计算修复
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:4101"

print("="*80)
print("测试时间计算修复")
print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# 启动一个小批量任务
print("\n启动批量任务（2023年1月，94条）...")
try:
    start_local = time.time()
    response = requests.post(
        f"{BASE_URL}/api/qc/check/batch",
        json={"periodType": "month", "year": 2023, "month": 1},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['code'] == 200:
            result = data['data']
            batch_key = result.get('batchKey', '')
            
            print(f"✓ 任务已启动")
            print(f"  批次键: {batch_key}")
            print(f"  病案数: {result.get('caseCount', 0)}")
            print(f"  开始时间: {result.get('startTime', '')}")
            
            # 等待5秒后查询
            print(f"\n等待5秒后查询进度...")
            time.sleep(5)
            
            status_response = requests.get(
                f"{BASE_URL}/api/qc/batch/status/{batch_key}",
                timeout=10
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                if status_data['code'] == 200:
                    status_result = status_data['data']
                    elapsed = status_result.get('elapsedSeconds', 0)
                    local_elapsed = int(time.time() - start_local)
                    
                    print(f"\n查询结果:")
                    print(f"  服务器报告已执行时间: {elapsed}秒")
                    print(f"  本地计算已执行时间: {local_elapsed}秒")
                    print(f"  差异: {abs(elapsed - local_elapsed)}秒")
                    
                    if abs(elapsed - local_elapsed) <= 2:
                        print(f"  ✅ 时间计算正确！")
                    else:
                        print(f"  ❌ 时间计算不正确，差异过大")
                        print(f"  开始时间: {status_result.get('startTime', '')}")
                        print(f"  当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print(f"✗ API错误: {status_data.get('message', '')}")
            else:
                print(f"✗ HTTP错误: {status_response.status_code}")
        else:
            print(f"✗ API错误: {data.get('message', '')}")
    else:
        print(f"✗ HTTP错误: {response.status_code}")
        
except Exception as e:
    print(f"✗ 异常: {str(e)}")

print("\n" + "="*80)
