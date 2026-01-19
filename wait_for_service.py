import requests
import time

def check_service():
    try:
        response = requests.get("http://localhost:4101/api/qc/status", timeout=3)
        return response.status_code == 200
    except:
        return False

print("等待服务启动...")
max_wait = 180
wait_time = 0

while wait_time < max_wait:
    if check_service():
        print(f"✅ 服务已启动! (等待时间: {wait_time}秒)")
        break
    print(f"⏳ 等待中... ({wait_time}s/{max_wait}s)")
    time.sleep(10)
    wait_time += 10
else:
    print("❌ 服务启动超时")
    exit(1)

print("🎯 准备测试cross规则...")