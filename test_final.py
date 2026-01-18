import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:4101/api"

print("="*60)
print(f"Starting Optimized Performance Test")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

# Start batch
print("\nStarting 2023 batch processing...")
response = requests.post(f"{BASE_URL}/qc/check/batch/optimized",
                        json={"periodType": "year", "year": 2023},
                        timeout=10)

if response.status_code == 200:
    data = response.json().get('data', {})
    batch_key = data.get('batchKey', '')
    case_count = data.get('caseCount', 0)
    print(f"OK - Batch started: {batch_key}")
    print(f"Cases: {case_count}")

    # Monitor
    print("\nMonitoring progress...")
    start_time = time.time()
    last_progress = -1

    while True:
        response = requests.get(f"{BASE_URL}/qc/batch/status/{batch_key}", timeout=10)
        if response.status_code == 200:
            status = response.json().get('data', {})
            progress = status.get('progress', 0)
            batch_status = status.get('status', '')
            elapsed = time.time() - start_time

            if progress != last_progress:
                print(f"[{int(elapsed)}s] {progress}% | {batch_status}")
                last_progress = progress

            if batch_status == 'completed':
                print(f"\n{'='*60}")
                print(f"COMPLETED!")
                print(f"Total Time: {elapsed:.1f}s ({elapsed/60:.2f}min)")
                print(f"Speed: {case_count/elapsed:.2f} cases/s")
                print(f"Per Case: {elapsed/case_count:.2f}s")

                target = 5 * 60
                if elapsed <= target:
                    print(f"\nTARGET ACHIEVED!")
                    print(f"Target: {target}s | Actual: {elapsed:.1f}s")
                    print(f"Ahead by: {target-elapsed:.1f}s")
                else:
                    print(f"\nTarget: {target}s | Actual: {elapsed:.1f}s")
                    print(f"Over by: {elapsed-target:.1f}s")

                # Calculate speedup
                old_time = 46 * 60
                speedup = old_time / elapsed
                print(f"\nSpeedup: {speedup:.1f}x")
                print(f"Before: {old_time/60:.1f}min | After: {elapsed/60:.2f}min")
                break

            if batch_status == 'failed':
                print("\nFAILED!")
                break

            if elapsed > 600:  # 10min timeout
                print("\nTimeout!")
                break

            time.sleep(3)
        else:
            print(f"Error: {response.status_code}")
            break
else:
    print(f"Failed to start: {response.status_code}")
    print(response.text)
