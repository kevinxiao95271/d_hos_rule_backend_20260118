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

# 读取SQL文件
with open('init_kiro_tables.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# 分割并执行每个SQL语句
sql_statements = sql_content.split(';')
for sql in sql_statements:
    sql = sql.strip()
    if sql:
        try:
            cursor.execute(sql)
            print(f"✓ 执行成功")
        except Exception as e:
            print(f"✗ 执行失败: {e}")

conn.commit()

# 验证表创建
cursor.execute("SHOW TABLES LIKE 'kiro_%'")
tables = cursor.fetchall()
print("\n创建的表:")
for table in tables:
    print(f"  - {table[0]}")

cursor.close()
conn.close()
print("\n表创建完成！")
