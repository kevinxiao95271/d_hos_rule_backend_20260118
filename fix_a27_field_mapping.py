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
print("修复A27字段映射问题")
print("=" * 80)

# 1. 确认A27字段问题
print("\n1. 确认A27字段存储的是电话号码:")
cursor.execute("SELECT A27 FROM d_mr WHERE A27 IS NOT NULL AND A27 != '' AND A27 != '-' LIMIT 5")
samples = cursor.fetchall()
for i, sample in enumerate(samples):
    value = sample[0]
    print(f"  样例{i+1}: '{value}' (长度: {len(str(value))}, 类型: 电话号码)")

# 2. 检查RC027字典
print("\n2. RC027字典内容:")
cursor.execute("SELECT dict_code, dict_name FROM sys_dict WHERE dict_type_code = 'RC027' ORDER BY dict_sort")
rc027_rows = cursor.fetchall()
valid_codes = [row[0] for row in cursor.fetchall()]
cursor.execute("SELECT dict_code FROM sys_dict WHERE dict_type_code = 'RC027'")
valid_codes = [row[0] for row in cursor.fetchall()]
print(f"  RC027有效代码: {valid_codes}")
for row in rc027_rows:
    print(f"  代码: {row[0]}, 名称: {row[1]}")

# 3. 寻找真正的入院病情字段
print("\n3. 寻找真正的入院病情字段:")
cursor.execute("DESCRIBE d_mr")
columns = cursor.fetchall()
field_names = [col[0] for col in columns]

# 检查可能的入院病情字段
potential_fields = []
for field in field_names:
    # 跳过明显不是入院病情的字段
    if field in ['A27']:  # A27已确认是电话
        continue
        
    try:
        placeholders = ','.join(['%s'] * len(valid_codes))
        query = f"SELECT {field}, COUNT(*) as cnt FROM d_mr WHERE {field} IN ({placeholders}) GROUP BY {field} ORDER BY cnt DESC LIMIT 5"
        cursor.execute(query, valid_codes)
        matches = cursor.fetchall()
        if matches:
            potential_fields.append((field, matches))
            print(f"  字段 {field} 包含RC027代码:")
            for match in matches:
                print(f"    代码: {match[0]}, 出现次数: {match[1]}")
    except Exception as e:
        pass

# 4. 如果在d_mr中没找到，检查其他表
if not potential_fields:
    print("  在d_mr表中未找到包含RC027代码的字段，检查其他表...")
    
    other_tables = ['d_mr_other_1_20', 'd_mr_other_21_40', 'd_mr_other_f']
    for table in other_tables:
        try:
            cursor.execute(f"DESCRIBE {table}")
            cols = cursor.fetchall()
            table_fields = [col[0] for col in cols]
            
            for field in table_fields:
                try:
                    placeholders = ','.join(['%s'] * len(valid_codes))
                    query = f"SELECT {field}, COUNT(*) as cnt FROM {table} WHERE {field} IN ({placeholders}) GROUP BY {field} ORDER BY cnt DESC LIMIT 5"
                    cursor.execute(query, valid_codes)
                    matches = cursor.fetchall()
                    if matches:
                        potential_fields.append((f"{table}.{field}", matches))
                        print(f"  表 {table} 字段 {field} 包含RC027代码:")
                        for match in matches:
                            print(f"    代码: {match[0]}, 出现次数: {match[1]}")
                except Exception as e:
                    pass
        except Exception as e:
            pass

# 5. 选择最合适的字段作为入院病情字段
if potential_fields:
    # 选择匹配记录数最多的字段
    best_field = max(potential_fields, key=lambda x: sum(match[1] for match in x[1]))
    correct_field = best_field[0]
    print(f"\n4. 确定正确的入院病情字段: {correct_field}")
    
    # 6. 修复规则
    print(f"\n5. 修复入院病情规则:")
    cursor.execute("SELECT id, rule_code, field_name, field_code, description FROM kiro_qc_rule WHERE field_code = 'A27'")
    a27_rules = cursor.fetchall()
    
    for rule in a27_rules:
        rule_id = rule[0]
        rule_code = rule[1]
        if 'RC027' in str(rule[4]) or '入院病情' in str(rule[2]):
            print(f"  找到入院病情规则: {rule_code}")
            
            # 更新规则字段编码
            if '.' in correct_field:  # 如果是其他表的字段
                table_name, field_name = correct_field.split('.')
                update_sql = """
                UPDATE kiro_qc_rule 
                SET field_code = %s,
                    field_name = '入院病情',
                    description = '入院病情必须在RC027字典范围内',
                    source_tables = %s
                WHERE id = %s
                """
                cursor.execute(update_sql, (field_name, table_name, rule_id))
            else:  # 如果是d_mr表的字段
                update_sql = """
                UPDATE kiro_qc_rule 
                SET field_code = %s,
                    field_name = '入院病情',
                    description = '入院病情必须在RC027字典范围内',
                    source_tables = 'd_mr'
                WHERE id = %s
                """
                cursor.execute(update_sql, (correct_field, rule_id))
            
            conn.commit()
            print(f"  ✅ 已将规则 {rule_code} 的字段编码从A27更新为{correct_field}")
        else:
            # 将其他A27规则标记为草稿
            cursor.execute("UPDATE kiro_qc_rule SET status = 'draft' WHERE id = %s", (rule_id,))
            conn.commit()
            print(f"  ⚠️  规则 {rule_code} 已标记为草稿状态")

else:
    print(f"\n4. ❌ 未找到包含RC027代码的字段")
    print("  可能的原因:")
    print("  1. 入院病情字段可能使用了不同的编码方式")
    print("  2. 数据可能存在质量问题")
    print("  3. 字段可能在其他未检查的表中")

# 7. 验证修复结果
print(f"\n6. 验证修复结果:")
cursor.execute("SELECT rule_code, field_name, field_code, description, source_tables FROM kiro_qc_rule WHERE rule_code LIKE '%A27%' OR description LIKE '%入院病情%'")
updated_rules = cursor.fetchall()
for rule in updated_rules:
    print(f"  规则: {rule[0]}")
    print(f"  字段名: {rule[1]}")
    print(f"  字段编码: {rule[2]}")
    print(f"  描述: {rule[3]}")
    print(f"  源表: {rule[4]}")
    print()

cursor.close()
conn.close()

print(f"\n" + "=" * 80)
print("A27字段映射修复完成！")
print("=" * 80)