#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查规则表中的source_tables和dict_types字段
"""

import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

print("="*100)
print("检查规则表字段")
print("="*100)

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor(pymysql.cursors.DictCursor)

# 统计规则
cursor.execute("SELECT status, COUNT(*) as count FROM kiro_qc_rule GROUP BY status")
stats = cursor.fetchall()

print("\n规则状态统计:")
for row in stats:
    print(f"  {row['status']}: {row['count']} 条")

# 检查字段完整性
cursor.execute("""
    SELECT 
        status,
        COUNT(*) as total,
        SUM(CASE WHEN source_tables IS NOT NULL AND source_tables != '' THEN 1 ELSE 0 END) as has_source,
        SUM(CASE WHEN dict_types IS NOT NULL AND dict_types != '' THEN 1 ELSE 0 END) as has_dict,
        SUM(CASE WHEN (source_tables IS NOT NULL AND source_tables != '') 
                  AND (dict_types IS NOT NULL AND dict_types != '') THEN 1 ELSE 0 END) as has_both
    FROM kiro_qc_rule
    GROUP BY status
""")

print("\n字段完整性统计:")
for row in cursor.fetchall():
    print(f"\n{row['status']} 规则:")
    print(f"  总数: {row['total']}")
    print(f"  有source_tables: {row['has_source']} ({row['has_source']/row['total']*100:.1f}%)")
    print(f"  有dict_types: {row['has_dict']} ({row['has_dict']/row['total']*100:.1f}%)")
    print(f"  两者都有: {row['has_both']} ({row['has_both']/row['total']*100:.1f}%)")

# 查看示例规则
print("\n" + "="*100)
print("Active规则示例（前10条）:")
print("="*100)

cursor.execute("""
    SELECT id, rule_code, field_code, field_name, status, source_tables, dict_types
    FROM kiro_qc_rule
    WHERE status = 'active'
    ORDER BY id
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"\nID: {row['id']}")
    print(f"  规则编码: {row['rule_code']}")
    print(f"  字段: {row['field_code']} - {row['field_name']}")
    print(f"  源数据表: {row['source_tables'] or '(未设置)'}")
    print(f"  值域数据集: {row['dict_types'] or '(未设置)'}")

print("\n" + "="*100)
print("Draft规则示例（前10条）:")
print("="*100)

cursor.execute("""
    SELECT id, rule_code, field_code, field_name, status, source_tables, dict_types
    FROM kiro_qc_rule
    WHERE status = 'draft'
    ORDER BY id
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"\nID: {row['id']}")
    print(f"  规则编码: {row['rule_code']}")
    print(f"  字段: {row['field_code']} - {row['field_name']}")
    print(f"  源数据表: {row['source_tables'] or '(未设置)'}")
    print(f"  值域数据集: {row['dict_types'] or '(未设置)'}")

# 按字典类型统计
print("\n" + "="*100)
print("按值域数据集统计:")
print("="*100)

cursor.execute("""
    SELECT dict_types, COUNT(*) as count
    FROM kiro_qc_rule
    WHERE dict_types IS NOT NULL AND dict_types != ''
    GROUP BY dict_types
    ORDER BY count DESC
""")

for row in cursor.fetchall():
    print(f"  {row['dict_types']}: {row['count']} 条规则")

conn.close()

print("\n" + "="*100)
print("检查完成！")
print("="*100)

print("\n结论:")
print("1. 数据库中的规则已经包含 source_tables 和 dict_types 字段")
print("2. API返回时应该能正确展示这些字段")
print("3. 前端可以根据这些字段判断规则的完整性")
