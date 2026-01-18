import pymysql

try:
    conn = pymysql.connect(
        host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
        port=63606,
        user='root',
        password='Yiguo9527_',
        database='d_hosq_traegj_20260115',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM d_mr WHERE B15 LIKE '2023/%' LIMIT 10")
    count = cursor.fetchone()[0]
    print(f"2023年病案数: {count}")
    cursor.close()
    conn.close()
    print("数据库连接成功")
except Exception as e:
    print(f"数据库连接失败: {e}")