import pymysql

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    print("检查缺陷详情表...")
    
    # 检查表结构
    cursor.execute("DESCRIBE kiro_qc_defect_detail")
    columns = cursor.fetchall()
    print("表结构:")
    for col in columns:
        print(f"  {col[0]}: {col[1]}")
    
    # 检查民族相关记录
    cursor.execute("""
        SELECT rule_code, field_code, actual_value, COUNT(*) as cnt
        FROM kiro_qc_defect_detail 
        WHERE rule_code LIKE '%RC035%' OR rule_code LIKE '%A01%'
        GROUP BY rule_code, field_code, actual_value
        ORDER BY cnt DESC
        LIMIT 10
    """)
    
    records = cursor.fetchall()
    if records:
        print("\n民族相关缺陷记录:")
        for rule_code, field_code, actual_value, count in records:
            print(f"  {rule_code} | {field_code} | '{actual_value}' | {count}条")
    else:
        print("\n✅ 无民族相关缺陷记录")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"错误: {e}")