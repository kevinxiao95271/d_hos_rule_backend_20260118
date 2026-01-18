#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控批量质控进度
"""

import requests
import time
from datetime import datetime

BATCH_KEY = "2023_opt"
BASE_URL = "http://localhost:4101/api"

print("="*60)
print(f"监控批量质控: {BATCH_KEY}")
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)
print()

start_time = time.time()
last_progress = -1

while True:
    try:
        response = requests.get(f"{BASE_URL}/qc/batch/status/{BATCH_KEY}", timeout=10)

        if response.status_code == 200:
            data = response.json().get('data', {})
            progress = data.get('progress', 0)
            status = data.get('status', 'unknown')
            case_count = data.get('caseCount', 0)

            elapsed = time.time() - start_time

            # 只在进度变化时打印
            if progress != last_progress:
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"[{current_time}] 进度: {progress:3d}% | 已处理: {case_count} | 已用时: {elapsed:6.1f}秒")
                last_progress = progress

            if status == 'completed':
                print()
                print("="*60)
                print("质控完成!")
                print("="*60)
                print(f"总病案数: {case_count}")
                print(f"总耗时: {elapsed:.1f}秒 = {elapsed/60:.2f}分钟")
                if case_count > 0:
                    print(f"平均速度: {elapsed/case_count:.3f}秒/条 = {case_count/elapsed:.1f}条/秒")
                print(f"总缺陷: {data.get('totalDefectCount', 0)}")
                print(f"平均分: {data.get('avgScore', 0)}")

                # 检查是否达标
                target = 5 * 60  # 5分钟
                if elapsed <= target:
                    print(f"\n✓ 达成目标! (目标{target}秒, 实际{elapsed:.1f}秒, 提前{target-elapsed:.1f}秒)")
                else:
                    print(f"\n✗ 超时 (目标{target}秒, 实际{elapsed:.1f}秒, 超时{elapsed-target:.1f}秒)")
                break

            elif status == 'failed':
                print()
                print("质控失败!")
                break

            # 超时检查 (30分钟)
            if elapsed > 1800:
                print()
                print("超时 (30分钟)")
                break

        time.sleep(2)

    except Exception as e:
        print(f"错误: {e}")
        time.sleep(5)

print()
print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)
