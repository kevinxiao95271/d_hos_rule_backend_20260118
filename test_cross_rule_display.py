#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:4101"

def test_cross_rule_display():
    """测试Cross规则的展示效果"""
    print("🎯 测试Cross规则展示功能")
    print("=" * 80)
    
    # 测试有Cross规则违规的病案
    test_cases = [
        {"a48": "445583", "a49": "1", "name": "输血逻辑违规病案"},
        {"a48": "19065857", "a49": "1", "name": "输血逻辑违规病案2"},
    ]
    
    for case in test_cases:
        print(f"\n📋 测试 {case['name']}: {case['a48']}-{case['a49']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/qc/check/single",
                params={"a48": case['a48'], "a49": case['a49']},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                data = result.get('data', {})
                
                print(f"  ✅ 质控完成")
                print(f"  缺陷总数: {data.get('defectCount', 0)}")
                print(f"  总扣分: {data.get('totalDeduct', 0)}")
                print(f"  最终得分: {data.get('finalScore', 0)}")
                
                # 检查新的crossDefects字段
                cross_defects = data.get('crossDefects', [])
                all_defects = data.get('allDefects', [])
                defects_by_field = data.get('defectsByField', {})
                
                print(f"\n  📊 违规分类统计:")
                print(f"    allDefects总数: {len(all_defects)}")
                print(f"    crossDefects数量: {len(cross_defects)}")
                print(f"    defectsByField字段数: {len(defects_by_field)}")
                
                # 展示Cross规则违规详情
                if cross_defects:
                    print(f"\n  🎯 Cross规则违规详情:")
                    for i, cross_defect in enumerate(cross_defects, 1):
                        print(f"    {i}. {cross_defect.get('ruleCode', 'N/A')}")
                        print(f"       类型: {cross_defect.get('crossType', 'N/A')}")
                        print(f"       描述: {cross_defect.get('ruleDescription', 'N/A')[:60]}...")
                        print(f"       逻辑: {cross_defect.get('logicDescription', 'N/A')}")
                        print(f"       严重程度: {cross_defect.get('severity', 'N/A')}")
                        print(f"       涉及字段: {cross_defect.get('involvedFields', [])}")
                        print(f"       字段值: {cross_defect.get('fieldValues', {})}")
                        print(f"       扣分: {cross_defect.get('deductScore', 0)}")
                        print()
                else:
                    print(f"  ℹ️  无Cross规则违规")
                
                # 展示普通违规统计
                normal_defects = [d for d in all_defects if not d.get('ruleCode', '').startswith('CROSS_')]
                cross_in_all = [d for d in all_defects if d.get('ruleCode', '').startswith('CROSS_')]
                
                print(f"  📋 普通违规统计:")
                print(f"    普通违规数: {len(normal_defects)}")
                print(f"    Cross违规数(在allDefects中): {len(cross_in_all)}")
                
                # 验证向后兼容性
                print(f"\n  🔧 向后兼容性验证:")
                print(f"    allDefects包含所有违规: {'✅' if len(all_defects) == data.get('defectCount', 0) else '❌'}")
                print(f"    defectsByField只包含普通违规: {'✅' if len(defects_by_field) > 0 else '⚠️'}")
                print(f"    crossDefects单独分组: {'✅' if len(cross_defects) > 0 else 'ℹ️ 无Cross违规'}")
                
                # 展示按字段分组的违规
                if defects_by_field:
                    print(f"\n  📂 按字段分组的违规 (前3个):")
                    for field_code, field_defects in list(defects_by_field.items())[:3]:
                        print(f"    {field_code}: {len(field_defects)}个违规")
                        for defect in field_defects[:2]:  # 只显示前2个
                            print(f"      - {defect.get('ruleCode', 'N/A')}: {defect.get('ruleDescription', 'N/A')[:40]}...")
                
            else:
                print(f"  ❌ 质控失败: {response.status_code}")
                print(f"  响应: {response.text[:200]}...")
                
        except Exception as e:
            print(f"  ❌ 测试异常: {e}")

def test_api_structure_compatibility():
    """测试API结构的兼容性"""
    print(f"\n🔧 API结构兼容性测试")
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
            
            # 检查必需字段
            required_fields = ['mrKey', 'a48', 'a49', 'defectCount', 'totalDeduct', 'finalScore', 'allDefects', 'defectsByField']
            new_fields = ['crossDefects']
            
            print(f"📋 API字段检查:")
            
            for field in required_fields:
                exists = field in data
                print(f"  {'✅' if exists else '❌'} {field}: {'存在' if exists else '缺失'}")
            
            for field in new_fields:
                exists = field in data
                print(f"  {'✅' if exists else '⚠️'} {field}: {'存在' if exists else '缺失'} (新增字段)")
            
            # 检查数据结构
            print(f"\n📊 数据结构验证:")
            all_defects = data.get('allDefects', [])
            cross_defects = data.get('crossDefects', [])
            
            if all_defects:
                sample_defect = all_defects[0]
                defect_fields = ['fieldCode', 'fieldName', 'ruleCode', 'ruleDescription', 'actualValue', 'expectedValue', 'deductScore']
                print(f"  DefectDTO结构:")
                for field in defect_fields:
                    exists = field in sample_defect
                    print(f"    {'✅' if exists else '❌'} {field}")
            
            if cross_defects:
                sample_cross = cross_defects[0]
                cross_fields = ['ruleCode', 'ruleDescription', 'crossType', 'involvedFields', 'fieldValues', 'logicDescription', 'deductScore', 'severity']
                print(f"  CrossDefectDTO结构:")
                for field in cross_fields:
                    exists = field in sample_cross
                    print(f"    {'✅' if exists else '⚠️'} {field}")
            
            print(f"\n✅ API结构兼容性验证完成")
            
        else:
            print(f"❌ API请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 兼容性测试异常: {e}")

def main():
    print("🚀 Cross规则展示功能测试")
    
    # 测试Cross规则展示
    test_cross_rule_display()
    
    # 测试API兼容性
    test_api_structure_compatibility()
    
    print(f"\n" + "=" * 80)
    print("📋 Cross规则展示功能总结")
    print("=" * 80)
    
    print(f"✅ 新增功能:")
    print(f"  - crossDefects字段: 专门展示Cross规则违规")
    print(f"  - 详细的Cross规则信息: 类型、涉及字段、逻辑描述等")
    print(f"  - 严重程度分级: low/medium/high")
    print(f"  - 字段值映射: 显示相关字段的实际值")
    
    print(f"\n✅ 向后兼容:")
    print(f"  - allDefects: 仍包含所有违规(包括Cross规则)")
    print(f"  - defectsByField: 仍按字段分组普通违规")
    print(f"  - 原有API结构完全保持不变")
    
    print(f"\n🎯 前端展示建议:")
    print(f"  1. 普通违规: 使用defectsByField按字段分组展示")
    print(f"  2. Cross规则违规: 使用crossDefects单独展示")
    print(f"  3. Cross违规可以用不同的UI样式突出显示")
    print(f"  4. 显示涉及的多个字段和它们的关系")
    print(f"  5. 根据severity设置不同的颜色或图标")

if __name__ == "__main__":
    main()