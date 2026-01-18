#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试批量任务进度查询接口
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
print("批量任务进度查询测试")
print("="*80)

# 步骤1: 启动一个批量任务
print("\n步骤1: 启动批量任务（2023年1月，94条病案）")
print("-"*80)

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
            batch_key = result.get('batchKey', '')
            case_count = result.get('caseCount', 0)
            
            print(f"✓ 批量任务已启动")
            print(f"  批次键: {batch_key}")
            print(f"  病案总数: {case_count}")
            print(f"  初始进度: {result.get('progress', 0)}%")
            
            # 步骤2: 轮询查询进度
            print(f"\n步骤2: 轮询查询任务进度")
            print("-"*80)
            
            max_polls = 30  # 最多查询30次
            poll_interval = 2  # 每2秒查询一次
            
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
                            
                            # 提取关键信息
                            status = status_result.get('status', '')
                            progress = status_result.get('progress', 0)
                            case_count = status_result.get('caseCount', 0)
                            total_defects = status_result.get('totalDefectCount', 0)
                            avg_score = status_result.get('avgScore', 0)
                            elapsed_seconds = status_result.get('elapsedSeconds', 0)
                            
                            # 显示进度
                            print(f"\n查询 #{i+1}:")
                            print(f"  状态: {status}")
                            print(f"  进度: {progress}%")
                            print(f"  已完成: {case_count} 条")
                            print(f"  总缺陷: {total_defects}")
                            print(f"  平均得分: {avg_score}")
                            print(f"  已执行时间: {format_time(elapsed_seconds)}")
                            
                            if status == 'completed':
                                print(f"\n✓ 任务完成！")
                                print(f"  最终统计:")
                                print(f"    病案数: {case_count}")
                                print(f"    总缺陷数: {total_defects}")
                                print(f"    平均缺陷: {status_result.get('avgDefect', 0):.2f}")
                                print(f"    平均得分: {avg_score:.2f}")
                                print(f"    总耗时: {format_time(elapsed_seconds)}")
                                
                                # 计算处理速度
                                if elapsed_seconds > 0:
                                    speed = case_count / elapsed_seconds
                                    print(f"    处理速度: {speed:.2f} 病案/秒")
                                
                                break
                            elif status == 'failed':
                                print(f"\n✗ 任务失败")
                                break
                        else:
                            print(f"  ✗ API错误: {status_data.get('message', 'Unknown')}")
                            break
                    else:
                        print(f"  ✗ HTTP错误: {status_response.status_code}")
                        break
                        
                except Exception as e:
                    print(f"  ✗ 查询异常: {str(e)}")
                    break
            else:
                print(f"\n⚠ 达到最大查询次数（{max_polls}次）")
                
        else:
            print(f"✗ API错误: {data.get('message', 'Unknown')}")
    else:
        print(f"✗ HTTP错误: {response.status_code}")
        
except Exception as e:
    print(f"✗ 异常: {str(e)}")

print("\n" + "="*80)
print("测试完成！")
print("="*80)

# 显示API使用说明
print("\n" + "="*80)
print("API使用说明")
print("="*80)
print("""
1. 启动批量任务:
   POST /api/qc/check/batch
   Body: {"periodType": "month", "year": 2023, "month": 1}
   返回: {
     "batchKey": "2023_M1",
     "caseCount": 94,
     "progress": 0,
     "status": "processing",
     ...
   }

2. 查询任务进度:
   GET /api/qc/batch/status/{batchKey}
   例如: GET /api/qc/batch/status/2023_M1
   返回: {
     "batchKey": "2023_M1",
     "caseCount": 50,           # 已完成数
     "progress": 53,            # 进度百分比
     "status": "processing",    # 状态: processing/completed/failed
     "totalDefectCount": 150,   # 总缺陷数
     "avgScore": 88.5,          # 平均得分
     "elapsedSeconds": 45,      # 已执行时间（秒）
     "startTime": "2023-01-16T16:00:00",
     "endTime": null,           # 未完成时为null
     ...
   }

3. 批次键格式:
   - 按年: "2023"
   - 按季度: "2023_Q1"
   - 按月: "2023_M1"
""")
