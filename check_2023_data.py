#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查2023年数据
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
print("检查2023年数据分布")
print("="*80)

# 总数
cursor.execute("SELECT COUNT(*) FROM d_mr WHERE B15 LIKE '2023/%'")
total_2023 = cursor.fetchone()[0]
print(f"\n2023年总数 (LIKE '2023/%'): {total_2023} 条")

# 按月分布
print("\n2023年按月分布:")
for month in range(1, 13):
    cursor.execute(f"SELECT COUNT(*) FROM d_mr WHERE B15 LIKE '2023/{month}/%'")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"  {month}月: {count} 条")

# 使用STR_TO_DATE
print("\n使用STR_TO_DATE解析:")
cursor.execute("""
    SELECT COUNT(*) FROM d_mr 
    WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
""")
count_parsed = cursor.fetchone()[0]
print(f"  总数: {count_parsed} 条")

# 检查无法解析的记录
cursor.execute("""
    SELECT COUNT(*) FROM d_mr 
    WHERE B15 LIKE '2023/%'
    AND STR_TO_DATE(B15, '%Y/%c/%e %H:%i') IS NULL
""")
unparseable = cursor.fetchone()[0]
print(f"  无法解析: {unparseable} 条")

# 查看所有2023年的B15值
print("\n所有2023年的B15值:")
cursor.execute("""
    SELECT A48, A49, B15
    FROM d_mr 
    WHERE B15 LIKE '2023/%'
    ORDER BY B15
""")
all_2023 = cursor.fetchall()
for a48, a49, b15 in all_2023:
    parsed = "✓" if b15 else "✗"
    print(f"  {parsed} A48={a48}, A49={a49}, B15={b15}")

conn.close()
