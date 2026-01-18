import pymysql

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

# 查看附属表结构
for table in ['d_mr_other_1_20', 'd_mr_other_21_40', 'd_mr_other_f']:
    print(f"\n{'='*80}")
    print(f"{table} 表结构:")
    print('='*80)
    cursor.execute(f"DESCRIBE {table}")
    columns = cursor.fetchall()
    print(f"字段数: {len(columns)}")
    print("\n前20个字段:")
    for i, col in enumerate(columns[:20]):
        print(f"  {col[0]:<30} {col[1]:<20}")
    
    # 查看数据量
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"\n总记录数: {count}")
    
    # 查看样例数据
    print(f"\n样例数据 (前2条):")
    cursor.execute(f"SELECT A48, A49 FROM {table} LIMIT 2")
    for row in cursor.fetchall():
        print(f"  A48: {row[0]}, A49: {row[1]}")

# 验证关联关系
print(f"\n{'='*80}")
print("验证d_mr与附属表的关联:")
print('='*80)
cursor.execute("""
    SELECT 
        (SELECT COUNT(*) FROM d_mr) as d_mr_count,
        (SELECT COUNT(*) FROM d_mr_other_1_20) as other_1_20_count,
        (SELECT COUNT(*) FROM d_mr_other_21_40) as other_21_40_count,
        (SELECT COUNT(*) FROM d_mr_other_f) as other_f_count
""")
counts = cursor.fetchone()
print(f"d_mr: {counts[0]} 条")
print(f"d_mr_other_1_20: {counts[1]} 条")
print(f"d_mr_other_21_40: {counts[2]} 条")
print(f"d_mr_other_f: {counts[3]} 条")

# 测试关联查询
print(f"\n{'='*80}")
print("测试关联查询 (d_mr LEFT JOIN d_mr_other_1_20):")
print('='*80)
cursor.execute("""
    SELECT m.A48, m.A49, m.B15, o.C35x01C
    FROM d_mr m
    LEFT JOIN d_mr_other_1_20 o ON m.A48 = o.A48 AND m.A49 = o.A49
    LIMIT 3
""")
for row in cursor.fetchall():
    print(f"  A48: {row[0]}, A49: {row[1]}, B15: {row[2]}, C35x01C: {row[3]}")

cursor.close()
conn.close()
