#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import json
import pymysql
from datetime import datetime

# 数据库连接配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

BASE_URL = "http://localhost:4101/api"

def clear_previous_results():
    """清理之前的测试结果"""
    print("=== 清理之前的测试结果 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 清理2023年的质控结果
        cursor.execute("""
            DELETE FROM kiro_qc_case_result 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
        """)
        
        cursor.execute("""
            DELETE FROM kiro_qc_defect_detail 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
        """)
        
        # 清理批次汇总
        cursor.execute("DELETE FROM kiro_qc_batch_summary WHERE batch_key LIKE '%2023%'")
        
        conn.commit()
        
        print("✅ 清理完成")
        
    finally:
        cursor.close()
        conn.close()

def test_optimized_batch():
    """测试优化的批量处理"""
    print("\n=== 测试优化批量处理 ===")
    
    # 启动优化批量处理
    start_time = time.time()
    
    try:
        response = requests.post(f"{BASE_URL}/qc/check/batch/optimized", 
                               json={
                                   'periodType': 'year',
                                   'year': 2023
                               }, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 优化批量处理启动失败: {response.status_code}")
            print(f"响应: {response.text}")
            return None
        
        result = response.json().get('data', {})
        batch_key = result.get('batchKey', '')
        case_count = result.get('caseCount', 0)
        
        print(f"✅ 优化批量处理已启动")
        print(f"批次键: {batch_key}")
        print(f"病案数量: {case_count}")
        
        # 监控进度
        return monitor_batch_progress(batch_key, start_time, "优化版本")
        
    except Exception as e:
        print(f"❌ 优化批量处理异常: {e}")
        return None

def test_standard_batch():
    """测试标准批量处理（对比）"""
    print("\n=== 测试标准批量处理（对比） ===")
    
    # 启动标准批量处理
    start_time = time.time()
    
    try:
        response = requests.post(f"{BASE_URL}/qc/check/batch", 
                               json={
                                   'periodType': 'year',
                                   'year': 2023
                               }, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 标准批量处理启动失败: {response.status_code}")
            print(f"响应: {response.text}")
            return None
        
        result = response.json().get('data', {})
        batch_key = result.get('batchKey', '')
        case_count = result.get('caseCount', 0)
        
        print(f"✅ 标准批量处理已启动")
        print(f"批次键: {batch_key}")
        print(f"病案数量: {case_count}")
        
        # 监控进度
        return monitor_batch_progress(batch_key, start_time, "标准版本")
        
    except Exception as e:
        print(f"❌ 标准批量处理异常: {e}")
        return None

def monitor_batch_progress(batch_key, start_time, version_name):
    """监控批量处理进度"""
    print(f"\n=== 监控{version_name}处理进度 ===")
    
    max_wait = 600  # 最多等待10分钟
    wait_time = 0
    last_progress = 0
    
    while wait_time < max_wait:
        time.sleep(10)
        wait_time += 10
        
        try:
            response = requests.get(f"{BASE_URL}/qc/batch/status/{batch_key}", timeout=10)
            
            if response.status_code == 200:
                status = response.json().get('data', {})
                progress = status.get('progress', 0)
                batch_status = status.get('status', 'unknown')
                processed_count = status.get('caseCount', 0)
                
                current_time = time.time() - start_time
                
                if progress != last_progress:
                    print(f"  进度: {progress}% ({processed_count}个病案), 已用时: {current_time/60:.1f}分钟, 状态: {batch_status}")
                    last_progress = progress
                
                if batch_status == 'completed':
                    total_time = time.time() - start_time
                    
                    print(f"  ✅ {version_name}处理完成！")
                    print(f"  总耗时: {total_time/60:.1f}分钟")
                    print(f"  平均每病案: {total_time/processed_count:.2f}秒")
                    
                    # 分析结果
                    result_stats = analyze_batch_results(batch_key)
                    
                    return {
                        'version': version_name,
                        'batch_key': batch_key,
                        'total_time': total_time,
                        'total_minutes': total_time / 60,
                        'case_count': processed_count,
                        'avg_per_case': total_time / processed_count,
                        'success': True,
                        'stats': result_stats
                    }
                
                elif batch_status == 'failed':
                    print(f"  ❌ {version_name}处理失败")
                    return {'success': False, 'reason': 'batch_failed', 'version': version_name}
            
            else:
                print(f"    状态查询失败: {response.status_code}")
        
        except Exception as e:
            print(f"    状态查询异常: {e}")
    
    print(f"  ⏰ {version_name}处理超时")
    return {'success': False, 'reason': 'timeout', 'version': version_name}

def analyze_batch_results(batch_key):
    """分析批量处理结果"""
    print(f"  分析结果...")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取批次汇总
        cursor.execute("SELECT * FROM kiro_qc_batch_summary WHERE batch_key = %s", (batch_key,))
        summary = cursor.fetchone()
        
        if summary:
            return {
                'total_cases': summary['case_count'],
                'total_defects': summary['total_defect_count'],
                'avg_defects': float(summary['avg_defect']),
                'avg_score': float(summary['avg_score'])
            }
        else:
            return None
        
    finally:
        cursor.close()
        conn.close()

def compare_performance(optimized_result, standard_result):
    """比较性能"""
    print(f"\n" + "=" * 60)
    print("🚀 性能对比结果")
    print("=" * 60)
    
    if optimized_result and optimized_result.get('success') and standard_result and standard_result.get('success'):
        opt_time = optimized_result['total_minutes']
        std_time = standard_result['total_minutes']
        speedup = std_time / opt_time if opt_time > 0 else 0
        
        print(f"📊 处理时间对比:")
        print(f"   标准版本: {std_time:.1f}分钟")
        print(f"   优化版本: {opt_time:.1f}分钟")
        print(f"   性能提升: {speedup:.1f}倍")
        
        print(f"\n📋 质控效果对比:")
        if optimized_result.get('stats') and standard_result.get('stats'):
            opt_stats = optimized_result['stats']
            std_stats = standard_result['stats']
            
            print(f"   病案数: 标准{std_stats['total_cases']} vs 优化{opt_stats['total_cases']}")
            print(f"   缺陷数: 标准{std_stats['total_defects']} vs 优化{opt_stats['total_defects']}")
            print(f"   平均得分: 标准{std_stats['avg_score']:.2f} vs 优化{opt_stats['avg_score']:.2f}")
        
        print(f"\n🎯 目标达成情况:")
        if opt_time <= 5:
            print(f"   ✅ 优化版本达到5分钟目标！")
        else:
            print(f"   ⚠️  优化版本未达到5分钟目标，还需{opt_time-5:.1f}分钟")
        
        return speedup
    
    elif optimized_result and optimized_result.get('success'):
        print(f"📊 优化版本结果:")
        print(f"   处理时间: {optimized_result['total_minutes']:.1f}分钟")
        print(f"   平均每病案: {optimized_result['avg_per_case']:.2f}秒")
        
        if optimized_result['total_minutes'] <= 5:
            print(f"   ✅ 达到5分钟目标！")
        
        return None
    
    else:
        print(f"❌ 性能测试未完成，无法进行对比")
        return None

def main():
    """主函数"""
    print("医疗质控系统优化性能测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 清理之前的结果
    clear_previous_results()
    
    # 2. 测试优化版本
    optimized_result = test_optimized_batch()
    
    # 3. 清理结果，准备测试标准版本
    if optimized_result and optimized_result.get('success'):
        print(f"\n⏳ 等待30秒后测试标准版本...")
        time.sleep(30)
        clear_previous_results()
        
        # 4. 测试标准版本（对比）
        standard_result = test_standard_batch()
        
        # 5. 性能对比
        speedup = compare_performance(optimized_result, standard_result)
        
    else:
        print(f"\n⚠️  优化版本测试失败，跳过标准版本测试")
        speedup = None
    
    # 6. 生成总结报告
    print(f"\n" + "=" * 60)
    print("📋 测试总结")
    print("=" * 60)
    
    if optimized_result and optimized_result.get('success'):
        print(f"✅ 优化版本测试成功")
        print(f"   处理时间: {optimized_result['total_minutes']:.1f}分钟")
        print(f"   处理病案: {optimized_result['case_count']}个")
        
        if speedup:
            print(f"   性能提升: {speedup:.1f}倍")
        
        if optimized_result['total_minutes'] <= 5:
            print(f"   🎉 成功达到5分钟目标！")
        else:
            print(f"   💡 建议进一步优化:")
            print(f"      • 增加线程数")
            print(f"      • 优化数据库连接池")
            print(f"      • 增加服务器资源")
    
    else:
        print(f"❌ 优化版本测试失败")
        print(f"💡 建议检查:")
        print(f"   • 服务是否正常启动")
        print(f"   • 数据库连接是否正常")
        print(f"   • Redis缓存是否可用")

if __name__ == "__main__":
    main()