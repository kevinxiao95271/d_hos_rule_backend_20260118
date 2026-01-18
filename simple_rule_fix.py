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
    
    print("检查和修复民族规则...")
    
    # 检查当前规则
    cursor.execute("""
        SELECT rule_code, field_code, status 
        FROM kiro_qc_rule 
        WHERE dict_types = 'RC035'
    """)
    rules = cursor.fetchall()
    
    print("当前民族规则:")
    for rule_code, field_code, status in rules:
        print(f"  {rule_code}: {field_code} - {status}")
    
    # 查找错误的A01民族规则
    cursor.execute("""
        SELECT id, rule_code 
        FROM kiro_qc_rule 
        WHERE field_code = 'A01' AND dict_types = 'RC035'
    """)
    wrong_rules = cursor.fetchall()
    
    if wrong_rules:
        print(f"\n发现 {len(wrong_rules)} 个错误的A01民族规则，正在修复...")
        for rule_id, rule_code in wrong_rules:
            new_rule_code = rule_code.replace('A01', 'A19C')
            cursor.execute("""
                UPDATE kiro_qc_rule 
                SET field_code = 'A19C', rule_code = %s
                WHERE id = %s
            """, (new_rule_code, rule_id))
            print(f"  修复: {rule_code} -> {new_rule_code}")
    
    # 清理旧结果
    cursor.execute("DELETE FROM kiro_qc_defect_detail")
    cursor.execute("DELETE FROM kiro_qc_case_result") 
    cursor.execute("DELETE FROM kiro_qc_batch_summary")
    
    conn.commit()
    print("✅ 修复完成")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"错误: {e}")