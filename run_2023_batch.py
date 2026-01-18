#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import json

BASE_URL = "http://localhost:4101/api"

def run_2023_batch():
    """运行2023年批量质控"""
    print("=== 运行2023年批量质控 ===")
    
    batch_data = {
        "startDate": "2023-01-01",
        "endDate": "2023-12-31",
        "batchType": "year"
    }
    
    print("启动2023年批量质控...")
    start_time = time.time()
    
    try:
        response = requests.post(f"{BASE_URL}/qc/check/batch", 
                               json=batch_data,
                               timeout=600)  # 10分钟超时
        
        if response.status_code == 200:
            result = response.json()
            print(f"批量质控启动成功: {result.get('message', 'N/A')}")
            
            # 监控处理进度
            print("监控处理进度...")
            max_wait = 300  # 最多等待5分钟
            wait_time = 0
            
            while wait_time < max_wait:
                time.sleep(5)
                wait_time += 5
                
                # 检查状态
                status_response = requests.get(f"{BASE_URL}/qc/batch/status/2023")
                if status_response.status_code == 200:
                    status_data = status_response.json().get('data', {})
                    status = status_data.get('status', 'unknown')
                    progress = status_data.get('progress', 0)
                    
                    print(f"  进度: {progress}%, 状态: {status}")
                    
                    if status == 'completed':
                        end_time = time.time()
                        total_time = end_time - start_time
                        print(f"✅ 批量质控完成！总耗时: {total_time:.1f}秒 ({total_time/60:.1f}分钟)")
                        break
                    elif status == 'failed':
                        print("❌ 批量质控失败！")
                        return
                else:
                    print(f"  状态查询失败: {status_response.status_code}")
            
            if wait_time >= max_wait:
                print("⚠️  等待超时，但可能仍在处理中")
            
            # 获取最终结果
            print(f"\n获取批量质控结果...")
            summary_response = requests.post(f"{BASE_URL}/qc/result/batch/summary", json=batch_data)
            
            if summary_response.status_code == 200:
                summary = summary_response.json().get('data', {})
                print(f"2023年批量质控汇总:")
                print(f"  病案总数: {summary.get('caseCount', 0)}")
                print(f"  总缺陷数: {summary.get('totalDefectCount', 0)}")
                print(f"  平均缺陷: {summary.get('avgDefect', 0):.2f}")
                print(f"  平均得分: {summary.get('avgScore', 0):.2f}")
                
                # 获取详细结果
                cases_response = requests.post(f"{BASE_URL}/qc/result/batch/cases", json=batch_data)
                if cases_response.status_code == 200:
                    cases = cases_response.json().get('data', [])
                    print(f"  处理病案数: {len(cases)}")
                    
                    if cases:
                        # 显示前5个病案的结果
                        print(f"\n前5个病案结果:")
                        for i, case in enumerate(cases[:5], 1):
                            print(f"  {i}. {case.get('mrKey')}: {case.get('defectCount')}个缺陷, 得分{case.get('finalScore')}")
            
            else:
                print(f"获取结果失败: {summary_response.status_code}")
        
        else:
            print(f"批量质控启动失败: {response.status_code}")
            print(f"错误: {response.text}")
    
    except Exception as e:
        print(f"批量质控异常: {e}")

if __name__ == "__main__":
    run_2023_batch()