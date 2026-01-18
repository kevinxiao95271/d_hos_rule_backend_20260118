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

def check_rule_description():
    """检查规则描述"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 查看C43x03C的规则描述
        cursor.execute("""
            SELECT rule_code, field_code, field_name, rule_type, description, dict_types
            FROM kiro_qc_rule 
            WHERE field_code = 'C43x03C'
        """)
        rule = cursor.fetchone()
        
        if rule:
            print("=== C43x03C规则详情 ===")
            print(f"规则代码: {rule['rule_code']}")
            print(f"字段代码: {rule['field_code']}")
            print(f"字段名称: {rule['field_name']}")
            print(f"规则类型: {rule['rule_type']}")
            print(f"规则描述: {rule['description']}")
            print(f"字典类型: {rule['dict_types']}")
            
            # 分析规则描述
            desc = rule['description']
            print(f"\n=== 规则分析 ===")
            print(f"是否包含'不为空': {'是' if '不为空' in desc else '否'}")
            print(f"是否包含'必须': {'是' if '必须' in desc else '否'}")
            print(f"是否包含'取值不为空': {'是' if '取值不为空' in desc else '否'}")
            
            # 根据你提供的规则：其他手术操作3麻醉方式	C43x03C	D	-0.5	value_check	其他手术操作3麻醉方式取值不为空且不符合国家标准值域定义
            # 这个规则明确说了"取值不为空且不符合国家标准值域定义"
            # 所以"-"值应该被检测为违规
            
        else:
            print("未找到C43x03C规则")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_rule_description()