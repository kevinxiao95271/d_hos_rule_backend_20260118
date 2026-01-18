#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import json
from datetime import datetime

def monitor_batch():
    """监控优化批量处理进度"""
    batch_key = "2023_opt"
    start_time = time.time()
    
    print(f"=== 监控优化批量处理进度 ===")
    print(f"批次键: {batch_key}")
    print(f"开始时间: {datetime.now().strftime('%H:%M:%S')}")
    
    last_progress = -1
    
    for i in range(60):  # 监控10分钟
        try:
            response = requests.get(f"http://localhost:4101/api/qc/batch/status/{batch_key}", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                data = result.get('data', {})
                
                progress = data.get('progress', 0)
                status = data.get('status', 'unknown')
                case_count = data.get('caseCount', 0)
                
                elapsed = time.time() - start_time
                
                if progress != last_progress:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 进度: {progress}%, 状态: {status}, 处理数: {case_count}, 耗时: {elapsed/60:.1f}分钟")
                    last_progress = progress
                
                if status == 'completed':
                    print(f"✅ 批量处理完成！")
                    print(f"总耗时: {elapsed/60:.1f}分钟")
                    print(f"处理病案: {case_count}个")
                    print(f"平均每病案: {elapsed/case_count:.2f}秒")
                    
                    if elapsed <= 300:  # 5分钟
                        print(f"🎉 成功达到5分钟目标！")
                    else:
                        print(f"⚠️  超过5分钟目标，但仍有显著提升")
                    
                    return True
                
                elif status == 'failed':
                    print(f"❌ 批量处理失败")
                    return False
            
            else:
                print(f"状态查询失败: {response.status_code}")
        
        except Exception as e:
            print(f"查询异常: {e}")
        
        time.sleep(10)  # 每10秒检查一次
    
    print(f"⏰ 监控超时")
    return False

if __name__ == "__main__":
    monitor_batch()