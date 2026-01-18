import pymysql

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("修复规则字段映射")
    print("=" * 60)
    
    # 1. 检查当前所有民族相关规则
    print("\n1. 检查当前民族相关规则:")
    cursor.execute("""
        SELECT id, rule_code, field_code, field_name, description, status, dict_types
        FROM kiro_qc_rule 
        WHERE dict_types = 'RC035' OR description LIKE '%民族%'
        ORDER BY rule_code
    """)
    rules = cursor.fetchall()
    
    for rule in rules:
        rule_id, rule_code, field_code, field_name, description, status, dict_types = rule
        print(f"  ID: {rule_id}")
        print(f"  规则: {rule_code}")
        print(f"  字段: {field_code} ({field_name})")
        print(f"  状态: {status}")
        print(f"  描述: {description}")
        print()
    
    # 2. 查找并修复错误的规则
    print("2. 修复错误的规则:")
    
    # 查找使用A01字段但应该使用A19C的规则
    cursor.execute("""
        SELECT id, rule_code, field_code, field_name 
        FROM kiro_qc_rule 
        WHERE field_code = 'A01' AND dict_types = 'RC035'
    """)
    wrong_rules = cursor.fetchall()
    
    if wrong_rules:
        print("  发现错误的A01民族规则:")
        for rule_id, rule_code, field_code, field_name in wrong_rules:
            print(f"    规则ID: {rule_id}, 代码: {rule_code}")
            
            # 修复字段映射
            new_rule_code = rule_code.replace('A01', 'A19C')
            cursor.execute("""
                UPDATE kiro_qc_rule 
                SET field_code = 'A19C', 
                    field_name = '民族',
                    rule_code = %s
                WHERE id = %s
            """, (new_rule_code, rule_id))
            
            print(f"    ✅ 已修复: {rule_code} -> {new_rule_code}")
            print(f"    ✅ 字段: A01 -> A19C")
    else:
        print("  ✅ 未发现使用A01字段的民族规则")
    
    # 3. 禁用所有非民族的A01规则
    print("\n3. 禁用非民族的A01规则:")
    cursor.execute("""
        UPDATE kiro_qc_rule 
        SET status = 'draft' 
        WHERE field_code = 'A01' AND (dict_types != 'RC035' OR dict_types IS NULL)
    """)
    disabled_count = cursor.rowcount
    print(f"  ✅ 禁用了 {disabled_count} 个A01规则")
    
    # 4. 确保A19C民族规则是活跃的
    print("\n4. 激活A19C民族规则:")
    cursor.execute("""
        UPDATE kiro_qc_rule 
        SET status = 'active' 
        WHERE field_code = 'A19C' AND dict_types = 'RC035'
    """)
    activated_count = cursor.rowcount
    print(f"  ✅ 激活了 {activated_count} 个A19C民族规则")
    
    # 5. 验证修复结果
    print("\n5. 验证修复结果:")
    cursor.execute("""
        SELECT rule_code, field_code, field_name, status 
        FROM kiro_qc_rule 
        WHERE dict_types = 'RC035' AND status = 'active'
        ORDER BY rule_code
    """)
    active_rules = cursor.fetchall()
    
    print("  当前活跃的民族规则:")
    for rule_code, field_code, field_name, status in active_rules:
        print(f"    {rule_code}: {field_code} ({field_name}) - {status}")
    
    # 6. 清理旧的质控结果
    print("\n6. 清理旧的质控结果:")
    cursor.execute("DELETE FROM kiro_qc_defect_detail WHERE rule_code LIKE '%A01%RC035%'")
    deleted_defects = cursor.rowcount
    print(f"  ✅ 删除了 {deleted_defects} 条旧的A01民族缺陷记录")
    
    cursor.execute("DELETE FROM kiro_qc_case_result")
    deleted_cases = cursor.rowcount
    print(f"  ✅ 删除了 {deleted_cases} 条病案结果")
    
    cursor.execute("DELETE FROM kiro_qc_batch_summary")
    deleted_batches = cursor.rowcount
    print(f"  ✅ 删除了 {deleted_batches} 条批次汇总")
    
    conn.commit()
    print("\n✅ 所有修复已提交到数据库")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("修复完成")
    print("=" * 60)
    
    print("\n下一步:")
    print("1. 重启Spring Boot应用")
    print("2. 运行新的质控批次")
    print("3. 验证民族字段现在显示正确的A19C值('1')")
    
except Exception as e:
    print(f"错误: {e}")