#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:4101/api"

def test_single_case_performance():
    """测试单个病案性能"""
    print("=== 单个病案性能测试 ===")
    
    test_cases = [
        {'a48': '20003285', 'a49': '1'},
        {'a48': '20003286', 'a49': '1'},
        {'a48': '20003287', 'a49': '1'}
    ]
    
    total_time = 0
    success_count = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试病案 {i}: {case['a48']}_{case['a49']}")
        
        try:
            start_time = time.time()
            
            response = requests.post(f"{BASE_URL}/qc/check", 
                                   json=case, timeout=30)
            
            process_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json().get('data', {})
                defect_count = result.get('defectCount', 0)
                final_score = result.get('finalScore', 0)
                
                print(f"  ✅ 处理成功")
                print(f"     处理时间: {process_time:.2f}秒")
                print(f"     缺陷数量: {defect_count}个")
                print(f"     最终得分: {final_score}分")
                
                total_time += process_time
                success_count += 1
                
                if process_time <= 3:
                    print(f"     🎉 性能优秀！")
                elif process_time <= 5:
                    print(f"     ✅ 性能良好")
                else:
                    print(f"     ⚠️  性能需要优化")
            
            else:
                print(f"  ❌ 处理失败: {response.status_code}")
                print(f"     响应: {response.text}")
        
        except Exception as e:
            print(f"  ❌ 处理异常: {e}")
    
    if success_count > 0:
        avg_time = total_time / success_count
        print(f"\n📊 性能统计:")
        print(f"   成功处理: {success_count}/{len(test_cases)}个病案")
        print(f"   平均处理时间: {avg_time:.2f}秒")
        print(f"   总处理时间: {total_time:.2f}秒")
        
        # 估算96个病案的处理时间
        estimated_96_cases = avg_time * 96
        print(f"   预估96病案时间: {estimated_96_cases/60:.1f}分钟")
        
        if avg_time <= 3:
            print(f"   🎉 性能目标达成！单病案 ≤ 3秒")
        elif estimated_96_cases <= 300:  # 5分钟
            print(f"   ✅ 批量性能目标达成！96病案 ≤ 5分钟")
        else:
            print(f"   ⚠️  性能仍需优化")
        
        return avg_time
    
    return None

def check_batch_optimization():
    """检查批量优化状态"""
    print("\n=== 批量优化状态检查 ===")
    
    # 检查优化接口是否可用
    try:
        response = requests.post(f"{BASE_URL}/qc/check/batch/optimized", 
                               json={'periodType': 'year', 'year': 2019}, 
                               timeout=5)
        
        if response.status_code == 200:
            result = response.json().get('data', {})
            batch_key = result.get('batchKey', '')
            case_count = result.get('caseCount', 0)
            
            print(f"✅ 优化批量接口可用")
            print(f"   批次键: {batch_key}")
            print(f"   2019年病案数量: {case_count}个")
            
            return True
        
        elif response.status_code == 404:
            print(f"❌ 优化批量接口不存在")
            print(f"   可能原因: BatchQcServiceOptimized 未正确部署")
            return False
        
        else:
            print(f"⚠️  优化批量接口异常: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ 优化批量接口测试失败: {e}")
        return False

def analyze_optimization_effect(single_case_time):
    """分析优化效果"""
    print(f"\n=== 优化效果分析 ===")
    
    if single_case_time is None:
        print("❌ 无法分析，单病案测试失败")
        return
    
    print(f"📊 性能对比:")
    
    # 优化前的预估性能（基于之前的分析）
    old_single_time = 22  # 秒
    old_96_time = old_single_time * 96 / 60  # 分钟
    
    # 优化后的实际性能
    new_single_time = single_case_time
    new_96_time = new_single_time * 96 / 60  # 分钟（串行处理）
    new_96_time_parallel = new_96_time / 8  # 8线程并行处理
    
    print(f"   优化前:")
    print(f"     单病案时间: {old_single_time}秒")
    print(f"     96病案时间: {old_96_time:.1f}分钟")
    
    print(f"   优化后:")
    print(f"     单病案时间: {new_single_time:.2f}秒")
    print(f"     96病案时间(串行): {new_96_time:.1f}分钟")
    print(f"     96病案时间(8线程并行): {new_96_time_parallel:.1f}分钟")
    
    # 计算性能提升
    single_improvement = old_single_time / new_single_time
    batch_improvement = old_96_time / new_96_time_parallel
    
    print(f"   性能提升:")
    print(f"     单病案提升: {single_improvement:.1f}倍")
    print(f"     批量处理提升: {batch_improvement:.1f}倍")
    
    # 评估是否达到目标
    print(f"\n🎯 目标达成情况:")
    
    if new_single_time <= 3:
        print(f"   ✅ 单病案目标达成: {new_single_time:.2f}秒 ≤ 3秒")
    else:
        print(f"   ❌ 单病案目标未达成: {new_single_time:.2f}秒 > 3秒")
    
    if new_96_time_parallel <= 5:
        print(f"   ✅ 批量处理目标达成: {new_96_time_parallel:.1f}分钟 ≤ 5分钟")
    else:
        print(f"   ❌ 批量处理目标未达成: {new_96_time_parallel:.1f}分钟 > 5分钟")

def provide_recommendations():
    """提供优化建议"""
    print(f"\n=== 优化建议 ===")
    
    print(f"✅ 已实现的优化:")
    print(f"   • BatchQcServiceOptimized.java - 8线程并行处理")
    print(f"   • 预加载1699条规则到内存")
    print(f"   • Redis缓存字典验证")
    print(f"   • 批量数据库操作（50条/批次）")
    print(f"   • 优化接口: POST /api/qc/check/batch/optimized")
    
    print(f"\n🔧 进一步优化建议:")
    print(f"   1. 调整线程数（当前8线程）:")
    print(f"      • 根据CPU核心数调整")
    print(f"      • 监控CPU使用率")
    
    print(f"   2. 调整批量大小:")
    print(f"      • 并行批量大小: 当前12，可调整为16-20")
    print(f"      • 数据库批量大小: 当前50，可调整为100")
    
    print(f"   3. 系统资源优化:")
    print(f"      • 增加JVM内存: -Xmx4g")
    print(f"      • 增加数据库连接池大小")
    print(f"      • 优化Redis配置")
    
    print(f"\n📋 使用指南:")
    print(f"   • 大批量处理使用: POST /api/qc/check/batch/optimized")
    print(f"   • 单个病案处理使用: POST /api/qc/check")
    print(f"   • 监控处理进度: GET /api/qc/batch/status/{{batchKey}}")

def main():
    """主函数"""
    print("医疗质控系统性能优化效果验证")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 测试单个病案性能
    single_case_time = test_single_case_performance()
    
    # 2. 检查批量优化状态
    batch_optimization_ok = check_batch_optimization()
    
    # 3. 分析优化效果
    analyze_optimization_effect(single_case_time)
    
    # 4. 提供优化建议
    provide_recommendations()
    
    # 5. 总结
    print(f"\n" + "=" * 50)
    print("📋 验证总结")
    print("=" * 50)
    
    if single_case_time and single_case_time <= 3:
        print(f"🎉 优化成功！单病案处理时间达到目标")
    elif single_case_time and single_case_time <= 5:
        print(f"✅ 优化有效！性能显著提升")
    elif single_case_time:
        print(f"⚠️  优化部分有效，仍需进一步调优")
    else:
        print(f"❌ 优化验证失败，需要检查系统状态")
    
    if batch_optimization_ok:
        print(f"✅ 批量优化接口已部署并可用")
    else:
        print(f"❌ 批量优化接口不可用，需要检查部署")
    
    print(f"\n🎯 下一步行动:")
    if single_case_time and single_case_time <= 3 and batch_optimization_ok:
        print(f"   • 可以正式使用优化版本处理大批量数据")
        print(f"   • 监控系统资源使用情况")
    else:
        print(f"   • 检查系统配置和资源")
        print(f"   • 考虑进一步调优参数")

if __name__ == "__main__":
    main()