import requests
import json
import time

print("🎯 民族字段修复测试 (正确API)")
print("=" * 50)

base_url = "http://localhost:4101"

# 1. 检查服务状态
print("\n1. 检查服务状态...")
try:
    response = requests.get(f"{base_url}/api/qc/status", timeout=5)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 服务状态: {result.get('data', 'OK')}")
    else:
        print(f"⚠️  服务状态: HTTP {response.status_code}")
except Exception as e:
    print(f"❌ 服务状态检查失败: {e}")

# 2. 检查民族相关规则
print("\n2. 检查民族相关规则...")
try:
    response = requests.get(f"{base_url}/api/qc/rules", timeout=10)
    if response.status_code == 200:
        result = response.json()
        rules = result.get('data', [])
        print(f"✅ 获取到 {len(rules)} 条规则")
        
        # 查找民族相关规则
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
                print(f"   字典: {rule.get('dictTypes')}")
                print()
        else:
            print("⚠️  未找到民族相关规则")
            
    else:
        print(f"❌ 规则API失败: HTTP {response.status_code}")
        
except Exception as e:
    print(f"❌ 规则检查失败: {e}")

# 3. 测试单个病案质控
print("\n3. 测试病案445583_1的质控...")
try:
    response = requests.post(
        f"{base_url}/api/qc/check/single",
        params={"a48": "445583", "a49": "1"},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        qc_result = result.get('data', {})
        
        print(f"✅ 单病案质控完成")
        print(f"   病案: {qc_result.get('mrKey', 'N/A')}")
        print(f"   缺陷数: {qc_result.get('defectCount', 0)}")
        print(f"   总扣分: {qc_result.get('totalDeduct', 0)}")
        print(f"   最终得分: {qc_result.get('finalScore', 0)}")
        
        # 检查缺陷详情
        violations = qc_result.get('violations', [])
        if violations:
            print(f"\n   发现 {len(violations)} 个缺陷:")
            
            ethnicity_violations = []
            for violation in violations:
                rule_code = violation.get('ruleCode', '')
                field_code = violation.get('fieldCode', '')
                field_name = violation.get('fieldName', '')
                
                if ('RC035' in rule_code or 'A19C' in field_code or 
                    '民族' in field_name or 'A01' in rule_code):
                    ethnicity_violations.append(violation)
            
            if ethnicity_violations:
                print(f"   ⚠️  民族相关缺陷 ({len(ethnicity_violations)}个):")
                for violation in ethnicity_violations:
                    print(f"      规则: {violation.get('ruleCode')}")
                    print(f"      字段: {violation.get('fieldCode')} ({violation.get('fieldName')})")
                    print(f"      实际值: '{violation.get('actualValue')}'")
                    print(f"      期望值: {violation.get('expectedValue')}")
                    print(f"      扣分: {violation.get('deductScore')}")
                    
                    # 检查修复效果
                    if violation.get('ruleCode') == 'RULE_A01_RC035':
                        print(f"      ❌ 仍然使用旧的规则代码!")
                    elif 'ABS' in str(violation.get('actualValue', '')):
                        print(f"      ❌ 仍然显示错误的实际值!")
                    else:
                        print(f"      ✅ 规则代码和实际值看起来正确")
                    print()
            else:
                print(f"   ✅ 无民族相关缺陷 (修复成功!)")
                print(f"   这意味着A19C='1'被正确识别为有效的民族代码")
        else:
            print(f"   ✅ 无任何缺陷 (完美!)")
            
    else:
        print(f"❌ 单病案质控失败: HTTP {response.status_code}")
        print(f"响应: {response.text}")
        
except Exception as e:
    print(f"❌ 单病案质控异常: {e}")

# 4. 运行小批量质控测试
print("\n4. 运行小批量质控测试...")
try:
    payload = {
        "year": 2023,
        "limit": 5
    }
    
    response = requests.post(
        f"{base_url}/api/qc/check/batch",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        batch_result = result.get('data', {})
        
        print(f"✅ 批量质控完成")
        print(f"   批次: {batch_result.get('batchKey', 'N/A')}")
        print(f"   病案数: {batch_result.get('caseCount', 0)}")
        print(f"   总缺陷: {batch_result.get('totalDefectCount', 0)}")
        print(f"   平均缺陷: {batch_result.get('avgDefect', 0)}")
        print(f"   平均得分: {batch_result.get('avgScore', 0)}")
        
    else:
        print(f"❌ 批量质控失败: HTTP {response.status_code}")
        print(f"响应: {response.text}")
        
except Exception as e:
    print(f"❌ 批量质控异常: {e}")

print("\n" + "=" * 50)
print("🎯 测试完成")
print("=" * 50)

print("\n📋 修复验证结果:")
print("✅ 如果看到'无民族相关缺陷'，说明修复成功!")
print("✅ 规则应该使用RULE_A19C_RC035而不是RULE_A01_RC035")
print("✅ 字段应该是A19C而不是A01")
print("✅ 实际值应该是'1'而不是'ABS478045'")
print("✅ 由于'1'是有效的汉族代码，不应该有违规")