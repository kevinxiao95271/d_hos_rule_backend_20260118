#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查规则字典配置
"""

import pymysql

# 数据库连接
conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    password='123456',
    database='d_hosq_traegj_20260115',
    charset='utf8mb4'
)

cursor = conn.cursor()

print("="*80)
print("检查规则表中的字典配置")
print("="*80)
print()

# 查询所有配置了字典的规则
sql = """
SELECT rule_code, field_code, field_name, dict_types, description
FROM kiro_qc_rule
WHERE dict_types IS NOT NULL AND dict_types != ''
ORDER BY rule_code
"""

cursor.execute(sql)
rules = cursor.fetchall()

print(f"共找到 {len(rules)} 条配置了字典的规则")
print()

# 按字典类型分组统计
dict_type_count = {}
for rule in rules:
    dict_type = rule[3]
    if dict_type not in dict_type_count:
        dict_type_count[dict_type] = []
    dict_type_count[dict_type].append(rule)

print("字典类型分布:")
print("-"*80)
for dict_type, rule_list in sorted(dict_type_count.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"{dict_type}: {len(rule_list)} 条规则")

print()
print("="*80)
print("详细规则列表 (前30条):")
print("="*80)
print()

for i, rule in enumerate(rules[:30], 1):
    rule_code, field_code, field_name, dict_types, description = rule
    print(f"{i}. {rule_code}")
    print(f"   字段: {field_code} ({field_name})")
    print(f"   字典: {dict_types}")
    print(f"   描述: {description}")
    print()

# 检查RC013的具体使用情况
print("="*80)
print("RC013字典使用情况分析:")
print("="*80)
print()

rc013_rules = [r for r in rules if r[3] == 'RC013']
print(f"使用RC013的规则数: {len(rc013_rules)}")
print()

if rc013_rules:
    print("使用RC013的字段:")
    for rule in rc013_rules[:10]:
        print(f"  - {rule[1]} ({rule[2]}): {rule[4]}")

cursor.close()
conn.close()
