#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

# API配置
BASE_URL = "http://localhost:4101"
API_ENDPOINTS = {
    'qc_single': f"{BASE_URL}/api/qc/check/single",
    'service_status': f"{BASE_URL}/api/qc/status"
}

def test_service_status():
    """测试服务状态"""
    print("🔍 检查服务状态...")
    try:
        response = requests.get(API_ENDPOINTS['service_status'], timeout=5)
        if response.status_code == 200:
            print("✅ 服务运行正常")
            return True
        else:
            print(f"❌ 服务状态异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 服务连接失败: {e}")
        return False

def test_cross_rule_functionality():
    """测试跨字段规则功能"""
    
    print("\n" + "="*80)
    print("🧪 测试跨字段规则功能")
    print("="*80)
    
    # 使用真实的病案记录进行测试
    test_cases = [
        {
            "name": "测试病案1 - 基础跨字段规则检查",
            "a48": "19063452",
            "a49": "1"
        },
        {
            "name": "测试病案2 - 年龄性别相关规则",
            "a48": "19065857",
            "a49": "1"
        },
        {
            "name": "测试病案3 - 诊断编码相关规则",
            "a48": "19071898",
            "a49": "1"
        },
        {
            "name": "测试病案4 - 输血相关规则",
            "a48": "19072516",
            "a49": "1"
        },
        {
            "name": "测试病案5 - 综合规则检查",
            "a48": "19072517",
            "a49": "1"
        }
    ]
    
    # 执行测试
    total_tests = len(test_cases)
    successful_tests = 0
    cross_rule_violations = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试 {i}/{total_tests}: {test_case['name']}")
        
        try:
            # 发送QC请求
            params = {
                'a48': test_case['a48'],
                'a49': test_case['a49']
            }
            
            response = requests.post(
                API_ENDPOINTS['qc_single'],
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    data = result.get('data', {})
                    violations = data.get('violations', [])
                    
                    print(f"   病案: {test_case['a48']}-{test_case['a49']}")
                    print(f"   总违规数: {len(violations)}")
                    
                    # 统计跨字段违规
                    cross_violations = [v for v in violations if v.get('ruleCode', '').startswith('CROSS_')]
                    if cross_violations:
                        cross_rule_violations += len(cross_violations)
                        print(f"   跨字段违规数: {len(cross_violations)}")
                        
                        # 显示跨字段违规详情
                        print(f"   跨字段违规详情:")
                        for violation in cross_violations[:3]:  # 显示前3条
                            print(f"     - {violation.get('ruleCode')}: {violation.get('ruleDescription', '')[:60]}...")
                            print(f"       字段: {violation.get('fieldCode')} = '{violation.get('actualValue')}'")
                            print(f"       期望: {violation.get('expectedValue', '')[:40]}...")
                            print(f"       扣分: {violation.get('deductScore')}")
                    else:
                        print(f"   ✅ 无跨字段违规")
                    
                    # 显示其他类型违规统计
                    other_violations = [v for v in violations if not v.get('ruleCode', '').startswith('CROSS_')]
                    if other_violations:
                        print(f"   其他违规数: {len(other_violations)}")
                    
                    successful_tests += 1
                    print(f"   ✅ 测试执行成功")
                        
                else:
                    print(f"   ❌ API返回失败: {result.get('message', '未知错误')}")
                
            else:
                print(f"   ❌ API请求失败: {response.status_code}")
                print(f"   响应: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ 测试异常: {e}")
    
    # 测试总结
    print(f"\n" + "="*80)
    print(f"📊 跨字段规则测试总结")
    print(f"   总测试数: {total_tests}")
    print(f"   成功执行: {successful_tests}")
    print(f"   执行成功率: {successful_tests/total_tests*100:.1f}%")
    print(f"   发现跨字段违规总数: {cross_rule_violations}")
    
    if successful_tests >= total_tests * 0.8:  # 80%成功率
        if cross_rule_violations > 0:
            print(f"🎉 跨字段规则功能正常！发现了 {cross_rule_violations} 个跨字段违规")
        else:
            print(f"✅ 跨字段规则功能正常运行，当前测试病案无跨字段违规")
    else:
        print(f"⚠️  部分测试失败，需要检查系统状态")
    
    print("="*80)

def test_specific_cross_rules():
    """测试特定的跨字段规则类型"""
    
    print("\n" + "="*80)
    print("🔬 测试特定跨字段规则类型")
    print("="*80)
    
    # 检查跨字段规则是否被正确加载和执行
    test_records = [
        "19063452-1", "19065857-1", "19071898-1", "19072516-1", "19072517-1"
    ]
    
    cross_rule_types_found = set()
    
    for record in test_records:
        a48, a49 = record.split('-')
        print(f"\n🔍 检查记录 {record}:")
        
        try:
            params = {'a48': a48, 'a49': a49}
            response = requests.post(API_ENDPOINTS['qc_single'], params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    violations = result.get('data', {}).get('violations', [])
                    cross_violations = [v for v in violations if v.get('ruleCode', '').startswith('CROSS_')]
                    
                    if cross_violations:
                        for violation in cross_violations:
                            rule_code = violation.get('ruleCode', '')
                            if 'FIELD_PAIR' in rule_code:
                                cross_rule_types_found.add('field_pair')
                            elif 'AGE' in rule_code:
                                cross_rule_types_found.add('age_diagnosis')
                            elif 'ANESTHESIA' in rule_code:
                                cross_rule_types_found.add('conditional_required')
                            elif 'TRANSFUSION' in rule_code:
                                cross_rule_types_found.add('transfusion_logic')
                            
                            print(f"   找到跨字段违规: {rule_code}")
                    else:
                        print(f"   无跨字段违规")
                        
        except Exception as e:
            print(f"   测试异常: {e}")
    
    print(f"\n📊 跨字段规则类型统计:")
    print(f"   发现的规则类型: {list(cross_rule_types_found)}")
    
    expected_types = ['field_pair', 'age_diagnosis', 'conditional_required', 'transfusion_logic']
    missing_types = set(expected_types) - cross_rule_types_found
    
    if missing_types:
        print(f"   未触发的规则类型: {list(missing_types)}")
        print(f"   这可能是因为测试数据不满足触发条件")
    else:
        print(f"   ✅ 所有规则类型都有触发记录")
    
    print("="*80)

def main():
    """主函数"""
    print("🚀 跨字段规则综合测试")
    
    # 检查服务状态
    if not test_service_status():
        print("❌ 服务未启动，请先启动服务")
        return
    
    # 等待服务完全启动
    print("⏳ 等待服务完全启动...")
    time.sleep(2)
    
    # 执行功能测试
    test_cross_rule_functionality()
    
    # 执行特定规则类型测试
    test_specific_cross_rules()

if __name__ == "__main__":
    main()