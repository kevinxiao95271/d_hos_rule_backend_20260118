#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql

# 数据库连接配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def check_tables():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 查看所有表
        cursor.execute("SHOW TABLES")
        all_tables = cursor.fetchall()
        
        print(f"数据库中共有 {len(all_tables)} 个表:")
        
        # 查找病案相关的表
        mr_tables = []
        for table in all_tables:
            table_name = table[0]
            if 'mr' in table_name.lower() or 'b15' in table_name.lower():
                mr_tables.append(table_name)
        
        print(f"\n病案相关表 ({len(mr_tables)} 个):")
        for table in mr_tables:
            print(f"  {table}")
        
        # 如果找到病案表，查看结构
        if mr_tables:
            main_table = mr_tables[0]
            print(f"\n查看表 {main_table} 的结构:")
            cursor.execute(f"DESCRIBE {main_table}")
            columns = cursor.fetchall()
            
            for col in columns[:10]:  # 只显示前10个字段
                print(f"  {col[0]:<15} {col[1]:<20} {col[2]}")
            
            if len(columns) > 10:
                print(f"  ... 还有 {len(columns) - 10} 个字段")
            
            # 查看数据量
            cursor.execute(f"SELECT COUNT(*) FROM {main_table}")
            count = cursor.fetchone()[0]
            print(f"\n表 {main_table} 共有 {count} 条记录")
            
            # 查看2023年数据
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {main_table} WHERE YEAR(in_date) = 2023")
                count_2023 = cursor.fetchone()[0]
                print(f"2023年数据: {count_2023} 条")
            except:
                print("无法查询2023年数据（可能没有in_date字段）")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_tables()