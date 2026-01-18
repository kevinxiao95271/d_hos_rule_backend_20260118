#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import re
from collections import defaultdict

# 数据库连接配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def analyze_rule_exp():
    """分析rule_exp.txt文件中的所有规则"""
    print("=== 分析rule_exp.txt文件中的所有规则 ===")
    
    try:
        # 1. 读取rule_exp.txt文件
        print("1. 读取D:\\rule_exp.txt文件...")
        with open('D:\\rule_exp.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 按行分割
        lines = content.strip().split('\n')
        print(f"文件总行数: {len(lines)}")
        
        # 2. 解析规则
        print("\n2. 解析规则...")
        rules = []
        field_stats = defaultdict(list)
        rule_type_stats = defaultdict(int)
        dict_type_stats = defaultdict(set)
        
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            
            # 规则格式：字段名称\t字段代码\t等级\t扣分\t规则类型\t规则描述
            parts = line.split('\t')
            if len(parts) >= 6:
                field_name = parts[0].strip()
                field_code = parts[1].strip()
                level = parts[2].strip()
                deduct_score = parts[3].strip()
                rule_type = parts[4].strip()
                description = parts[5].strip()
                
                rule = {
                    'line_no': i + 1,
                    'field_name': field_name,
                    'field_code': field_code,
                    'level': level,
                    'deduct_score': deduct_score,
                    'rule_type': rule_type,
                    'description': description
                }
                
                rules.append(rule)
                field_stats[field_code].append(rule)
                rule_type_stats[rule_type] += 1
                
                # 检查是否涉及字典
                if 'RC0' in description:
                    # 提取RC0xx字典类型
                    rc_matches = re.findall(r'RC0\d+', description)
                    for rc_code in rc_matches:
                        dict_type_stats[rc_code].add(field_code)
        
        print(f"解析到规则数量: {len(rules)}")
        print(f"涉及字段数量: {len(field_stats)}")
        
        # 3. 统计规则类型
        print(f"\n3. 规则类型统计:")
        for rule_type, count in sorted(rule_type_stats.items()):
            print(f"  {rule_type}: {count}条规则")
        
        # 4. 统计字典类型
        print(f"\n4. 字典类型统计:")
        for dict_type, fields in sorted(dict_type_stats.items()):
            print(f"  {dict_type}: {len(fields)}个字段")
        
        # 5. 统计字段分布
        print(f"\n5. 字段规则数量分布:")
        field_rule_counts = [(field, len(rules)) for field, rules in field_stats.items()]
        field_rule_counts.sort(key=lambda x: x[1], reverse=True)
        
        print("字段规则数量排行（前20个）:")
        for field, count in field_rule_counts[:20]:
            print(f"  {field}: {count}条规则")
        
        # 6. 检查字段在数据库表中的存在情况
        print(f"\n6. 检查字段在数据库表中的存在情况...")
        
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        try:
            # 获取所有表的字段
            tables = ['d_mr', 'd_mr_other_1_20', 'd_mr_other_21_40', 'd_mr_other_f']
            all_db_fields = {}
            
            for table in tables:
                try:
                    cursor.execute(f"SHOW COLUMNS FROM {table}")
                    columns = cursor.fetchall()
                    all_db_fields[table] = [col['Field'] for col in columns]
                    print(f"  {table}: {len(all_db_fields[table])}个字段")
                except Exception as e:
                    print(f"  {table}: 查询失败 - {e}")
            
            # 检查规则中的字段是否存在于数据库表中
            print(f"\n7. 字段存在性检查:")
            
            existing_fields = set()
            missing_fields = set()
            field_locations = defaultdict(list)
            
            for field_code in field_stats.keys():
                found = False
                for table, columns in all_db_fields.items():
                    if field_code in columns:
                        existing_fields.add(field_code)
                        field_locations[field_code].append(table)
                        found = True
                
                if not found:
                    missing_fields.add(field_code)
            
            print(f"存在于数据库的字段: {len(existing_fields)}个")
            print(f"不存在于数据库的字段: {len(missing_fields)}个")
            
            if missing_fields:
                print(f"\n不存在的字段列表（前20个）:")
                for field in sorted(list(missing_fields))[:20]:
                    rule_count = len(field_stats[field])
                    print(f"  {field}: {rule_count}条规则")
            
            # 8. 按表分组统计存在的字段
            print(f"\n8. 按表分组的字段统计:")
            table_field_stats = defaultdict(set)
            
            for field_code, tables in field_locations.items():
                for table in tables:
                    table_field_stats[table].add(field_code)
            
            for table in sorted(table_field_stats.keys()):
                fields = table_field_stats[table]
                total_rules = sum(len(field_stats[field]) for field in fields)
                print(f"  {table}: {len(fields)}个字段, {total_rules}条规则")
            
            # 9. 生成完整的规则创建SQL
            print(f"\n9. 生成完整的规则创建SQL...")
            
            sql_statements = []
            created_count = 0
            skipped_count = 0
            
            for rule in rules:
                field_code = rule['field_code']
                
                # 只为存在于数据库中的字段创建规则
                if field_code not in existing_fields:
                    skipped_count += 1
                    continue
                
                # 生成规则代码
                rule_code = f"{field_code}_{rule['rule_type']}"
                if rule['rule_type'] == 'value_check' and 'RC0' in rule['description']:
                    # 提取字典类型
                    rc_matches = re.findall(r'RC0\d+', rule['description'])
                    if rc_matches:
                        dict_type = rc_matches[0]
                        rule_code = f"RULE_{field_code}_{dict_type}"
                
                # 确定源表
                source_tables = ','.join(field_locations.get(field_code, []))
                
                # 提取字典类型
                dict_types = ''
                canonical_expr = ''
                if 'RC0' in rule['description']:
                    rc_matches = re.findall(r'RC0\d+', rule['description'])
                    if rc_matches:
                        dict_types = rc_matches[0]
                        canonical_expr = f"{field_code} IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = '{dict_types}')"
                
                # 处理扣分
                try:
                    deduct_score = float(rule['deduct_score'])
                except:
                    deduct_score = -1.0
                
                sql = f"""INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    '{rule_code}', '{field_code}', '{rule['field_name']}', '{rule['rule_type']}', '{rule['description'].replace("'", "''")}',
    {deduct_score}, 'active', '{dict_types}', '{source_tables}', '{canonical_expr.replace("'", "''")}'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);"""
                
                sql_statements.append(sql)
                created_count += 1
            
            # 保存SQL到文件
            with open('complete_rules_from_exp.sql', 'w', encoding='utf-8') as f:
                f.write("-- 从rule_exp.txt生成的完整规则\n")
                f.write(f"-- 总规则数: {len(rules)}\n")
                f.write(f"-- 可创建规则数: {created_count}\n")
                f.write(f"-- 跳过规则数: {skipped_count} (字段不存在于数据库)\n\n")
                
                for sql in sql_statements:
                    f.write(sql + "\n\n")
            
            print(f"已生成 {created_count} 条规则SQL")
            print(f"跳过 {skipped_count} 条规则（字段不存在）")
            print(f"SQL文件已保存到: complete_rules_from_exp.sql")
            
        finally:
            cursor.close()
            conn.close()
        
        # 10. 总结
        print(f"\n10. 总结:")
        print(f"rule_exp.txt文件包含 {len(rules)} 条规则")
        print(f"涉及 {len(field_stats)} 个字段")
        print(f"其中 {len(existing_fields)} 个字段存在于数据库中")
        print(f"可以创建 {created_count} 条有效规则")
        
    except FileNotFoundError:
        print("错误: 找不到D:\\rule_exp.txt文件")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    analyze_rule_exp()