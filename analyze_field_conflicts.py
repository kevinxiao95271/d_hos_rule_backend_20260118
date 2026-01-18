#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析规则表中的字段编码冲突
"""
import requests
import json
from collections import defaultdict

def analyze_field_conflicts():
    """分析字段编码冲突"""
    print("正在获取所有规则...")

    # 获取所有规则
    response = requests.get("http://localhost:4101/api/qc/rules")
    data = response.json()

    if data['code'] != 200:
        print(f"错误: {data['message']}")
        return

    rules = data['data']
    print(f"共获取 {len(rules)} 条规则\n")

    # 按字段编码分组
    field_map = defaultdict(lambda: {'names': set(), 'rules': []})

    for rule in rules:
        field_code = rule['fieldCode']
        field_name = rule['fieldName']
        field_map[field_code]['names'].add(field_name)
        field_map[field_code]['rules'].append({
            'id': rule['id'],
            'ruleCode': rule['ruleCode'],
            'fieldName': field_name,
            'ruleType': rule['ruleType'],
            'description': rule['description']
        })

    # 找出有冲突的字段
    conflicts = {k: v for k, v in field_map.items() if len(v['names']) > 1}

    print(f"=" * 80)
    print(f"发现 {len(conflicts)} 个字段编码有多个不同的字段名称")
    print(f"=" * 80)
    print()

    # 输出前20个冲突
    for i, (field_code, info) in enumerate(sorted(conflicts.items())[:20], 1):
        print(f"{i}. 字段编码: {field_code}")
        print(f"   字段名称冲突: {list(info['names'])}")
        print(f"   涉及规则数: {len(info['rules'])}")

        for rule in info['rules']:
            print(f"     - [ID:{rule['id']}] {rule['ruleCode']}: {rule['fieldName']} ({rule['ruleType']})")
        print()

    if len(conflicts) > 20:
        print(f"... 还有 {len(conflicts) - 20} 个冲突未显示")

    # 保存完整报告
    with open('field_conflicts_report.txt', 'w', encoding='utf-8') as f:
        f.write(f"字段编码冲突分析报告\n")
        f.write(f"=" * 80 + "\n")
        f.write(f"总规则数: {len(rules)}\n")
        f.write(f"冲突字段数: {len(conflicts)}\n")
        f.write(f"=" * 80 + "\n\n")

        for field_code, info in sorted(conflicts.items()):
            f.write(f"字段编码: {field_code}\n")
            f.write(f"字段名称冲突: {list(info['names'])}\n")
            f.write(f"涉及规则:\n")
            for rule in info['rules']:
                f.write(f"  - [ID:{rule['id']}] {rule['ruleCode']}\n")
                f.write(f"    字段名: {rule['fieldName']}\n")
                f.write(f"    规则类型: {rule['ruleType']}\n")
                f.write(f"    说明: {rule['description']}\n")
            f.write("\n")

    print(f"\n完整报告已保存到: field_conflicts_report.txt")

if __name__ == '__main__':
    analyze_field_conflicts()
