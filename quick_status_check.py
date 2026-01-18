import requests
import time

# Wait 30 seconds then check status
time.sleep(30)

response = requests.get('http://localhost:4101/api/qc/batch/status/2023_opt')
data = response.json().get('data', {})

progress = data.get('progress', 0)
status = data.get('status', 'unknown')
case_count = data.get('caseCount', 0)

print(f'进度: {progress}%')
print(f'状态: {status}')
print(f'处理数: {case_count}')
print(f'完整响应: {data}')