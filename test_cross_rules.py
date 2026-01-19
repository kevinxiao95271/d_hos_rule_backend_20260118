import requests
import json
import time

print("🔄 测试Cross跨字段规则")
print("=" * 60)

base_url = "http://localhost:4101"

# 1. 检查服务状态
print("\n1. 检查服务状态...")
try:
    response = requests.get(f"{base_url}/api/qc/status", timeout=5)
    if response.status_code == 200:
        print("✅ 服务正常运行")
    else:
        print(f"⚠️  服务状态异常: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ 服务连接失败: {e}")
    exit(1)

# 2. 测试单个病案质控（包含cross规则）
print("\n2. 测试病案质控（包含cross规则检查）...")
try:
    # 测试几个不同的病案
    test_cases = [
        {"a48": "445583", "a49": "1", "desc": "正常病案"},
        {"a48": "260487537", "a49": "1", "desc": "另一个病案"},
    ]
    
    for test_case in test_cases:
        print(f"\n测试病案: {test_case['a48']}_{test_case['a49']} ({test_case['desc']})")
        
        response = requests.post(
            f"{base_url}/api/qc/check/single",
            params={"a48": test_case["a48"], "a49": test_case["a49"]},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            qc_result = result.get('data', {})
            
            print(f"  病案: {qc_result.get('mrKey', 'N/A')}")
            print(f"  缺陷数: {qc_result.get('defectCount', 0)}")
            print(f"  总扣分: {qc_result.get('totalDeduct', 0)}")
            print(f"  最终得分: {qc_result.get('finalScore', 0)}")
            
            # 检查违规详情
            violations = qc_result.get('violations', [])
            if violations:
                print(f"  发现 {len(violations)} 个违规:")
                
                cross_violations = []
                for violation in violations:
                    rule_code = violation.get('ruleCode', '')
                    if rule_code.startswith('CROSS_'):
                        cross_violations.append(violation)
                
                if cross_violations:
                    print(f"  🎯 跨字段规则违规 ({len(cross_violations)}个):")
                    for violation in cross_violations:
                        print(f"    规则: {violation.get('ruleCode')}")
                        print(f"    字段: {violation.get('fieldCode')} ({violation.get('fieldName')})")
                        print(f"    实际值: '{violation.get('actualValue')}'")
                        print(f"    期望值: {violation.get('expectedValue')}")
                        print(f"    描述: {violation.get('ruleDescription')}")
                        print(f"    扣分: {violation.get('deductScore')}")
                        print()
                else:
                    print(f"  ✅ 无跨字段规则违规")
                    
                # 显示其他类型的违规
                other_violations = [v for v in violations if not v.get('ruleCode', '').startswith('CROSS_')]
                if other_violations:
                    print(f"  其他违规 ({len(other_violations)}个):")
                    for violation in other_violations[:3]:  # 只显示前3个
                        print(f"    {violation.get('ruleCode')}: {violation.get('fieldCode')} - {violation.get('actualValue')}")
            else:
                print(f"  ✅ 无任何违规")
                
        else:
            print(f"  ❌ 质控失败: HTTP {response.status_code}")
            print(f"  响应: {response.text}")
            
except Exception as e:
    print(f"❌ 测试异常: {e}")

# 3. 运行小批量测试
print("\n3. 运行小批量测试...")
try:
    payload = {
        "year": 2023,
        "limit": 10
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
        print(f"  批次: {batch_result.get('batchKey', 'N/A')}")
        print(f"  病案数: {batch_result.get('caseCount', 0)}")
        print(f"  总缺陷: {batch_result.get('totalDefectCount', 0)}")
        print(f"  平均缺陷: {batch_result.get('avgDefect', 0)}")
        print(f"  平均得分: {batch_result.get('avgScore', 0)}")
        
    else:
        print(f"❌ 批量质控失败: HTTP {response.status_code}")
        
except Exception as e:
    print(f"❌ 批量测试异常: {e}")

print("\n" + "=" * 60)
print("🎯 Cross规则测试完成")
print("=" * 60)

print("\n📋 测试要点:")
print("✅ 检查是否有CROSS_开头的规则代码")
print("✅ 验证字段配对规则（编码与名称同时有值或同时为空）")
print("✅ 验证性别诊断逻辑规则（男性不应有妇科诊断）")
print("✅ 确认cross规则正确集成到质控流程中")

print("\n🔧 如果没有看到CROSS_规则违规:")
print("1. 检查数据库中是否有cross规则记录")
print("2. 确认Spring Boot应用已重启并加载了新代码")
print("3. 检查日志中是否有cross规则相关错误")