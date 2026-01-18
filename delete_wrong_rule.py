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
    
    print("删除错误的RULE_A01_RC035规则...")
    
    # 查找并显示错误规则
    cursor.execute("SELECT id, rule_code, field_code, field_name, status FROM kiro_qc_rule WHERE rule_code = 'RULE_A01_RC035'")
    wrong_rule = cursor.fetchone()
    
    if wrong_rule:
        rule_id, rule_code, field_code, field_name, status = wrong_rule
        print(f"发现错误规则:")
        print(f"  ID: {rule_id}")
        print(f"  规则代码: {rule_code}")
        print(f"  字段: {field_code} ({field_name})")
        print(f"  状态: {status}")
        
        # 删除错误规则
        cursor.execute("DELETE FROM kiro_qc_rule WHERE id = %s", (rule_id,))
        print(f"✅ 已删除错误规则 (ID: {rule_id})")
        
        # 清理相关的缺陷记录
        cursor.execute("DELETE FROM kiro_qc_defect_detail WHERE rule_id = %s", (rule_id,))
        deleted_defects = cursor.rowcount
        print(f"✅ 已删除相关缺陷记录: {deleted_defects}条")
        
    else:
        print("✅ 未找到RULE_A01_RC035规则")
    
    # 验证正确的规则存在
    cursor.execute("SELECT rule_code, field_code, field_name, status FROM kiro_qc_rule WHERE dict_types = 'RC035' AND status = 'active'")
    correct_rules = cursor.fetchall()
    
    print("\n当前正确的民族规则:")
    for rule_code, field_code, field_name, status in correct_rules:
        print(f"  {rule_code}: {field_code} ({field_name}) - {status}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n✅ 修复完成！现在重启应用测试")
    
except Exception as e:
    print(f"错误: {e}")