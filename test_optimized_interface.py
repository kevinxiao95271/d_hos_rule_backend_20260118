#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:4101/api"

def test_optimized_interface():
    """测试优化接口"""
    print("=== 测试优化批量接口 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 先用2020年数据测试（数据量少）
    print("\n1. 测试优化接口可用性（2020年数据）...")
    
    try:
        response = requests.post(f"{BASE_URL}/qc/check/batch/optimized", 
                               json={
                                   'periodType': 'year',
                                   'year': 2020
                               }, timeout=10)
        
        if response.status_code == 200:
            result = response.json().get('data', {})
            batch_key = result.get('batchKey', '')
            case_count = result.get('caseCount', 0)
            
            print(f"✅ 优化接口可用")
            print(f"   批次键: {batch_key}")
            print(f"   病案数量: {case_count}个")
            
            if case_count > 0:
                # 监控2020年处理进度
                monitor_progress(batch_key, case_count, max_wait=60)
            
        elif response.status_code == 404:
            print(f"❌ 优化接口不存在")
            print(f"   需要检查 QcController 是否包含优化接口")
            return False
        
        else:
            print(f"❌ 优化接口异常: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ 优化接口测试失败: {e}")
        return False
    
    # 如果2020年测试成功，再测试2023年
    print(f"\n2. 测试2023年数据处理...")
    
    try:
        response = requests.post(f"{BASE_URL}/qc/check/batch/optimized", 
                               json={
                                   'periodType': 'year',
                                   'year': 2023
                               }, timeout=10)
        
        if response.status_code == 200:
            result = response.json().get('data', {})
            batch_key = result.get('batchKey', '')
            case_count = result.get('caseCount', 0)
            
            print(f"✅ 2023年批量处理已启动")
            print(f"   批次键: {batch_key}")
            print(f"   病案数量: {case_count}个")
            
            # 监控处理进度
            return monitor_progress(batch_key, case_count, max_wait=300)  # 5分钟
        
        else:
            print(f"❌ 2023年处理启动失败: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ 2023年处理异常: {e}")
        return False

def monitor_progress(batch_key, total_cases, max_wait=300):
    """监控处理进度"""
    print(f"\n=== 监控处理进度 ===")
    print(f"批次: {batch_key}, 病案数: {total_cases}, 最大等待: {max_wait}秒")
    
    start_time = time.time()
    last_progress = -1
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{BASE_URL}/qc/batch/status/{batch_key}", timeout=10)
            
            if response.status_code == 200:
                status = response.json().get('data', {})
                progress = status.get('progress', 0)
                batch_status = status.get('status', 'unknown')
                processed_count = status.get('caseCount', 0)
                
                current_time = time.time() - start_time
                
                # 只在进度变化或每30秒输出一次
                if progress != last_progress or int(current_time) % 30 == 0:
                    print(f"  进度: {progress}% ({processed_count}个病案), 已用时: {current_time/60:.1f}分钟, 状态: {batch_status}")
                    last_progress = progress
                
                if batch_status == 'completed':
                    total_time = time.time() - start_time
                    
                    print(f"  ✅ 处理完成！")
                    print(f"  总耗时: {total_time/60:.1f}分钟")
                    print(f"  平均每病案: {total_time/processed_count:.2f}秒")
                    
                    # 评估性能
                    avg_per_case = total_time / processed_count
                    if avg_per_case <= 3:
                        print(f"  🎉 性能优秀！平均每病案 {avg_per_case:.2f}秒")
                    elif avg_per_case <= 5:
                        print(f"  ✅ 性能良好！平均每病案 {avg_per_case:.2f}秒")
                    else:
                        print(f"  ⚠️  性能一般，平均每病案 {avg_per_case:.2f}秒")
                    
                    return {
                        'success': True,
                        'completed': True,
                        'total_time': total_time,
                        'case_count': processed_count,
                        'avg_per_case': avg_per_case
                    }
                
                elif batch_status == 'failed':
                    print(f"  ❌ 处理失败")
                    return {'success': False, 'reason': 'batch_failed'}
            
            else:
                print(f"    状态查询失败: {response.status_code}")
        
        except Exception as e:
            print(f"    状态查询异常: {e}")
        
        time.sleep(5)  # 每5秒检查一次
    
    # 超时处理
    current_time = time.time() - start_time
    
    try:
        response = requests.get(f"{BASE_URL}/qc/batch/status/{batch_key}", timeout=10)
        if response.status_code == 200:
            status = response.json().get('data', {})
            progress = status.get('progress', 0)
            processed_count = status.get('caseCount', 0)
            
            print(f"  ⏰ 监控超时 ({max_wait}秒)")
            print(f"  当前进度: {progress}% ({processed_count}个病案)")
            print(f"  已用时: {current_time/60:.1f}分钟")
            
            if processed_count > 0:
                avg_per_case = current_time / processed_count
                estimated_total_time = avg_per_case * total_cases
                
                print(f"  平均每病案: {avg_per_case:.2f}秒")
                print(f"  预估总时间: {estimated_total_time/60:.1f}分钟")
                
                return {
                    'success': True,
                    'completed': False,
                    'partial_time': current_time,
                    'processed_count': processed_count,
                    'total_cases': total_cases,
                    'progress': progress,
                    'avg_per_case': avg_per_case,
                    'estimated_total_minutes': estimated_total_time / 60
                }
    
    except Exception as e:
        print(f"    最终状态查询异常: {e}")
    
    return {'success': False, 'reason': 'timeout'}

def compare_with_standard_interface():
    """与标准接口对比"""
    print(f"\n=== 接口对比说明 ===")
    
    print(f"标准接口:")
    print(f"  POST /api/qc/check/batch")
    print(f"  • 单线程顺序处理")
    print(f"  • 每病案重复查询规则")
    print(f"  • 预估96病案需要35分钟")
    
    print(f"\n优化接口:")
    print(f"  POST /api/qc/check/batch/optimized")
    print(f"  • 8线程并行处理")
    print(f"  • 预加载规则到内存")
    print(f"  • Redis缓存字典验证")
    print(f"  • 批量数据库操作")
    print(f"  • 预估96病案需要5分钟以内")

def main():
    """主函数"""
    print("医疗质控系统优化接口测试")
    print("=" * 50)
    
    # 1. 测试优化接口
    result = test_optimized_interface()
    
    # 2. 接口对比说明
    compare_with_standard_interface()
    
    # 3. 总结
    print(f"\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    
    if result and result.get('success'):
        if result.get('completed'):
            print(f"✅ 优化接口测试成功")
            print(f"   总耗时: {result['total_time']/60:.1f}分钟")
            print(f"   处理病案: {result['case_count']}个")
            print(f"   平均每病案: {result['avg_per_case']:.2f}秒")
            
            if result['avg_per_case'] <= 3:
                print(f"   🎉 性能目标达成！")
            else:
                print(f"   ⚠️  性能仍需优化")
        
        else:
            print(f"⏱️  部分测试结果")
            print(f"   已处理: {result['processed_count']}/{result['total_cases']}个")
            print(f"   平均每病案: {result['avg_per_case']:.2f}秒")
            print(f"   预估总时间: {result['estimated_total_minutes']:.1f}分钟")
            
            if result['estimated_total_minutes'] <= 5:
                print(f"   ✅ 预估性能达标")
            else:
                print(f"   ⚠️  预估性能仍需优化")
    
    else:
        print(f"❌ 优化接口测试失败")
        print(f"   可能原因: 接口未部署或服务异常")
    
    print(f"\n🎯 下一步:")
    print(f"   1. 如果性能达标，可以正式使用优化接口")
    print(f"   2. 如果性能不达标，需要进一步调优")
    print(f"   3. 监控系统资源使用情况")

if __name__ == "__main__":
    main()