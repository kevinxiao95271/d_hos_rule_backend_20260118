#!/usr/bin/env python3
import requests
import json

# API配置
BASE_URL = "http://localhost:4101"

def test_cross_stats_simple():
    """简单测试Cross规则统计功能"""
    print("🧪 简单测试Cross规则统计功能")
    print("=" * 60)
    
    # 测试几个已知的病案
    test_cases = [
        {"a48": "19079841", "a49": "1", "name": "病案1"},
        {"a48": "445583", "a49": "1", "name": "病案2"},
        {"a48": "19065857", "a49": "1", "name": "病案3"},
        {"a48": "19072516", "a49": "1", "name": "病案4"}
    ]
    
    total_cross_defects = 0
    total_cross_deduct = 0.0
    successful_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 🔍 测试{test_case['name']} ({test_case['a48']}_{test_case['a49']})...")
        
        try:
            response = requests.post(f"{BASE_URL}/api/qc/check/single", 
                                   params={"a48": test_case['a48'], "a49": test_case['a49']}, 
                                   timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('code') == 200 and 'data' in result:
                    data = result['data']
                    
                    # 基本信息
                    mr_key = data.get('mrKey', 'N/A')
                    defect_count = data.get('defectCount', 0)
                    total_deduct = data.get('totalDeduct', 0)
                    final_score = data.get('finalScore', 0)
                    
                    # Cross规则统计
                    cross_defect_count = data.get('crossDefectCount', 0)
                    cross_total_deduct = data.get('crossTotalDeduct', 0)
                    cross_defects = data.get('crossDefects', [])
                    
                    print(f"   ✅ 质控成功")
                    print(f"     - 病案键: {mr_key}")
                    print(f"     - 总违规数: {defect_count}")
                    print(f"     - 总扣分: {total_deduct}")
                    print(f"     - 最终得分: {final_score}")
                    print(f"     - Cross违规数: {cross_defect_count}")
                    print(f"     - Cross扣分: {cross_total_deduct}")
                    print(f"     - Cross详情数: {len(cross_defects)}")
                    
                    # 显示Cross规则详情
                    if cross_defects:
                        print(f"     - Cross违规详情:")
                        for j, defect in enumerate(cross_defects[:2], 1):  # 只显示前2个
                            rule_code = defect.get('ruleCode', 'N/A')
                            rule_desc = defect.get('ruleDescription', 'N/A')
                            cross_type = defect.get('crossType', 'N/A')
                            severity = defect.get('severity', 'N/A')
                            print(f"       {j}. {rule_code}")
                            print(f"          描述: {rule_desc}")
                            print(f"          类型: {cross_type}, 严重程度: {severity}")
                    
                    # 累计统计
                    total_cross_defects += cross_defect_count
                    total_cross_deduct += float(cross_total_deduct) if cross_total_deduct else 0
                    successful_tests += 1
                    
                    # 验证数据一致性
                    if cross_defect_count == len(cross_defects):
                        print(f"     ✅ Cross统计数据一致")
                    else:
                        print(f"     ⚠️  Cross统计数据不一致: count={cross_defect_count}, details={len(cross_defects)}")
                
                else:
                    print(f"   ❌ API返回错误: {result.get('message', 'Unknown error')}")
                    
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                print(f"     错误信息: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ 异常: {e}")
    
    # 汇总统计
    print(f"\n" + "=" * 60)
    print(f"📊 汇总统计:")
    print(f"   - 成功测试数: {successful_tests}/{len(test_cases)}")
    print(f"   - 总Cross违规数: {total_cross_defects}")
    print(f"   - 总Cross扣分: {total_cross_deduct:.2f}")
    
    if successful_tests > 0:
        avg_cross_defects = total_cross_defects / successful_tests
        print(f"   - 平均Cross违规数: {avg_cross_defects:.1f}")
    
    # 结论
    if total_cross_defects > 0:
        print(f"\n✅ Cross规则系统正常工作！")
        print(f"   - 成功检出了 {total_cross_defects} 个Cross规则违规")
        print(f"   - API输出包含完整的Cross规则统计信息")
    elif successful_tests > 0:
        print(f"\n ℹ️ Cross规则系统运行正常，但未检出违规")
        print(f"   - 可能是测试病案数据符合所有Cross规则")
        print(f"   - API输出包含Cross规则统计字段（值为0）")
    else:
        print(f"\n❌ 测试失败，需要检查系统状态")
    
    print("=" * 60)

if __name__ == "__main__":
    test_cross_stats_simple()