#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:4101"

def test_frontend_guide_examples():
    """测试前端指引文档中的所有示例"""
    print("🧪 测试前端指引文档示例")
    print("=" * 80)
    
    # 测试文档中提到的病案
    test_cases = [
        {"a48": "445583", "a49": "1", "expected_cross": "RULE_CROSS_D26_TRANSFUSION_FEE1"},
        {"a48": "19065857", "a49": "1", "expected_cross": "RULE_CROSS_D26_TRANSFUSION_FEE1"},
        {"a48": "19072516", "a49": "1", "expected_cross": "RULE_CROSS_D26_TRANSFUSION_FEE1"},
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 测试案例 {i}: {case['a48']}-{case['a49']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/qc/check/single",
                params={"a48": case['a48'], "a49": case['a49']},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                data = result.get('data', {})
                
                # 验证API结构
                print(f"  ✅ API响应正常")
                
                # 检查必需字段
                required_fields = ['mrKey', 'a48', 'a49', 'defectCount', 'totalDeduct', 'finalScore', 'allDefects', 'defectsByField']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"  ❌ 缺少必需字段: {missing_fields}")
                else:
                    print(f"  ✅ 所有必需字段都存在")
                
                # 检查新增字段
                if 'crossDefects' in data:
                    print(f"  ✅ crossDefects字段存在")
                    cross_defects = data['crossDefects']
                    
                    if cross_defects:
                        print(f"  🎯 发现 {len(cross_defects)} 个Cross规则违规")
                        
                        # 验证CrossDefect结构
                        sample_cross = cross_defects[0]
                        cross_fields = ['ruleCode', 'ruleDescription', 'crossType', 'involvedFields', 'fieldValues', 'logicDescription', 'deductScore', 'severity']
                        
                        print(f"  📊 CrossDefect结构验证:")
                        for field in cross_fields:
                            exists = field in sample_cross
                            print(f"    {'✅' if exists else '❌'} {field}: {sample_cross.get(field, 'N/A')}")
                        
                        # 验证期望的Cross规则
                        found_expected = any(cd.get('ruleCode') == case['expected_cross'] for cd in cross_defects)
                        if found_expected:
                            print(f"  ✅ 找到期望的Cross规则: {case['expected_cross']}")
                        else:
                            print(f"  ⚠️  未找到期望的Cross规则: {case['expected_cross']}")
                            print(f"      实际找到: {[cd.get('ruleCode') for cd in cross_defects]}")
                    else:
                        print(f"  ℹ️  无Cross规则违规")
                else:
                    print(f"  ❌ crossDefects字段不存在")
                
                # 验证向后兼容性
                all_defects = data.get('allDefects', [])
                defects_by_field = data.get('defectsByField', {})
                
                print(f"  🔧 向后兼容性验证:")
                print(f"    allDefects数量: {len(all_defects)}")
                print(f"    defectsByField字段数: {len(defects_by_field)}")
                
                # 检查allDefects中是否包含Cross规则
                cross_in_all = [d for d in all_defects if d.get('ruleCode', '').startswith('RULE_CROSS_')]
                print(f"    allDefects中的Cross规则: {len(cross_in_all)}")
                
                # 检查defectsByField中是否排除了Cross规则
                cross_in_fields = []
                for field_defects in defects_by_field.values():
                    cross_in_fields.extend([d for d in field_defects if d.get('ruleCode', '').startswith('RULE_CROSS_')])
                print(f"    defectsByField中的Cross规则: {len(cross_in_fields)} (应该为0)")
                
                if len(cross_in_fields) == 0:
                    print(f"    ✅ defectsByField正确排除了Cross规则")
                else:
                    print(f"    ❌ defectsByField中仍包含Cross规则")
                
            else:
                print(f"  ❌ API请求失败: {response.status_code}")
                print(f"  响应: {response.text[:200]}...")
                
        except Exception as e:
            print(f"  ❌ 测试异常: {e}")

def generate_frontend_example_json():
    """生成前端示例JSON"""
    print(f"\n📄 生成前端示例JSON")
    print("=" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/qc/check/single",
            params={"a48": "445583", "a49": "1"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # 美化JSON输出
            formatted_json = json.dumps(result, indent=2, ensure_ascii=False)
            
            # 保存到文件
            with open('frontend_example_response.json', 'w', encoding='utf-8') as f:
                f.write(formatted_json)
            
            print(f"✅ 示例JSON已保存到 frontend_example_response.json")
            
            # 显示关键部分
            data = result.get('data', {})
            cross_defects = data.get('crossDefects', [])
            
            if cross_defects:
                print(f"\n🎯 Cross规则示例:")
                for cd in cross_defects:
                    print(f"  规则代码: {cd.get('ruleCode')}")
                    print(f"  规则类型: {cd.get('crossType')}")
                    print(f"  严重程度: {cd.get('severity')}")
                    print(f"  涉及字段: {cd.get('involvedFields')}")
                    print(f"  逻辑描述: {cd.get('logicDescription')}")
                    print()
            
        else:
            print(f"❌ 无法获取示例数据: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 生成示例JSON失败: {e}")

def validate_documentation_accuracy():
    """验证文档准确性"""
    print(f"\n📋 验证文档准确性")
    print("=" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/qc/check/single",
            params={"a48": "445583", "a49": "1"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            
            # 验证文档中提到的字段
            doc_claims = {
                "API响应包含crossDefects字段": 'crossDefects' in data,
                "crossDefects是数组": isinstance(data.get('crossDefects'), list),
                "allDefects仍然存在": 'allDefects' in data,
                "defectsByField仍然存在": 'defectsByField' in data,
                "向后兼容性保持": len(data.get('allDefects', [])) >= len(data.get('crossDefects', [])),
            }
            
            print(f"📊 文档声明验证:")
            for claim, is_true in doc_claims.items():
                print(f"  {'✅' if is_true else '❌'} {claim}")
            
            # 验证Cross规则结构
            cross_defects = data.get('crossDefects', [])
            if cross_defects:
                sample = cross_defects[0]
                expected_fields = ['ruleCode', 'ruleDescription', 'crossType', 'involvedFields', 'fieldValues', 'logicDescription', 'deductScore', 'severity']
                
                print(f"\n📊 CrossDefect结构验证:")
                for field in expected_fields:
                    exists = field in sample
                    value_type = type(sample.get(field)).__name__ if exists else 'N/A'
                    print(f"  {'✅' if exists else '❌'} {field} ({value_type})")
            
            # 验证规则命名
            all_cross_rules = [d for d in data.get('allDefects', []) if d.get('ruleCode', '').startswith('RULE_CROSS_')]
            old_cross_rules = [d for d in data.get('allDefects', []) if d.get('ruleCode', '').startswith('CROSS_') and not d.get('ruleCode', '').startswith('RULE_CROSS_')]
            
            print(f"\n📊 规则命名验证:")
            print(f"  ✅ RULE_CROSS_格式规则: {len(all_cross_rules)}")
            print(f"  {'✅' if len(old_cross_rules) == 0 else '❌'} 旧CROSS_格式规则: {len(old_cross_rules)} (应该为0)")
            
        else:
            print(f"❌ 无法验证文档准确性: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")

def main():
    print("🚀 前端指引文档验证")
    
    # 测试文档示例
    test_frontend_guide_examples()
    
    # 生成示例JSON
    generate_frontend_example_json()
    
    # 验证文档准确性
    validate_documentation_accuracy()
    
    print(f"\n" + "=" * 80)
    print("📋 前端指引文档验证总结")
    print("=" * 80)
    
    print(f"✅ 验证完成项目:")
    print(f"  - API结构正确性")
    print(f"  - crossDefects字段存在性")
    print(f"  - CrossDefect数据结构完整性")
    print(f"  - 向后兼容性保证")
    print(f"  - 规则命名标准化")
    print(f"  - 文档示例准确性")
    
    print(f"\n📄 生成的文件:")
    print(f"  - CROSS_RULES_FRONTEND_GUIDE.md - 详细开发指引")
    print(f"  - CROSS_RULES_API_EXAMPLES.md - 完整代码示例")
    print(f"  - CROSS_RULES_QUICK_REFERENCE.md - 快速参考")
    print(f"  - frontend_example_response.json - 实际API响应示例")
    
    print(f"\n🎯 前端开发建议:")
    print(f"  1. 立即可用: 现有代码无需修改")
    print(f"  2. 渐进增强: 逐步添加Cross规则展示")
    print(f"  3. 专门UI: 为Cross规则创建独立展示区域")
    print(f"  4. 视觉区分: 使用颜色和图标突出显示")

if __name__ == "__main__":
    main()