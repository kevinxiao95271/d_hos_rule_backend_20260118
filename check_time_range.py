#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查时间范围判定逻辑
"""

import pymysql
from datetime import datetime

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

print("="*100)
print("检查时间范围判定")
print("="*100)

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor(pymysql.cursors.DictCursor)

# 1. 检查B15字段的数据类型和格式
print("\n1. 检查B15字段类型:")
cursor.execute("""
    SELECT COLUMN_TYPE, DATA_TYPE, COLUMN_COMMENT
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'd_hosq_traegj_20260115'
    AND TABLE_NAME = 'd_mr'
    AND COLUMN_NAME = 'B15'
""")
col_info = cursor.fetchone()
print(f"  字段类型: {col_info['COLUMN_TYPE']}")
print(f"  数据类型: {col_info['DATA_TYPE']}")
print(f"  注释: {col_info['COLUMN_COMMENT']}")

# 2. 查看B15字段的实际数据样本
print("\n2. B15字段数据样本:")
cursor.execute("SELECT B15 FROM d_mr LIMIT 10")
for row in cursor.fetchall():
    print(f"  {row['B15']} (类型: {type(row['B15'])})")

# 3. 按年份统计（使用不同的方法）
print("\n3. 按年份统计（方法1 - YEAR函数）:")
cursor.execute("""
    SELECT YEAR(B15) as year, COUNT(*) as count
    FROM d_mr
    WHERE B15 IS NOT NULL
    GROUP BY YEAR(B15)
    ORDER BY year
""")
for row in cursor.fetchall():
    print(f"  {row['year']}: {row['count']:,} 条")

# 4. 按年份统计（方法2 - 字符串截取）
print("\n4. 按年份统计（方法2 - SUBSTRING）:")
cursor.execute("""
    SELECT SUBSTRING(B15, 1, 4) as year, COUNT(*) as count
    FROM d_mr
    WHERE B15 IS NOT NULL
    GROUP BY SUBSTRING(B15, 1, 4)
    ORDER BY year
""")
for row in cursor.fetchall():
    print(f"  {row['year']}: {row['count']:,} 条")

# 5. 检查2020年的数据
print("\n5. 2020年数据详情:")
cursor.execute("""
    SELECT 
        MIN(B15) as min_date,
        MAX(B15) as max_date,
        COUNT(*) as count
    FROM d_mr
    WHERE YEAR(B15) = 2020
""")
row = cursor.fetchone()
print(f"  最早日期: {row['min_date']}")
print(f"  最晚日期: {row['max_date']}")
print(f"  总数: {row['count']:,}")

# 6. 检查2020年按月分布
print("\n6. 2020年按月分布:")
cursor.execute("""
    SELECT 
        MONTH(B15) as month,
        COUNT(*) as count
    FROM d_mr
    WHERE YEAR(B15) = 2020
    GROUP BY MONTH(B15)
    ORDER BY month
""")
for row in cursor.fetchall():
    print(f"  {row['month']:2d}月: {row['count']:,} 条")

# 7. 检查时间范围查询
print("\n7. 测试时间范围查询:")

# 测试1: 2020年全年
cursor.execute("""
    SELECT COUNT(*) as count
    FROM d_mr
    WHERE B15 >= '2020-01-01' AND B15 < '2021-01-01'
""")
count1 = cursor.fetchone()['count']
print(f"  2020-01-01 到 2021-01-01: {count1:,} 条")

# 测试2: 2020年1月
cursor.execute("""
    SELECT COUNT(*) as count
    FROM d_mr
    WHERE B15 >= '2020-01-01' AND B15 < '2020-02-01'
""")
count2 = cursor.fetchone()['count']
print(f"  2020-01-01 到 2020-02-01: {count2:,} 条")

# 测试3: 使用YEAR和MONTH
cursor.execute("""
    SELECT COUNT(*) as count
    FROM d_mr
    WHERE YEAR(B15) = 2020 AND MONTH(B15) = 1
""")
count3 = cursor.fetchone()['count']
print(f"  YEAR=2020 AND MONTH=1: {count3:,} 条")

# 8. 检查B15字段是否有异常值
print("\n8. 检查B15字段异常值:")
cursor.execute("""
    SELECT B15, COUNT(*) as count
    FROM d_mr
    WHERE B15 IS NOT NULL
    GROUP BY B15
    HAVING COUNT(*) > 100
    ORDER BY count DESC
    LIMIT 10
""")
print("  出现次数最多的日期:")
for row in cursor.fetchall():
    print(f"    {row['B15']}: {row['count']:,} 次")

conn.close()

print("\n" + "="*100)
print("检查完成！")
print("="*100)
