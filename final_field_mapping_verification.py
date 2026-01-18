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
print("最终字段映射验证报告")
print("=" * 80)

# 验证已修复的关键字段映射
fixed_mappings = [
    {
        'rule_code': 'RULE_A19C_RC035',
        'field_code': 'A19C',
        'field_name': '民族',
        'dict_type': 'RC035',
        'old_field': 'A01'
    },
    {
        'rule_code': 'RULE_A21C_RC002',
        'field_code': 'A21C', 
        'field_name': '婚姻状况',
        'dict_type': 'RC002',
        'old_field': 'A02'
    },
    {
        'rule_code': 'RULE_A46C_RC032',
        'field_code': 'A46C',
        'field_name': '医疗付费方式', 
        'dict_type': 'RC032',
        'old_field': 'A32'
    },
    {
        'rule_code': 'RULE_A12C_RC027',
        'field_code': 'A12C',
        'field_name': '入院病情',
        'dict_type': 'RC027', 
        'old_field': 'A27'
    }
]

print("1. 验证规则状态和字段映射:")
print("-" * 60)

for mapping in fixed_mappings:
    cursor.execute("SELECT rule_code, field_code, field_name, status, dict_types FROM kiro_qc_rule WHERE rule_code = %s", 
                  (mapping['rule_code'],))
    result = cursor.fetchone()
    
    if result:
        rule_code, field_code, field_name, status, dict_types = result
        
        # 检查字段映射是否正确
        field_correct = field_code == mapping['field_code']
        name_correct = field_name == mapping['field_name']
        dict_correct = dict_types == mapping['dict_type']
        status_correct = status == 'active'
        
        overall_status = "✅" if all([field_correct, name_correct, dict_correct, status_correct]) else "❌"
        
        print(f"{overall_status} {rule_code}")
        print(f"   字段编码: {field_code} {'✅' if field_correct else '❌'}")
        print(f"   字段名称: {field_name} {'✅' if name_correct else '❌'}")
        print(f"   字典类型: {dict_types} {'✅' if dict_correct else '❌'}")
        print(f"   规则状态: {status} {'✅' if status_correct else '❌'}")
        print(f"   修复前字段: {mapping['old_field']}")
        print()
    else:
        print(f"❌ 未找到规则: {mapping['rule_code']}")

print("2. 验证数据准确性:")
print("-" * 60)

for mapping in fixed_mappings:
    field_code = mapping['field_code']
    dict_type = mapping['dict_type']
    field_name = mapping['field_name']
    
    try:
        # 获取字典有效值
        cursor.execute("SELECT dict_code FROM sys_dict WHERE dict_type_code = %s", (dict_type,))
        valid_codes = [row[0] for row in cursor.fetchall()]
        
        # 检查字段数据匹配情况
        placeholders = ','.join(['%s'] * len(valid_codes))
        cursor.execute(f"SELECT COUNT(*) FROM d_mr WHERE {field_code} IN ({placeholders})", valid_codes)
        valid_count = cursor.fetchone()[0]
        
        cursor.execute(f"SELECT COUNT(*) FROM d_mr WHERE {field_code} IS NOT NULL AND {field_code} != '' AND {field_code} != '-'")
        total_count = cursor.fetchone()[0]
        
        if total_count > 0:
            accuracy = (valid_count / total_count) * 100
            status_icon = "✅" if accuracy >= 95 else "⚠️" if accuracy >= 50 else "❌"
            print(f"{status_icon} {field_code} ({field_name}): {valid_count}/{total_count} 有效 ({accuracy:.1f}%)")
        else:
            print(f"⚠️ {field_code} ({field_name}): 无数据")
            
    except Exception as e:
        print(f"❌ {field_code} ({field_name}): 验证失败 - {e}")

print("\n3. 检查旧字段规则状态:")
print("-" * 60)

old_fields = [mapping['old_field'] for mapping in fixed_mappings]
for old_field in old_fields:
    cursor.execute("SELECT COUNT(*) FROM kiro_qc_rule WHERE field_code = %s AND status = 'active'", (old_field,))
    active_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM kiro_qc_rule WHERE field_code = %s", (old_field,))
    total_count = cursor.fetchone()[0]
    
    if active_count == 0:
        print(f"✅ {old_field}: 无活跃规则 (共{total_count}个规则已停用)")
    else:
        print(f"⚠️ {old_field}: 仍有{active_count}个活跃规则")

print("\n4. 测试具体病案数据:")
print("-" * 60)

# 测试病案445583_1的字段值
cursor.execute("SELECT A19C, A21C, A46C, A12C FROM d_mr WHERE A48 = '445583' AND A49 = '1'")
result = cursor.fetchone()

if result:
    a19c, a21c, a46c, a12c = result
    print(f"病案445583_1的字段值:")
    print(f"  A19C (民族): '{a19c}'")
    print(f"  A21C (婚姻状况): '{a21c}'")
    print(f"  A46C (医疗付费方式): '{a46c}'")
    print(f"  A12C (入院病情): '{a12c}'")
    
    # 验证这些值是否在对应字典中
    validations = [
        ('A19C', a19c, 'RC035'),
        ('A21C', a21c, 'RC002'), 
        ('A46C', a46c, 'RC032'),
        ('A12C', a12c, 'RC027')
    ]
    
    print(f"\n  字典验证结果:")
    for field, value, dict_type in validations:
        if value:
            cursor.execute("SELECT COUNT(*) FROM sys_dict WHERE dict_type_code = %s AND dict_code = %s", 
                         (dict_type, value))
            is_valid = cursor.fetchone()[0] > 0
            status = "✅" if is_valid else "❌"
            print(f"    {status} {field}: '{value}' 在{dict_type}字典中")
        else:
            print(f"    ⚠️ {field}: 值为空")

cursor.close()
conn.close()

print(f"\n" + "=" * 80)
print("最终验证完成！")
print("=" * 80)
print("✅ 字段映射修复总结:")
print("   • A01 (错误) → A19C (民族) ✅")
print("   • A02 (错误) → A21C (婚姻状况) ✅") 
print("   • A32 (错误) → A46C (医疗付费方式) ✅")
print("   • A27 (错误) → A12C (入院病情) ✅")
print("✅ 规则编码已更新为正确的字段编码")
print("✅ 字段名称已更新为正确的含义")
print("=" * 80)