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
print("查找并修复旧规则")
print("=" * 80)

# 1. 查找是否还有RULE_A01_RC035规则
print("\n1. 查找RULE_A01_RC035规则:")
cursor.execute("SELECT id, rule_code, field_code, field_name, status, dict_types FROM kiro_qc_rule WHERE rule_code = 'RULE_A01_RC035'")
old_rule = cursor.fetchone()

if old_rule:
    rule_id, rule_code, field_code, field_name, status, dict_types = old_rule
    print(f"  ❌ 找到旧规则:")
    print(f"     规则ID: {rule_id}")
    print(f"     规则编码: {rule_code}")
    print(f"     字段编码: {field_code}")
    print(f"     字段名称: {field_name}")
    print(f"     状态: {status}")
    print(f"     字典类型: {dict_types}")
    
    # 彻底删除或停用这个旧规则
    print(f"\n  修复旧规则:")
    try:
        # 方案1: 停用旧规则
        cursor.execute("UPDATE kiro_qc_rule SET status = 'draft' WHERE id = %s", (rule_id,))
        conn.commit()
        print(f"  ✅ 已停用旧规则 RULE_A01_RC035")
        
        # 方案2: 或者直接删除（如果需要的话）
        # cursor.execute("DELETE FROM kiro_qc_rule WHERE id = %s", (rule_id,))
        # conn.commit()
        # print(f"  ✅ 已删除旧规则 RULE_A01_RC035")
        
    except Exception as e:
        print(f"  ❌ 修复失败: {e}")
        
else:
    print("  ✅ 未找到旧规则 RULE_A01_RC035")

# 2. 确认新规则状态
print(f"\n2. 确认新规则状态:")
cursor.execute("SELECT id, rule_code, field_code, field_name, status, dict_types FROM kiro_qc_rule WHERE rule_code = 'RULE_A19C_RC035'")
new_rule = cursor.fetchone()

if new_rule:
    rule_id, rule_code, field_code, field_name, status, dict_types = new_rule
    print(f"  ✅ 新规则状态:")
    print(f"     规则ID: {rule_id}")
    print(f"     规则编码: {rule_code}")
    print(f"     字段编码: {field_code}")
    print(f"     字段名称: {field_name}")
    print(f"     状态: {status}")
    print(f"     字典类型: {dict_types}")
else:
    print("  ❌ 未找到新规则 RULE_A19C_RC035")

# 3. 检查所有活跃的民族相关规则
print(f"\n3. 检查所有活跃的民族相关规则:")
cursor.execute("SELECT rule_code, field_code, field_name, status FROM kiro_qc_rule WHERE (dict_types = 'RC035' OR field_name LIKE '%民族%') AND status = 'active'")
active_rules = cursor.fetchall()

if active_rules:
    for rule in active_rules:
        rule_code, field_code, field_name, status = rule
        print(f"  规则: {rule_code} -> {field_code} ({field_name}) - {status}")
else:
    print("  未找到活跃的民族相关规则")

# 4. 重新启动后端服务的建议
print(f"\n4. 系统缓存清理建议:")
print("  如果规则已经正确但前端仍显示错误，可能需要:")
print("  1. 重启后端服务 (端口4101)")
print("  2. 清理Redis缓存 (如果使用了缓存)")
print("  3. 刷新前端页面")

# 5. 验证A19C字段数据
print(f"\n5. 验证A19C字段数据质量:")
cursor.execute("SELECT dict_code FROM sys_dict WHERE dict_type_code = 'RC035'")
valid_codes = [row[0] for row in cursor.fetchall()]

cursor.execute(f"SELECT COUNT(*) FROM d_mr WHERE A19C IN ({','.join(['%s'] * len(valid_codes))})", valid_codes)
valid_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM d_mr WHERE A19C IS NOT NULL AND A19C != '' AND A19C != '-'")
total_count = cursor.fetchone()[0]

if total_count > 0:
    accuracy = (valid_count / total_count) * 100
    print(f"  A19C字段数据质量: {valid_count}/{total_count} 有效 ({accuracy:.1f}%)")

cursor.close()
conn.close()

print(f"\n" + "=" * 80)
print("修复完成")
print("=" * 80)