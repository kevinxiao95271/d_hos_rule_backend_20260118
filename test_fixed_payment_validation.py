import requests
import json

# 测试修复后的医疗付费方式验证
base_url = "http://localhost:4101/api"

print("=" * 80)
print("测试修复后的医疗付费方式验证")
print("=" * 80)

# 1. 测试单个病案质控 - 使用之前有问题的病案445583_1
print("\n1. 测试病案445583_1的质控结果:")
test_data = {
    "recordId": "445583_1",
    "timeRange": {
        "startDate": "2023-01-01",
        "endDate": "2023-12-31"
    }
}

try:
    response = requests.post(f"{base_url}/qc/check/single", json=test_data)
    if response.status_code == 200:
        result = response.json()
        print(f"  ✅ 请求成功")
        print(f"  病案ID: {result.get('recordId')}")
        print(f"  总分: {result.get('totalScore')}")
        print(f"  缺陷数: {result.get('defectCount')}")
        
        # 检查A46C字段的验证结果
        defects = result.get('defects', [])
        payment_defects = [d for d in defects if d.get('fieldCode') == 'A46C']
        
        if payment_defects:
            print(f"  ❌ A46C字段仍有缺陷:")
            for defect in payment_defects:
                print(f"    规则: {defect.get('ruleCode')}")
                print(f"    实际值: {defect.get('actualValue')}")
                print(f"    期望值: {defect.get('expectedValue')}")
        else:
            print(f"  ✅ A46C字段验证通过，无缺陷")
            
        # 检查A32字段是否还有缺陷
        a32_defects = [d for d in defects if d.get('fieldCode') == 'A32']
        if a32_defects:
            print(f"  ⚠️  A32字段仍有缺陷:")
            for defect in a32_defects:
                print(f"    规则: {defect.get('ruleCode')}")
                print(f"    实际值: {defect.get('actualValue')}")
        else:
            print(f"  ✅ A32字段无缺陷")
            
    else:
        print(f"  ❌ 请求失败: {response.status_code}")
        print(f"  错误信息: {response.text}")
        
except Exception as e:
    print(f"  ❌ 请求异常: {e}")

# 2. 测试批量质控
print(f"\n2. 测试2023年1月批量质控:")
batch_data = {
    "timeRange": {
        "startDate": "2023-01-01", 
        "endDate": "2023-01-31"
    },
    "limit": 10
}

try:
    response = requests.post(f"{base_url}/qc/check/batch", json=batch_data)
    if response.status_code == 200:
        result = response.json()
        print(f"  ✅ 批量质控请求成功")
        print(f"  处理病案数: {result.get('totalRecords')}")
        print(f"  平均分: {result.get('averageScore')}")
        print(f"  总缺陷数: {result.get('totalDefects')}")
        
        # 检查A46C相关的缺陷统计
        defect_stats = result.get('defectStats', [])
        payment_stats = [s for s in defect_stats if s.get('fieldCode') == 'A46C']
        
        if payment_stats:
            print(f"  A46C字段缺陷统计:")
            for stat in payment_stats:
                print(f"    规则: {stat.get('ruleCode')}")
                print(f"    缺陷数: {stat.get('count')}")
        else:
            print(f"  ✅ A46C字段无缺陷")
            
    else:
        print(f"  ❌ 批量质控失败: {response.status_code}")
        print(f"  错误信息: {response.text}")
        
except Exception as e:
    print(f"  ❌ 批量质控异常: {e}")

# 3. 验证A46C字段的字典验证
print(f"\n3. 测试A46C字段字典验证:")
dict_test_data = {
    "dictTypeCode": "RC032",
    "value": "2.1"
}

try:
    response = requests.post(f"{base_url}/dict/validate", json=dict_test_data)
    if response.status_code == 200:
        result = response.json()
        print(f"  ✅ 字典验证请求成功")
        print(f"  值 '2.1' 验证结果: {result.get('isValid')}")
    else:
        print(f"  ❌ 字典验证失败: {response.status_code}")
        
except Exception as e:
    print(f"  ❌ 字典验证异常: {e}")

# 4. 测试无效的付费方式代码
print(f"\n4. 测试无效付费方式代码验证:")
invalid_test_data = {
    "dictTypeCode": "RC032", 
    "value": "朱兰若"  # 这是之前错误显示的姓名
}

try:
    response = requests.post(f"{base_url}/dict/validate", json=invalid_test_data)
    if response.status_code == 200:
        result = response.json()
        print(f"  ✅ 字典验证请求成功")
        print(f"  值 '朱兰若' 验证结果: {result.get('isValid')} (应该是false)")
    else:
        print(f"  ❌ 字典验证失败: {response.status_code}")
        
except Exception as e:
    print(f"  ❌ 字典验证异常: {e}")

print(f"\n" + "=" * 80)
print("测试完成")
print("=" * 80)