#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试 - 简化版(避免编码问题)
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
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute(f"SELECT COUNT(*) as count FROM d_mr WHERE B15 LIKE '{year}/%'")
        result = cursor.fetchone()
        return result['count'] if result else 0
    finally:
        cursor.close()
        conn.close()

def test_2023():
    year = 2023
    case_count = get_case_count(year)

    print("="*60)
    print(f"Performance Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Year: {year} | Cases: {case_count}")
    print("="*60)

    # Start batch processing
    print("\nStarting batch QC...")

    batch_request = {"periodType": "year", "year": year}
    start_time = time.time()

    try:
        response = requests.post(f"{BASE_URL}/qc/check/batch/optimized",
                               json=batch_request, timeout=10)

        if response.status_code != 200:
            print(f"Failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return

        result = response.json().get('data', {})
        batch_key = result.get('batchKey', '')
        print(f"OK - Batch started: {batch_key}")

    except Exception as e:
        print(f"Error: {e}")
        return

    # Monitor progress
    print("\nProgress:")
    print("-"*60)

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

                        print(f"{progress:3d}% | {elapsed:6.1f}s elapsed | "
                              f"{speed:5.1f} cases/s | ETA: {eta:6.1f}s")
                    last_progress = progress

                if batch_status == 'completed':
                    end_time = time.time()
                    total_time = end_time - start_time

                    print("-"*60)
                    print(f"\nCOMPLETED!")
                    print(f"\nPerformance Stats:")
                    print(f"  Total cases: {case_count}")
                    print(f"  Total time: {total_time:.1f}s ({total_time/60:.2f}min)")
                    print(f"  Avg speed: {case_count/total_time:.2f} cases/s")
                    print(f"  Per case: {total_time/case_count:.2f}s")

                    # Check target
                    target_time = 5 * 60
                    if total_time <= target_time:
                        print(f"\nTARGET ACHIEVED!")
                        print(f"  Target: {target_time}s (5min)")
                        print(f"  Actual: {total_time:.1f}s")
                        print(f"  Ahead: {target_time - total_time:.1f}s")
                    else:
                        print(f"\nTARGET MISSED")
                        print(f"  Target: {target_time}s (5min)")
                        print(f"  Actual: {total_time:.1f}s")
                        print(f"  Over: {total_time - target_time:.1f}s")

                    # Calculate speedup
                    old_time = 46 * 60
                    speedup = old_time / total_time
                    print(f"\nSpeedup:")
                    print(f"  Before: {old_time/60:.1f}min (estimated)")
                    print(f"  After: {total_time/60:.2f}min (actual)")
                    print(f"  Speedup: {speedup:.1f}x")

                    return

                elif batch_status == 'failed':
                    print(f"\nFAILED")
                    return

                if elapsed > 1800:
                    print(f"\nTIMEOUT (30min)")
                    return

                time.sleep(5)
            else:
                print(f"Status query failed: {response.status_code}")
                time.sleep(5)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    test_2023()
