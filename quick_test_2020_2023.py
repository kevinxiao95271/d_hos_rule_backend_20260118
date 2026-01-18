#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试：2020年和2023年数据
"""

import pymysql
import requests
import time
from datetime import datetime

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

BASE_URL = "http://localhost:4101"

print("="*80)
print("快速测试 - 2020年和2023年数据")
print("="*80)

# 1. 数据统计
print("\n1. 数据统计")
print("-"*80)

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM d_mr WHERE YEAR(B15) = 2020")
count_2020 = cursor.fetchone()[0]
print(f"2020年病案数: {count_2020:,}")

cursor.execute("SELECT COUNT(*) FROM d_mr WHERE YEAR(B15) = 2023")
count_2023 = cursor.fetchone()[0]
print(f"2023年病案数: {count_2023:,}")

# 2. 获取样本病案
print("\n2. 获取样本病案")
print("-"*80)

cursor.execute("""
    SELECT A48, A49, B15
    FROM d_mr
    WHERE YEAR(B15) = 2020
    LIMIT 2
""")
cases_2020 = cursor.fetchall()
print(f"2020年样本: {len(cases_2020)} 个")

cursor.execute("""
    SELECT A48, A49, B15
    FROM d_mr
    WHERE YEAR(B15) = 2023
    LIMIT 2
""")
cases_2023 = cursor.fetchall()
print(f"2023年样本: {len(cases_2023)} 个")

conn.close()

# 3. 测试单个病案
print("\n3. 测试单个病案检查")
print("-"*80)

all_cases = list(cases_2020) + list(cases_2023)

for i, (a48, a49, b15) in enumerate(all_cases, 1):
    year = b15.year if hasattr(b15, 'year') else 'Unknown'
    print(f"\n病案 {i}: A48={a48}, A49={a49}, 年份={year}")
    
    try:
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/qc/check",
            json={"a48": a48, "a49": a49},
            timeout=30
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                result = data['data']
                print(f"  ✓ 耗时: {elapsed:.2f}秒")
                print(f"  缺陷数: {result.get('defectCount', 0)}")
                print(f"  扣分: {result.get('totalDeduct', 0)}")
                print(f"  得分: {result.get('finalScore', 100)}")
            else:
                print(f"  ✗ API错误: {data.get('message', 'Unknown')}")
        else:
            print(f"  ✗ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"  ✗ 异常: {str(e)}")

# 4. 测试按月批量（小数据量）
print("\n4. 测试按月批量检查")
print("-"*80)

# 获取2020年1月的数据量
conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM d_mr WHERE YEAR(B15) = 2020 AND MONTH(B15) = 1")
jan_2020_count = cursor.fetchone()[0]
conn.close()

print(f"\n2020年1月病案数: {jan_2020_count:,}")

if jan_2020_count > 0:
    print("启动批量检查...")
    try:
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/qc/batch/month",
            json={"year": 2020, "month": 1},
            timeout=60
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                result = data['data']
                batch_key = result.get('batchKey', '')
                print(f"  ✓ 任务已启动")
                print(f"  批次键: {batch_key}")
                print(f"  启动耗时: {elapsed:.2f}秒")
                print(f"  预期处理: {result.get('caseCount', 0):,} 病案")
                
                # 等待一小段时间后检查状态
                print("\n  等待5秒后检查状态...")
                time.sleep(5)
                
                status_response = requests.get(
                    f"{BASE_URL}/api/qc/batch/status/{batch_key}",
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data['code'] == 200:
                        status_result = status_data['data']
                        print(f"  状态: {status_result.get('status', 'unknown')}")
                        print(f"  进度: {status_result.get('progress', 0)}%")
                        
                        if status_result.get('status') == 'completed':
                            print(f"  ✓ 已完成")
                            print(f"  病案数: {status_result.get('caseCount', 0):,}")
                            print(f"  总缺陷: {status_result.get('totalDefectCount', 0):,}")
                            print(f"  平均缺陷: {status_result.get('avgDefect', 0):.2f}")
                            print(f"  平均得分: {status_result.get('avgScore', 100):.2f}")
            else:
                print(f"  ✗ API错误: {data.get('message', 'Unknown')}")
        else:
            print(f"  ✗ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"  ✗ 异常: {str(e)}")

print("\n" + "="*80)
print("测试完成")
print("="*80)
