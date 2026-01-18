import requests
import json

print("🔍 测试主要API")
print("=" * 40)

base_url = "http://localhost:4101"

# 测试不同的API端点
endpoints = [
    ("规则列表", "/api/qc/rules"),
    ("字典类型", "/api/dict/types"),
    ("字段统计", "/api/qc/field-stats"),
    ("批次列表", "/api/qc/batches")
]

for name, endpoint in endpoints:
    try:
        response = requests.get(f"{base_url}{endpoint}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ {name}: 返回 {len(data)} 条记录")
            else:
                print(f"✅ {name}: 正常响应")
        else:
            print(f"⚠️  {name}: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ {name}: {e}")

# 如果规则API正常，查找民族规则
try:
    response = requests.get(f"{base_url}/api/qc/rules", timeout=10)
    if response.status_code == 200:
        rules = response.json()
        print(f"\n📋 规则详情:")
        
        ethnicity_rules = []
        for rule in rules:
            dict_types = rule.get('dictTypes', '')
            if 'RC035' in str(dict_types):
                ethnicity_rules.append(rule)
        
        if ethnicity_rules:
            print(f"✅ 找到 {len(ethnicity_rules)} 条民族规则:")
            for rule in ethnicity_rules:
                print(f"   规则: {rule.get('ruleCode')}")
                print(f"   字段: {rule.get('fieldCode')} ({rule.get('fieldName')})")
                print(f"   状态: {rule.get('status')}")
                print()
        else:
            print("⚠️  未找到民族相关规则")
            
except Exception as e:
    print(f"❌ 获取规则详情失败: {e}")

print("🎯 准备运行质控测试...")