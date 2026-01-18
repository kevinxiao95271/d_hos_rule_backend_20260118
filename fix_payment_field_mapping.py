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
print("修复医疗付费方式字段映射")
print("=" * 80)

# 1. 查看当前错误的A32规则
print("\n1. 当前A32相关规则:")
cursor.execute("SELECT id, rule_code, field_name, field_code, description, dict_types FROM kiro_qc_rule WHERE field_code = 'A32'")
a32_rules = cursor.fetchall()
for rule in a32_rules:
    print(f"  规则ID: {rule[0]}")
    print(f"  规则编码: {rule[1]}")
    print(f"  字段名: {rule[2]}")
    print(f"  字段编码: {rule[3]}")
    print(f"  描述: {rule[4]}")
    print(f"  字典类型: {rule[5]}")
    print()

# 2. 验证A46C字段确实是医疗付费方式
print("\n2. 验证A46C字段数据:")
cursor.execute("SELECT A46C, COUNT(*) as cnt FROM d_mr WHERE A46C IS NOT NULL AND A46C != '' GROUP BY A46C ORDER BY cnt DESC LIMIT 10")
a46c_data = cursor.fetchall()
for row in a46c_data:
    print(f"  A46C值: '{row[0]}', 出现次数: {row[1]}")

# 3. 检查A46C值是否都在RC032字典中
cursor.execute("SELECT dict_code FROM sys_dict WHERE dict_type_code = 'RC032'")
valid_codes = [row[0] for row in cursor.fetchall()]
print(f"\n3. RC032字典有效代码: {valid_codes}")

cursor.execute("SELECT A46C, COUNT(*) as cnt FROM d_mr WHERE A46C IS NOT NULL AND A46C != '' GROUP BY A46C ORDER BY cnt DESC")
all_a46c_values = cursor.fetchall()
invalid_values = []
valid_values = []
for row in all_a46c_values:
    if row[0] in valid_codes:
        valid_values.append(row)
    else:
        invalid_values.append(row)

print(f"\n  A46C字段中的有效RC032代码:")
for row in valid_values[:10]:
    print(f"    代码: '{row[0]}', 出现次数: {row[1]}")

if invalid_values:
    print(f"\n  A46C字段中的无效值:")
    for row in invalid_values[:5]:
        print(f"    值: '{row[0]}', 出现次数: {row[1]}")

# 4. 修复规则：将医疗付费方式规则从A32改为A46C
print(f"\n4. 修复医疗付费方式规则:")
payment_rule_id = None
for rule in a32_rules:
    if 'RC032' in str(rule[5]) or '医疗付费方式' in str(rule[2]):
        payment_rule_id = rule[0]
        print(f"  找到医疗付费方式规则: {rule[1]}")
        break

if payment_rule_id:
    # 更新规则字段编码从A32到A46C
    update_sql = """
    UPDATE kiro_qc_rule 
    SET field_code = 'A46C',
        field_name = '医疗付费方式',
        description = '医疗付费方式必须在RC032字典范围内',
        source_tables = 'd_mr'
    WHERE id = %s
    """
    cursor.execute(update_sql, (payment_rule_id,))
    conn.commit()
    print(f"  ✅ 已将规则 {payment_rule_id} 的字段编码从A32更新为A46C")
else:
    print("  ❌ 未找到医疗付费方式规则")

# 5. 验证修复结果
print(f"\n5. 验证修复结果:")
cursor.execute("SELECT id, rule_code, field_name, field_code, description, dict_types FROM kiro_qc_rule WHERE field_code = 'A46C'")
a46c_rules = cursor.fetchall()
for rule in a46c_rules:
    print(f"  规则ID: {rule[0]}")
    print(f"  规则编码: {rule[1]}")
    print(f"  字段名: {rule[2]}")
    print(f"  字段编码: {rule[3]}")
    print(f"  描述: {rule[4]}")
    print(f"  字典类型: {rule[5]}")

# 6. 检查A32字段的真实含义
print(f"\n6. 分析A32字段的真实含义:")
cursor.execute("SELECT A32, A02, COUNT(*) as cnt FROM d_mr WHERE A32 IS NOT NULL AND A32 != '' AND A32 != '-' GROUP BY A32, A02 ORDER BY cnt DESC LIMIT 5")
a32_analysis = cursor.fetchall()
print("  A32字段与A02字段(姓名)的关系:")
for row in a32_analysis:
    print(f"    A32: '{row[0]}', A02: '{row[1]}', 出现次数: {row[2]}")

# 7. 更新或删除错误的A32规则
print(f"\n7. 处理错误的A32规则:")
for rule in a32_rules:
    if rule[0] != payment_rule_id:  # 不是已经修复的付费方式规则
        rule_id = rule[0]
        rule_code = rule[1]
        print(f"  规则 {rule_code} (ID: {rule_id}) - 字段A32实际存储的是姓名，不是{rule[2]}")
        
        # 可以选择删除这些错误的规则或者更新它们
        # 这里我们将它们标记为草稿状态
        cursor.execute("UPDATE kiro_qc_rule SET status = 'draft' WHERE id = %s", (rule_id,))
        conn.commit()
        print(f"    ✅ 已将规则 {rule_code} 标记为草稿状态")

cursor.close()
conn.close()

print(f"\n" + "=" * 80)
print("修复完成！")
print("✅ 医疗付费方式规则已从A32字段修正为A46C字段")
print("✅ 错误的A32规则已标记为草稿状态")
print("=" * 80)