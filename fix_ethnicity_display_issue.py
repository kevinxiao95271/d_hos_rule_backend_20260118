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
print("修复民族字段显示问题")
print("=" * 80)

# 1. 检查所有kiro开头的表
print("\n1. 检查所有kiro开头的表:")
cursor.execute("SHOW TABLES LIKE 'kiro%'")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

# 2. 检查质控结果相关的表
print("\n2. 检查质控结果相关的表:")
cursor.execute("SHOW TABLES LIKE '%result%'")
result_tables = cursor.fetchall()
for table in result_tables:
    print(f"  - {table[0]}")

cursor.execute("SHOW TABLES LIKE '%qc%'")
qc_tables = cursor.fetchall()
for table in qc_tables:
    print(f"  - {table[0]}")

# 3. 检查是否有批次结果表
print("\n3. 检查批次相关表:")
cursor.execute("SHOW TABLES LIKE '%batch%'")
batch_tables = cursor.fetchall()
for table in batch_tables:
    print(f"  - {table[0]}")

# 4. 如果找到了结果表，清理旧的结果
result_table_found = False
for table_tuple in tables:
    table_name = table_tuple[0]
    if 'result' in table_name.lower() or 'batch' in table_name.lower():
        print(f"\n4. 检查表 {table_name} 中的民族相关记录:")
        try:
            # 检查表结构
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]
            print(f"  表结构: {column_names}")
            
            # 如果有rule_code列，检查民族相关记录
            if 'rule_code' in column_names:
                cursor.execute(f"""
                    SELECT rule_code, COUNT(*) as cnt 
                    FROM {table_name} 
                    WHERE rule_code LIKE '%RC035%' OR rule_code LIKE '%A01%'
                    GROUP BY rule_code
                """)
                old_results = cursor.fetchall()
                
                if old_results:
                    print(f"  发现旧的民族相关记录:")
                    for rule_code, count in old_results:
                        print(f"    {rule_code}: {count}条")
                    
                    # 删除旧的A01相关记录
                    cursor.execute(f"""
                        DELETE FROM {table_name} 
                        WHERE rule_code LIKE '%A01%' AND rule_code LIKE '%RC035%'
                    """)
                    deleted_count = cursor.rowcount
                    if deleted_count > 0:
                        print(f"  ✅ 删除了 {deleted_count} 条旧的A01民族记录")
                        conn.commit()
                else:
                    print(f"  ✅ 表中无旧的民族相关记录")
                    
                result_table_found = True
                
        except Exception as e:
            print(f"  ❌ 检查表 {table_name} 失败: {e}")

# 5. 确认当前活跃的民族规则
print(f"\n5. 确认当前活跃的民族规则:")
cursor.execute("""
    SELECT rule_code, field_code, field_name, description, status 
    FROM kiro_qc_rule 
    WHERE dict_types = 'RC035' AND status = 'active'
    ORDER BY rule_code
""")
active_rules = cursor.fetchall()

print(f"  当前活跃的民族规则:")
for rule_code, field_code, field_name, description, status in active_rules:
    print(f"    {rule_code}: {field_code} ({field_name}) - {status}")

# 6. 验证A19C字段数据
print(f"\n6. 验证A19C字段数据:")
cursor.execute("""
    SELECT A19C, COUNT(*) as cnt 
    FROM d_mr 
    WHERE A19C IS NOT NULL AND A19C != '' AND A19C != '-'
    GROUP BY A19C 
    ORDER BY cnt DESC 
    LIMIT 10
""")
a19c_data = cursor.fetchall()

print(f"  A19C字段数据分布:")
for value, count in a19c_data:
    print(f"    '{value}': {count}次")

# 7. 检查病案445583_1的A19C值
print(f"\n7. 检查病案445583_1的A19C值:")
cursor.execute("SELECT A19C FROM d_mr WHERE A48 = '445583' AND A49 = '1'")
result = cursor.fetchone()
if result:
    print(f"  病案445583_1的A19C值: '{result[0]}'")
else:
    print(f"  ❌ 未找到病案445583_1")

# 8. 检查Redis缓存键（如果有的话）
print(f"\n8. 建议清理缓存:")
print(f"  - 重启Spring Boot应用以清理内存缓存")
print(f"  - 如果使用Redis，清理相关缓存键")
print(f"  - 清理浏览器缓存")

cursor.close()
conn.close()

print(f"\n" + "=" * 80)
print("修复完成")
print("=" * 80)
print("\n建议操作:")
print("1. 重启Spring Boot应用")
print("2. 清理浏览器缓存")
print("3. 重新运行质控批次")
print("4. 验证民族字段显示正确的代码值")