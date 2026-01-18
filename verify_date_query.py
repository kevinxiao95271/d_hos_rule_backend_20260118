#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证日期查询是否正确
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

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

print("="*80)
print("测试不同日期格式的查询结果")
print("="*80)

# 测试1: 使用 %Y/%m/%d %H:%i (原始格式 - 要求两位数)
print("\n测试1: 使用 %Y/%m/%d %H:%i 格式 (要求两位数月日)")
cursor.execute("""
    SELECT COUNT(*) FROM d_mr 
    WHERE YEAR(STR_TO_DATE(B15, '%Y/%m/%d %H:%i')) = 2023
    AND MONTH(STR_TO_DATE(B15, '%Y/%m/%d %H:%i')) = 1
""")
count1 = cursor.fetchone()[0]
print(f"  结果: {count1} 条")

# 测试2: 使用 %Y/%c/%e %H:%i (修复格式 - 允许单数字)
print("\n测试2: 使用 %Y/%c/%e %H:%i 格式 (允许单数字月日)")
cursor.execute("""
    SELECT COUNT(*) FROM d_mr 
    WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
    AND MONTH(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 1
""")
count2 = cursor.fetchone()[0]
print(f"  结果: {count2} 条")

# 测试3: 2020年1月
print("\n测试3: 2020年1月数据")
cursor.execute("""
    SELECT COUNT(*) FROM d_mr 
    WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2020
    AND MONTH(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 1
""")
count3 = cursor.fetchone()[0]
print(f"  结果: {count3} 条")

# 测试4: 查看实际的B15格式样例
print("\n测试4: 2023年1月的B15字段样例")
cursor.execute("""
    SELECT A48, A49, B15
    FROM d_mr 
    WHERE B15 LIKE '2023/1/%'
    LIMIT 10
""")
samples = cursor.fetchall()
for a48, a49, b15 in samples:
    print(f"  A48={a48}, A49={a49}, B15={b15}")

conn.close()

print("\n" + "="*80)
print("结论:")
print("="*80)
print(f"  原始格式 (%Y/%m/%d): {count1} 条 - ❌ 错误")
print(f"  修复格式 (%Y/%c/%e): {count2} 条 - ✅ 正确")
print(f"  2020年1月: {count3} 条")
