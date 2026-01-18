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
    
    print("1. 数据库原始数据:")
    cursor.execute("SELECT A01, A19C FROM d_mr WHERE A48 = '445583' AND A49 = '1'")
    result = cursor.fetchone()
    if result:
        print(f"  A01: '{result[0]}'")
        print(f"  A19C: '{result[1]}'")
    
    print("\n2. MedicalRecordMapper模拟查询:")
    cursor.execute("""
        SELECT m.A01, m.A19C, o1.A01 as other_A01
        FROM d_mr m 
        LEFT JOIN d_mr_other_1_20 o1 ON m.A48 = o1.A48 AND m.A49 = o1.A49 
        WHERE m.A48 = '445583' AND m.A49 = '1'
    """)
    result = cursor.fetchone()
    if result:
        print(f"  d_mr.A01: '{result[0]}'")
        print(f"  d_mr.A19C: '{result[1]}'")
        print(f"  d_mr_other_1_20.A01: '{result[2]}'")
    
    print("\n3. 检查字段冲突:")
    cursor.execute("DESCRIBE d_mr_other_1_20")
    columns = [col[0] for col in cursor.fetchall()]
    if 'A01' in columns:
        print("  ⚠️  d_mr_other_1_20表也有A01字段，可能导致冲突")
    else:
        print("  ✅ d_mr_other_1_20表无A01字段")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"错误: {e}")