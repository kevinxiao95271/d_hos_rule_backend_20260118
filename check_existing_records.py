#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

print("🔍 检查现有病案记录")
print("=" * 80)

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    # 检查各个表的记录数
    tables = ['d_mr', 'd_mr_other_1_20', 'd_mr_other_21_40', 'd_mr_other_f']
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"📊 {table}: {count} 条记录")
            
            if count > 0:
                # 获取前几条记录的A48和A49
                cursor.execute(f"SELECT A48, A49 FROM {table} LIMIT 5")
                records = cursor.fetchall()
                print(f"   前5条记录:")
                for record in records:
                    print(f"     A48: {record[0]}, A49: {record[1]}")
                    
        except Exception as e:
            print(f"❌ 查询 {table} 失败: {e}")
    
    # 查找有特定字段数据的记录（用于跨字段规则测试）
    print(f"\n🔍 查找适合跨字段规则测试的记录:")
    
    # 查找有手术编码的记录
    try:
        cursor.execute("""
            SELECT A48, A49, C35x01C, C36x01N 
            FROM d_mr 
            WHERE C35x01C IS NOT NULL AND C35x01C != '' 
            LIMIT 3
        """)
        surgery_records = cursor.fetchall()
        if surgery_records:
            print(f"   有手术编码的记录:")
            for record in surgery_records:
                print(f"     A48: {record[0]}, A49: {record[1]}, 手术编码: {record[2]}, 手术名称: {record[3]}")
    except Exception as e:
        print(f"   查询手术记录失败: {e}")
    
    # 查找有年龄和性别的记录
    try:
        cursor.execute("""
            SELECT A48, A49, A12C, A13 
            FROM d_mr 
            WHERE A12C IS NOT NULL AND A13 IS NOT NULL 
            LIMIT 3
        """)
        age_gender_records = cursor.fetchall()
        if age_gender_records:
            print(f"   有年龄性别的记录:")
            for record in age_gender_records:
                print(f"     A48: {record[0]}, A49: {record[1]}, 性别: {record[2]}, 年龄: {record[3]}")
    except Exception as e:
        print(f"   查询年龄性别记录失败: {e}")
    
    # 查找有输血相关字段的记录
    try:
        cursor.execute("""
            SELECT A48, A49, D21, D22, D23, D24, D25, D26, F21 
            FROM d_mr 
            WHERE (D21 IS NOT NULL AND D21 != '0') 
               OR (D22 IS NOT NULL AND D22 != '0')
               OR (D23 IS NOT NULL AND D23 != '0')
               OR (D24 IS NOT NULL AND D24 != '0')
               OR (D25 IS NOT NULL AND D25 != '0')
               OR (D26 IS NOT NULL AND D26 != '0')
               OR (F21 IS NOT NULL AND F21 != '0')
            LIMIT 3
        """)
        transfusion_records = cursor.fetchall()
        if transfusion_records:
            print(f"   有输血相关的记录:")
            for record in transfusion_records:
                print(f"     A48: {record[0]}, A49: {record[1]}")
                print(f"       输血: D21={record[2]}, D22={record[3]}, D23={record[4]}, D24={record[5]}, D25={record[6]}")
                print(f"       血费: D26={record[7]}, 输血反应: F21={record[8]}")
    except Exception as e:
        print(f"   查询输血记录失败: {e}")
    
    cursor.close()
    conn.close()
    
    print("=" * 80)
    
except Exception as e:
    print(f"❌ 数据库连接失败: {e}")