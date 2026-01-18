#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质控性能测试
测试2020年1月和2023年1月的数据
"""

import pymysql
import requests
import time
import json
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

def format_time(seconds):
    """格式化时间"""
    if seconds < 60:
        return f"{seconds:.2f}秒"
    elif seconds < 3600:
        return f"{seconds/60:.2f}分钟"
    else:
        return f"{seconds/3600:.2f}小时"

print("="*100)
print("  质控系统性能测试")
print(f"  测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*100)

# ========================================
# 测试1：单个病案检查
# ========================================
print("\n" + "="*100)
print("测试1：单个病案检查（测试响应时间）")
print("="*100)

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

# 获取样本
cursor.execute("""
    SELECT A48, A49, YEAR(B15) as year
    FROM d_mr
    WHERE YEAR(B15) IN (2020, 2023)
    ORDER BY B15
    LIMIT 5
""")
samples = cursor.fetchall()
conn.close()

single_test_results = []

for i, (a48, a49, year) in enumerate(samples, 1):
    print(f"\n病案 {i}/5: A48={a48}, A49={a49}, 年份={year}")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/qc/check/single",
            params={"a48": str(a48), "a49": str(a49)},
            timeout=30
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                result = data['data']
                defect_count = result.get('defectCount', 0)
                total_deduct = result.get('totalDeduct', 0)
                final_score = result.get('finalScore', 100)
                
                print(f"  ✓ 检查完成")
                print(f"    耗时: {elapsed:.3f}秒")
                print(f"    缺陷数: {defect_count}")
                print(f"    扣分: {total_deduct}")
                print(f"    得分: {final_score}")
                
                single_test_results.append({
                    'elapsed': elapsed,
                    'defect_count': defect_count,
                    'total_deduct': total_deduct,
                    'final_score': final_score
                })
            else:
                print(f"  ✗ API返回错误: {data.get('message', 'Unknown')}")
        else:
            print(f"  ✗ HTTP错误: {response.status_code}")
            print(f"    响应: {response.text[:200]}")
    except requests.exceptions.Timeout:
        print(f"  ✗ 请求超时（>30秒）")
    except Exception as e:
        print(f"  ✗ 异常: {str(e)}")

# 单个病案统计
if single_test_results:
    avg_time = sum(r['elapsed'] for r in single_test_results) / len(single_test_results)
    min_time = min(r['elapsed'] for r in single_test_results)
    max_time = max(r['elapsed'] for r in single_test_results)
    avg_defects = sum(r['defect_count'] for r in single_test_results) / len(single_test_results)
    avg_score = sum(r['final_score'] for r in single_test_results) / len(single_test_results)
    
    print("\n单个病案检查统计:")
    print(f"  成功数: {len(single_test_results)}/5")
    print(f"  平均耗时: {avg_time:.3f}秒")
    print(f"  最快: {min_time:.3f}秒")
    print(f"  最慢: {max_time:.3f}秒")
    print(f"  平均缺陷数: {avg_defects:.1f}")
    print(f"  平均得分: {avg_score:.2f}")

# ========================================
# 测试2：按月批量检查 - 2023年1月（96条）
# ========================================
print("\n" + "="*100)
print("测试2：按月批量检查 - 2023年1月（96条病案）")
print("="*100)

print("\n启动批量检查...")
try:
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/qc/check/batch",
        json={"periodType": "month", "year": 2023, "month": 1},
        timeout=60
    )
    launch_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        if data['code'] == 200:
            result = data['data']
            batch_key = result.get('batchKey', '')
            case_count = result.get('caseCount', 0)
            
            print(f"✓ 批量任务已启动")
            print(f"  批次键: {batch_key}")
            print(f"  启动耗时: {launch_time:.2f}秒")
            print(f"  病案数: {case_count}")
            
            # 轮询检查状态
            print(f"\n等待任务完成...")
            check_start = time.time()
            max_wait = 300  # 最多等待5分钟
            check_interval = 2  # 每2秒检查一次
            
            while time.time() - check_start < max_wait:
                try:
                    status_response = requests.get(
                        f"{BASE_URL}/api/qc/batch/status/{batch_key}",
                        timeout=10
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data['code'] == 200:
                            status_result = status_data['data']
                            status = status_result.get('status', '')
                            progress = status_result.get('progress', 0)
                            
                            print(f"  进度: {progress}% - 状态: {status}", end='\r')
                            
                            if status == 'completed':
                                total_time = time.time() - start_time
                                print(f"\n\n✓ 批量检查完成")
                                print(f"  总耗时: {format_time(total_time)}")
                                print(f"  病案数: {status_result.get('caseCount', 0)}")
                                print(f"  总缺陷数: {status_result.get('totalDefectCount', 0)}")
                                print(f"  平均缺陷: {status_result.get('avgDefect', 0):.2f}")
                                print(f"  平均得分: {status_result.get('avgScore', 100):.2f}")
                                
                                if status_result.get('caseCount', 0) > 0:
                                    speed = status_result.get('caseCount', 0) / total_time
                                    print(f"  处理速度: {speed:.2f} 病案/秒")
                                
                                break
                            elif status == 'failed':
                                print(f"\n\n✗ 批量检查失败")
                                break
                        
                        time.sleep(check_interval)
                    else:
                        print(f"\n✗ 状态查询HTTP错误: {status_response.status_code}")
                        break
                        
                except Exception as e:
                    print(f"\n✗ 状态查询异常: {str(e)}")
                    break
            else:
                print(f"\n✗ 等待超时（>{max_wait}秒）")
        else:
            print(f"✗ API返回错误: {data.get('message', 'Unknown')}")
    else:
        print(f"✗ HTTP错误: {response.status_code}")
        print(f"  响应: {response.text[:200]}")
except Exception as e:
    print(f"✗ 异常: {str(e)}")

# ========================================
# 测试3：按月批量检查 - 2020年1月（6,095条）
# ========================================
print("\n" + "="*100)
print("测试3：按月批量检查 - 2020年1月（6,095条病案）")
print("="*100)

print("\n启动批量检查...")
try:
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/qc/check/batch",
        json={"periodType": "month", "year": 2020, "month": 1},
        timeout=60
    )
    launch_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        if data['code'] == 200:
            result = data['data']
            batch_key = result.get('batchKey', '')
            case_count = result.get('caseCount', 0)
            
            print(f"✓ 批量任务已启动")
            print(f"  批次键: {batch_key}")
            print(f"  启动耗时: {launch_time:.2f}秒")
            print(f"  病案数: {case_count}")
            
            # 轮询检查状态
            print(f"\n等待任务完成（这可能需要几分钟）...")
            check_start = time.time()
            max_wait = 600  # 最多等待10分钟
            check_interval = 3  # 每3秒检查一次
            
            while time.time() - check_start < max_wait:
                try:
                    status_response = requests.get(
                        f"{BASE_URL}/api/qc/batch/status/{batch_key}",
                        timeout=10
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data['code'] == 200:
                            status_result = status_data['data']
                            status = status_result.get('status', '')
                            progress = status_result.get('progress', 0)
                            
                            elapsed = time.time() - start_time
                            print(f"  进度: {progress}% - 状态: {status} - 已用时: {format_time(elapsed)}", end='\r')
                            
                            if status == 'completed':
                                total_time = time.time() - start_time
                                print(f"\n\n✓ 批量检查完成")
                                print(f"  总耗时: {format_time(total_time)}")
                                print(f"  病案数: {status_result.get('caseCount', 0)}")
                                print(f"  总缺陷数: {status_result.get('totalDefectCount', 0)}")
                                print(f"  平均缺陷: {status_result.get('avgDefect', 0):.2f}")
                                print(f"  平均得分: {status_result.get('avgScore', 100):.2f}")
                                
                                if status_result.get('caseCount', 0) > 0:
                                    speed = status_result.get('caseCount', 0) / total_time
                                    print(f"  处理速度: {speed:.2f} 病案/秒")
                                    
                                    # 估算全年处理时间
                                    if speed > 0:
                                        est_full_year = 6095 * 12 / speed / 60  # 分钟
                                        print(f"  估算全年处理时间: {est_full_year:.1f}分钟")
                                
                                break
                            elif status == 'failed':
                                print(f"\n\n✗ 批量检查失败")
                                break
                        
                        time.sleep(check_interval)
                    else:
                        print(f"\n✗ 状态查询HTTP错误: {status_response.status_code}")
                        break
                        
                except Exception as e:
                    print(f"\n✗ 状态查询异常: {str(e)}")
                    break
            else:
                print(f"\n✗ 等待超时（>{max_wait}秒）")
        else:
            print(f"✗ API返回错误: {data.get('message', 'Unknown')}")
    else:
        print(f"✗ HTTP错误: {response.status_code}")
        print(f"  响应: {response.text[:200]}")
except Exception as e:
    print(f"✗ 异常: {str(e)}")

print("\n" + "="*100)
print("测试完成！")
print("="*100)
