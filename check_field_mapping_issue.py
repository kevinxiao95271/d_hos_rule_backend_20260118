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

print("=" * 80)
print("检查字段映射问题")
print("=" * 80)

# 1. 检查A32字段在d_mr表中的实际数据
print("\n1. 检查A32字段在d_mr表中的数据样例:")
cursor.execute("SELECT A48, A49, A32 FROM d_mr WHERE A32 IS NOT NULL AND A32 != '' LIMIT 10")
rows = cursor.fetchall()
for row in rows:
    print(f"  病案: {row[0]}_{row[1]}, A32值: '{row[2]}'")

# 2. 检查A32字段的数据类型和长度
print("\n2. 检查A32字段定义:")
cursor.execute("DESCRIBE d_mr")
columns = cursor.fetchall()
for col in columns:
    if col[0] == 'A32':
        print(f"  字段名: {col[0]}")
        print(f"  数据类型: {col[1]}")
        print(f"  是否可空: {col[2]}")
        print(f"  默认值: {col[4]}")

# 3. 检查RC032字典内容
print("\n3. 检查RC032字典内容:")
cursor.execute("SELECT dict_code, dict_name FROM sys_dict WHERE dict_type_code = 'RC032' ORDER BY dict_sort LIMIT 10")
rc032_rows = cursor.fetchall()
print(f"  RC032字典条目数: {len(rc032_rows)}")
for row in rc032_rows:
    print(f"  代码: {row[0]}, 名称: {row[1]}")

# 4. 检查病案445583的A32字段值
print("\n4. 检查病案445583的A32字段:")
cursor.execute("SELECT A48, A49, A32, A02 FROM d_mr WHERE A48 = '445583' AND A49 = '1'")
row = cursor.fetchone()
if row:
    print(f"  病案号: {row[0]}")
    print(f"  住院次数: {row[1]}")
    print(f"  A32值: '{row[2]}'")
    print(f"  A02值(姓名): '{row[3]}'")
else:
    print("  未找到病案445583_1")

# 5. 检查当前规则表中的A32相关规则
print("\n5. 检查A32相关规则:")
cursor.execute("SELECT rule_code, field_name, field_code, description FROM kiro_qc_rule WHERE field_code = 'A32'")
rules = cursor.fetchall()
for rule in rules:
    print(f"  规则: {rule[0]}")
    print(f"  字段名: {rule[1]}")
    print(f"  字段编码: {rule[2]}")
    print(f"  描述: {rule[3]}")

# 6. 检查A32字段的数据分布
print("\n6. 检查A32字段数据分布:")
cursor.execute("SELECT A32, COUNT(*) as cnt FROM d_mr WHERE A32 IS NOT NULL AND A32 != '' GROUP BY A32 ORDER BY cnt DESC LIMIT 10")
dist_rows = cursor.fetchall()
for row in dist_rows:
    print(f"  值: '{row[0]}', 出现次数: {row[1]}")

cursor.close()
conn.close()