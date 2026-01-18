import pymysql

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

# 规则数据（从需求文档中提取）
rules = [
    {
        'rule_code': 'A18x03_value_check',
        'field_name': '新生儿出生体重(克)3',
        'field_code': 'A18x03',
        'table_name': 'd_mr',
        'rule_type': 'value_check',
        'deduct_score': -4,
        'description': 'error16：产妇诊断编码中含有Z37.5，Z37.6编码时，必须填写新生儿出生体重3',
        'status': 'active'
    },
    {
        'rule_code': 'A18x01_cross_check_null',
        'field_name': '新生儿出生体重(克)',
        'field_code': 'A18x01',
        'table_name': 'd_mr',
        'rule_type': 'cross_check_null',
        'deduct_score': -4,
        'description': 'error16：产妇诊断编码中含有Z37.0，Z37.2，Z37.3，Z37.5，Z37.6编码时，必须填写新生儿出生体重',
        'status': 'active'
    },
    {
        'rule_code': 'A18x01_range_check',
        'field_name': '新生儿出生体重(克)',
        'field_code': 'A18x01',
        'table_name': 'd_mr',
        'rule_type': 'range_check',
        'deduct_score': -4,
        'description': '新生儿出生体重范围：100克-9999克，需为整数且精确到10g',
        'status': 'active'
    },
    {
        'rule_code': 'A18x02_value_check',
        'field_name': '新生儿出生体重(克)2',
        'field_code': 'A18x02',
        'table_name': 'd_mr',
        'rule_type': 'value_check',
        'deduct_score': -4,
        'description': 'error16：产妇诊断编码中含有Z37.2，Z37.5，Z37.6编码时，必须填写新生儿出生体重2',
        'status': 'active'
    },
    {
        'rule_code': 'A18x02_range_check',
        'field_name': '新生儿出生体重(克)2',
        'field_code': 'A18x02',
        'table_name': 'd_mr',
        'rule_type': 'range_check',
        'deduct_score': -4,
        'description': '新生儿出生体重2范围：100克-9999克，需为整数且精确到10g',
        'status': 'active'
    },
    {
        'rule_code': 'A18x03_range_check',
        'field_name': '新生儿出生体重(克)3',
        'field_code': 'A18x03',
        'table_name': 'd_mr',
        'rule_type': 'range_check',
        'deduct_score': -4,
        'description': '新生儿出生体重3范围：100克-9999克，需为整数且精确到10g',
        'status': 'active'
    }
]

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

print("开始初始化规则...")
for rule in rules:
    try:
        cursor.execute("""
            INSERT INTO kiro_qc_rule 
            (rule_code, field_name, field_code, table_name, rule_type, deduct_score, description, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            field_name=VALUES(field_name),
            field_code=VALUES(field_code),
            table_name=VALUES(table_name),
            rule_type=VALUES(rule_type),
            deduct_score=VALUES(deduct_score),
            description=VALUES(description),
            status=VALUES(status)
        """, (
            rule['rule_code'],
            rule['field_name'],
            rule['field_code'],
            rule['table_name'],
            rule['rule_type'],
            rule['deduct_score'],
            rule['description'],
            rule['status']
        ))
        print(f"✓ 规则 {rule['rule_code']} 初始化成功")
    except Exception as e:
        print(f"✗ 规则 {rule['rule_code']} 初始化失败: {e}")

conn.commit()

# 查看初始化结果
cursor.execute("SELECT rule_code, field_name, rule_type, deduct_score, status FROM kiro_qc_rule")
print("\n当前规则列表:")
print(f"{'规则编码':<30} {'字段名称':<25} {'规则类型':<20} {'扣分':<10} {'状态'}")
print("=" * 100)
for row in cursor.fetchall():
    print(f"{row[0]:<30} {row[1]:<25} {row[2]:<20} {row[3]:<10} {row[4]}")

cursor.close()
conn.close()
print("\n规则初始化完成！")
