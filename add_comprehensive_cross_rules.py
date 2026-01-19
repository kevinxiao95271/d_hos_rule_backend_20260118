import pymysql
import json

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

print("🔧 添加综合Cross规则")
print("=" * 80)

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    # 定义综合cross规则
    comprehensive_rules = [
        # 1. 手术编码与名称配对规则 (C35x40C)
        {
            'rule_code': 'CROSS_C35x40C_C36x40N',
            'description': '其他手术操作编码40为空，但其他手术名称40不为空，两者必须同时有值或同时为空',
            'cross_type': 'field_pair',
            'primary_field': 'C35x40C',
            'primary_field_name': '其他手术操作编码40',
            'related_fields': json.dumps([{"field": "C36x40N", "name": "其他手术操作名称40"}]),
            'constraint_conditions': json.dumps({"type": "both_or_neither", "logic": "AND"}),
            'error_message': '手术编码与名称必须同时填写或同时为空',
            'expected_value': '编码和名称同时有值或同时为空',
            'deduct_score': 0.5,
            'source_tables': 'd_mr'
        },
        
        # 2. 条件必填规则 - 手术级别
        {
            'rule_code': 'CROSS_C38x12_SURGERY_REQUIRED',
            'description': '其他手术操作级别12，其他手术及操作编码12属性为手术或介入治疗时必填',
            'cross_type': 'conditional_required',
            'primary_field': 'C38x12',
            'primary_field_name': '其他手术操作级别12',
            'related_fields': json.dumps([{"field": "C35x12C", "name": "其他手术操作编码12"}]),
            'constraint_conditions': json.dumps({
                "type": "conditional_required",
                "condition_field": "C35x12C",
                "condition_values": ["手术", "介入治疗"],
                "required_when": "condition_matched"
            }),
            'error_message': '当手术编码属性为手术或介入治疗时，手术级别必填',
            'expected_value': '手术级别不能为空',
            'deduct_score': 0.5,
            'source_tables': 'd_mr'
        },
        
        # 3. 麻醉医师必填规则
        {
            'rule_code': 'CROSS_C44x21_ANESTHESIA_REQUIRED',
            'description': '其他手术操作21麻醉医师，其他手术及操作编码21属性为手术时必填',
            'cross_type': 'conditional_required',
            'primary_field': 'C44x21',
            'primary_field_name': '其他手术操作21麻醉医师',
            'related_fields': json.dumps([{"field": "C35x21C", "name": "其他手术操作编码21"}]),
            'constraint_conditions': json.dumps({
                "type": "conditional_required",
                "condition_field": "C35x21C",
                "condition_values": ["手术"],
                "required_when": "condition_matched"
            }),
            'error_message': '当手术编码属性为手术时，麻醉医师必填',
            'expected_value': '麻醉医师不能为空',
            'deduct_score': 0.5,
            'source_tables': 'd_mr'
        },
        
        # 4. 麻醉方式必填规则
        {
            'rule_code': 'CROSS_C43x21C_ANESTHESIA_METHOD',
            'description': '其他手术操作21麻醉方式，其他手术及操作编码属性为手术时必填',
            'cross_type': 'conditional_required',
            'primary_field': 'C43x21C',
            'primary_field_name': '其他手术操作21麻醉方式',
            'related_fields': json.dumps([{"field": "C35x21C", "name": "其他手术操作编码21"}]),
            'constraint_conditions': json.dumps({
                "type": "conditional_required",
                "condition_field": "C35x21C",
                "condition_values": ["手术"],
                "required_when": "condition_matched"
            }),
            'error_message': '当手术编码属性为手术时，麻醉方式必填',
            'expected_value': '麻醉方式不能为空',
            'deduct_score': 0.5,
            'source_tables': 'd_mr'
        },
        
        # 5. 儿童诊断逻辑规则
        {
            'rule_code': 'CROSS_C06x24C_AGE_CHILD',
            'description': '出院其他诊断编码24不符合逻辑判断，12岁以下儿童一般不应编码"C50-C63，D24-D29"',
            'cross_type': 'age_diagnosis',
            'primary_field': 'C06x24C',
            'primary_field_name': '出院其他诊断编码24',
            'related_fields': json.dumps([{"field": "A13", "name": "年龄"}]),
            'constraint_conditions': json.dumps({
                "type": "age_diagnosis",
                "age_limit": 12,
                "comparison": "<",
                "forbidden_codes": ["C50-C63", "D24-D29"]
            }),
            'error_message': '12岁以下儿童不应编码成人相关疾病',
            'expected_value': '符合年龄的诊断编码',
            'deduct_score': 1.0,
            'source_tables': 'd_mr'
        },
        
        # 6. 成人诊断逻辑规则
        {
            'rule_code': 'CROSS_C06x13C_AGE_ADULT',
            'description': '出院其他诊断编码13不符合逻辑判断，17岁及以上不应编"E30.1，E30.8，F64.2，F84.3，G93.7，L12.2，L21.1，L44.4，L70.4，N92.2，R62.0，Z00.2-Z00.3"',
            'cross_type': 'age_diagnosis',
            'primary_field': 'C06x13C',
            'primary_field_name': '出院其他诊断编码13',
            'related_fields': json.dumps([{"field": "A13", "name": "年龄"}]),
            'constraint_conditions': json.dumps({
                "type": "age_diagnosis",
                "age_limit": 17,
                "comparison": ">=",
                "forbidden_codes": ["E30.1", "E30.8", "F64.2", "F84.3", "G93.7", "L12.2", "L21.1", "L44.4", "L70.4", "N92.2", "R62.0", "Z00.2", "Z00.3"]
            }),
            'error_message': '17岁及以上不应编码儿童相关疾病',
            'expected_value': '符合年龄的诊断编码',
            'deduct_score': 1.0,
            'source_tables': 'd_mr'
        },
        
        # 7. 输血反应逻辑规则
        {
            'rule_code': 'CROSS_F21_TRANSFUSION_REACTION',
            'description': '红细胞、血小板、血浆、全血、自体血回输这五个字段都为0值，存在输血反应',
            'cross_type': 'transfusion_logic',
            'primary_field': 'F21',
            'primary_field_name': '输血反应',
            'related_fields': json.dumps([
                {"field": "D21", "name": "红细胞"},
                {"field": "D22", "name": "血小板"},
                {"field": "D23", "name": "血浆"},
                {"field": "D24", "name": "全血"},
                {"field": "D25", "name": "自体血回输"}
            ]),
            'constraint_conditions': json.dumps({
                "type": "transfusion_reaction",
                "logic": "no_transfusion_but_reaction"
            }),
            'error_message': '无输血记录但存在输血反应',
            'expected_value': '输血记录与输血反应保持一致',
            'deduct_score': 0.0,
            'source_tables': 'd_mr'
        },
        
        # 8. 血费与输血记录一致性规则1
        {
            'rule_code': 'CROSS_D26_TRANSFUSION_FEE1',
            'description': '存在输血记录，未发生血液费用',
            'cross_type': 'transfusion_logic',
            'primary_field': 'D26',
            'primary_field_name': '血费',
            'related_fields': json.dumps([
                {"field": "D21", "name": "红细胞"},
                {"field": "D22", "name": "血小板"},
                {"field": "D23", "name": "血浆"},
                {"field": "D24", "name": "全血"},
                {"field": "D25", "name": "自体血回输"}
            ]),
            'constraint_conditions': json.dumps({
                "type": "transfusion_fee",
                "logic": "has_transfusion_no_fee"
            }),
            'error_message': '存在输血记录但未产生血费',
            'expected_value': '输血记录与血费保持一致',
            'deduct_score': 0.0,
            'source_tables': 'd_mr'
        },
        
        # 9. 血费与输血记录一致性规则2
        {
            'rule_code': 'CROSS_D26_TRANSFUSION_FEE2',
            'description': '血费>0时，未发生输血行为',
            'cross_type': 'transfusion_logic',
            'primary_field': 'D26',
            'primary_field_name': '血费',
            'related_fields': json.dumps([
                {"field": "D21", "name": "红细胞"},
                {"field": "D22", "name": "血小板"},
                {"field": "D23", "name": "血浆"},
                {"field": "D24", "name": "全血"},
                {"field": "D25", "name": "自体血回输"}
            ]),
            'constraint_conditions': json.dumps({
                "type": "transfusion_fee",
                "logic": "has_fee_no_transfusion"
            }),
            'error_message': '产生血费但无输血记录',
            'expected_value': '血费与输血记录保持一致',
            'deduct_score': 0.0,
            'source_tables': 'd_mr'
        }
    ]
    
    print(f"\n准备插入 {len(comprehensive_rules)} 条综合cross规则...")
    
    # 插入规则
    for i, rule in enumerate(comprehensive_rules, 1):
        try:
            insert_sql = """
            INSERT INTO kiro_qc_rule_cross (
                rule_code, description, cross_type, primary_field, primary_field_name,
                related_fields, constraint_conditions, error_message, expected_value, 
                deduct_score, source_tables, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
            """
            
            cursor.execute(insert_sql, (
                rule['rule_code'],
                rule['description'],
                rule['cross_type'],
                rule['primary_field'],
                rule['primary_field_name'],
                rule['related_fields'],
                rule['constraint_conditions'],
                rule['error_message'],
                rule['expected_value'],
                rule['deduct_score'],
                rule['source_tables']
            ))
            
            print(f"  {i}. ✅ {rule['rule_code']}: {rule['cross_type']}")
            
        except Exception as e:
            if "Duplicate entry" in str(e):
                print(f"  {i}. ⚠️  {rule['rule_code']}: 已存在，跳过")
            else:
                print(f"  {i}. ❌ {rule['rule_code']}: {e}")
    
    conn.commit()
    
    # 验证插入结果
    print(f"\n验证插入结果:")
    cursor.execute("SELECT COUNT(*) FROM kiro_qc_rule_cross WHERE status = 'active'")
    total_count = cursor.fetchone()[0]
    print(f"  活跃cross规则总数: {total_count}")
    
    # 按类型统计
    cursor.execute("""
        SELECT cross_type, COUNT(*) as cnt 
        FROM kiro_qc_rule_cross 
        WHERE status = 'active' 
        GROUP BY cross_type
    """)
    type_stats = cursor.fetchall()
    
    print(f"  按类型统计:")
    for cross_type, count in type_stats:
        print(f"    {cross_type}: {count}条")
    
    cursor.close()
    conn.close()
    
    print(f"\n" + "=" * 80)
    print("综合Cross规则添加完成")
    print("=" * 80)
    
except Exception as e:
    print(f"❌ 添加失败: {e}")
    import traceback
    traceback.print_exc()