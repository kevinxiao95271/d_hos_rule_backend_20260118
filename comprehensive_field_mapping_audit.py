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
print("全面字段映射审查")
print("=" * 80)

# 获取所有字典类型和对应的有效代码
dict_types = {
    'RC001': '性别',
    'RC002': '婚姻状况', 
    'RC003': '职业',
    'RC011': '病案质量',
    'RC013': '麻醉方式',
    'RC014': '切口愈合等级',
    'RC016': '死亡患者尸检',
    'RC019': '离院方式',
    'RC023': '科别',
    'RC026': '入院途径',
    'RC027': '入院病情',
    'RC028': '出院31天内再住院计划',
    'RC029': '手术级别',
    'RC030': 'ABO血型',
    'RC031': 'Rh血型',
    'RC032': '医疗付费方式',
    'RC033': '联系人关系',
    'RC035': '民族',
    'RC036': '省、自治区、直辖市',
    'RC037': '有无药物过敏',
    'RC038': '患者证件类别',
    'RC039': '判断代码'
}

# 检查每个字典类型对应的规则和字段映射
field_mapping_issues = []

for dict_type, dict_name in dict_types.items():
    print(f"\n{'='*60}")
    print(f"检查 {dict_type} ({dict_name}) 字典")
    print(f"{'='*60}")
    
    # 获取该字典的有效代码
    cursor.execute("SELECT dict_code FROM sys_dict WHERE dict_type_code = %s", (dict_type,))
    valid_codes = [row[0] for row in cursor.fetchall()]
    print(f"有效代码: {valid_codes[:10]}{'...' if len(valid_codes) > 10 else ''}")
    
    # 查找使用该字典的规则
    cursor.execute("SELECT rule_code, field_code, field_name, description FROM kiro_qc_rule WHERE dict_types = %s AND status = 'active'", (dict_type,))
    rules = cursor.fetchall()
    
    if not rules:
        print(f"⚠️  未找到使用 {dict_type} 字典的活跃规则")
        continue
        
    for rule in rules:
        rule_code, field_code, field_name, description = rule
        print(f"\n规则: {rule_code}")
        print(f"字段: {field_code} ({field_name})")
        
        # 检查该字段的实际数据
        try:
            cursor.execute(f"SELECT {field_code}, COUNT(*) as cnt FROM d_mr WHERE {field_code} IS NOT NULL AND {field_code} != '' AND {field_code} != '-' GROUP BY {field_code} ORDER BY cnt DESC LIMIT 5")
            field_data = cursor.fetchall()
            
            if field_data:
                print(f"字段 {field_code} 的实际数据:")
                valid_count = 0
                invalid_count = 0
                invalid_samples = []
                
                for value, count in field_data:
                    is_valid = str(value) in [str(code) for code in valid_codes]
                    status = "✅" if is_valid else "❌"
                    print(f"  {status} '{value}': {count}次")
                    
                    if is_valid:
                        valid_count += count
                    else:
                        invalid_count += count
                        invalid_samples.append(str(value))
                
                # 计算总记录数
                cursor.execute(f"SELECT COUNT(*) FROM d_mr WHERE {field_code} IS NOT NULL AND {field_code} != '' AND {field_code} != '-'")
                total_records = cursor.fetchone()[0]
                
                if invalid_count > 0:
                    issue = {
                        'dict_type': dict_type,
                        'dict_name': dict_name,
                        'rule_code': rule_code,
                        'field_code': field_code,
                        'field_name': field_name,
                        'total_records': total_records,
                        'valid_count': valid_count,
                        'invalid_count': invalid_count,
                        'invalid_samples': invalid_samples[:3],
                        'accuracy': (valid_count / total_records * 100) if total_records > 0 else 0
                    }
                    field_mapping_issues.append(issue)
                    print(f"  ❌ 字段映射问题: {invalid_count}/{total_records} 条记录无效 ({invalid_count/total_records*100:.1f}%)")
                else:
                    print(f"  ✅ 字段映射正确: {valid_count}/{total_records} 条记录有效 (100%)")
            else:
                print(f"  ⚠️  字段 {field_code} 无数据")
                
        except Exception as e:
            print(f"  ❌ 检查字段 {field_code} 失败: {e}")

# 总结字段映射问题
print(f"\n" + "=" * 80)
print("字段映射问题总结")
print("=" * 80)

if field_mapping_issues:
    print(f"发现 {len(field_mapping_issues)} 个字段映射问题:")
    
    for i, issue in enumerate(field_mapping_issues, 1):
        print(f"\n{i}. {issue['dict_type']} - {issue['dict_name']}")
        print(f"   规则: {issue['rule_code']}")
        print(f"   字段: {issue['field_code']} ({issue['field_name']})")
        print(f"   准确率: {issue['accuracy']:.1f}%")
        print(f"   无效数据样例: {issue['invalid_samples']}")
        print(f"   影响记录: {issue['invalid_count']}/{issue['total_records']}")

    # 按准确率排序，优先修复最严重的问题
    field_mapping_issues.sort(key=lambda x: x['accuracy'])
    
    print(f"\n优先修复顺序 (按准确率从低到高):")
    for i, issue in enumerate(field_mapping_issues, 1):
        print(f"{i}. {issue['field_code']} ({issue['dict_name']}) - {issue['accuracy']:.1f}%准确率")

else:
    print("✅ 未发现字段映射问题")

cursor.close()
conn.close()

print(f"\n" + "=" * 80)
print("全面字段映射审查完成")
print("=" * 80)