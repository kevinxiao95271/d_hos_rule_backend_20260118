#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试优化效果
"""

import requests
import time
import pymysql
from datetime import datetime

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

BASE_URL = "http://localhost:4101/api"

def get_case_count(year):
    """获取指定年份病案数"""
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

def test_2023_batch():
    """测试2023年批量处理"""

    year = 2023
    case_count = get_case_count(year)

    print("=" * 60)
    print(f"医疗质控系统 - 优化效果测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试年份: {year}")
    print(f"病案数量: {case_count}")
    print("=" * 60)

    # 启动批量处理
    print("\n启动批量质控...")

    batch_request = {
        "periodType": "year",
        "year": year
    }

    start_time = time.time()

    try:
        response = requests.post(f"{BASE_URL}/qc/check/batch/optimized",
                               json=batch_request,
                               timeout=10)

        if response.status_code != 200:
            print(f"启动失败: HTTP {response.status_code}")
            print(f"响应: {response.text}")
            return

        result = response.json().get('data', {})
        batch_key = result.get('batchKey', '')

        print(f"✓ 批量任务已启动")
        print(f"  批次键: {batch_key}")

    except Exception as e:
        print(f"启动异常: {e}")
        return

    # 监控进度
    print("\n监控处理进度:")
    print("-" * 60)

    last_progress = 0

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
                    if progress > 0:
                        processed = (case_count * progress) / 100
                        speed = processed / elapsed if elapsed > 0 else 0
                        remaining = case_count - processed
                        eta = remaining / speed if speed > 0 else 0

                        print(f"进度: {progress:3d}% | 用时: {elapsed:6.1f}秒 | "
                              f"速度: {speed:5.1f}病案/秒 | 预计剩余: {eta:6.1f}秒")

                    last_progress = progress

                if batch_status == 'completed':
                    end_time = time.time()
                    total_time = end_time - start_time

                    print("-" * 60)
                    print(f"\n✓ 批量处理完成!")
                    print("\n性能统计:")
                    print(f"  总病案数: {case_count}")
                    print(f"  总耗时: {total_time:.1f}秒 ({total_time/60:.2f}分钟)")
                    print(f"  平均速度: {case_count/total_time:.2f}病案/秒")
                    print(f"  单病案时间: {total_time/case_count:.2f}秒")

                    # 性能评级
                    target_time = 5 * 60  # 5分钟
                    if total_time <= target_time:
                        grade = "优秀"
                        print(f"\n✓ 已达成目标 (5分钟内完成)!")
                        print(f"  目标时间: {target_time}秒")
                        print(f"  实际时间: {total_time:.1f}秒")
                        print(f"  提前完成: {target_time - total_time:.1f}秒")
                    else:
                        grade = "待优化"
                        print(f"\n× 未达成目标")
                        print(f"  目标时间: {target_time}秒")
                        print(f"  实际时间: {total_time:.1f}秒")
                        print(f"  超时: {total_time - target_time:.1f}秒")

                    print(f"\n性能评级: {grade}")

                    # 计算性能提升
                    old_time = 46 * 60  # 优化前预估46分钟
                    speedup = old_time / total_time
                    print(f"\n性能提升:")
                    print(f"  优化前预估: {old_time/60:.1f}分钟")
                    print(f"  优化后实际: {total_time/60:.2f}分钟")
                    print(f"  提升倍数: {speedup:.1f}倍")

                    return

                elif batch_status == 'failed':
                    print(f"\n× 批量处理失败")
                    return

                # 超时检查(30分钟)
                if elapsed > 1800:
                    print(f"\n× 处理超时(30分钟)")
                    return

                time.sleep(5)

            else:
                print(f"状态查询失败: HTTP {response.status_code}")
                time.sleep(5)

        except Exception as e:
            print(f"状态查询异常: {e}")
            time.sleep(5)

if __name__ == "__main__":
    test_2023_batch()
