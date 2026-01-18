#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成正确的SQL语句
"""

import json
from datetime import datetime

# 读取分析结果
with open('rule_analysis_result.json', 'r', encoding='utf-8') as f:
    result = json.load(f)

high_confidence_rules = result['high_confidence_rules']

print(f"读取到 {len(high_confidence_rules)} 条高置信度规则")

# 生成SQL
sql_file = 'auto_generated_rules_fixed.sql'
with open(sql_file, 'w', encoding='utf-8') as f:
    f.write("-- 自动生成的质控规则（修正版）\n")
    f.write(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"-- 高置信度规则: {len(high_confidence_rules)} 条\n\n")
    
    for rule in high_confidence_rules:
        if rule['rule_type'] == 'value_check' and rule['dict_type']:
            expression = f"{rule['field_code']} IN {rule['dict_type']}"
            message = f"{rule['field_name']}必须在{rule['dict_type']}字典范围内"
            score = 2 if 'required' in rule['reason'] else 1
            rule_code = f"RULE_{rule['field_code']}_{rule['dict_type']}"
            
            sql = f"""INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    '{rule_code}', '{rule['field_code']}', '{rule['field_name']}', 'value_check', '{expression}',
    '{message}', {score}, 'draft', '{rule['source_tables']}', '{rule['dict_type']}',
    NOW(), NOW()
);\n\n"""
            f.write(sql)
        
        elif rule['rule_type'] == 'range_check' and rule['range']:
            expression = f"{rule['field_code']} >= {rule['range'][0]} AND {rule['field_code']} <= {rule['range'][1]}"
            message = f"{rule['field_name']}应在{rule['range'][0]}-{rule['range'][1]}范围内"
            rule_code = f"RULE_{rule['field_code']}_RANGE"
            
            sql = f"""INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    '{rule_code}', '{rule['field_code']}', '{rule['field_name']}', 'range_check', '{expression}',
    '{message}', 2, 'draft', '{rule['source_tables']}', '',
    NOW(), NOW()
);\n\n"""
            f.write(sql)

print(f"✓ SQL已生成到: {sql_file}")
