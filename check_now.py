import requests

response = requests.get('http://localhost:4101/api/qc/batch/status/2023_opt')
data = response.json().get('data', {})

print(f'进度: {data.get("progress", 0)}%')
print(f'状态: {data.get("status", "unknown")}')
print(f'处理数: {data.get("caseCount", 0)}')

# Also check if it's completed
if data.get('status') == 'completed':
    print('🎉 处理完成！')
elif data.get('status') == 'processing':
    print('⏳ 正在处理中...')
elif data.get('status') == 'failed':
    print('❌ 处理失败')