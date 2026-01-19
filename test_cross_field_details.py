#!/usr/bin/env python3
import requests
import json

# API配置
BASE_URL = "http://localhost:4101"

def test_cross_field_details():
    """测试Cross规则违规的具体字段信息"""
    print("🔍 测试Cross规则违规的具体字段信息")
    print("=" * 70)
    
    # 测试已知有Cross规则违规的病案
    test_cases = [
        {"a48": "445583", "a49": "1", "name": "输血逻辑违规病案"},
        {"a48": "19065857", "a49": "1", "name": "输血逻辑违规病案2"},
        {"a48": "19072516", "a49": "1", "name": "输血逻辑违规病案3"}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 🧪 测试{test_case['name']} ({test_case['a48']}_{test_case['a49']})...")
        
        try:
            response = requests.post(f"{BASE_URL}/api/qc/check/single", 
                                   params={"a48": test_case['a48'], "a49": test_case['a49']}, 
                                   timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('code') == 200 and 'data' in result:
                    data = result['data']
                    
                    print(f"   ✅ 质控成功")
                    print(f"   📋 基本信息:")
                    print(f"     - 病案键: {data.get('mrKey')}")
                    print(f"     - 总违规数: {data.get('defectCount', 0)}")
                    print(f"     - Cross违规数: {data.get('crossDefectCount', 0)}")
                    
                    # 详细分析Cross规则违规
                    cross_defects = data.get('crossDefects', [])
                    if cross_defects:
                        print(f"   🎯 Cross规则违规详情:")
                        
                        for j, defect in enumerate(cross_defects, 1):
                            print(f"     违规 {j}:")
                            print(f"       规则代码: {defect.get('ruleCode', 'N/A')}")
                            print(f"       规则描述: {defect.get('ruleDescription', 'N/A')}")
                            print(f"       Cross类型: {defect.get('crossType', 'N/A')}")
                            print(f"       严重程度: {defect.get('severity', 'N/A')}")
                            print(f"       扣分: {defect.get('deductScore', 'N/A')}")
                            
                            # 涉及字段信息
                            involved_fields = defect.get('involvedFields', [])
                            if involved_fields:
                                print(f"       涉及字段: {', '.join(involved_fields)}")
                            
                            # 字段值映射
                            field_values = defect.get('fieldValues', {})
                            if field_values:
                                print(f"       字段值:")
                                for field, value in field_values.items():
                                    print(f"         - {field}: {value}")
                            
                            # 逻辑描述
                            logic_desc = defect.get('logicDescription', '')
                            if logic_desc:
                                print(f"       逻辑描述: {logic_desc}")
                            
                            print()  # 空行分隔
                    
                    # 对比普通违规的字段信息
                    all_defects = data.get('allDefects', [])
                    normal_defects = [d for d in all_defects if not d.get('ruleCode', '').startswith('RULE_CROSS_')]
                    
                    if normal_defects:
                        print(f"   📝 普通规则违规对比 (前2个):")
                        for j, defect in enumerate(normal_defects[:2], 1):
                            print(f"     违规 {j}:")
                            print(f"       规则代码: {defect.get('ruleCode', 'N/A')}")
                            print(f"       字段代码: {defect.get('fieldCode', 'N/A')}")
                            print(f"       字段名称: {defect.get('fieldName', 'N/A')}")
                            print(f"       实际值: {defect.get('actualValue', 'N/A')}")
                            print(f"       期望值: {defect.get('expectedValue', 'N/A')}")
                            print(f"       扣分: {defect.get('deductScore', 'N/A')}")
                            print()
                    
                else:
                    print(f"   ❌ API返回错误: {result.get('message', 'Unknown error')}")
                    
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 异常: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 Cross规则字段信息测试完成")
    print("=" * 70)

if __name__ == "__main__":
    test_cross_field_details()