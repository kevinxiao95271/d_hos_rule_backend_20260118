#!/usr/bin/env python3
import requests
import json
import time

# API配置
BASE_URL = "http://localhost:4101"

def test_cross_stats_api():
    """测试Cross规则统计API"""
    print("🧪 测试Cross规则统计API")
    print("=" * 60)
    
    # 1. 测试单个病案质控的Cross规则统计
    print("\n1. 🔍 测试单个病案质控...")
    try:
        response = requests.post(f"{BASE_URL}/api/qc/check/single", 
                               params={"a48": "19079841", "a49": "1"}, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            
            print(f"✅ 单病案质控成功")
            print(f"   病案键: {data.get('mrKey')}")
            print(f"   总违规数: {data.get('defectCount', 0)}")
            print(f"   总扣分: {data.get('totalDeduct', 0)}")
            print(f"   最终得分: {data.get('finalScore', 0)}")
            
            # 检查Cross规则统计
            cross_defect_count = data.get('crossDefectCount', 0)
            cross_total_deduct = data.get('crossTotalDeduct', 0)
            cross_defects = data.get('crossDefects', [])
            
            print(f"   📊 Cross规则统计:")
            print(f"     - Cross违规数量: {cross_defect_count}")
            print(f"     - Cross总扣分: {cross_total_deduct}")
            print(f"     - Cross违规详情数: {len(cross_defects)}")
            
            if cross_defects:
                print(f"     - Cross违规详情:")
                for i, defect in enumerate(cross_defects[:3], 1):
                    print(f"       {i}. {defect.get('ruleCode')}: {defect.get('ruleDescription')}")
                    print(f"          类型: {defect.get('crossType')}, 严重程度: {defect.get('severity')}")
            
            # 验证数据一致性
            if cross_defect_count == len(cross_defects):
                print(f"   ✅ Cross规则统计数据一致")
            else:
                print(f"   ⚠️  Cross规则统计数据不一致: count={cross_defect_count}, details={len(cross_defects)}")
                
        else:
            print(f"❌ 单病案质控失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 单病案质控异常: {e}")
    
    # 2. 测试批量质控的Cross规则统计
    print("\n2. 📈 测试批量质控Cross规则统计...")
    try:
        response = requests.post(f"{BASE_URL}/api/qc/check/batch", json={
            "periodType": "month",
            "year": 2023,
            "month": 1
        }, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            
            print(f"✅ 批量质控成功")
            print(f"   📋 基本统计:")
            print(f"     - 处理病案数: {data.get('caseCount', 0)}")
            print(f"     - 总违规数: {data.get('totalDefectCount', 0)}")
            print(f"     - 平均违规数: {data.get('avgDefect', 0)}")
            print(f"     - 平均得分: {data.get('avgScore', 0)}")
            
            # 检查Cross规则统计
            cross_defect_count = data.get('crossDefectCount', 0)
            cross_total_deduct = data.get('crossTotalDeduct', 0)
            avg_cross_defect = data.get('avgCrossDefect', 0)
            
            print(f"   🎯 Cross规则统计:")
            print(f"     - Cross违规总数: {cross_defect_count}")
            print(f"     - Cross总扣分: {cross_total_deduct}")
            print(f"     - 平均Cross违规数: {avg_cross_defect}")
            
            # 计算Cross规则占比
            total_defects = data.get('totalDefectCount', 0)
            if total_defects > 0:
                cross_ratio = (cross_defect_count / total_defects) * 100
                print(f"     - Cross规则占比: {cross_ratio:.1f}%")
            
            if cross_defect_count > 0:
                print(f"   ✅ 检出了Cross规则违规！")
            else:
                print(f"   ⚠️  未检出Cross规则违规")
                
        else:
            print(f"❌ 批量质控失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 批量质控异常: {e}")
    
    # 3. 测试多个病案的Cross规则统计
    print("\n3. 🔄 测试多个病案Cross规则统计...")
    test_cases = [
        {"a48": "19079841", "a49": "1"},
        {"a48": "445583", "a49": "1"},
        {"a48": "2023001", "a49": "001"}
    ]
    
    total_cross_defects = 0
    total_cross_deduct = 0
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            response = requests.post(f"{BASE_URL}/api/qc/check/single", 
                                   params=test_case, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                data = result.get('data', {})
                
                cross_count = data.get('crossDefectCount', 0)
                cross_deduct = data.get('crossTotalDeduct', 0)
                
                print(f"   病案{i} ({test_case['a48']}_{test_case['a49']}):")
                print(f"     - Cross违规: {cross_count} 个")
                print(f"     - Cross扣分: {cross_deduct}")
                
                total_cross_defects += cross_count
                total_cross_deduct += float(cross_deduct) if cross_deduct else 0
                
            else:
                print(f"   病案{i}: 检查失败 ({response.status_code})")
                
        except Exception as e:
            print(f"   病案{i}: 检查异常 - {e}")
    
    print(f"\\n   📊 汇总统计:")
    print(f"     - 总Cross违规数: {total_cross_defects}")
    print(f"     - 总Cross扣分: {total_cross_deduct:.2f}")
    print(f"     - 平均Cross违规: {total_cross_defects/len(test_cases):.1f}")
    
    print("\n" + "=" * 60)
    print("🎯 Cross规则统计API测试完成")
    
    if total_cross_defects > 0:
        print("✅ Cross规则系统正常工作，已检出违规！")
    else:
        print("⚠️  Cross规则系统未检出违规，可能需要检查规则逻辑")
    
    print("=" * 60)

if __name__ == "__main__":
    test_cross_stats_api()