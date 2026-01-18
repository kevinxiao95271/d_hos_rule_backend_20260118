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

def check_rule_dict_types():
    """检查规则中的字典类型"""
    print("=== 检查规则中的字典类型 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 查看所有字典验证规则的dict_types
        cursor.execute("""
            SELECT dict_types, COUNT(*) as count, 
                   GROUP_CONCAT(DISTINCT field_code LIMIT 5) as sample_fields
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            AND rule_type = 'value_check'
            GROUP BY dict_types
            ORDER BY count DESC
        """)
        
        dict_rules = cursor.fetchall()
        
        print("字典验证规则分布:")
        print(f"{'字典类型':<30} {'规则数':<8} {'示例字段'}")
        print("-" * 70)
        
        for rule in dict_rules:
            dict_type = rule['dict_types'] if rule['dict_types'] else '空'
            count = rule['count']
            fields = rule['sample_fields'] if rule['sample_fields'] else '无'
            
            print(f"{dict_type:<30} {count:<8} {fields}")
        
        # 特别检查空的dict_types
        cursor.execute("""
            SELECT rule_code, field_code, field_name, description
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            AND rule_type = 'value_check'
            AND (dict_types IS NULL OR dict_types = '')
            LIMIT 10
        """)
        
        empty_dict_rules = cursor.fetchall()
        
        if empty_dict_rules:
            print(f"\n空字典类型的规则示例:")
            for rule in empty_dict_rules:
                print(f"  {rule['rule_code']}: {rule['field_code']} - {rule['field_name']}")
                desc = rule['description'][:60] + "..." if len(rule['description']) > 60 else rule['description']
                print(f"    {desc}")
        
        return dict_rules
        
    finally:
        cursor.close()
        conn.close()

def check_medical_fields_in_tables():
    """检查医疗编码字段在哪些表中"""
    print(f"\n=== 检查医疗编码字段分布 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 检查各个表的字段
        tables = ['d_mr', 'd_mr_other_1_20', 'd_mr_other_21_40', 'd_mr_other_f']
        
        medical_field_patterns = ['C01', 'C02', 'C03', 'C21', 'C38', 'C43']
        
        for table in tables:
            print(f"\n{table}表中的医疗编码字段:")
            
            # 获取表结构
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            
            medical_columns = []
            for col in columns:
                col_name = col['Field']
                for pattern in medical_field_patterns:
                    if col_name.startswith(pattern):
                        medical_columns.append(col_name)
                        break
            
            if medical_columns:
                print(f"  找到{len(medical_columns)}个医疗编码字段:")
                for col in medical_columns[:10]:  # 只显示前10个
                    print(f"    {col}")
                if len(medical_columns) > 10:
                    print(f"    ... 还有{len(medical_columns) - 10}个字段")
            else:
                print("  未找到医疗编码字段")
        
    finally:
        cursor.close()
        conn.close()

def check_sample_medical_data():
    """检查样本医疗数据"""
    print(f"\n=== 检查样本医疗数据 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取测试病案
        cursor.execute("""
            SELECT A48, A49 
            FROM d_mr 
            WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
            LIMIT 1
        """)
        test_case = cursor.fetchone()
        
        if test_case:
            print(f"测试病案: {test_case['A48']}_{test_case['A49']}")
            
            # 检查d_mr表中以C开头的字段
            cursor.execute("DESCRIBE d_mr")
            columns = cursor.fetchall()
            
            c_fields = [col['Field'] for col in columns if col['Field'].startswith('C')]
            
            if c_fields:
                print(f"\nd_mr表中的C字段 (前10个):")
                for field in c_fields[:10]:
                    cursor.execute(f"""
                        SELECT {field}
                        FROM d_mr 
                        WHERE A48 = %s AND A49 = %s
                    """, (test_case['A48'], test_case['A49']))
                    
                    result = cursor.fetchone()
                    value = result[field] if result and result[field] else '空'
                    
                    if value and value != '空' and value.strip() and value != '-':
                        print(f"  {field}: {value}")
            
            # 检查附表数据
            for table_suffix in ['1_20', '21_40', 'f']:
                table_name = f'd_mr_other_{table_suffix}'
                
                cursor.execute(f"""
                    SELECT COUNT(*) as count
                    FROM {table_name}
                    WHERE A48 = %s AND A49 = %s
                """, (test_case['A48'], test_case['A49']))
                
                count = cursor.fetchone()['count']
                print(f"\n{table_name}: {count}条记录")
                
                if count > 0:
                    # 获取表结构
                    cursor.execute(f"DESCRIBE {table_name}")
                    columns = cursor.fetchall()
                    
                    c_fields = [col['Field'] for col in columns if col['Field'].startswith('C')]
                    
                    if c_fields:
                        # 查看第一条记录的数据
                        cursor.execute(f"""
                            SELECT *
                            FROM {table_name}
                            WHERE A48 = %s AND A49 = %s
                            LIMIT 1
                        """, (test_case['A48'], test_case['A49']))
                        
                        record = cursor.fetchone()
                        if record:
                            print(f"  示例记录中的C字段:")
                            for field in c_fields[:5]:  # 只显示前5个
                                value = record.get(field, '空')
                                if value and value != '空' and str(value).strip() and value != '-':
                                    print(f"    {field}: {value}")
        
    finally:
        cursor.close()
        conn.close()

def analyze_missing_medical_rules():
    """分析缺失的医疗编码规则"""
    print(f"\n=== 分析缺失的医疗编码规则 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 检查是否有涉及医疗编码字段的规则
        medical_field_patterns = ['C01', 'C02', 'C03', 'C21', 'C38', 'C43']
        
        for pattern in medical_field_patterns:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM kiro_qc_rule 
                WHERE status = 'active' 
                AND field_code LIKE %s
            """, (f"{pattern}%",))
            
            count = cursor.fetchone()['count']
            print(f"{pattern}*字段相关规则: {count}条")
            
            if count > 0:
                # 显示一些示例
                cursor.execute("""
                    SELECT rule_code, field_code, rule_type, dict_types, description
                    FROM kiro_qc_rule 
                    WHERE status = 'active' 
                    AND field_code LIKE %s
                    LIMIT 3
                """, (f"{pattern}%",))
                
                rules = cursor.fetchall()
                for rule in rules:
                    print(f"  {rule['rule_code']}: {rule['field_code']} ({rule['rule_type']})")
                    if rule['dict_types']:
                        print(f"    字典类型: {rule['dict_types']}")
                    desc = rule['description'][:50] + "..." if len(rule['description']) > 50 else rule['description']
                    print(f"    描述: {desc}")
        
        # 检查可能需要医疗编码验证的规则
        print(f"\n可能需要医疗编码验证的规则:")
        cursor.execute("""
            SELECT rule_code, field_code, description
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            AND rule_type = 'value_check'
            AND (dict_types IS NULL OR dict_types = '')
            AND (description LIKE '%编码%' OR description LIKE '%ICD%' OR description LIKE '%手术%' OR description LIKE '%诊断%')
            LIMIT 10
        """)
        
        potential_rules = cursor.fetchall()
        
        for rule in potential_rules:
            print(f"  {rule['rule_code']}: {rule['field_code']}")
            desc = rule['description'][:60] + "..." if len(rule['description']) > 60 else rule['description']
            print(f"    {desc}")
        
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    print("医疗编码规则问题诊断")
    print("=" * 50)
    
    # 1. 检查规则中的字典类型
    check_rule_dict_types()
    
    # 2. 检查医疗字段分布
    check_medical_fields_in_tables()
    
    # 3. 检查样本数据
    check_sample_medical_data()
    
    # 4. 分析缺失的规则
    analyze_missing_medical_rules()
    
    print(f"\n=== 问题诊断结果 ===")
    print("发现的问题:")
    print("1. 有281条字典验证规则的dict_types为空")
    print("2. 医疗编码字典数据量巨大(68,283条)但未被规则使用")
    print("3. 需要检查规则生成时是否正确设置了dict_types字段")
    
    print(f"\n解决方案:")
    print("1. 修复规则中的dict_types字段，将空值规则与正确的字典类型关联")
    print("2. 扩展Redis缓存预加载，包含所有医疗编码字典")
    print("3. 重新测试医疗编码验证功能")

if __name__ == "__main__":
    main()