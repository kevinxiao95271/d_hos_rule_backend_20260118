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

def execute_dict_rules():
    """执行字典验证规则SQL"""
    print("=== 执行字典验证规则SQL ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 读取SQL文件
        with open('generate_dict_validation_rules.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句
        sql_statements = []
        current_statement = ""
        
        for line in sql_content.split('\n'):
            if line.strip().startswith('--') or not line.strip():
                continue
            
            current_statement += line + '\n'
            
            if line.strip().endswith(';'):
                sql_statements.append(current_statement.strip())
                current_statement = ""
        
        print(f"准备执行 {len(sql_statements)} 条SQL语句...")
        
        # 执行SQL语句
        success_count = 0
        error_count = 0
        
        for i, sql in enumerate(sql_statements, 1):
            try:
                cursor.execute(sql)
                success_count += 1
                if i % 10 == 0:
                    print(f"已执行 {i}/{len(sql_statements)} 条语句...")
            except Exception as e:
                error_count += 1
                print(f"执行第 {i} 条语句失败: {e}")
                print(f"SQL: {sql[:100]}...")
        
        # 提交事务
        conn.commit()
        
        print(f"\n执行完成:")
        print(f"  成功: {success_count} 条")
        print(f"  失败: {error_count} 条")
        
        # 验证规则是否正确插入
        print(f"\n验证规则插入情况...")
        cursor.execute("""
            SELECT COUNT(*) as total_rules,
                   COUNT(CASE WHEN dict_types IS NOT NULL AND dict_types != '' THEN 1 END) as dict_rules,
                   COUNT(CASE WHEN status = 'active' THEN 1 END) as active_rules
            FROM kiro_qc_rule
        """)
        stats = cursor.fetchone()
        
        print(f"规则统计:")
        print(f"  总规则数: {stats[0]}")
        print(f"  字典规则数: {stats[1]}")
        print(f"  激活规则数: {stats[2]}")
        
        # 按字典类型统计
        cursor.execute("""
            SELECT dict_types, COUNT(*) as count
            FROM kiro_qc_rule
            WHERE dict_types IS NOT NULL AND dict_types != ''
            GROUP BY dict_types
            ORDER BY dict_types
        """)
        dict_stats = cursor.fetchall()
        
        print(f"\n按字典类型统计:")
        for dict_type, count in dict_stats:
            print(f"  {dict_type}: {count}个规则")
        
    except Exception as e:
        print(f"执行失败: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    execute_dict_rules()