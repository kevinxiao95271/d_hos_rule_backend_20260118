#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化验证测试脚本
测试优化前后的性能对比
"""

import requests
import time
import pymysql
from datetime import datetime
import json

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

BASE_URL = "http://localhost:4101/api"

def check_optimization_applied():
    """检查优化是否已应用"""
    print("=== 检查优化状态 ===")

    file_path = "src/main/java/com/medical/qc/service/BatchQcServiceOptimized.java"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        checks = {
            "并行处理": "processBatchRecordsParallel" in content and "第83行附近",
            "动态线程池": "Runtime.getRuntime().availableProcessors()" in content,
            "批次大小200": "DB_BATCH_SIZE = 200" in content
        }

        print("\n优化检查结果:")
        all_applied = True
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
            if not result:
                all_applied = False

        if all_applied:
            print("\n✅ 所有优化已应用")
        else:
            print("\n⚠️  部分优化未应用,请运行: python quick_performance_boost.py")

        return all_applied

    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
        return False

def get_case_count(year):
    """获取指定年份的病案数量"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute(f"""
            SELECT COUNT(*) as count
            FROM d_mr
            WHERE B15 LIKE '{year}/%'
        """)
        result = cursor.fetchone()
        return result['count'] if result else 0
    finally:
        cursor.close()
        conn.close()

def test_batch_performance(year, use_optimized=True):
    """测试批量处理性能"""

    case_count = get_case_count(year)

    print(f"\n{'='*60}")
    print(f"测试 {year}年数据")
    print(f"病案数量: {case_count}")
    print(f"使用接口: {'优化版' if use_optimized else '标准版'}")
    print(f"{'='*60}")

    # 清理之前的结果
    print("\n1. 清理之前的质控结果...")
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        cursor.execute(f"""
            DELETE FROM kiro_qc_case_result
            WHERE check_year = {year}
        """)
        cursor.execute(f"""
            DELETE FROM kiro_qc_defect_detail
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49)
                FROM d_mr
                WHERE B15 LIKE '{year}/%'
            )
        """)
        conn.commit()
        print("✅ 清理完成")
    finally:
        cursor.close()
        conn.close()

    # 启动批量处理
    print("\n2. 启动批量处理...")

    endpoint = "/qc/check/batch/optimized" if use_optimized else "/qc/check/batch"

    batch_request = {
        "periodType": "year",
        "year": year
    }

    start_time = time.time()

    try:
        response = requests.post(f"{BASE_URL}{endpoint}",
                               json=batch_request,
                               timeout=10)

        if response.status_code != 200:
            print(f"❌ 批量任务启动失败: {response.status_code}")
            return None

        result = response.json().get('data', {})
        batch_key = result.get('batchKey', '')

        print(f"✅ 批量任务已启动")
        print(f"   批次键: {batch_key}")
        print(f"   病案数: {case_count}")

    except Exception as e:
        print(f"❌ 批量任务启动异常: {e}")
        return None

    # 监控进度
    print("\n3. 监控处理进度...")

    last_progress = 0
    last_update_time = start_time
    samples = []

    while True:
        try:
            response = requests.get(f"{BASE_URL}/qc/batch/status/{batch_key}", timeout=10)

            if response.status_code == 200:
                status = response.json().get('data', {})

                progress = status.get('progress', 0)
                batch_status = status.get('status', 'unknown')

                current_time = time.time()
                elapsed = current_time - start_time

                if progress != last_progress:
                    # 计算处理速度
                    if progress > 0:
                        processed = (case_count * progress) / 100
                        speed = processed / elapsed if elapsed > 0 else 0

                        # 估算剩余时间
                        remaining = case_count - processed
                        eta = remaining / speed if speed > 0 else 0

                        print(f"   进度: {progress:3d}% | "
                              f"已用时: {elapsed:6.1f}秒 | "
                              f"速度: {speed:5.1f}病案/秒 | "
                              f"预计剩余: {eta:6.1f}秒")

                        samples.append({
                            'progress': progress,
                            'elapsed': elapsed,
                            'speed': speed
                        })

                    last_progress = progress
                    last_update_time = current_time

                if batch_status == 'completed':
                    end_time = time.time()
                    total_time = end_time - start_time

                    print(f"\n✅ 批量处理完成!")
                    print(f"{'='*60}")
                    print(f"性能统计:")
                    print(f"  总病案数: {case_count}")
                    print(f"  总耗时: {total_time:.1f}秒 ({total_time/60:.2f}分钟)")
                    print(f"  平均速度: {case_count/total_time:.2f}病案/秒")
                    print(f"  单病案时间: {total_time/case_count:.2f}秒")
                    print(f"{'='*60}")

                    return {
                        'year': year,
                        'case_count': case_count,
                        'total_time': total_time,
                        'avg_speed': case_count/total_time,
                        'per_case_time': total_time/case_count,
                        'samples': samples,
                        'optimized': use_optimized
                    }

                elif batch_status == 'failed':
                    print(f"\n❌ 批量处理失败")
                    return None

                # 超时检查(30分钟)
                if elapsed > 1800:
                    print(f"\n⚠️  处理超时(30分钟)")
                    return None

                time.sleep(5)  # 每5秒检查一次

            else:
                print(f"⚠️  状态查询失败: {response.status_code}")
                time.sleep(5)

        except Exception as e:
            print(f"⚠️  状态查询异常: {e}")
            time.sleep(5)

def compare_performance(result_optimized, result_standard):
    """对比优化前后的性能"""

    print("\n" + "="*60)
    print("性能对比分析")
    print("="*60)

    if not result_standard:
        print("\n⚠️  标准版本未测试,无法对比")
        return

    if not result_optimized:
        print("\n⚠️  优化版本未测试,无法对比")
        return

    speedup = result_standard['total_time'] / result_optimized['total_time']
    time_saved = result_standard['total_time'] - result_optimized['total_time']

    print(f"\n📊 测试数据:")
    print(f"  年份: {result_optimized['year']}")
    print(f"  病案数: {result_optimized['case_count']}")

    print(f"\n⏱️  处理时间:")
    print(f"  标准版: {result_standard['total_time']:.1f}秒 ({result_standard['total_time']/60:.2f}分钟)")
    print(f"  优化版: {result_optimized['total_time']:.1f}秒 ({result_optimized['total_time']/60:.2f}分钟)")
    print(f"  节省: {time_saved:.1f}秒 ({time_saved/60:.2f}分钟)")

    print(f"\n🚀 性能提升:")
    print(f"  速度提升: {speedup:.2f}倍")
    print(f"  单病案时间: {result_standard['per_case_time']:.2f}秒 → {result_optimized['per_case_time']:.2f}秒")

    print(f"\n📈 处理速度:")
    print(f"  标准版: {result_standard['avg_speed']:.2f}病案/秒")
    print(f"  优化版: {result_optimized['avg_speed']:.2f}病案/秒")

    # 性能评级
    if speedup >= 20:
        grade = "🌟🌟🌟 优秀"
    elif speedup >= 10:
        grade = "🌟🌟 良好"
    elif speedup >= 5:
        grade = "🌟 一般"
    else:
        grade = "⚠️  需要进一步优化"

    print(f"\n🎯 性能评级: {grade}")

    # 目标达成情况
    target_time = 5 * 60  # 5分钟
    if result_optimized['total_time'] <= target_time:
        print(f"\n✅ 已达成目标(5分钟内完成)!")
    else:
        print(f"\n⚠️  未达成目标")
        print(f"   目标时间: {target_time}秒 (5分钟)")
        print(f"   实际时间: {result_optimized['total_time']:.1f}秒")
        print(f"   差距: {result_optimized['total_time'] - target_time:.1f}秒")

def save_test_result(result):
    """保存测试结果"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"performance_test_{result['year']}_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n💾 测试结果已保存: {filename}")

def main():
    print("="*60)
    print("医疗质控系统 - 性能优化验证测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 检查优化是否应用
    if not check_optimization_applied():
        print("\n⚠️  请先运行优化脚本:")
        print("   python quick_performance_boost.py")
        return

    print("\n请选择测试模式:")
    print("1. 快速测试 (2020年数据,病案较少)")
    print("2. 完整测试 (2023年数据,96个病案)")
    print("3. 性能对比 (标准版 vs 优化版)")

    choice = input("\n请输入选择 (1/2/3): ").strip()

    if choice == '1':
        # 快速测试
        result = test_batch_performance(2020, use_optimized=True)
        if result:
            save_test_result(result)

    elif choice == '2':
        # 完整测试
        result = test_batch_performance(2023, use_optimized=True)
        if result:
            save_test_result(result)

    elif choice == '3':
        # 性能对比
        print("\n开始性能对比测试...")
        print("\n第1步: 测试标准版本")
        result_standard = test_batch_performance(2020, use_optimized=False)

        if result_standard:
            print("\n第2步: 测试优化版本")
            result_optimized = test_batch_performance(2020, use_optimized=True)

            if result_optimized:
                compare_performance(result_optimized, result_standard)

                # 保存对比结果
                comparison = {
                    'standard': result_standard,
                    'optimized': result_optimized,
                    'speedup': result_standard['total_time'] / result_optimized['total_time']
                }

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"performance_comparison_{timestamp}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(comparison, f, indent=2, ensure_ascii=False)
                print(f"\n💾 对比结果已保存: {filename}")

    else:
        print("\n❌ 无效选择")

if __name__ == "__main__":
    main()
