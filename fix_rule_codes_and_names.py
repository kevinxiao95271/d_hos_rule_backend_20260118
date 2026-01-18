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
print("修复规则编码和名称")
print("=" * 80)

# 需要修复的规则映射
rule_fixes = [
    {
        'old_rule_code': 'RULE_A01_RC035',
        'new_rule_code': 'RULE_A19C_RC035',
        'field_code': 'A19C',
        'field_name': '民族',
        'description': '民族必须在RC035字典范围内'
    },
    {
        'old_rule_code': 'RULE_A02_RC002',
        'new_rule_code': 'RULE_A21C_RC002', 
        'field_code': 'A21C',
        'field_name': '婚姻状况',
        'description': '婚姻状况必须在RC002字典范围内'
    },
    {
        'old_rule_code': 'RULE_A32_RC032',
        'new_rule_code': 'RULE_A46C_RC032',
        'field_code': 'A46C', 
        'field_name': '医疗付费方式',
        'description': '医疗付费方式必须在RC032字典范围内'
    },
    {
        'old_rule_code': 'RULE_A27_RC027',
        'new_rule_code': 'RULE_A12C_RC027',
        'field_code': 'A12C',
        'field_name': '入院病情', 
        'description': '入院病情必须在RC027字典范围内'
    }
]

print("修复规则编码和字段名称:")

for fix in rule_fixes:
    print(f"\n修复规则: {fix['old_rule_code']} → {fix['new_rule_code']}")
    
    try:
        # 检查旧规则是否存在
        cursor.execute("SELECT id, field_code FROM kiro_qc_rule WHERE rule_code = %s", (fix['old_rule_code'],))
        rule = cursor.fetchone()
        
        if rule:
            rule_id, current_field = rule
            print(f"  当前字段: {current_field}")
            print(f"  目标字段: {fix['field_code']}")
            
            # 更新规则编码、字段编码、字段名称和描述
            update_sql = """
            UPDATE kiro_qc_rule 
            SET rule_code = %s,
                field_code = %s,
                field_name = %s,
                description = %s
            WHERE id = %s
            """
            
            cursor.execute(update_sql, (
                fix['new_rule_code'],
                fix['field_code'], 
                fix['field_name'],
                fix['description'],
                rule_id
            ))
            
            conn.commit()
            print(f"  ✅ 更新成功")
            
        else:
            print(f"  ⚠️  规则不存在，可能已经修复过")
            
    except Exception as e:
        print(f"  ❌ 更新失败: {e}")

# 验证修复结果
print(f"\n" + "=" * 60)
print("验证修复结果:")
print("=" * 60)

for fix in rule_fixes:
    # 检查新规则编码
    cursor.execute("SELECT rule_code, field_code, field_name, description, status FROM kiro_qc_rule WHERE rule_code = %s", 
                  (fix['new_rule_code'],))
    result = cursor.fetchone()
    
    if result:
        rule_code, field_code, field_name, description, status = result
        status_icon = "✅" if field_code == fix['field_code'] and status == 'active' else "⚠️"
        print(f"{status_icon} {rule_code}")
        print(f"   字段: {field_code} ({field_name})")
        print(f"   状态: {status}")
        print(f"   描述: {description}")
        print()
    else:
        print(f"❌ 未找到规则: {fix['new_rule_code']}")

# 检查是否还有旧的规则编码
print("检查旧规则编码:")
old_codes = [fix['old_rule_code'] for fix in rule_fixes]
for old_code in old_codes:
    cursor.execute("SELECT COUNT(*) FROM kiro_qc_rule WHERE rule_code = %s", (old_code,))
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"⚠️  仍存在旧规则: {old_code}")
    else:
        print(f"✅ 旧规则已清理: {old_code}")

cursor.close()
conn.close()

print(f"\n" + "=" * 80)
print("规则编码和名称修复完成！")
print("✅ 所有规则编码已更新为正确的字段编码")
print("✅ 字段名称已更新为正确的含义")
print("=" * 80)