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

print("🔍 检查表结构和字段名")
print("=" * 80)

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    # 检查d_mr表的字段
    print("📊 d_mr 表字段:")
    cursor.execute("DESCRIBE d_mr")
    fields = cursor.fetchall()
    
    # 查找相关字段
    relevant_fields = []
    for field in fields:
        field_name = field[0]
        if any(keyword in field_name.upper() for keyword in ['C35', 'C36', 'C44', 'C43', 'C06', 'D21', 'D22', 'D23', 'D24', 'D25', 'D26', 'F21', 'A12', 'A13']):
            relevant_fields.append(field_name)
    
    print("相关字段:")
    for field in relevant_fields:
        print(f"  {field}")
    
    # 检查一些具体记录
    print(f"\n🔍 检查具体记录数据:")
    cursor.execute("SELECT A48, A49, A12C, A13 FROM d_mr WHERE A48 = '19063452' AND A49 = '1'")
    record = cursor.fetchone()
    if record:
        print(f"记录 19063452-1: A12C={record[2]}, A13={record[3]}")
    
    # 测试跨字段规则
    print(f"\n🧪 测试跨字段规则功能:")
    
    cursor.close()
    conn.close()
    
    print("=" * 80)
    
except Exception as e:
    print(f"❌ 数据库连接失败: {e}")
    import traceback
    traceback.print_exc()