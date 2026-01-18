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

print("=" * 60)
print("快速修复关键字段映射")
print("=" * 60)

# 1. 修复民族字段 A01 → A19C
print("\n1. 修复民族字段映射:")
try:
    cursor.execute("""
        UPDATE kiro_qc_rule 
        SET field_code = 'A19C',
            field_name = '民族',
            description = '民族必须在RC035字典范围内'
        WHERE rule_code = 'RULE_A01_RC035'
    """)
    
    cursor.execute("UPDATE kiro_qc_rule SET status = 'draft' WHERE field_code = 'A01' AND rule_code != 'RULE_A01_RC035'")
    
    conn.commit()
    print("  ✅ 民族字段: A01 → A19C")
except Exception as e:
    print(f"  ❌ 修复失败: {e}")

# 2. 修复婚姻状况字段 A02 → A21C  
print("\n2. 修复婚姻状况字段映射:")
try:
    cursor.execute("""
        UPDATE kiro_qc_rule 
        SET field_code = 'A21C',
            field_name = '婚姻状况',
            description = '婚姻状况必须在RC002字典范围内'
        WHERE rule_code = 'RULE_A02_RC002'
    """)
    
    cursor.execute("UPDATE kiro_qc_rule SET status = 'draft' WHERE field_code = 'A02' AND rule_code != 'RULE_A02_RC002'")
    
    conn.commit()
    print("  ✅ 婚姻状况字段: A02 → A21C")
except Exception as e:
    print(f"  ❌ 修复失败: {e}")

# 3. 停用其他严重问题字段的规则
problem_fields = ['A16', 'A17', 'A20', 'A22', 'A26']
print(f"\n3. 停用问题字段规则:")

for field in problem_fields:
    try:
        cursor.execute("UPDATE kiro_qc_rule SET status = 'draft' WHERE field_code = %s", (field,))
        affected = cursor.rowcount
        conn.commit()
        print(f"  ✅ {field}: 停用 {affected} 个规则")
    except Exception as e:
        print(f"  ❌ {field}: {e}")

# 4. 验证修复结果
print(f"\n4. 验证修复结果:")
cursor.execute("SELECT rule_code, field_code, field_name, status FROM kiro_qc_rule WHERE rule_code IN ('RULE_A01_RC035', 'RULE_A02_RC002')")
results = cursor.fetchall()

for rule_code, field_code, field_name, status in results:
    print(f"  {rule_code}: {field_code} ({field_name}) - {status}")

cursor.close()
conn.close()

print(f"\n" + "=" * 60)
print("快速修复完成！")
print("=" * 60)