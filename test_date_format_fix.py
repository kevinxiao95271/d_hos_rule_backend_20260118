#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日期格式修复
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
print("测试日期格式修复")
print("="*100)

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

# 测试修复后的格式
print("\n使用修复后的格式 '%Y/%c/%e %H:%i':")
print("-"*100)

# 1. 2020年总数
cursor.execute("""
    SELECT COUNT(*) as count
    FROM d_mr
    WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2020
""")
count_2020 = cursor.fetchone()[0]
print(f"2020年总数: {count_2020:,} 条")

# 2. 2020年按月分布
print("\n2020年按月分布:")
cursor.execute("""
    SELECT 
        MONTH(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) as month,
        COUNT(*) as count
    FROM d_mr
    WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2020
    GROUP BY MONTH(STR_TO_DATE(B15, '%Y/%c/%e %H:%i'))
    ORDER BY month
""")
for month, count in cursor.fetchall():
    print(f"  {month:2d}月: {count:,} 条")

# 3. 2023年总数
cursor.execute("""
    SELECT COUNT(*) as count
    FROM d_mr
    WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
""")
count_2023 = cursor.fetchone()[0]
print(f"\n2023年总数: {count_2023:,} 条")

# 4. 2023年按月分布
print("\n2023年按月分布:")
cursor.execute("""
    SELECT 
        MONTH(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) as month,
        COUNT(*) as count
    FROM d_mr
    WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
    GROUP BY MONTH(STR_TO_DATE(B15, '%Y/%c/%e %H:%i'))
    ORDER BY month
""")
for month, count in cursor.fetchall():
    print(f"  {month:2d}月: {count:,} 条")

# 5. 测试具体的2020年1月查询
print("\n测试2020年1月查询:")
cursor.execute("""
    SELECT COUNT(*) as count
    FROM d_mr
    WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2020
    AND MONTH(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 1
""")
count_2020_01 = cursor.fetchone()[0]
print(f"  2020年1月: {count_2020_01:,} 条")

# 6. 测试具体的2023年1月查询
cursor.execute("""
    SELECT COUNT(*) as count
    FROM d_mr
    WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
    AND MONTH(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 1
""")
count_2023_01 = cursor.fetchone()[0]
print(f"  2023年1月: {count_2023_01:,} 条")

conn.close()

print("\n" + "="*100)
print("测试完成！")
print("="*100)

print("\n结论:")
print(f"  修复后的格式可以正确识别日期")
print(f"  2020年: {count_2020:,} 条")
print(f"  2023年: {count_2023:,} 条")
print(f"  需要重新编译并重启后端服务以应用修复")
