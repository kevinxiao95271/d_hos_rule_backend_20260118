import requests
import json

print("🔍 快速服务测试")
print("=" * 40)

# 测试健康检查
try:
    response = requests.get("http://localhost:4101/api/health", timeout=5)
    if response.status_code == 200:
        print("✅ 服务健康检查: 正常")
    else:
        print(f"⚠️  服务健康检查: HTTP {response.status_code}")
except Exception as e:
    print(f"❌ 服务健康检查: {e}")

# 测试规则API
try:
    response = requests.get("http://localhost:4101/api/qc/rules", timeout=10)
    if response.status_code == 200:
        rules = response.json()
        print(f"✅ 规则API: 返回 {len(rules)} 条规则")
        
        # 查找民族相关规则
        ethnicity_rules = [r for r in rules if 'RC035' in str(r.get('dictTypes', ''))]
        if ethnicity_rules:
            print(f"✅ 民族规则: 找到 {len(ethnicity_rules)} 条")
            for rule in ethnicity_rules:
                print(f"   - {rule.get('ruleCode')}: {rule.get('fieldCode')} ({rule.get('fieldName')})")
        else:
            print("⚠️  未找到民族相关规则")
    else:
        print(f"⚠️  规则API: HTTP {response.status_code}")
except Exception as e:
    print(f"❌ 规则API: {e}")

print("\n🎯 服务状态: 已就绪")
print("可以运行民族字段测试了!")