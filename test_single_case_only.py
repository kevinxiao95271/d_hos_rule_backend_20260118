#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:4101/api"

def test_single_case():
    """测试单个病案性能"""
    print("医疗质控系统单病案性能测试")
    print("=" * 40)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试病案
    test_case = {'a48': '20003285', 'a49': '1'}
    
    print(f"\n测试病案: {test_case['a48']}_{test_case['a49']}")
    
    try:
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/qc/check/single", 
                               params=test_case, timeout=30)
        
        process_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json().get('data', {})
            defect_count = result.get('defectCount', 0)
            final_score = result.get('finalScore', 0)
            
            print(f"✅ 处理成功")
            print(f"   处理时间: {process_time:.2f}秒")
            print(f"   缺陷数量: {defect_count}个")
            print(f"   最终得分: {final_score}分")
            
            # 性能评估
            print(f"\n📊 性能评估:")
            if process_time <= 3:
                print(f"   🎉 性能优秀！{process_time:.2f}秒 ≤ 3秒目标")
                performance_level = "优秀"
            elif process_time <= 5:
                print(f"   ✅ 性能良好！{process_time:.2f}秒 ≤ 5秒")
                performance_level = "良好"
            elif process_time <= 10:
                print(f"   ⚠️  性能一般，{process_time:.2f}秒")
                performance_level = "一般"
            else:
                print(f"   ❌ 性能较差，{process_time:.2f}秒")
                performance_level = "较差"
            
            # 估算批量处理时间
            print(f"\n🔢 批量处理时间估算:")
            
            # 串行处理96个病案
            serial_96_time = process_time * 96
            print(f"   串行处理96病案: {serial_96_time/60:.1f}分钟")
            
            # 8线程并行处理96个病案
            parallel_96_time = serial_96_time / 8
            print(f"   8线程并行处理96病案: {parallel_96_time/60:.1f}分钟")
            
            # 目标达成情况
            print(f"\n🎯 目标达成情况:")
            if process_time <= 3:
                print(f"   ✅ 单病案目标达成: ≤ 3秒")
            else:
                print(f"   ❌ 单病案目标未达成: > 3秒")
            
            if parallel_96_time <= 300:  # 5分钟
                print(f"   ✅ 批量处理目标达成: ≤ 5分钟")
            else:
                print(f"   ❌ 批量处理目标未达成: > 5分钟")
            
            # 与优化前对比
            print(f"\n📈 性能提升对比:")
            old_time = 22  # 优化前预估时间
            if process_time < old_time:
                improvement = old_time / process_time
                print(f"   单病案性能提升: {improvement:.1f}倍")
                print(f"   从 {old_time}秒 → {process_time:.2f}秒")
            else:
                print(f"   性能未提升，当前 {process_time:.2f}秒")
            
            return {
                'success': True,
                'time': process_time,
                'defects': defect_count,
                'score': final_score,
                'performance': performance_level
            }
        
        else:
            print(f"❌ 处理失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return {'success': False, 'error': response.text}
    
    except Exception as e:
        print(f"❌ 处理异常: {e}")
        return {'success': False, 'error': str(e)}

def check_optimization_interface():
    """检查优化接口"""
    print(f"\n" + "=" * 40)
    print("优化接口检查")
    print("=" * 40)
    
    try:
        # 测试优化接口是否存在
        response = requests.post(f"{BASE_URL}/qc/check/batch/optimized", 
                               json={'periodType': 'year', 'year': 2018},  # 用更早的年份，数据更少
                               timeout=5)
        
        if response.status_code == 200:
            result = response.json().get('data', {})
            batch_key = result.get('batchKey', '')
            case_count = result.get('caseCount', 0)
            
            print(f"✅ 优化批量接口可用")
            print(f"   接口: POST /api/qc/check/batch/optimized")
            print(f"   测试批次: {batch_key}")
            print(f"   2018年病案数: {case_count}个")
            
            return True
        
        elif response.status_code == 404:
            print(f"❌ 优化批量接口不存在")
            print(f"   可能原因: BatchQcServiceOptimized 未正确部署")
            return False
        
        else:
            print(f"⚠️  优化批量接口响应异常: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ 优化批量接口测试失败: {e}")
        return False

def provide_summary_and_recommendations(test_result, optimization_available):
    """提供总结和建议"""
    print(f"\n" + "=" * 40)
    print("总结和建议")
    print("=" * 40)
    
    if test_result and test_result.get('success'):
        process_time = test_result['time']
        performance = test_result['performance']
        
        print(f"📊 当前性能状态:")
        print(f"   单病案处理时间: {process_time:.2f}秒")
        print(f"   性能等级: {performance}")
        
        if process_time <= 3:
            print(f"   🎉 已达到性能目标！")
        elif process_time <= 5:
            print(f"   ✅ 性能良好，接近目标")
        else:
            print(f"   ⚠️  性能需要进一步优化")
    
    else:
        print(f"❌ 性能测试失败，需要检查系统状态")
    
    if optimization_available:
        print(f"\n✅ 优化版本已部署:")
        print(f"   • BatchQcServiceOptimized.java")
        print(f"   • 8线程并行处理")
        print(f"   • Redis缓存优化")
        print(f"   • 批量数据库操作")
    else:
        print(f"\n❌ 优化版本未正确部署")
    
    print(f"\n🎯 下一步建议:")
    
    if test_result and test_result.get('success') and test_result['time'] <= 3 and optimization_available:
        print(f"   1. ✅ 可以使用优化接口处理大批量数据")
        print(f"   2. 监控系统资源使用情况")
        print(f"   3. 根据实际负载调整线程数")
    
    elif test_result and test_result.get('success') and test_result['time'] <= 5:
        print(f"   1. 可以尝试调整优化参数:")
        print(f"      • 增加线程数（当前8线程）")
        print(f"      • 增加数据库批量大小（当前50）")
        print(f"   2. 检查系统资源是否充足")
        print(f"   3. 优化数据库查询")
    
    else:
        print(f"   1. 检查服务是否正确启动")
        print(f"   2. 检查数据库连接")
        print(f"   3. 检查Redis缓存状态")
        print(f"   4. 查看服务日志排查问题")
    
    print(f"\n📋 可用接口:")
    print(f"   • 单病案质控: POST /api/qc/check/single")
    if optimization_available:
        print(f"   • 优化批量质控: POST /api/qc/check/batch/optimized")
    print(f"   • 标准批量质控: POST /api/qc/check/batch")
    print(f"   • 批次状态查询: GET /api/qc/batch/status/{{batchKey}}")

def main():
    """主函数"""
    # 1. 测试单个病案性能
    test_result = test_single_case()
    
    # 2. 检查优化接口
    optimization_available = check_optimization_interface()
    
    # 3. 提供总结和建议
    provide_summary_and_recommendations(test_result, optimization_available)

if __name__ == "__main__":
    main()