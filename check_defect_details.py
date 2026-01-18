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
print("检查缺陷详情表")
print("=" * 80)

# 检查kiro_qc_defect_detail表结构
print("\n1. 检查kiro_qc_defect_detail表结构:")
cursor.execute("DESCRIBE kiro_qc_defect_detail")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[0]}: {col[1]}")

# 检查民族相关的缺陷记录
print("\n2. 检查民族相关的缺陷记录:")
cursor.execute("""
    SELECT rule_code, field_code, field_name, actual_value, expected_value, COUNT(*) as cnt
    FROM kiro_qc_defect_detail 
    WHERE rule_code LIKE '%RC035%' OR field_code IN ('A01', 'A19C') OR field_name LIKE '%民族%'
    GROUP BY rule_code, field_code, field_name, actual_value, expected_value
    ORDER BY cnt DESC
    LIMIT 10
""")
defect_records = cursor.fetchall()

if defect_records:
    print("  发现民族相关缺陷记录:")
    for rule_code, field_code, field_name, actual_value, expected_value, count in defect_records:
        print(f"    规则: {rule_code}")
        print(f"    字段: {field_code} ({field_name})")
        print(f"    实际值: '{actual_value}'")
        print(f"    期望值: {expected_value}")
        print(f"    数量: {count}")
        print()
else:
    print("  ✅ 未发现民族相关缺陷记录")

# 检查病案445583_1的缺陷记录
print("\n3. 检查病案445583_1的所有缺陷记录:")
cursor.execute("""
    SELECT rule_code, field_code, field_name, actual_value, expected_value, deduct_score
    FROM kiro_qc_defect_detail 
    WHERE mr_key = '445583_1'
    ORDER BY rule_code
""")
patient_defects = cursor.fetchall()

if patient_defects:
    print(f"  病案445583_1的缺陷记录:")
    for rule_code, field_code, field_name, actual_value, expected_value, deduct_score in patient_defects:
        print(f"    规则: {rule_code}")
        print(f"    字段: {field_code} ({field_name})")
        print(f"    实际值: '{actual_value}'")
        print(f"    期望值: {expected_value}")
        print(f"    扣分: {deduct_score}")
        print()
else:
    print("  ✅ 病案445583_1无缺陷记录")

# 检查是否有使用A01字段但显示错误值的记录
print("\n4. 检查是否有使用A01字段但显示错误值的记录:")
cursor.execute("""
    SELECT rule_code, field_code, actual_value, COUNT(*) as cnt
    FROM kiro_qc_defect_detail 
    WHERE field_code = 'A01' AND actual_value LIKE 'ABS%'
    GROUP BY rule_code, field_code, actual_value
    ORDER BY cnt DESC
    LIMIT 5
""")
wrong_a01_records = cursor.fetchall()

if wrong_a01_records:
    print("  发现A01字段错误值记录:")
    for rule_code, field_code, actual_value, count in wrong_a01_records:
        print(f"    规则: {rule_code}, 字段: {field_code}, 值: '{actual_value}', 数量: {count}")
        
    # 删除这些错误记录
    print("\n  删除A01字段的错误记录...")
    cursor.execute("""
        DELETE FROM kiro_qc_defect_detail 
        WHERE field_code = 'A01' AND actual_value LIKE 'ABS%'
    """)
    deleted_count = cursor.rowcount
    print(f"  ✅ 删除了 {deleted_count} 条A01字段错误记录")
    conn.commit()
else:
    print("  ✅ 未发现A01字段错误值记录")

# 检查最近的质控批次
print("\n5. 检查最近的质控批次:")
cursor.execute("""
    SELECT batch_key, check_year, check_quarter, check_month, case_count, status, created_at
    FROM kiro_qc_batch_summary 
    ORDER BY created_at DESC 
    LIMIT 3
""")
recent_batches = cursor.fetchall()

if recent_batches:
    print("  最近的质控批次:")
    for batch_key, year, quarter, month, case_count, status, created_at in recent_batches:
        print(f"    批次: {batch_key}")
        print(f"    时间: {year}年{quarter}季度{month}月")
        print(f"    病案数: {case_count}")
        print(f"    状态: {status}")
        print(f"    创建时间: {created_at}")
        print()

# 清理所有旧的民族相关缺陷记录（如果有错误的规则代码）
print("\n6. 清理旧的民族相关缺陷记录:")
cursor.execute("""
    DELETE FROM kiro_qc_defect_detail 
    WHERE rule_code = 'RULE_A01_RC035'
""")
deleted_old_rules = cursor.rowcount
if deleted_old_rules > 0:
    print(f"  ✅ 删除了 {deleted_old_rules} 条旧的RULE_A01_RC035记录")
    conn.commit()
else:
    print("  ✅ 未发现旧的RULE_A01_RC035记录")

cursor.close()
conn.close()

print(f"\n" + "=" * 80)
print("检查完成")
print("=" * 80)
print("\n下一步操作:")
print("1. 重启Spring Boot应用")
print("2. 重新运行质控批次")
print("3. 验证民族字段现在显示正确的A19C值")