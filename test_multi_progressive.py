#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Case Performance Test - Progressive Testing
Tests with increasing batch sizes: 1, 5, 10, 20, 50
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:4101/api"

def test_multi_cases(year, limit):
    """Test multi-case API with specified limit"""
    print(f"\n{'='*60}")
    print(f"Testing {limit} cases - {datetime.now().strftime('%H:%M:%S')}")
    print('='*60)

    start_time = time.time()

    try:
        response = requests.post(
            f"{BASE_URL}/qc/check/multi",
            json={"year": year, "limit": limit},
            timeout=300
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json().get('data', {})
            case_count = data.get('caseCount', 0)
            total_time = data.get('totalTime', 0)
            avg_time = data.get('avgTimePerCase', 0)
            total_defects = data.get('totalDefects', 0)
            avg_score = data.get('avgScore', 0)

            print(f"\nResults:")
            print(f"  Cases processed: {case_count}")
            print(f"  Total time: {total_time/1000:.2f}s")
            print(f"  Avg per case: {avg_time:.2f}ms = {avg_time/1000:.3f}s")
            print(f"  Total defects: {total_defects}")
            print(f"  Avg score: {avg_score}")
            print(f"  API response time: {elapsed:.2f}s")

            # Calculate throughput
            throughput = case_count / (total_time / 1000) if total_time > 0 else 0
            print(f"\nPerformance:")
            print(f"  Throughput: {throughput:.2f} cases/s")
            print(f"  Speed: {60 * throughput:.1f} cases/min")

            # Estimate time for full 2023 dataset (96 cases)
            if avg_time > 0:
                est_96_cases = (avg_time / 1000) * 96
                print(f"\nEstimated time for 96 cases: {est_96_cases:.1f}s = {est_96_cases/60:.2f}min")

                # Check against target
                target = 5 * 60  # 5 minutes
                if est_96_cases <= target:
                    print(f"  Status: TARGET MET (under {target/60}min)")
                else:
                    print(f"  Status: Target missed (over {target/60}min)")

            return {
                'success': True,
                'case_count': case_count,
                'total_time': total_time,
                'avg_time': avg_time,
                'throughput': throughput
            }
        else:
            print(f"  ERROR: HTTP {response.status_code}")
            print(f"  Response: {response.text}")
            return {'success': False}

    except Exception as e:
        print(f"  EXCEPTION: {e}")
        return {'success': False}

def main():
    year = 2023
    test_sizes = [1, 5, 10, 20, 50]

    print("="*60)
    print("Multi-Case Progressive Performance Test")
    print(f"Year: {year}")
    print(f"Test sizes: {test_sizes}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    results = []

    for limit in test_sizes:
        result = test_multi_cases(year, limit)
        if result['success']:
            results.append(result)
        time.sleep(2)  # Brief pause between tests

    # Summary
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"\n{'Cases':<8} {'Total(s)':<10} {'Avg(ms)':<10} {'Cases/s':<10}")
    print('-'*60)

    for i, limit in enumerate(test_sizes):
        if i < len(results) and results[i]['success']:
            r = results[i]
            print(f"{r['case_count']:<8} {r['total_time']/1000:<10.2f} {r['avg_time']:<10.2f} {r['throughput']:<10.2f}")

    print('\n' + '='*60)
    print("Test completed at", datetime.now().strftime('%H:%M:%S'))
    print('='*60)

if __name__ == "__main__":
    main()
