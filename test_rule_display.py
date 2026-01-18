#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试规则列表展示
验证source_tables和dict_types字段是否正确返回
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:4101"

def test_rule_search(status=None):
    """测试规则搜索API"""
    print(f"\n{'='*100}")
    print(f"测试规则搜索 - 状态: {status or '全部'}")
    print('='*100)
    
    params = {}
    if status:
        params['status'] = status
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/qc/rules/search",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                rules = data['data']
                print(f"\n找到 {len(rules)} 条规则")
                
                # 统计字段完整性
                complete_count = 0
                partial_count = 0
                empty_count = 0
                
                for rule in rules[:10]:  # 只显示前10条
                    source_tables = rule.get('sourceTables', '')
                    dict_types = rule.get('dictTypes', '')
                    
                    if source_tables and dict_types:
                        complete_count += 1
                        status_icon = "✓ 完整"
                    elif dict_types:
                        partial_count += 1
                        status_icon = "◐ 部分"
                    else:
                        empty_count += 1
                        status_icon = "✗ 空"
                    
                    print(f"\n{status_icon} 规则ID: {rule.get('id')}")
                    print(f"  规则编码: {rule.get('ruleCode', 'N/A')}")
                    print(f"  字段: {rule.get('fieldCode', 'N/A')} - {rule.get('fieldName', 'N/A')}")
                    print(f"  状态: {rule.get('status', 'N/A')}")
                    print(f"  源数据表: {source_tables or '(未设置)'}")
                    print(f"  值域数据集: {dict_types or '(未设置)'}")
                    print(f"  规则类型: {rule.get('ruleType', 'N/A')}")
                    print(f"  扣分: {rule.get('deductScore', 0)}")
                
                if len(rules) > 10:
                    print(f"\n... 还有 {len(rules) - 10} 条规则")
                
                # 统计汇总
                print(f"\n{'='*100}")
                print("字段完整性统计:")
                print(f"  ✓ 完整（source_tables + dict_types）: {complete_count} 条")
                print(f"  ◐ 部分（仅dict_types）: {partial_count} 条")
                print(f"  ✗ 空（都未设置）: {empty_count} 条")
                
                return rules
            else:
                print(f"✗ API返回错误: {data.get('message', 'Unknown')}")
        else:
            print(f"✗ HTTP错误: {response.status_code}")
            print(f"  响应: {response.text[:200]}")
    except Exception as e:
        print(f"✗ 异常: {str(e)}")
    
    return None

def test_rule_detail(rule_id):
    """测试单个规则详情"""
    print(f"\n{'='*100}")
    print(f"测试规则详情 - ID: {rule_id}")
    print('='*100)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/qc/rules/{rule_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                rule = data['data']
                
                print(f"\n规则详情:")
                print(f"  ID: {rule.get('id')}")
                print(f"  规则编码: {rule.get('ruleCode', 'N/A')}")
                print(f"  字段编码: {rule.get('fieldCode', 'N/A')}")
                print(f"  字段名称: {rule.get('fieldName', 'N/A')}")
                print(f"  规则类型: {rule.get('ruleType', 'N/A')}")
                print(f"  状态: {rule.get('status', 'N/A')}")
                print(f"  扣分: {rule.get('deductScore', 0)}")
                print(f"\n  源数据表: {rule.get('sourceTables', '(未设置)')}")
                print(f"  值域数据集: {rule.get('dictTypes', '(未设置)')}")
                print(f"\n  规则描述: {rule.get('description', 'N/A')}")
                print(f"  规范表达式: {rule.get('canonicalExpr', 'N/A')}")
                
                return rule
            else:
                print(f"✗ API返回错误: {data.get('message', 'Unknown')}")
        else:
            print(f"✗ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"✗ 异常: {str(e)}")
    
    return None

def analyze_rules_by_dict_type(rules):
    """按字典类型分析规则"""
    print(f"\n{'='*100}")
    print("按值域数据集分类统计")
    print('='*100)
    
    dict_type_stats = {}
    
    for rule in rules:
        dict_types = rule.get('dictTypes', '')
        if dict_types:
            # 可能有多个字典类型，用逗号分隔
            for dt in dict_types.split(','):
                dt = dt.strip()
                if dt:
                    if dt not in dict_type_stats:
                        dict_type_stats[dt] = []
                    dict_type_stats[dt].append(rule)
    
    print(f"\n发现 {len(dict_type_stats)} 种字典类型:")
    for dt, dt_rules in sorted(dict_type_stats.items()):
        print(f"\n  {dt}: {len(dt_rules)} 条规则")
        for rule in dt_rules[:3]:  # 只显示前3条
            print(f"    - {rule.get('fieldCode')}: {rule.get('fieldName')}")
        if len(dt_rules) > 3:
            print(f"    ... 还有 {len(dt_rules) - 3} 条")

def main():
    """主函数"""
    print("="*100)
    print("  规则列表展示测试")
    print(f"  测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)
    
    # 测试1：查询所有规则
    print("\n【测试1】查询所有规则")
    all_rules = test_rule_search()
    
    # 测试2：查询active规则
    print("\n【测试2】查询active规则")
    active_rules = test_rule_search(status='active')
    
    # 测试3：查询draft规则
    print("\n【测试3】查询draft规则")
    draft_rules = test_rule_search(status='draft')
    
    # 测试4：查看单个规则详情
    if all_rules and len(all_rules) > 0:
        print("\n【测试4】查看规则详情")
        test_rule_detail(all_rules[0]['id'])
    
    # 测试5：按字典类型分析
    if all_rules:
        print("\n【测试5】按字典类型分析")
        analyze_rules_by_dict_type(all_rules)
    
    print("\n" + "="*100)
    print("测试完成！")
    print("="*100)
    
    print("\n总结:")
    print("1. 规则列表API应该返回 sourceTables 和 dictTypes 字段")
    print("2. 已完善的规则（active）应该有完整的字段信息")
    print("3. 未完善的规则（draft）如果有明确的dictTypes，也应该显示")
    print("4. 前端页面可以根据这些字段展示规则的完整性状态")

if __name__ == "__main__":
    main()
