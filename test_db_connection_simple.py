#!/usr/bin/env python3
import pymysql

# 数据库配置
db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

try:
    print("连接数据库...")
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    print("检查表结构...")
    cursor.execute("DESCRIBE kiro_qc_batch_summary")
    columns = cursor.fetchall()
    
    print("当前字段:")
    for column in columns:
        print(f"  {column[0]}: {column[1]}")
    
    cursor.close()
    conn.close()
    print("连接成功")
    
except Exception as e:
    print(f"连接失败: {e}")