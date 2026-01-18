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
print("检查A27字段映射问题")
print("=" * 80)

# 1. 检查A27字段的实际数据
print("\n1. 检查A27字段的实际数据样例:")
cursor.execute("SELECT A27, COUNT(*) as cnt FROM d_mr WHERE A27 IS NOT NULL AND A27 != '' AND A27 != '-' GROUP BY A27 ORDER BY cnt DESC LIMIT 10")
rows = cursor.fetchall()
for row in rows:
    print(f"  A27值: '{row[0]}', 出现次数: {row[1]}")

# 2. 检查RC027字典内容
print("\n2. 检查RC027字典内容:")
cursor.execute("SELECT dict_code, dict_name FROM sys_dict WHERE dict_type_code = 'RC027' ORDER BY dict_sort")
rc027_rows = cursor.fetchall()
print(f"  RC027字典条目数: {len(rc027_rows)}")
for row in rc027_rows:
    print(f"  代码: {row[0]}, 名称: {row[1]}")

# 3. 检查病案445583的A27字段值
print("\n3. 检查病案445583的A27字段:")
cursor.execute("SELECT A48, A49, A27, A05 FROM d_mr WHERE A48 = '445583' AND A49 = '1'")
row = cursor.fetchone()
if row:
    print(f"  病案号: {row[0]}")
    print(f"  住院次数: {row[1]}")
    print(f"  A27值: '{row[2]}'")
    print(f"  A05值(电话): '{row[3]}'")
else:
    print("  未找到病案445583_1")

# 4. 分析A27字段的数据特征
print("\n4. 分析A27字段数据特征:")
cursor.execute("SELECT A27 FROM d_mr WHERE A27 IS NOT NULL AND A27 != '' AND A27 != '-' LIMIT 20")
samples = cursor.fetchall()
print("  A27字段样例数据:")
for i, sample in enumerate(samples):
    value = sample[0]
    print(f"    {i+1:2d}. '{value}' (长度: {len(value)}, 是否全数字: {'是' if value.isdigit() else '否'})")

# 5. 寻找真正的入院病情字段
print("\n5. 寻找真正的入院病情字段:")
# 获取RC027字典的有效值
cursor.execute("SELECT dict_code FROM sys_dict WHERE dict_type_code = 'RC027'")
valid_codes = [row[0] for row in cursor.fetchall()]
print(f"  RC027有效代码: {valid_codes}")

# 检查d_mr表中可能包含这些代码的字段
cursor.execute("DESCRIBE d_mr")
columns = cursor.fetchall()
field_names = [col[0] for col in columns]

found_fields = []
for field in field_names:
    try:
        placeholders = ','.join(['%s'] * len(valid_codes))
        query = f"SELECT {field}, COUNT(*) as cnt FROM d_mr WHERE {field} IN ({placeholders}) GROUP BY {field} ORDER BY cnt DESC LIMIT 5"
        cursor.execute(query, valid_codes)
        matches = cursor.fetchall()
        if matches:
            found_fields.append(field)
            print(f"  字段 {field} 包含RC027代码:")
            for match in matches:
                print(f"    代码: {match[0]}, 出现次数: {match[1]}")
    except Exception as e:
        pass

if not found_fields:
    print("  在d_mr表中未找到包含RC027代码的字段")

# 6. 检查其他表中的入院病情字段
other_tables = ['d_mr_other_1_20', 'd_mr_other_21_40', 'd_mr_other_f']
for table in other_tables:
    print(f"\n6. 检查表 {table}:")
    try:
        cursor.execute(f"DESCRIBE {table}")
        cols = cursor.fetchall()
        table_fields = [col[0] for col in cols]
        
        found_in_table = []
        for field in table_fields:
            try:
                placeholders = ','.join(['%s'] * len(valid_codes))
                query = f"SELECT {field}, COUNT(*) as cnt FROM {table} WHERE {field} IN ({placeholders}) GROUP BY {field} ORDER BY cnt DESC LIMIT 5"
                cursor.execute(query, valid_codes)
                matches = cursor.fetchall()
                if matches:
                    found_in_table.append(field)
                    print(f"  字段 {field} 包含RC027代码:")
                    for match in matches:
                        print(f"    代码: {match[0]}, 出现次数: {match[1]}")
            except Exception as e:
                pass
        
        if not found_in_table:
            print(f"  在表 {table} 中未找到包含RC027代码的字段")
            
    except Exception as e:
        print(f"  表 {table} 检查失败: {e}")

# 7. 检查A27相关规则
print(f"\n7. 检查A27相关规则:")
cursor.execute("SELECT rule_code, field_name, field_code, description, dict_types FROM kiro_qc_rule WHERE field_code = 'A27'")
rules = cursor.fetchall()
for rule in rules:
    print(f"  规则: {rule[0]}")
    print(f"  字段名: {rule[1]}")
    print(f"  字段编码: {rule[2]}")
    print(f"  描述: {rule[3]}")
    print(f"  字典类型: {rule[4]}")

cursor.close()
conn.close()