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
print("批量修复字段映射问题")
print("=" * 80)

# 定义需要修复的字段映射问题和对应的正确字段
field_mapping_fixes = [
    {
        'dict_type': 'RC035',
        'dict_name': '民族',
        'wrong_field': 'A01',
        'correct_field': 'A19C',
        'rule_pattern': 'RULE_A01_RC035'
    },
    {
        'dict_type': 'RC002', 
        'dict_name': '婚姻状况',
        'wrong_field': 'A02',
        'correct_field': 'A21C',
        'rule_pattern': 'RULE_A02_RC002'
    },
    {
        'dict_type': 'RC016',
        'dict_name': '死亡患者尸检',
        'wrong_field': 'A16',
        'correct_field': None,  # 需要查找
        'rule_pattern': 'RULE_A16_RC016'
    },
    {
        'dict_type': 'RC019',
        'dict_name': '离院方式',
        'wrong_field': 'A17',
        'correct_field': None,  # 需要查找
        'rule_pattern': 'RULE_A17_RC019'
    },
    {
        'dict_type': 'RC030',
        'dict_name': 'ABO血型',
        'wrong_field': 'A20',
        'correct_field': None,  # 需要查找
        'rule_pattern': 'RULE_A20_RC030'
    },
    {
        'dict_type': 'RC011',
        'dict_name': '病案质量',
        'wrong_field': 'A22',
        'correct_field': None,  # 需要查找
        'rule_pattern': 'RULE_A22_RC011'
    },
    {
        'dict_type': 'RC026',
        'dict_name': '入院途径',
        'wrong_field': 'A26',
        'correct_field': None,  # 需要查找
        'rule_pattern': 'RULE_A26_RC026'
    }
]

# 为每个需要修复的字段寻找正确的映射字段
for fix in field_mapping_fixes:
    if fix['correct_field'] is None:
        print(f"\n寻找 {fix['dict_name']} ({fix['dict_type']}) 的正确字段:")
        
        # 获取该字典的有效代码
        cursor.execute("SELECT dict_code FROM sys_dict WHERE dict_type_code = %s", (fix['dict_type'],))
        valid_codes = [row[0] for row in cursor.fetchall()]
        print(f"  有效代码: {valid_codes[:10]}{'...' if len(valid_codes) > 10 else ''}")
        
        # 在d_mr表中寻找包含这些代码的字段
        cursor.execute("DESCRIBE d_mr")
        columns = cursor.fetchall()
        field_names = [col[0] for col in columns]
        
        best_field = None
        best_match_count = 0
        
        for field in field_names:
            if field == fix['wrong_field']:  # 跳过错误的字段
                continue
                
            try:
                placeholders = ','.join(['%s'] * len(valid_codes))
                query = f"SELECT COUNT(*) FROM d_mr WHERE {field} IN ({placeholders})"
                cursor.execute(query, valid_codes)
                match_count = cursor.fetchone()[0]
                
                if match_count > best_match_count:
                    best_match_count = match_count
                    best_field = field
                    
            except Exception as e:
                pass
        
        if best_field and best_match_count > 0:
            fix['correct_field'] = best_field
            print(f"  ✅ 找到正确字段: {best_field} (匹配 {best_match_count} 条记录)")
        else:
            print(f"  ❌ 未找到合适的字段")

print(f"\n" + "=" * 60)
print("开始批量修复字段映射")
print("=" * 60)

fixed_count = 0
failed_count = 0

for fix in field_mapping_fixes:
    print(f"\n修复 {fix['dict_name']} ({fix['dict_type']}):")
    print(f"  错误字段: {fix['wrong_field']}")
    print(f"  正确字段: {fix['correct_field']}")
    
    if fix['correct_field'] is None:
        print(f"  ❌ 跳过修复 - 未找到正确字段")
        failed_count += 1
        continue
    
    try:
        # 查找需要修复的规则
        cursor.execute("SELECT id, rule_code FROM kiro_qc_rule WHERE rule_code = %s", (fix['rule_pattern'],))
        rule = cursor.fetchone()
        
        if rule:
            rule_id, rule_code = rule
            
            # 更新规则字段映射
            update_sql = """
            UPDATE kiro_qc_rule 
            SET field_code = %s,
                field_name = %s,
                description = %s
            WHERE id = %s
            """
            
            new_description = f"{fix['dict_name']}必须在{fix['dict_type']}字典范围内"
            cursor.execute(update_sql, (fix['correct_field'], fix['dict_name'], new_description, rule_id))
            
            # 将错误字段的其他规则标记为草稿
            cursor.execute("UPDATE kiro_qc_rule SET status = 'draft' WHERE field_code = %s AND id != %s", 
                         (fix['wrong_field'], rule_id))
            
            conn.commit()
            print(f"  ✅ 修复成功: {rule_code}")
            fixed_count += 1
            
        else:
            print(f"  ❌ 未找到规则: {fix['rule_pattern']}")
            failed_count += 1
            
    except Exception as e:
        print(f"  ❌ 修复失败: {e}")
        failed_count += 1

print(f"\n" + "=" * 60)
print("批量修复完成")
print("=" * 60)
print(f"成功修复: {fixed_count} 个字段映射")
print(f"修复失败: {failed_count} 个字段映射")

# 验证修复结果
print(f"\n验证修复结果:")
for fix in field_mapping_fixes:
    if fix['correct_field']:
        cursor.execute("SELECT rule_code, field_code, field_name FROM kiro_qc_rule WHERE rule_code = %s", 
                      (fix['rule_pattern'],))
        result = cursor.fetchone()
        if result:
            rule_code, field_code, field_name = result
            status = "✅" if field_code == fix['correct_field'] else "❌"
            print(f"  {status} {rule_code}: {field_code} ({field_name})")

cursor.close()
conn.close()

print(f"\n" + "=" * 80)
print("批量字段映射修复完成！")
print("=" * 80)