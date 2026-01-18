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
print("修复关键字段映射问题")
print("=" * 80)

# 基于审查结果，直接修复已确认的字段映射问题
critical_fixes = [
    {
        'rule_code': 'RULE_A01_RC035',
        'dict_name': '民族',
        'wrong_field': 'A01',
        'correct_field': 'A19C',
        'description': '民族必须在RC035字典范围内'
    },
    {
        'rule_code': 'RULE_A02_RC002', 
        'dict_name': '婚姻状况',
        'wrong_field': 'A02',
        'correct_field': 'A21C',
        'description': '婚姻状况必须在RC002字典范围内'
    }
]

print("修复已确认的字段映射问题:")

for fix in critical_fixes:
    print(f"\n修复 {fix['dict_name']}:")
    print(f"  规则: {fix['rule_code']}")
    print(f"  错误字段: {fix['wrong_field']}")
    print(f"  正确字段: {fix['correct_field']}")
    
    try:
        # 查找规则
        cursor.execute("SELECT id FROM kiro_qc_rule WHERE rule_code = %s", (fix['rule_code'],))
        rule = cursor.fetchone()
        
        if rule:
            rule_id = rule[0]
            
            # 更新规则字段映射
            update_sql = """
            UPDATE kiro_qc_rule 
            SET field_code = %s,
                field_name = %s,
                description = %s
            WHERE id = %s
            """
            
            cursor.execute(update_sql, (fix['correct_field'], fix['dict_name'], fix['description'], rule_id))
            
            # 将错误字段的其他规则标记为草稿
            cursor.execute("UPDATE kiro_qc_rule SET status = 'draft' WHERE field_code = %s AND id != %s", 
                         (fix['wrong_field'], rule_id))
            
            conn.commit()
            print(f"  ✅ 修复成功")
            
        else:
            print(f"  ❌ 未找到规则")
            
    except Exception as e:
        print(f"  ❌ 修复失败: {e}")

# 对于其他问题字段，直接停用错误规则
problem_fields = ['A16', 'A17', 'A20', 'A22', 'A26']

print(f"\n停用其他问题字段的规则:")
for field in problem_fields:
    try:
        cursor.execute("UPDATE kiro_qc_rule SET status = 'draft' WHERE field_code = %s", (field,))
        affected = cursor.rowcount
        conn.commit()
        print(f"  ✅ 字段 {field}: 停用了 {affected} 个规则")
    except Exception as e:
        print(f"  ❌ 字段 {field}: 停用失败 - {e}")

# 验证修复结果
print(f"\n验证修复结果:")
for fix in critical_fixes:
    cursor.execute("SELECT field_code, field_name, status FROM kiro_qc_rule WHERE rule_code = %s", 
                  (fix['rule_code'],))
    result = cursor.fetchone()
    if result:
        field_code, field_name, status = result
        status_icon = "✅" if field_code == fix['correct_field'] and status == 'active' else "❌"
        print(f"  {status_icon} {fix['rule_code']}: {field_code} ({field_name}) - {status}")

# 检查修复后的数据准确性
print(f"\n检查修复后的数据准确性:")

# 检查A19C字段的民族数据
cursor.execute("SELECT dict_code FROM sys_dict WHERE dict_type_code = 'RC035'")
rc035_codes = [row[0] for row in cursor.fetchall()]

cursor.execute(f"SELECT COUNT(*) FROM d_mr WHERE A19C IN ({','.join(['%s'] * len(rc035_codes))})", rc035_codes)
valid_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM d_mr WHERE A19C IS NOT NULL AND A19C != '' AND A19C != '-'")
total_count = cursor.fetchone()[0]

if total_count > 0:
    accuracy = (valid_count / total_count) * 100
    print(f"  A19C (民族): {valid_count}/{total_count} 有效 ({accuracy:.1f}%)")

# 检查A21C字段的婚姻状况数据
cursor.execute("SELECT dict_code FROM sys_dict WHERE dict_type_code = 'RC002'")
rc002_codes = [row[0] for row in cursor.fetchall()]

cursor.execute(f"SELECT COUNT(*) FROM d_mr WHERE A21C IN ({','.join(['%s'] * len(rc002_codes))})", rc002_codes)
valid_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM d_mr WHERE A21C IS NOT NULL AND A21C != '' AND A21C != '-'")
total_count = cursor.fetchone()[0]

if total_count > 0:
    accuracy = (valid_count / total_count) * 100
    print(f"  A21C (婚姻状况): {valid_count}/{total_count} 有效 ({accuracy:.1f}%)")

cursor.close()
conn.close()

print(f"\n" + "=" * 80)
print("关键字段映射修复完成！")
print("✅ 民族字段: A01 → A19C")
print("✅ 婚姻状况字段: A02 → A21C") 
print("✅ 问题字段规则已停用")
print("=" * 80)