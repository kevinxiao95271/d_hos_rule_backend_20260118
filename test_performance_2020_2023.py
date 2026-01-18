#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试：2020年和2023年数据质控
测试场景：
1. 单个病案检查
2. 按月批量检查
3. 记录执行时间和结果
"""

import pymysql
import requests
import json
import time
from datetime import datetime
from collections import defaultdict

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

BASE_URL = "http://localhost:4101"

def get_data_statistics():
    """获取数据统计信息"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    print("\n" + "="*100)
    print("数据统计")
    print("="*100)
    
    # 2020年数据统计
    cursor.execute("""
        SELECT 
            YEAR(B15) as year,
            MONTH(B15) as month,
            COUNT(*) as count
        FROM d_mr
        WHERE YEAR(B15) = 2020
        GROUP BY YEAR(B15), MONTH(B15)
        ORDER BY month
    """)
    data_2020 = cursor.fetchall()
    
    print("\n2020年数据分布（按月）:")
    total_2020 = 0
    for row in data_2020:
        print(f"  {row['year']}-{row['month']:02d}: {row['count']:,} 条")
        total_2020 += row['count']
    print(f"  总计: {total_2020:,} 条")
    
    # 2023年数据统计
    cursor.execute("""
        SELECT 
            YEAR(B15) as year,
            MONTH(B15) as month,
            COUNT(*) as count
        FROM d_mr
        WHERE YEAR(B15) = 2023
        GROUP BY YEAR(B15), MONTH(B15)
        ORDER BY month
    """)
    data_2023 = cursor.fetchall()
    
    print("\n2023年数据分布（按月）:")
    total_2023 = 0
    for row in data_2023:
        print(f"  {row['year']}-{row['month']:02d}: {row['count']:,} 条")
        total_2023 += row['count']
    print(f"  总计: {total_2023:,} 条")
    
    conn.close()
    
    return data_2020, data_2023

def get_sample_cases(year, month, limit=5):
    """获取指定年月的样本病案"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute(f"""
        SELECT A48, A49, B15
        FROM d_mr
        WHERE YEAR(B15) = {year} AND MONTH(B15) = {month}
        LIMIT {limit}
    """)
    
    cases = cursor.fetchall()
    conn.close()
    return cases

def test_single_case(a48, a49):
    """测试单个病案"""
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/qc/check",
            json={"a48": a48, "a49": a49},
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                result = data['data']
                return {
                    'success': True,
                    'elapsed': elapsed,
                    'defect_count': result.get('defectCount', 0),
                    'total_deduct': result.get('totalDeduct', 0),
                    'final_score': result.get('finalScore', 100)
                }
        
        return {
            'success': False,
            'elapsed': elapsed,
            'error': f"HTTP {response.status_code}"
        }
    except Exception as e:
        return {
            'success': False,
            'elapsed': 0,
            'error': str(e)
        }

def test_batch_month(year, month):
    """测试按月批量检查"""
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/qc/batch/month",
            json={
                "year": year,
                "month": month
            },
            timeout=300  # 5分钟超时
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                result = data['data']
                return {
                    'success': True,
                    'elapsed': elapsed,
                    'batch_key': result.get('batchKey', ''),
                    'case_count': result.get('caseCount', 0),
                    'status': result.get('status', '')
                }
        
        return {
            'success': False,
            'elapsed': elapsed,
            'error': f"HTTP {response.status_code}"
        }
    except Exception as e:
        return {
            'success': False,
            'elapsed': 0,
            'error': str(e)
        }

def check_batch_status(batch_key, max_wait=300):
    """检查批量任务状态"""
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(
                f"{BASE_URL}/api/qc/batch/status/{batch_key}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['code'] == 200:
                    result = data['data']
                    status = result.get('status', '')
                    progress = result.get('progress', 0)
                    
                    if status == 'completed':
                        return {
                            'success': True,
                            'elapsed': time.time() - start_time,
                            'case_count': result.get('caseCount', 0),
                            'total_defect_count': result.get('totalDefectCount', 0),
                            'avg_defect': result.get('avgDefect', 0),
                            'avg_score': result.get('avgScore', 100)
                        }
                    elif status == 'failed':
                        return {
                            'success': False,
                            'elapsed': time.time() - start_time,
                            'error': 'Batch processing failed'
                        }
                    
                    # 继续等待
                    print(f"    进度: {progress}%", end='\r')
                    time.sleep(2)
            
        except Exception as e:
            print(f"    检查状态失败: {str(e)}")
            time.sleep(2)
    
    return {
        'success': False,
        'elapsed': time.time() - start_time,
        'error': 'Timeout waiting for batch completion'
    }

def main():
    """主函数"""
    print("="*100)
    print("  质控系统性能测试 - 2020年和2023年数据")
    print(f"  测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)
    
    # 获取数据统计
    data_2020, data_2023 = get_data_statistics()
    
    # ========================================
    # 测试1：单个病案检查
    # ========================================
    print("\n" + "="*100)
    print("测试1：单个病案检查")
    print("="*100)
    
    test_cases = []
    
    # 2020年样本
    if data_2020:
        year = 2020
        month = data_2020[0]['month']
        cases = get_sample_cases(year, month, 3)
        for case in cases:
            test_cases.append({
                'year': year,
                'month': month,
                'a48': case['A48'],
                'a49': case['A49'],
                'b15': case['B15']
            })
    
    # 2023年样本
    if data_2023:
        year = 2023
        month = data_2023[0]['month']
        cases = get_sample_cases(year, month, 3)
        for case in cases:
            test_cases.append({
                'year': year,
                'month': month,
                'a48': case['A48'],
                'a49': case['A49'],
                'b15': case['B15']
            })
    
    single_case_results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试病案 {i}/{len(test_cases)}")
        print(f"  年份: {case['year']}")
        print(f"  病案: A48={case['a48']}, A49={case['a49']}")
        print(f"  出院日期: {case['b15']}")
        
        result = test_single_case(case['a48'], case['a49'])
        
        if result['success']:
            print(f"  ✓ 检查完成")
            print(f"    耗时: {result['elapsed']:.2f}秒")
            print(f"    缺陷数: {result['defect_count']}")
            print(f"    扣分: {result['total_deduct']}")
            print(f"    得分: {result['final_score']}")
            single_case_results.append(result)
        else:
            print(f"  ✗ 检查失败: {result.get('error', 'Unknown error')}")
    
    # 单个病案统计
    if single_case_results:
        avg_time = sum(r['elapsed'] for r in single_case_results) / len(single_case_results)
        avg_defects = sum(r['defect_count'] for r in single_case_results) / len(single_case_results)
        avg_score = sum(r['final_score'] for r in single_case_results) / len(single_case_results)
        
        print("\n单个病案检查统计:")
        print(f"  成功数: {len(single_case_results)}/{len(test_cases)}")
        print(f"  平均耗时: {avg_time:.2f}秒")
        print(f"  平均缺陷数: {avg_defects:.1f}")
        print(f"  平均得分: {avg_score:.2f}")
    
    # ========================================
    # 测试2：按月批量检查
    # ========================================
    print("\n" + "="*100)
    print("测试2：按月批量检查")
    print("="*100)
    
    batch_tests = []
    
    # 选择2020年第一个月
    if data_2020:
        batch_tests.append({
            'year': 2020,
            'month': data_2020[0]['month'],
            'expected_count': data_2020[0]['count']
        })
    
    # 选择2023年第一个月
    if data_2023:
        batch_tests.append({
            'year': 2023,
            'month': data_2023[0]['month'],
            'expected_count': data_2023[0]['count']
        })
    
    batch_results = []
    
    for i, test in enumerate(batch_tests, 1):
        print(f"\n批量测试 {i}/{len(batch_tests)}")
        print(f"  时间段: {test['year']}-{test['month']:02d}")
        print(f"  预期病案数: {test['expected_count']:,}")
        
        # 启动批量任务
        print(f"  启动批量检查...")
        result = test_batch_month(test['year'], test['month'])
        
        if result['success']:
            batch_key = result['batch_key']
            print(f"  ✓ 任务已启动")
            print(f"    批次键: {batch_key}")
            print(f"    启动耗时: {result['elapsed']:.2f}秒")
            
            # 等待任务完成
            print(f"  等待任务完成...")
            status_result = check_batch_status(batch_key)
            
            if status_result['success']:
                print(f"\n  ✓ 批量检查完成")
                print(f"    总耗时: {status_result['elapsed']:.2f}秒")
                print(f"    病案数: {status_result['case_count']:,}")
                print(f"    总缺陷数: {status_result['total_defect_count']:,}")
                print(f"    平均缺陷: {status_result['avg_defect']:.2f}")
                print(f"    平均得分: {status_result['avg_score']:.2f}")
                
                # 计算性能指标
                if status_result['case_count'] > 0:
                    cases_per_second = status_result['case_count'] / status_result['elapsed']
                    print(f"    处理速度: {cases_per_second:.2f} 病案/秒")
                
                batch_results.append({
                    'year': test['year'],
                    'month': test['month'],
                    'elapsed': status_result['elapsed'],
                    'case_count': status_result['case_count'],
                    'total_defect_count': status_result['total_defect_count'],
                    'avg_defect': status_result['avg_defect'],
                    'avg_score': status_result['avg_score']
                })
            else:
                print(f"  ✗ 任务失败: {status_result.get('error', 'Unknown error')}")
        else:
            print(f"  ✗ 启动失败: {result.get('error', 'Unknown error')}")
    
    # ========================================
    # 测试总结
    # ========================================
    print("\n" + "="*100)
    print("测试总结")
    print("="*100)
    
    print("\n1. 单个病案检查性能:")
    if single_case_results:
        print(f"   - 测试数量: {len(single_case_results)} 个病案")
        print(f"   - 平均耗时: {avg_time:.2f} 秒/病案")
        print(f"   - 平均缺陷: {avg_defects:.1f} 个/病案")
        print(f"   - 平均得分: {avg_score:.2f} 分")
    else:
        print("   - 无成功测试")
    
    print("\n2. 批量检查性能:")
    if batch_results:
        for result in batch_results:
            print(f"\n   {result['year']}-{result['month']:02d}:")
            print(f"   - 病案数: {result['case_count']:,}")
            print(f"   - 总耗时: {result['elapsed']:.2f} 秒")
            print(f"   - 处理速度: {result['case_count']/result['elapsed']:.2f} 病案/秒")
            print(f"   - 总缺陷数: {result['total_defect_count']:,}")
            print(f"   - 平均缺陷: {result['avg_defect']:.2f}")
            print(f"   - 平均得分: {result['avg_score']:.2f}")
    else:
        print("   - 无成功测试")
    
    print("\n3. 系统评估:")
    if single_case_results and batch_results:
        # 估算处理大量数据的时间
        total_cases_2020 = sum(row['count'] for row in data_2020)
        total_cases_2023 = sum(row['count'] for row in data_2023)
        
        if batch_results:
            avg_speed = sum(r['case_count']/r['elapsed'] for r in batch_results) / len(batch_results)
            
            est_time_2020 = total_cases_2020 / avg_speed / 60  # 分钟
            est_time_2023 = total_cases_2023 / avg_speed / 60  # 分钟
            
            print(f"   - 平均处理速度: {avg_speed:.2f} 病案/秒")
            print(f"   - 处理2020年全年预计: {est_time_2020:.1f} 分钟 ({total_cases_2020:,} 病案)")
            print(f"   - 处理2023年全年预计: {est_time_2023:.1f} 分钟 ({total_cases_2023:,} 病案)")
    
    # 保存测试结果
    test_report = {
        'test_time': datetime.now().isoformat(),
        'data_statistics': {
            '2020': [dict(row) for row in data_2020],
            '2023': [dict(row) for row in data_2023]
        },
        'single_case_results': single_case_results,
        'batch_results': batch_results
    }
    
    with open('performance_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(test_report, f, ensure_ascii=False, indent=2, default=str)
    
    print("\n✓ 测试报告已保存到: performance_test_report.json")
    
    print("\n" + "="*100)
    print("测试完成！")
    print("="*100)

if __name__ == "__main__":
    main()
