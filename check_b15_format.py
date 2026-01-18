#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查B15字段格式
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

print("="*100)
print("检查B15字段格式")
print("="*100)

# 1. 查看B15字段的数据类型
print("\n1. B15字段数据类型:")
cursor.execute("DESCRIBE d_mr B15")
print(f"  {cursor.fetchone()}")

# 2. 查看2020年的B15样本
print("\n2. 2020年B15样本（前20条）:")
cursor.execute("""
    SELECT A48, A49, B15
    FROM d_mr
    WHERE B15 LIKE '2020%'
    LIMIT 20
""")
for a48, a49, b15 in cursor.fetchall():
    print(f"  {b15}")

# 3. 测试不同的日期解析方式
print("\n3. 测试日期解析:")

# 方法1: STR_TO_DATE with %Y/%m/%d %H:%i
cursor.execute("""
    SELECT COUNT(*) as count
    FROM d_mr
    WHERE YEAR(STR_TO_DATE(B15, '%Y/%m/%d %H:%i')) = 2020
""")
count1 = cursor.fetchone()[0]
print(f"  STR_TO_DATE(B15, '%Y/%m/%d %H:%i'): {count1:,} 条")

# 方法2: STR_TO_DATE with %Y/%c/%e %H:%i (允许单数字月日)
cursor.execute("""
    SELECT COUNT(*) as count
    FROM d_mr
    WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2020
""")
count2 = cursor.fetchone()[0]
print(f"  STR_TO_DATE(B15, '%Y/%c/%e %H:%i'): {count2:,} 条")

# 方法3: 直接用YEAR函数（如果B15是datetime类型）
cursor.execute("""
    SELECT COUNT(*) as count
    FROM d_mr
    WHERE YEAR(B15) = 2020
""")
count3 = cursor.fetchone()[0]
print(f"  YEAR(B15): {count3:,} 条")

# 方法4: 字符串匹配
cursor.execute("""
    SELECT COUNT(*) as count
    FROM d_mr
    WHERE B15 LIKE '2020%'
""")
count4 = cursor.fetchone()[0]
print(f"  B15 LIKE '2020%': {count4:,} 条")

# 4. 检查B15格式的多样性
print("\n4. B15格式样本:")
cursor.execute("""
    SELECT DISTINCT SUBSTRING(B15, 1, 20) as format_sample
    FROM d_mr
    WHERE B15 IS NOT NULL
    LIMIT 10
""")
for (sample,) in cursor.fetchall():
    print(f"  {sample}")

conn.close()

print("\n" + "="*100)
print("检查完成！")
print("="*100)
