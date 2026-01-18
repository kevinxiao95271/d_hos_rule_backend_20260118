#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的批量质控性能
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:4101"

def format_time(seconds):
    """格式化时间"""
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        return f"{seconds//60}分{seconds%60}秒"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}小时{minutes}分"

print("="*80)
print("优化后的批量质控性能测试")
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# 测试1: 2023年1月（94条病案）
print("\n测试1: 2023年1月（94条病案）")
print("-"*80)

try:
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/qc/check/batch",
        json={"periodType": "month", "year": 2023, "month": 1},
        timeout=10
    )
    launch_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        if data['code'] == 200:
            result = data['data']
            batch_key = result.get('batchKey', '')
            case_count = result.get('caseCount', 0)
            
            print(f"✓ 批量任务已启动（异步执行）")
            print(f"  批次键: {batch_key}")
            print(f"  病案总数: {case_count}")
            print(f"  启动耗时: {launch_time:.2f}秒")
            print(f"  状态: {result.get('status', '')}")
            
            # 轮询查询进度
            print(f"\n轮询查询进度...")
            max_polls = 60
            poll_interval = 2
            
            for i in range(max_polls):
                time.sleep(poll_interval)
                
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
                            completed = status_result.get('caseCount', 0)
                            elapsed = status_result.get('elapsedSeconds', 0)
                            
                            print(f"  [{i+1}] 进度: {progress}%, 已完成: {completed}/{case_count}, 耗时: {format_time(elapsed)}", end='\r')
                            
                            if status == 'completed':
                                print(f"\n\n✓ 任务完成！")
                                print(f"  总耗时: {format_time(elapsed)}")
                                print(f"  病案数: {completed}")
                                print(f"  总缺陷数: {status_result.get('totalDefectCount', 0)}")
                                print(f"  平均缺陷: {status_result.get('avgDefect', 0):.2f}")
                                print(f"  平均得分: {status_result.get('avgScore', 0):.2f}")
                                
                                if elapsed > 0:
                                    speed = completed / elapsed
                                    print(f"  处理速度: {speed:.2f} 病案/秒")
                                    print(f"  预计1万条耗时: {format_time(int(10000 / speed))}")
                                
                                break
                            elif status == 'failed':
                                print(f"\n\n✗ 任务失败")
                                break
                        
                except Exception as e:
                    print(f"\n  ✗ 查询异常: {str(e)}")
                    break
            else:
                print(f"\n\n⚠ 达到最大查询次数")
                
        else:
            print(f"✗ API错误: {data.get('message', 'Unknown')}")
    else:
        print(f"✗ HTTP错误: {response.status_code}")
        
except Exception as e:
    print(f"✗ 异常: {str(e)}")

# 等待一下再测试下一个
time.sleep(5)

# 测试2: 2020年1月（6,095条病案）
print("\n" + "="*80)
print("测试2: 2020年1月（6,095条病案）")
print("-"*80)

try:
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/qc/check/batch",
        json={"periodType": "month", "year": 2020, "month": 1},
        timeout=10
    )
    launch_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        if data['code'] == 200:
            result = data['data']
            batch_key = result.get('batchKey', '')
            case_count = result.get('caseCount', 0)
            
            print(f"✓ 批量任务已启动（异步执行）")
            print(f"  批次键: {batch_key}")
            print(f"  病案总数: {case_count}")
            print(f"  启动耗时: {launch_time:.2f}秒")
            print(f"  状态: {result.get('status', '')}")
            
            # 轮询查询进度
            print(f"\n轮询查询进度（这可能需要几分钟）...")
            max_polls = 300  # 最多10分钟
            poll_interval = 2
            
            for i in range(max_polls):
                time.sleep(poll_interval)
                
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
                            completed = status_result.get('caseCount', 0)
                            elapsed = status_result.get('elapsedSeconds', 0)
                            
                            # 每10次查询显示一次
                            if i % 5 == 0 or status == 'completed':
                                print(f"  [{i+1}] 进度: {progress}%, 已完成: {completed}/{case_count}, 耗时: {format_time(elapsed)}")
                            
                            if status == 'completed':
                                print(f"\n✓ 任务完成！")
                                print(f"  总耗时: {format_time(elapsed)}")
                                print(f"  病案数: {completed}")
                                print(f"  总缺陷数: {status_result.get('totalDefectCount', 0)}")
                                print(f"  平均缺陷: {status_result.get('avgDefect', 0):.2f}")
                                print(f"  平均得分: {status_result.get('avgScore', 0):.2f}")
                                
                                if elapsed > 0:
                                    speed = completed / elapsed
                                    print(f"  处理速度: {speed:.2f} 病案/秒")
                                    
                                    # 性能评估
                                    if elapsed < 600:  # 10分钟
                                        print(f"  ✅ 性能优秀！在10分钟内完成")
                                    elif elapsed < 1800:  # 30分钟
                                        print(f"  ✓ 性能良好")
                                    else:
                                        print(f"  ⚠ 性能需要进一步优化")
                                
                                break
                            elif status == 'failed':
                                print(f"\n✗ 任务失败")
                                break
                        
                except Exception as e:
                    print(f"\n  ✗ 查询异常: {str(e)}")
                    break
            else:
                print(f"\n⚠ 达到最大查询次数（{max_polls * poll_interval}秒）")
                
        else:
            print(f"✗ API错误: {data.get('message', 'Unknown')}")
    else:
        print(f"✗ HTTP错误: {response.status_code}")
        
except Exception as e:
    print(f"✗ 异常: {str(e)}")

print("\n" + "="*80)
print("性能测试完成！")
print("="*80)

print("\n优化说明:")
print("  1. ✅ 异步执行 - 任务立即返回，后台执行")
print("  2. ✅ 规则缓存 - 避免重复查询数据库")
print("  3. ✅ 批量操作 - 每100条批量保存数据库")
print("  4. ✅ 进度更新 - 每100条更新一次进度")
print("  5. ✅ 自动清理 - 任务完成后清理缓存")
