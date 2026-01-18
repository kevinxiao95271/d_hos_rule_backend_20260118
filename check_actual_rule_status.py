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
print("检查实际规则状态")
print("=" * 80)

# 1. 检查所有与A01相关的规则
print("\n1. 检查A01相关的所有规则:")
cursor.execute("SELECT id, rule_code, field_code, field_name, status, dict_types FROM kiro_qc_rule WHERE field_code = 'A01' OR rule_code LIKE '%A01%'")
a01_rules = cursor.fetchall()

if a01_rules:
    for rule in a01_rules:
        rule_id, rule_code, field_code, field_name, status, dict_types = rule
        print(f"  规则ID: {rule_id}")
        print(f"  规则编码: {rule_code}")
        print(f"  字段编码: {field_code}")
        print(f"  字段名称: {field_name}")
        print(f"  状态: {status}")
        print(f"  字典类型: {dict_types}")
        print()
else:
    print("  未找到A01相关规则")

# 2. 检查所有与A19C相关的规则
print("\n2. 检查A19C相关的所有规则:")
cursor.execute("SELECT id, rule_code, field_code, field_name, status, dict_types FROM kiro_qc_rule WHERE field_code = 'A19C' OR rule_code LIKE '%A19C%'")
a19c_rules = cursor.fetchall()

if a19c_rules:
    for rule in a19c_rules:
        rule_id, rule_code, field_code, field_name, status, dict_types = rule
        print(f"  规则ID: {rule_id}")
        print(f"  规则编码: {rule_code}")
        print(f"  字段编码: {field_code}")
        print(f"  字段名称: {field_name}")
        print(f"  状态: {status}")
        print(f"  字典类型: {dict_types}")
        print()
else:
    print("  未找到A19C相关规则")

# 3. 检查所有与RC035相关的规则
print("\n3. 检查RC035相关的所有规则:")
cursor.execute("SELECT id, rule_code, field_code, field_name, status, dict_types FROM kiro_qc_rule WHERE dict_types = 'RC035'")
rc035_rules = cursor.fetchall()

if rc035_rules:
    for rule in rc035_rules:
        rule_id, rule_code, field_code, field_name, status, dict_types = rule
        print(f"  规则ID: {rule_id}")
        print(f"  规则编码: {rule_code}")
        print(f"  字段编码: {field_code}")
        print(f"  字段名称: {field_name}")
        print(f"  状态: {status}")
        print()
else:
    print("  未找到RC035相关规则")

# 4. 检查A01字段的实际数据
print("\n4. 检查A01字段的实际数据:")
cursor.execute("SELECT A01, COUNT(*) as cnt FROM d_mr WHERE A01 IS NOT NULL AND A01 != '' AND A01 != '-' GROUP BY A01 ORDER BY cnt DESC LIMIT 5")
a01_data = cursor.fetchall()
for row in a01_data:
    print(f"  A01值: '{row[0]}', 出现次数: {row[1]}")

# 5. 检查A19C字段的实际数据
print("\n5. 检查A19C字段的实际数据:")
cursor.execute("SELECT A19C, COUNT(*) as cnt FROM d_mr WHERE A19C IS NOT NULL AND A19C != '' AND A19C != '-' GROUP BY A19C ORDER BY cnt DESC LIMIT 5")
a19c_data = cursor.fetchall()
for row in a19c_data:
    print(f"  A19C值: '{row[0]}', 出现次数: {row[1]}")

# 6. 检查病案445583_1的A01和A19C字段值
print("\n6. 检查病案445583_1的字段值:")
cursor.execute("SELECT A01, A19C FROM d_mr WHERE A48 = '445583' AND A49 = '1'")
result = cursor.fetchone()
if result:
    a01_val, a19c_val = result
    print(f"  A01值: '{a01_val}'")
    print(f"  A19C值: '{a19c_val}'")
else:
    print("  未找到病案445583_1")

cursor.close()
conn.close()

print(f"\n" + "=" * 80)
print("检查完成")
print("=" * 80)