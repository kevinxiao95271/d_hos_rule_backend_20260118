#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:4101/api"

def test_dict_cache_system():
    print("字典缓存系统测试")
    print("=" * 40)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查缓存状态
    print("\n1. 检查缓存状态...")
    try:
        response = requests.get(f"{BASE_URL}/dict/cache/status", timeout=10)
        if response.status_code == 200:
            status = response.json().get('data', {})
            print(f"✅ 缓存状态:")
            for key, value in status.items():
                print(f"   {key}: {value}")
        else:
            print(f"❌ 缓存状态检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 缓存状态检查异常: {e}")
    
    # 2. 重新加载缓存
    print("\n2. 重新加载字典缓存...")
    try:
        response = requests.post(f"{BASE_URL}/dict/cache/reload", timeout=30)
        if response.status_code == 200:
            print(f"✅ 缓存重新加载成功")
        else:
            print(f"❌ 缓存重新加载失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 缓存重新加载异常: {e}")
    
    # 3. 测试字典验证
    print("\n3. 测试字典验证...")
    test_cases = [
        {"dictType": "RC001", "value": "1"},
        {"dictType": "RC002", "value": "1"},
        {"dictType": "RC011", "value": "1"},
        {"dictType": "RC001", "value": "999"}  # 无效值测试
    ]
    
    for case in test_cases:
        try:
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/dict/cache/validate", 
                                   params=case, timeout=5)
            validation_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json().get('data', False)
                print(f"  {case['dictType']}:{case['value']} = {result} ({validation_time*1000:.1f}ms)")
            else:
                print(f"  {case['dictType']}:{case['value']} = 验证失败")
        except Exception as e:
            print(f"  {case['dictType']}:{case['value']} = 异常: {e}")
    
    # 4. 测试批量验证
    print("\n4. 测试批量字典验证...")
    try:
        batch_values = ["1", "2", "3", "999"]
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/dict/cache/validate/batch", 
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
    except Exception as e:
        print(f"❌ 批量验证异常: {e}")
    
    # 5. 测试单病案性能
    print("\n5. 测试单病案性能（使用字典缓存）...")
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

def main():
    result = test_dict_cache_system()
    
    print(f"\n" + "=" * 40)
    print("测试总结")
    print("=" * 40)
    
    if result and result.get('success'):
        print(f"✅ 字典缓存系统测试成功")
        print(f"   处理时间: {result['time']:.2f}秒")
        print(f"   性能等级: {result['performance']}")
        
        if result['time'] <= 3:
            print(f"   🎯 已达到性能目标！")
        elif result['time'] <= 10:
            print(f"   ✅ 性能显著改善")
        
        # 估算批量处理性能
        estimated_96_cases = result['time'] * 96 / 8  # 8线程并行
        print(f"   预估96病案处理时间: {estimated_96_cases/60:.1f}分钟")
        
        if estimated_96_cases <= 300:  # 5分钟
            print(f"   🎯 批量处理目标可达成！")
    
    else:
        print(f"❌ 字典缓存系统测试失败")
        if result:
            print(f"   错误: {result.get('error', '未知错误')}")

if __name__ == "__main__":
    main()
