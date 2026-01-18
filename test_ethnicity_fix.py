import requests
import json
import time

print("=" * 80)
print("测试民族字段修复")
print("=" * 80)

base_url = "http://localhost:4101"

# 1. 检查服务状态
print("\n1. 检查服务状态...")
try:
    response = requests.get(f"{base_url}/api/health", timeout=5)
    if response.status_code == 200:
        print("  ✅ 服务运行正常")
    else:
        print(f"  ⚠️  服务响应异常: {response.status_code}")
except Exception as e:
    print(f"  ❌ 服务连接失败: {e}")
    print("  请先启动Spring Boot应用")
    exit(1)

# 2. 运行小批量质控测试
print("\n2. 运行小批量质控测试...")
try:
    payload = {
        "year": 2023,
        "limit": 10  # 只测试10条记录
    }
    
    response = requests.post(
        f"{base_url}/api/qc/batch",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print("  ✅ 质控批次启动成功")
        print(f"  批次ID: {result.get('batchKey', 'N/A')}")
        
        # 等待批次完成
        print("  等待批次完成...")
        time.sleep(5)
        
    else:
        print(f"  ❌ 质控批次启动失败: {response.status_code}")
        print(f"  响应: {response.text}")
        
except Exception as e:
    print(f"  ❌ 质控批次请求失败: {e}")

# 3. 检查民族字段的质控结果
print("\n3. 检查民族字段的质控结果...")
try:
    # 获取字段统计
    response = requests.get(f"{base_url}/api/qc/field-stats", timeout=10)
    
    if response.status_code == 200:
        stats = response.json()
        
        # 查找民族相关的统计
        ethnicity_found = False
        for field_stat in stats:
            field_code = field_stat.get('fieldCode', '')
            field_name = field_stat.get('fieldName', '')
            
            if 'A19C' in field_code or '民族' in field_name:
                ethnicity_found = True
                print(f"  ✅ 找到民族字段统计:")
                print(f"    字段代码: {field_code}")
                print(f"    字段名称: {field_name}")
                print(f"    缺陷数量: {field_stat.get('defectCount', 0)}")
                print(f"    规则数量: {field_stat.get('ruleCount', 0)}")
                break
        
        if not ethnicity_found:
            print("  ✅ 未发现民族字段缺陷 (说明数据正确)")
            
    else:
        print(f"  ⚠️  无法获取字段统计: {response.status_code}")
        
except Exception as e:
    print(f"  ❌ 字段统计请求失败: {e}")

# 4. 检查具体的缺陷详情
print("\n4. 检查具体的缺陷详情...")
try:
    # 获取病案445583_1的缺陷详情
    response = requests.get(
        f"{base_url}/api/qc/case-defects/445583_1",
        timeout=10
    )
    
    if response.status_code == 200:
        defects = response.json()
        
        ethnicity_defects = []
        for defect in defects:
            rule_code = defect.get('ruleCode', '')
            field_code = defect.get('fieldCode', '')
            
            if 'RC035' in rule_code or 'A19C' in field_code or '民族' in defect.get('fieldName', ''):
                ethnicity_defects.append(defect)
        
        if ethnicity_defects:
            print(f"  发现 {len(ethnicity_defects)} 个民族相关缺陷:")
            for defect in ethnicity_defects:
                print(f"    规则: {defect.get('ruleCode')}")
                print(f"    字段: {defect.get('fieldCode')} ({defect.get('fieldName')})")
                print(f"    实际值: '{defect.get('actualValue')}'")
                print(f"    期望值: {defect.get('expectedValue')}")
                print()
        else:
            print("  ✅ 病案445583_1无民族相关缺陷")
            
    else:
        print(f"  ⚠️  无法获取病案缺陷: {response.status_code}")
        
except Exception as e:
    print(f"  ❌ 缺陷详情请求失败: {e}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)

print("\n📋 验证要点:")
print("1. 规则代码应该是 RULE_A19C_RC035 (不是 RULE_A01_RC035)")
print("2. 字段代码应该是 A19C (不是 A01)")
print("3. 字段名称应该是 '民族' ")
print("4. 实际值应该是 '1', '13', '8' 等民族代码 (不是 'ABS478045')")
print("5. 如果A19C='1'是有效的民族代码，应该不会有缺陷记录")

print("\n🎯 如果仍然看到旧的错误:")
print("1. 确保重启了Spring Boot应用")
print("2. 清理浏览器缓存")
print("3. 检查前端是否有本地缓存")
print("4. 确认API返回的是最新数据")