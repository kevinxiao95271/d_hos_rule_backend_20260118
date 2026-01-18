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
print("清理旧的质控结果")
print("=" * 80)

# 1. 检查质控结果表中是否有旧规则的记录
print("\n1. 检查质控结果表:")
try:
    cursor.execute("SELECT COUNT(*) FROM kiro_qc_result WHERE rule_code = 'RULE_A01_RC035'")
    old_result_count = cursor.fetchone()[0]
    print(f"  旧规则 RULE_A01_RC035 的结果记录: {old_result_count} 条")
    
    cursor.execute("SELECT COUNT(*) FROM kiro_qc_defect WHERE rule_code = 'RULE_A01_RC035'")
    old_defect_count = cursor.fetchone()[0]
    print(f"  旧规则 RULE_A01_RC035 的缺陷记录: {old_defect_count} 条")
    
    if old_result_count > 0 or old_defect_count > 0:
        print(f"\n  清理旧的质控结果:")
        
        # 清理旧的质控结果
        cursor.execute("DELETE FROM kiro_qc_result WHERE rule_code = 'RULE_A01_RC035'")
        deleted_results = cursor.rowcount
        
        cursor.execute("DELETE FROM kiro_qc_defect WHERE rule_code = 'RULE_A01_RC035'")
        deleted_defects = cursor.rowcount
        
        conn.commit()
        
        print(f"  ✅ 已删除 {deleted_results} 条质控结果记录")
        print(f"  ✅ 已删除 {deleted_defects} 条缺陷记录")
    else:
        print(f"  ✅ 无需清理，没有旧规则的结果记录")
        
except Exception as e:
    print(f"  ❌ 检查失败: {e}")

# 2. 检查是否有A01字段相关的质控记录
print(f"\n2. 检查A01字段相关的质控记录:")
try:
    cursor.execute("SELECT COUNT(*) FROM kiro_qc_result WHERE field_code = 'A01'")
    a01_result_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM kiro_qc_defect WHERE field_code = 'A01'")
    a01_defect_count = cursor.fetchone()[0]
    
    print(f"  A01字段的结果记录: {a01_result_count} 条")
    print(f"  A01字段的缺陷记录: {a01_defect_count} 条")
    
    if a01_result_count > 0 or a01_defect_count > 0:
        print(f"\n  清理A01字段的质控记录:")
        
        cursor.execute("DELETE FROM kiro_qc_result WHERE field_code = 'A01'")
        deleted_results = cursor.rowcount
        
        cursor.execute("DELETE FROM kiro_qc_defect WHERE field_code = 'A01'")
        deleted_defects = cursor.rowcount
        
        conn.commit()
        
        print(f"  ✅ 已删除 {deleted_results} 条A01结果记录")
        print(f"  ✅ 已删除 {deleted_defects} 条A01缺陷记录")
    else:
        print(f"  ✅ 无需清理，没有A01字段的记录")
        
except Exception as e:
    print(f"  ❌ 清理失败: {e}")

# 3. 检查批次记录
print(f"\n3. 检查批次记录:")
try:
    cursor.execute("SELECT COUNT(*) FROM kiro_qc_batch")
    batch_count = cursor.fetchone()[0]
    print(f"  批次记录总数: {batch_count} 条")
    
    if batch_count > 0:
        # 可以选择清理所有批次记录，让用户重新运行质控
        print(f"  建议清理所有批次记录，让用户重新运行质控")
        
        # 取消注释下面的代码来清理批次记录
        # cursor.execute("DELETE FROM kiro_qc_batch")
        # deleted_batches = cursor.rowcount
        # conn.commit()
        # print(f"  ✅ 已删除 {deleted_batches} 条批次记录")
        
except Exception as e:
    print(f"  ❌ 检查批次记录失败: {e}")

# 4. 验证当前活跃规则
print(f"\n4. 验证当前活跃的民族规则:")
cursor.execute("SELECT rule_code, field_code, field_name, status FROM kiro_qc_rule WHERE dict_types = 'RC035' AND status = 'active'")
active_rules = cursor.fetchall()

for rule in active_rules:
    rule_code, field_code, field_name, status = rule
    print(f"  ✅ {rule_code}: {field_code} ({field_name}) - {status}")

cursor.close()
conn.close()

print(f"\n" + "=" * 80)
print("清理完成！")
print("建议用户:")
print("1. 刷新前端页面")
print("2. 重新运行质控")
print("3. 检查新的质控结果")
print("=" * 80)