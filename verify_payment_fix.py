import requests
import json

# 验证医疗付费方式字段修复
base_url = "http://localhost:4101/api"

print("=" * 80)
print("验证医疗付费方式字段修复")
print("=" * 80)

# 1. 检查规则列表，确认A46C规则存在
print("\n1. 检查A46C相关规则:")
try:
    response = requests.get(f"{base_url}/qc/rules")
    if response.status_code == 200:
        result = response.json()
        rules = result.get('data', [])
        
        # 查找A46C相关规则
        a46c_rules = [r for r in rules if r.get('fieldCode') == 'A46C']
        print(f"  找到 {len(a46c_rules)} 个A46C相关规则:")
        for rule in a46c_rules:
            print(f"    规则: {rule.get('ruleCode')}")
            print(f"    字段名: {rule.get('fieldName')}")
            print(f"    描述: {rule.get('description')}")
            print(f"    状态: {rule.get('status')}")
            print()
            
        # 查找A32相关规则
        a32_rules = [r for r in rules if r.get('fieldCode') == 'A32']
        print(f"  找到 {len(a32_rules)} 个A32相关规则:")
        for rule in a32_rules:
            print(f"    规则: {rule.get('ruleCode')}")
            print(f"    字段名: {rule.get('fieldName')}")
            print(f"    状态: {rule.get('status')}")
            print()
            
    else:
        print(f"  ❌ 获取规则失败: {response.status_code}")
        
except Exception as e:
    print(f"  ❌ 请求异常: {e}")

# 2. 测试字典验证功能
print("\n2. 测试RC032字典验证:")
test_values = ["2.1", "1.1", "7", "朱兰若", "invalid"]

for value in test_values:
    try:
        response = requests.post(f"{base_url}/dict/validate", 
                               json={"dictTypeCode": "RC032", "value": value})
        if response.status_code == 200:
            result = response.json()
            is_valid = result.get('data', {}).get('isValid', False)
            print(f"  值 '{value}': {'✅ 有效' if is_valid else '❌ 无效'}")
        else:
            print(f"  值 '{value}': ❌ 验证失败 ({response.status_code})")
    except Exception as e:
        print(f"  值 '{value}': ❌ 异常 ({e})")

# 3. 测试简单的质控功能
print("\n3. 测试质控统计:")
try:
    stats_data = {
        "startDate": "2023-01-01",
        "endDate": "2023-01-31"
    }
    response = requests.post(f"{base_url}/qc/stats", json=stats_data)
    if response.status_code == 200:
        result = response.json()
        print(f"  ✅ 统计请求成功")
        data = result.get('data', {})
        print(f"  病案总数: {data.get('totalRecords', 0)}")
        print(f"  平均分: {data.get('averageScore', 0)}")
        print(f"  总缺陷数: {data.get('totalDefects', 0)}")
    else:
        print(f"  ❌ 统计请求失败: {response.status_code}")
        print(f"  错误信息: {response.text}")
except Exception as e:
    print(f"  ❌ 统计请求异常: {e}")

print(f"\n" + "=" * 80)
print("验证完成")
print("=" * 80)