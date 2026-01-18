import requests
import time
import json

def test_service_and_rules():
    base_url = "http://localhost:4101/api"
    
    print("=" * 80)
    print("测试规则修复效果")
    print("=" * 80)
    
    # 等待服务启动
    print("\n1. 等待服务启动...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/qc/rules", timeout=5)
            if response.status_code == 200:
                print(f"  ✅ 服务已启动 (尝试 {i+1}/{max_retries})")
                break
        except:
            print(f"  ⏳ 等待服务启动... ({i+1}/{max_retries})")
            time.sleep(2)
    else:
        print("  ❌ 服务启动超时")
        return
    
    # 2. 检查规则列表
    print(f"\n2. 检查规则列表:")
    try:
        response = requests.get(f"{base_url}/qc/rules")
        if response.status_code == 200:
            result = response.json()
            rules = result.get('data', [])
            
            # 查找民族相关规则
            ethnic_rules = [r for r in rules if '民族' in r.get('fieldName', '') or 'RC035' in r.get('dictTypes', '')]
            
            print(f"  找到 {len(ethnic_rules)} 个民族相关规则:")
            for rule in ethnic_rules:
                print(f"    规则: {rule.get('ruleCode')}")
                print(f"    字段: {rule.get('fieldCode')} ({rule.get('fieldName')})")
                print(f"    状态: {rule.get('status')}")
                print(f"    字典: {rule.get('dictTypes')}")
                print()
                
            # 检查是否还有RULE_A01_RC035
            old_rule = [r for r in rules if r.get('ruleCode') == 'RULE_A01_RC035']
            if old_rule:
                print(f"  ❌ 仍然存在旧规则: RULE_A01_RC035")
                print(f"     状态: {old_rule[0].get('status')}")
            else:
                print(f"  ✅ 旧规则 RULE_A01_RC035 已清理")
                
            # 检查新规则
            new_rule = [r for r in rules if r.get('ruleCode') == 'RULE_A19C_RC035']
            if new_rule:
                print(f"  ✅ 新规则 RULE_A19C_RC035 存在")
                print(f"     字段: {new_rule[0].get('fieldCode')}")
                print(f"     状态: {new_rule[0].get('status')}")
            else:
                print(f"  ❌ 新规则 RULE_A19C_RC035 不存在")
                
        else:
            print(f"  ❌ 获取规则失败: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ 请求异常: {e}")
    
    # 3. 测试单个病案质控
    print(f"\n3. 测试病案445583_1质控:")
    try:
        test_data = {
            "recordId": "445583_1",
            "timeRange": {
                "startDate": "2023-01-01",
                "endDate": "2023-12-31"
            }
        }
        
        response = requests.post(f"{base_url}/qc/check/single", json=test_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ 质控请求成功")
            
            defects = result.get('defects', [])
            ethnic_defects = [d for d in defects if 'A01' in d.get('fieldCode', '') or 'A19C' in d.get('fieldCode', '') or '民族' in d.get('ruleDescription', '')]
            
            if ethnic_defects:
                print(f"  民族相关缺陷:")
                for defect in ethnic_defects:
                    print(f"    规则: {defect.get('ruleCode')}")
                    print(f"    字段: {defect.get('fieldCode')}")
                    print(f"    实际值: {defect.get('actualValue')}")
                    print(f"    期望值: {defect.get('expectedValue')}")
            else:
                print(f"  ✅ 无民族相关缺陷")
                
        else:
            print(f"  ❌ 质控请求失败: {response.status_code}")
            print(f"  错误信息: {response.text}")
            
    except Exception as e:
        print(f"  ❌ 质控请求异常: {e}")

if __name__ == "__main__":
    test_service_and_rules()