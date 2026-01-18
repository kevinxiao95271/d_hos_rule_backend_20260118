import requests
import time

def check_service():
    """检查服务状态"""
    try:
        response = requests.get("http://localhost:4101/api/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def wait_for_service(max_wait=180):
    """等待服务启动"""
    print("🔄 等待Spring Boot服务启动...")
    
    wait_time = 0
    while wait_time < max_wait:
        if check_service():
            print(f"✅ 服务已启动! (等待时间: {wait_time}秒)")
            return True
        
        print(f"  ⏳ 等待中... ({wait_time}s/{max_wait}s)")
        time.sleep(10)
        wait_time += 10
    
    print(f"❌ 服务启动超时 ({max_wait}秒)")
    return False

def test_basic_apis():
    """测试基本API"""
    print("\n🧪 测试基本API...")
    
    apis = [
        ("健康检查", "GET", "/api/health"),
        ("字典列表", "GET", "/api/dict/types"),
        ("规则列表", "GET", "/api/qc/rules")
    ]
    
    for name, method, endpoint in apis:
        try:
            url = f"http://localhost:4101{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"  ✅ {name}: 正常")
            else:
                print(f"  ⚠️  {name}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {name}: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("Spring Boot服务状态检查")
    print("=" * 60)
    
    if wait_for_service():
        test_basic_apis()
        
        print("\n🎯 服务已就绪!")
        print("可以运行以下测试:")
        print("- python quick_ethnicity_test.py  # 测试民族字段修复")
        print("- python test_api.py              # 测试完整API")
        
    else:
        print("\n❌ 服务启动失败")
        print("请检查应用日志或手动启动服务")
    
    print("\n" + "=" * 60)