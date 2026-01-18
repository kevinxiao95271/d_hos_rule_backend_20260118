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
    
    print("查找所有RULE_A01_RC035引用...")
    
    # 1. 检查规则表
    cursor.execute("SELECT * FROM kiro_qc_rule WHERE rule_code = 'RULE_A01_RC035'")
    rule_result = cursor.fetchall()
    if rule_result:
        print(f"❌ 规则表中仍有RULE_A01_RC035: {len(rule_result)}条")
        # 删除这个错误规则
        cursor.execute("DELETE FROM kiro_qc_rule WHERE rule_code = 'RULE_A01_RC035'")
        print("✅ 已删除错误规则")
    else:
        print("✅ 规则表中无RULE_A01_RC035")
    
    # 2. 检查缺陷详情表
    cursor.execute("SELECT COUNT(*) FROM kiro_qc_defect_detail WHERE rule_code = 'RULE_A01_RC035'")
    defect_count = cursor.fetchone()[0]
    if defect_count > 0:
        print(f"❌ 缺陷表中有RULE_A01_RC035: {defect_count}条")
        cursor.execute("DELETE FROM kiro_qc_defect_detail WHERE rule_code = 'RULE_A01_RC035'")
        print("✅ 已删除错误缺陷记录")
    else:
        print("✅ 缺陷表中无RULE_A01_RC035")
    
    # 3. 检查所有表中是否还有A01相关的民族记录
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    for table_tuple in tables:
        table_name = table_tuple[0]
        if 'kiro' in table_name.lower():
            try:
                cursor.execute(f"DESCRIBE {table_name}")
                columns = [col[0] for col in cursor.fetchall()]
                
                if 'rule_code' in columns:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE rule_code LIKE '%A01%RC035%'")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print(f"❌ 表{table_name}中有A01民族记录: {count}条")
                        cursor.execute(f"DELETE FROM {table_name} WHERE rule_code LIKE '%A01%RC035%'")
                        print(f"✅ 已清理表{table_name}")
            except:
                pass
    
    # 4. 验证当前正确的规则
    cursor.execute("""
        SELECT rule_code, field_code, field_name, status 
        FROM kiro_qc_rule 
        WHERE dict_types = 'RC035' AND status = 'active'
    """)
    correct_rules = cursor.fetchall()
    
    print("\n当前正确的民族规则:")
    for rule_code, field_code, field_name, status in correct_rules:
        print(f"  {rule_code}: {field_code} ({field_name}) - {status}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n✅ 清理完成，现在重启应用并测试")
    
except Exception as e:
    print(f"错误: {e}")