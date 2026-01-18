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
print("检查当前民族相关规则状态")
print("=" * 80)

# 检查所有与民族相关的规则
print("\n1. 检查所有与民族(RC035)相关的规则:")
cursor.execute("""
    SELECT rule_code, field_code, field_name, description, status, dict_types 
    FROM kiro_qc_rule 
    WHERE dict_types = 'RC035' OR description LIKE '%民族%'
    ORDER BY rule_code
""")
rules = cursor.fetchall()

for rule in rules:
    rule_code, field_code, field_name, description, status, dict_types = rule
    print(f"  规则: {rule_code}")
    print(f"  字段: {field_code} ({field_name})")
    print(f"  状态: {status}")
    print(f"  字典: {dict_types}")
    print(f"  描述: {description}")
    print()

# 检查是否还有使用A01字段的规则
print("\n2. 检查是否还有使用A01字段的规则:")
cursor.execute("""
    SELECT rule_code, field_code, field_name, description, status, dict_types 
    FROM kiro_qc_rule 
    WHERE field_code = 'A01'
    ORDER BY rule_code
""")
a01_rules = cursor.fetchall()

if a01_rules:
    print("  发现使用A01字段的规则:")
    for rule in a01_rules:
        rule_code, field_code, field_name, description, status, dict_types = rule
        print(f"    规则: {rule_code} - 状态: {status}")
        print(f"    字段: {field_code} ({field_name})")
        print(f"    字典: {dict_types}")
        print()
else:
    print("  ✅ 未发现使用A01字段的规则")

# 检查质控结果表中是否还有旧的规则代码
print("\n3. 检查质控结果表中的规则代码:")
cursor.execute("""
    SELECT DISTINCT rule_code, COUNT(*) as cnt
    FROM kiro_qc_result 
    WHERE rule_code LIKE '%RC035%' OR rule_code LIKE '%A01%'
    GROUP BY rule_code
    ORDER BY rule_code
""")
result_rules = cursor.fetchall()

if result_rules:
    print("  质控结果表中的规则代码:")
    for rule_code, count in result_rules:
        print(f"    {rule_code}: {count}条记录")
else:
    print("  ✅ 质控结果表中无相关记录")

# 检查最近的质控结果
print("\n4. 检查最近的民族字段质控结果:")
cursor.execute("""
    SELECT r.rule_code, r.field_code, r.actual_value, r.expected_value, r.created_time
    FROM kiro_qc_result r
    WHERE r.rule_code LIKE '%RC035%' OR r.field_code IN ('A01', 'A19C')
    ORDER BY r.created_time DESC
    LIMIT 5
""")
recent_results = cursor.fetchall()

if recent_results:
    print("  最近的质控结果:")
    for rule_code, field_code, actual_value, expected_value, created_time in recent_results:
        print(f"    时间: {created_time}")
        print(f"    规则: {rule_code}")
        print(f"    字段: {field_code}")
        print(f"    实际值: '{actual_value}'")
        print(f"    期望值: {expected_value}")
        print()
else:
    print("  ✅ 无最近的质控结果")

# 检查A19C字段的实际数据
print("\n5. 检查A19C字段的实际数据样例:")
cursor.execute("""
    SELECT A48, A49, A19C 
    FROM d_mr 
    WHERE A48 = '445583' AND A49 = '1'
""")
sample_data = cursor.fetchone()

if sample_data:
    a48, a49, a19c = sample_data
    print(f"  病案 {a48}_{a49} 的A19C值: '{a19c}'")
else:
    print("  ❌ 未找到样例数据")

cursor.close()
conn.close()

print(f"\n" + "=" * 80)
print("检查完成")
print("=" * 80)