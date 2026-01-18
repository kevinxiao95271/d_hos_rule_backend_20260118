#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import time

# 数据库连接配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def execute_complete_rules():
    """执行完整的规则SQL"""
    print("=== 执行完整的规则SQL ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 读取SQL文件
        with open('complete_rules_from_exp.sql', 'r', encoding='utf-8') as f:
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
        
        # 分批执行SQL语句
        batch_size = 100
        success_count = 0
        error_count = 0
        
        for i in range(0, len(sql_statements), batch_size):
            batch = sql_statements[i:i+batch_size]
            batch_start = i + 1
            batch_end = min(i + batch_size, len(sql_statements))
            
            print(f"执行批次 {batch_start}-{batch_end}...")
            
            for j, sql in enumerate(batch):
                try:
                    cursor.execute(sql)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"执行第 {i+j+1} 条语句失败: {e}")
                    # 只显示前几个错误，避免输出过多
                    if error_count <= 5:
                        print(f"SQL: {sql[:200]}...")
            
            # 每批次提交一次
            conn.commit()
            
            # 短暂休息，避免数据库压力过大
            if i + batch_size < len(sql_statements):
                time.sleep(0.1)
        
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
        
        # 按规则类型统计
        cursor.execute("""
            SELECT rule_type, COUNT(*) as count
            FROM kiro_qc_rule
            WHERE status = 'active'
            GROUP BY rule_type
            ORDER BY count DESC
        """)
        type_stats = cursor.fetchall()
        
        print(f"\n按规则类型统计:")
        for rule_type, count in type_stats:
            print(f"  {rule_type}: {count}个规则")
        
        # 按表统计字段覆盖情况
        cursor.execute("""
            SELECT source_tables, COUNT(DISTINCT field_code) as field_count, COUNT(*) as rule_count
            FROM kiro_qc_rule
            WHERE status = 'active' AND source_tables IS NOT NULL AND source_tables != ''
            GROUP BY source_tables
            ORDER BY rule_count DESC
        """)
        table_stats = cursor.fetchall()
        
        print(f"\n按表统计字段覆盖:")
        for tables, field_count, rule_count in table_stats:
            print(f"  {tables}: {field_count}个字段, {rule_count}条规则")
        
    except Exception as e:
        print(f"执行失败: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    execute_complete_rules()