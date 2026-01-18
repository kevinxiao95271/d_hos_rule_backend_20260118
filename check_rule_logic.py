#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import json

# 数据库连接配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def check_rule_logic():
    """检查规则逻辑和字典验证"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 检查麻醉方式规则
        print("=== 检查麻醉方式规则 ===")
        cursor.execute("""
            SELECT rule_code, field_code, field_name, rule_type, description, dict_types
            FROM kiro_qc_rule 
            WHERE field_code LIKE 'C43%' AND description LIKE '%麻醉方式%'
        """)
        anesthesia_rules = cursor.fetchall()
        print(f"找到麻醉方式规则: {len(anesthesia_rules)}")
        for rule in anesthesia_rules:
            print(f"  {rule['rule_code']}: {rule['field_code']} - {rule['description']}")
            print(f"    字典类型: {rule['dict_types']}")
        
        # 2. 检查RC013字典内容
        print("\n=== 检查RC013麻醉方式字典 ===")
        cursor.execute("""
            SELECT dict_code, dict_name 
            FROM sys_dict 
            WHERE dict_type_code = 'RC013'
            ORDER BY dict_code
        """)
        rc013_dict = cursor.fetchall()
        print(f"RC013字典项数量: {len(rc013_dict)}")
        for item in rc013_dict:
            print(f"  {item['dict_code']}: {item['dict_name']}")
        
        # 3. 检查C43x03C字段在哪个表
        print("\n=== 检查C43x03C字段位置 ===")
        tables = ['d_mr', 'd_mr_other_1_20', 'd_mr_other_21_40', 'd_mr_other_f']
        for table in tables:
            try:
                cursor.execute(f"SHOW COLUMNS FROM {table} LIKE 'C43x03C'")
                result = cursor.fetchone()
                if result:
                    print(f"  字段C43x03C在表: {table}")
                    print(f"    类型: {result['Type']}")
                    print(f"    允许NULL: {result['Null']}")
            except Exception as e:
                print(f"  检查表{table}失败: {e}")
        
        # 4. 检查实际数据中C43x03C的值
        print("\n=== 检查C43x03C字段实际数据 ===")
        for table in tables:
            try:
                cursor.execute(f"""
                    SELECT C43x03C, COUNT(*) as count 
                    FROM {table} 
                    WHERE C43x03C IS NOT NULL AND C43x03C != ''
                    GROUP BY C43x03C 
                    ORDER BY count DESC 
                    LIMIT 10
                """)
                results = cursor.fetchall()
                if results:
                    print(f"  表{table}中C43x03C的值分布:")
                    for row in results:
                        print(f"    {row['C43x03C']}: {row['count']}条记录")
            except Exception as e:
                print(f"  查询表{table}失败: {e}")
        
        # 5. 检查新生儿体重规则
        print("\n=== 检查新生儿体重规则 ===")
        cursor.execute("""
            SELECT rule_code, field_code, field_name, rule_type, description
            FROM kiro_qc_rule 
            WHERE field_code LIKE 'A18%'
            ORDER BY field_code
        """)
        weight_rules = cursor.fetchall()
        print(f"找到新生儿体重规则: {len(weight_rules)}")
        for rule in weight_rules:
            print(f"  {rule['rule_code']}: {rule['field_code']} - {rule['rule_type']}")
        
        # 6. 检查实际病案数据中的新生儿体重
        print("\n=== 检查实际新生儿体重数据 ===")
        cursor.execute("""
            SELECT A48, A49, A18x01, A18x02, A18x03
            FROM d_mr 
            WHERE (A18x01 IS NOT NULL AND A18x01 != '') 
               OR (A18x02 IS NOT NULL AND A18x02 != '')
               OR (A18x03 IS NOT NULL AND A18x03 != '')
            LIMIT 5
        """)
        weight_data = cursor.fetchall()
        print(f"找到有新生儿体重数据的病案: {len(weight_data)}")
        for data in weight_data:
            print(f"  {data['A48']}_{data['A49']}: A18x01={data['A18x01']}, A18x02={data['A18x02']}, A18x03={data['A18x03']}")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_rule_logic()