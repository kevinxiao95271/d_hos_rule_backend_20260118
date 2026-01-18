#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:4101/api"

def test_optimized_batch_performance():
    """测试优化批量接口的最终性能"""
    print("医疗质控系统优化批量接口最终测试")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n📊 当前状态:")
    print(f"   • 已禁用498条字典验证规则")
    print(f"   • 剩余1201条活跃规则")
    print(f"   • 单病案仍然较慢（>5秒）")
    print(f"   • 测试8线程并行批量处理")
    
    # 测试2023年数据（96个病案）
    print(f"\n🚀 启动2023年优化批量处理...")
    
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
            
            print(f"✅ 批量处理已启动")
            print(f"   批次键: {batch_key}")
            print(f"   病案数量: {case_count}个")
            
            if case_count > 0:
                # 监控处理进度
                return monitor_optimized_progress(batch_key, case_count, start_time)
            else:
                print(f"❌ 没有找到2023年病案数据")
                return None
        
        else:
            print(f"❌ 批量处理启动失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ 批量处理异常: {e}")
        return None

def monitor_optimized_progress(batch_key, total_cases, start_time):
    """监控优化批量处理进度"""
    print(f"\n=== 监控优化批量处理进度 ===")
    print(f"目标: {total_cases}个病案在5分钟内完成")
    
    max_wait = 600  # 10分钟最大等待时间
    last_progress = -1
    last_case_count = 0
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{BASE_URL}/qc/batch/status/{batch_key}", timeout=10)
            
            if response.status_code == 200:
                status = response.json().get('data', {})
                progress = status.get('progress', 0)
                batch_status = status.get('status', 'unknown')
                processed_count = status.get('caseCount', 0)
                
                current_time = time.time() - start_time
                
                # 显示进度（进度变化或每30秒）
                if progress != last_progress or processed_count != last_case_count or int(current_time) % 30 == 0:
                    print(f"  进度: {progress}% ({processed_count}/{total_cases}), 用时: {current_time/60:.1f}分钟, 状态: {batch_status}")
                    
                    # 计算处理速度
                    if processed_count > 0:
                        avg_time_per_case = current_time / processed_count
                        estimated_total_time = avg_time_per_case * total_cases
                        print(f"    平均每病案: {avg_time_per_case:.2f}秒, 预估总时间: {estimated_total_time/60:.1f}分钟")
                    
                    last_progress = progress
                    last_case_count = processed_count
                
                if batch_status == 'completed':
                    total_time = time.time() - start_time
                    
                    print(f"\n🎉 优化批量处理完成！")
                    print(f"   总耗时: {total_time/60:.1f}分钟")
                    print(f"   处理病案: {processed_count}个")
                    print(f"   平均每病案: {total_time/processed_count:.2f}秒")
                    
                    # 评估是否达到目标
                    if total_time <= 300:  # 5分钟
                        print(f"   🎯 目标达成！处理时间 ≤ 5分钟")
                        success_level = "优秀"
                    elif total_time <= 600:  # 10分钟
                        print(f"   ✅ 性能良好，处理时间 ≤ 10分钟")
                        success_level = "良好"
                    else:
                        print(f"   ⚠️  性能一般，超过10分钟")
                        success_level = "一般"
                    
                    return {
                        'success': True,
                        'completed': True,
                        'total_time': total_time,
                        'total_minutes': total_time / 60,
                        'case_count': processed_count,
                        'avg_per_case': total_time / processed_count,
                        'success_level': success_level
                    }
                
                elif batch_status == 'failed':
                    print(f"  ❌ 批量处理失败")
                    return {'success': False, 'reason': 'batch_failed'}
            
            else:
                print(f"    状态查询失败: {response.status_code}")
        
        except Exception as e:
            print(f"    状态查询异常: {e}")
        
        time.sleep(10)  # 每10秒检查一次
    
    # 超时处理
    current_time = time.time() - start_time
    
    try:
        response = requests.get(f"{BASE_URL}/qc/batch/status/{batch_key}", timeout=10)
        if response.status_code == 200:
            status = response.json().get('data', {})
            progress = status.get('progress', 0)
            processed_count = status.get('caseCount', 0)
            
            print(f"\n⏰ 监控超时 ({max_wait/60:.0f}分钟)")
            print(f"   当前进度: {progress}% ({processed_count}/{total_cases})")
            print(f"   已用时: {current_time/60:.1f}分钟")
            
            if processed_count > 0:
                avg_per_case = current_time / processed_count
                estimated_total_time = avg_per_case * total_cases
                
                print(f"   平均每病案: {avg_per_case:.2f}秒")
                print(f"   预估总时间: {estimated_total_time/60:.1f}分钟")
                
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

def analyze_final_results(result):
    """分析最终结果"""
    print(f"\n" + "=" * 50)
    print("📊 最终结果分析")
    print("=" * 50)
    
    if not result or not result.get('success'):
        print(f"❌ 优化批量处理失败")
        print(f"   可能原因: 系统资源不足、规则过于复杂、数据库性能问题")
        return
    
    if result.get('completed'):
        # 完整处理完成
        total_minutes = result['total_minutes']
        avg_per_case = result['avg_per_case']
        success_level = result['success_level']
        
        print(f"✅ 优化批量处理完成")
        print(f"   总处理时间: {total_minutes:.1f}分钟")
        print(f"   平均每病案: {avg_per_case:.2f}秒")
        print(f"   性能等级: {success_level}")
        
        # 与目标对比
        print(f"\n🎯 目标达成情况:")
        if total_minutes <= 5:
            print(f"   ✅ 主要目标达成: {total_minutes:.1f}分钟 ≤ 5分钟")
        else:
            print(f"   ❌ 主要目标未达成: {total_minutes:.1f}分钟 > 5分钟")
        
        if avg_per_case <= 3:
            print(f"   ✅ 单病案目标达成: {avg_per_case:.2f}秒 ≤ 3秒")
        else:
            print(f"   ❌ 单病案目标未达成: {avg_per_case:.2f}秒 > 3秒")
        
        # 性能分析
        print(f"\n📈 性能分析:")
        
        # 理论并行效果
        theoretical_serial_time = avg_per_case * result['case_count']
        actual_parallel_time = result['total_time']
        parallel_efficiency = theoretical_serial_time / actual_parallel_time
        
        print(f"   理论串行时间: {theoretical_serial_time/60:.1f}分钟")
        print(f"   实际并行时间: {actual_parallel_time/60:.1f}分钟")
        print(f"   并行效率: {parallel_efficiency:.1f}倍")
        
        if parallel_efficiency >= 6:
            print(f"   🎉 并行效果优秀！")
        elif parallel_efficiency >= 4:
            print(f"   ✅ 并行效果良好")
        else:
            print(f"   ⚠️  并行效果一般")
    
    else:
        # 部分处理结果
        estimated_minutes = result['estimated_total_minutes']
        progress = result['progress']
        avg_per_case = result['avg_per_case']
        
        print(f"⏱️  部分处理结果")
        print(f"   当前进度: {progress:.1f}%")
        print(f"   平均每病案: {avg_per_case:.2f}秒")
        print(f"   预估总时间: {estimated_minutes:.1f}分钟")
        
        if estimated_minutes <= 5:
            print(f"   ✅ 预估可达到目标")
        elif estimated_minutes <= 10:
            print(f"   ⚠️  预估接近目标")
        else:
            print(f"   ❌ 预估无法达到目标")

def provide_final_recommendations(result):
    """提供最终建议"""
    print(f"\n" + "=" * 50)
    print("🎯 最终建议和总结")
    print("=" * 50)
    
    print(f"📋 已实施的优化:")
    print(f"   ✅ 数据库索引优化（A48, A49, B15）")
    print(f"   ✅ 禁用498条字典验证规则")
    print(f"   ✅ BatchQcServiceOptimized 8线程并行处理")
    print(f"   ✅ 预加载规则到内存")
    print(f"   ✅ 批量数据库操作")
    
    if result and result.get('success'):
        if result.get('completed') and result['total_minutes'] <= 5:
            print(f"\n🎉 优化成功！")
            print(f"   • 96病案处理时间: {result['total_minutes']:.1f}分钟")
            print(f"   • 已达到5分钟内的目标")
            print(f"   • 可以正式使用优化批量接口")
            
            print(f"\n📋 使用指南:")
            print(f"   • 大批量处理: POST /api/qc/check/batch/optimized")
            print(f"   • 监控进度: GET /api/qc/batch/status/{{batchKey}}")
            print(f"   • 建议批量处理，避免单病案接口")
        
        elif result.get('completed') and result['total_minutes'] <= 10:
            print(f"\n✅ 优化有效！")
            print(f"   • 96病案处理时间: {result['total_minutes']:.1f}分钟")
            print(f"   • 虽未达到5分钟目标，但性能可接受")
            print(f"   • 可以使用优化批量接口")
            
            print(f"\n🔧 进一步优化建议:")
            print(f"   • 增加线程数（当前8线程）")
            print(f"   • 增加服务器内存和CPU")
            print(f"   • 继续优化规则逻辑")
        
        else:
            estimated_minutes = result.get('estimated_total_minutes', 0)
            print(f"\n⚠️  优化部分有效")
            print(f"   • 预估处理时间: {estimated_minutes:.1f}分钟")
            print(f"   • 性能有改善但未达到目标")
            
            print(f"\n🔧 进一步优化建议:")
            print(f"   • 考虑减少更多规则")
            print(f"   • 优化服务器配置")
            print(f"   • 分批处理大数据集")
    
    else:
        print(f"\n❌ 优化效果有限")
        print(f"   • 系统性能仍然不理想")
        print(f"   • 需要更深层次的优化")
        
        print(f"\n🔧 深度优化建议:")
        print(f"   • 重新设计规则引擎")
        print(f"   • 使用更高性能的硬件")
        print(f"   • 考虑分布式处理")
        print(f"   • 简化业务规则")
    
    print(f"\n📞 技术支持:")
    print(f"   • 如需恢复所有规则: python restore_rules.py")
    print(f"   • 性能监控: 关注CPU、内存、数据库连接")
    print(f"   • 日志分析: 查看服务运行日志")

def main():
    """主函数"""
    # 1. 测试优化批量性能
    result = test_optimized_batch_performance()
    
    # 2. 分析最终结果
    analyze_final_results(result)
    
    # 3. 提供最终建议
    provide_final_recommendations(result)
    
    print(f"\n" + "=" * 50)
    print(f"测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

if __name__ == "__main__":
    main()