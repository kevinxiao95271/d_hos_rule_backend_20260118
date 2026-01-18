#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查2020年和2023年的数据
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

print("连接数据库...")
conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

print("\n检查2020年数据...")
cursor.execute("SELECT COUNT(*) FROM d_mr WHERE YEAR(B15) = 2020")
count_2020 = cursor.fetchone()[0]
print(f"2020年: {count_2020:,} 条")

print("\n检查2023年数据...")
cursor.execute("SELECT COUNT(*) FROM d_mr WHERE YEAR(B15) = 2023")
count_2023 = cursor.fetchone()[0]
print(f"2023年: {count_2023:,} 条")

print("\n2020年按月分布:")
cursor.execute("""
    SELECT MONTH(B15) as month, COUNT(*) as count
    FROM d_mr
    WHERE YEAR(B15) = 2020
    GROUP BY MONTH(B15)
    ORDER BY month
""")
for month, count in cursor.fetchall():
    print(f"  {month:2d}月: {count:,} 条")

print("\n2023年按月分布:")
cursor.execute("""
    SELECT MONTH(B15) as month, COUNT(*) as count
    FROM d_mr
    WHERE YEAR(B15) = 2023
    GROUP BY MONTH(B15)
    ORDER BY month
""")
for month, count in cursor.fetchall():
    print(f"  {month:2d}月: {count:,} 条")

print("\n获取2020年样本病案...")
cursor.execute("""
    SELECT A48, A49, B15
    FROM d_mr
    WHERE YEAR(B15) = 2020
    LIMIT 3
""")
print("2020年样本:")
for a48, a49, b15 in cursor.fetchall():
    print(f"  A48={a48}, A49={a49}, B15={b15}")

print("\n获取2023年样本病案...")
cursor.execute("""
    SELECT A48, A49, B15
    FROM d_mr
    WHERE YEAR(B15) = 2023
    LIMIT 3
""")
print("2023年样本:")
for a48, a49, b15 in cursor.fetchall():
    print(f"  A48={a48}, A49={a49}, B15={b15}")

conn.close()
print("\n完成！")
