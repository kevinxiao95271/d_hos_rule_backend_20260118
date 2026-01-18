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

# 查看sys_dict表结构
print("sys_dict 表结构:")
cursor.execute("DESCRIBE sys_dict")
for col in cursor.fetchall():
    print(f"  {col[0]:<30} {col[1]:<20}")

# 查看样例数据
print("\nsys_dict 样例数据:")
cursor.execute("SELECT * FROM sys_dict WHERE dict_type_code = 'RC001' LIMIT 3")
for row in cursor.fetchall():
    print(f"  {row}")

# 查看已有的质控表
print("\n已有质控表结构:")
for table in ['qc_rule', 'qc_case_result', 'qc_field_mapping', 'qc_run_context', 'qc_agg_overview']:
    print(f"\n{table}:")
    try:
        cursor.execute(f"DESCRIBE {table}")
        for col in cursor.fetchall():
            print(f"  {col[0]:<30} {col[1]:<20}")
    except:
        print(f"  表不存在或无法访问")

cursor.close()
conn.close()
