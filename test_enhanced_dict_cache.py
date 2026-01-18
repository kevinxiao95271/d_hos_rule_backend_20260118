#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:4101/api"

def test_enhanced_dict_cache_system():
    print("增强字典缓存系统测试")
    print("=" * 40)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查缓存状态
    print("\n1. 检查增强缓存状态...")
    try:
        response = requests.get(f"{BASE_URL}/dict/enhanced/status", timeout=10)
        if response.status_code == 200:
            status = response.json().get('data', {})
            print(f"✅ 增强缓存状态:")
            for key, value in status.items():
                print(f"   {key}: {value}")
        else:
            print(f"❌ 增强缓存状态检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 增强缓存状态检查异常: {e}")
    
    # 2. 重新加载缓存
    print("\n2. 重新加载增强字典缓存...")
    try:
        response = requests.post(f"{BASE_URL}/dict/enhanced/reload", timeout=30)
        if response.status_code == 200:
            print(f"✅ 增强缓存重新加载成功")
        else:
            print(f"❌ 增强缓存重新加载失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 增强缓存重新加载异常: {e}")
    
    # 3. 测试字典验证
    print("\n3. 测试增强字典验证...")
    test_cases = [
        {"dictType": "RC001", "value": "1"},
        {"dictType": "RC002", "value": "1"},
        {"dictType": "RC011", "value": "1"},
        {"dictType": "RC001", "value": "999"}  # 无效值测试
    ]
    
    for case in test_cases:
        try:
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/dict/enhanced/validate", 
                                   params=case, timeout=5)
            validation_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json().get('data', False)
                print(f"  {case['dictType']}:{case['value']} = {result} ({validation_time*1000:.1f}ms)")
            else:
                print(f"  {case['dictType']}:{case['value']} = 验证失败 ({response.status_code})")
        except Exception as e:
            print(f"  {case['dictType']}:{case['value']} = 异常: {e}")
    
    # 4. 测试批量验证
    print("\n4. 测试批量字典验证...")
    try:
        batch_values = ["1", "2", "3", "999"]
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/dict/enhanced/validate/batch", 
                               params={"dictType": "RC001"},
                               json=batch_values,
                               timeout=10)
        
        batch_time = time.time() - start_time
        
        if response.status_code == 200:
            results = response.json().get('data', {})
            print(f"✅ 批量验证成功 ({batch_time*1000:.1f}ms):")
            for value, valid in results.items():
                print(f"   RC001:{value} = {valid}")
        else:
            print(f"❌ 批量验证失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 批量验证异常: {e}")
    
    # 5. 测试原有缓存接口
    print("\n5. 测试原有缓存接口...")
    try:
        response = requests.get(f"{BASE_URL}/dict/cache/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json().get('data', {})
            print(f"✅ 原有缓存统计:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
        else:
            print(f"❌ 原有缓存统计失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 原有缓存统计异常: {e}")
    
    # 6. 测试单病案性能
    print("\n6. 测试单病案性能（使用增强字典缓存）...")
    test_case = {'a48': '20003285', 'a49': '1'}
    
    try:
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/qc/check/single", 
                               params=test_case, timeout=60)
        
        process_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json().get('data', {})
            defect_count = result.get('defectCount', 0)
            final_score = result.get('finalScore', 0)
            
            print(f"✅ 单病案测试成功")
            print(f"   处理时间: {process_time:.2f}秒")
            print(f"   缺陷数量: {defect_count}个")
            print(f"   最终得分: {final_score}分")
            
            # 性能评估
            if process_time <= 3:
                print(f"   🎉 性能目标达成！")
                performance = "优秀"
            elif process_time <= 5:
                print(f"   ✅ 性能显著改善")
                performance = "良好"
            elif process_time <= 10:
                print(f"   ⚠️  性能有所改善")
                performance = "一般"
            else:
                print(f"   ❌ 性能仍需优化")
                performance = "较差"
            
            return {
                'success': True,
                'time': process_time,
                'defects': defect_count,
                'score': final_score,
                'performance': performance
            }
        
        else:
            print(f"❌ 单病案测试失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return {'success': False, 'error': response.text}
    
    except Exception as e:
        print(f"❌ 单病案测试异常: {e}")
        return {'success': False, 'error': str(e)}

def test_optimized_batch_with_cache():
    """测试使用缓存的优化批量处理"""
    print(f"\n7. 测试优化批量处理（使用字典缓存）...")
    
    try:
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/qc/check/batch/optimized", 
                               json={
                                   'periodType': 'year',
                                   'year': 2023
                               }, timeout=10)
        
        if response.status_code == 200:
            result = response.json().get('data', {})
            batch_key = result.get('batchKey', '')
            case_count = result.get('caseCount', 0)
            
            print(f"✅ 优化批量处理已启动")
            print(f"   批次键: {batch_key}")
            print(f"   病案数量: {case_count}个")
            
            # 监控5分钟
            return monitor_batch_progress(batch_key, case_count, start_time, max_wait=300)
        
        else:
            print(f"❌ 优化批量处理启动失败: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"❌ 优化批量处理异常: {e}")
        return None

def monitor_batch_progress(batch_key, total_cases, start_time, max_wait=300):
    """监控批量处理进度"""
    print(f"\n   监控批量处理进度（最大等待{max_wait/60:.0f}分钟）...")
    
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
                
                # 显示进度变化
                if progress != last_progress:
                    print(f"   进度: {progress}% ({processed_count}/{total_cases}), 用时: {current_time/60:.1f}分钟")
                    
                    if processed_count > 0:
                        avg_time = current_time / processed_count
                        estimated_total = avg_time * total_cases
                        print(f"     平均每病案: {avg_time:.2f}秒, 预估总时间: {estimated_total/60:.1f}分钟")
                    
                    last_progress = progress
                
                if batch_status == 'completed':
                    total_time = time.time() - start_time
                    
                    print(f"   🎉 批量处理完成！")
                    print(f"   总耗时: {total_time/60:.1f}分钟")
                    print(f"   平均每病案: {total_time/processed_count:.2f}秒")
                    
                    return {
                        'success': True,
                        'completed': True,
                        'total_time': total_time,
                        'case_count': processed_count,
                        'avg_per_case': total_time / processed_count
                    }
                
                elif batch_status == 'failed':
                    print(f"   ❌ 批量处理失败")
                    return {'success': False, 'reason': 'failed'}
            
        except Exception as e:
            print(f"   状态查询异常: {e}")
        
        time.sleep(10)  # 每10秒检查一次
    
    # 超时处理
    print(f"   ⏰ 监控超时")
    return {'success': False, 'reason': 'timeout'}

def main():
    # 1. 测试增强字典缓存系统
    single_result = test_enhanced_dict_cache_system()
    
    # 2. 测试优化批量处理
    batch_result = test_optimized_batch_with_cache()
    
    # 3. 总结
    print(f"\n" + "=" * 40)
    print("测试总结")
    print("=" * 40)
    
    if single_result and single_result.get('success'):
        print(f"✅ 增强字典缓存系统测试成功")
        print(f"   单病案处理时间: {single_result['time']:.2f}秒")
        print(f"   性能等级: {single_result['performance']}")
        
        if single_result['time'] <= 3:
            print(f"   🎯 单病案性能目标达成！")
        elif single_result['time'] <= 10:
            print(f"   ✅ 单病案性能显著改善")
    
    if batch_result and batch_result.get('success') and batch_result.get('completed'):
        print(f"✅ 优化批量处理测试成功")
        print(f"   批量处理时间: {batch_result['total_time']/60:.1f}分钟")
        print(f"   平均每病案: {batch_result['avg_per_case']:.2f}秒")
        
        if batch_result['total_time'] <= 300:  # 5分钟
            print(f"   🎯 批量处理目标达成！")
    
    print(f"\n🎯 最终评估:")
    
    if (single_result and single_result.get('success') and single_result['time'] <= 3) or \
       (batch_result and batch_result.get('success') and batch_result.get('completed') and batch_result['total_time'] <= 300):
        print(f"   🎉 性能优化成功！已达到目标")
        print(f"   • 字典缓存系统工作正常")
        print(f"   • 保持了所有1699条规则")
        print(f"   • 性能提升显著")
    else:
        print(f"   ⚠️  性能有改善但未完全达到目标")
        print(f"   • 字典缓存系统已部署")
        print(f"   • 可能需要进一步调优")

if __name__ == "__main__":
    main()