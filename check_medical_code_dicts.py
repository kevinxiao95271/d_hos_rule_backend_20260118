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

def check_medical_code_dictionaries():
    """检查医疗编码字典"""
    print("=== 检查医疗编码字典 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 医疗编码字典类型
        medical_dict_types = [
            ("level4_operation_code_v2", "四级手术编码"),
            ("operation_dict_v3", "手术编码"),
            ("RCJBBM", "疾病编码"),
            ("microfracture_oper_code_v2", "微创手术"),
            ("day_operation_code_2022", "日间手术"),
            ("operation_code_with_type", "手术类型")
        ]
        
        print("医疗编码字典数据量统计:")
        print(f"{'字典类型':<30} {'中文名称':<15} {'记录数':<10}")
        print("-" * 60)
        
        total_records = 0
        
        for dict_type, chinese_name in medical_dict_types:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM sys_dict 
                WHERE dict_type_code = %s
            """, (dict_type,))
            
            result = cursor.fetchone()
            count = result['count'] if result else 0
            total_records += count
            
            print(f"{dict_type:<30} {chinese_name:<15} {count:<10}")
            
            # 显示一些示例数据
            if count > 0:
                cursor.execute("""
                    SELECT dict_code, dict_name
                    FROM sys_dict 
                    WHERE dict_type_code = %s
                    LIMIT 3
                """, (dict_type,))
                
                samples = cursor.fetchall()
                for sample in samples:
                    code = sample['dict_code'][:20] + "..." if len(sample['dict_code']) > 20 else sample['dict_code']
                    name = sample['dict_name'][:30] + "..." if len(sample['dict_name']) > 30 else sample['dict_name']
                    print(f"  示例: {code} - {name}")
                print()
        
        print(f"医疗编码字典总记录数: {total_records}")
        
        return medical_dict_types
        
    finally:
        cursor.close()
        conn.close()

def check_medical_code_rules():
    """检查医疗编码相关的规则"""
    print(f"\n=== 检查医疗编码相关规则 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 查找涉及医疗编码的规则
        medical_dict_types = [
            "level4_operation_code_v2",
            "operation_dict_v3", 
            "RCJBBM",
            "microfracture_oper_code_v2",
            "day_operation_code_2022",
            "operation_code_with_type"
        ]
        
        print("医疗编码相关规则统计:")
        
        for dict_type in medical_dict_types:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM kiro_qc_rule 
                WHERE status = 'active' 
                AND dict_types = %s
            """, (dict_type,))
            
            rule_count = cursor.fetchone()['count']
            
            if rule_count > 0:
                print(f"\n{dict_type}: {rule_count}条规则")
                
                # 显示具体规则
                cursor.execute("""
                    SELECT rule_code, field_code, field_name, description
                    FROM kiro_qc_rule 
                    WHERE status = 'active' 
                    AND dict_types = %s
                    LIMIT 5
                """, (dict_type,))
                
                rules = cursor.fetchall()
                for rule in rules:
                    print(f"  {rule['rule_code']}: {rule['field_code']} - {rule['field_name']}")
                    print(f"    {rule['description'][:80]}...")
            else:
                print(f"{dict_type}: 0条规则")
        
        # 检查是否有规则但字典类型不匹配
        print(f"\n检查可能的字典类型不匹配:")
        cursor.execute("""
            SELECT DISTINCT dict_types, COUNT(*) as count
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            AND rule_type = 'value_check'
            AND dict_types IS NOT NULL
            AND dict_types NOT LIKE 'RC%'
            GROUP BY dict_types
            ORDER BY count DESC
        """)
        
        non_rc_rules = cursor.fetchall()
        
        if non_rc_rules:
            print("非RC类型的字典验证规则:")
            for rule in non_rc_rules:
                print(f"  {rule['dict_types']}: {rule['count']}条规则")
        else:
            print("未找到非RC类型的字典验证规则")
        
    finally:
        cursor.close()
        conn.close()

def check_test_case_data():
    """检查测试病案中的医疗编码数据"""
    print(f"\n=== 检查测试病案医疗编码数据 ===")
    
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
            
            # 检查主要诊断和手术编码字段
            medical_fields = [
                ('C01', '主要诊断ICD编码'),
                ('C02', '主要诊断中医疾病编码'),
                ('C03', '主要诊断中医证候编码'),
                ('C21x01', '手术及操作编码1'),
                ('C21x02', '手术及操作编码2'),
                ('C21x03', '手术及操作编码3'),
                ('C38x01', '其他手术操作编码1'),
                ('C38x02', '其他手术操作编码2'),
                ('C38x03', '其他手术操作编码3')
            ]
            
            # 查询主表数据
            field_list = [field[0] for field in medical_fields]
            field_sql = ', '.join(field_list)
            
            cursor.execute(f"""
                SELECT {field_sql}
                FROM d_mr 
                WHERE A48 = %s AND A49 = %s
            """, (test_case['A48'], test_case['A49']))
            
            data = cursor.fetchone()
            
            if data:
                print("\n病案医疗编码数据:")
                for field_code, field_name in medical_fields:
                    value = data.get(field_code, '')
                    if value and value.strip() and value != '-':
                        print(f"  {field_code} ({field_name}): {value}")
                        
                        # 检查这个值是否在对应的字典中
                        if field_code.startswith('C01'):  # 主要诊断
                            check_in_dict(cursor, value, 'RCJBBM', '疾病编码')
                        elif field_code.startswith('C21') or field_code.startswith('C38'):  # 手术编码
                            check_in_dict(cursor, value, 'operation_dict_v3', '手术编码')
                    else:
                        print(f"  {field_code} ({field_name}): 空值")
            
            # 检查附表数据
            print(f"\n检查附表手术编码数据:")
            for table_suffix in ['1_20', '21_40', 'f']:
                table_name = f'd_mr_other_{table_suffix}'
                
                cursor.execute(f"""
                    SELECT COUNT(*) as count
                    FROM {table_name}
                    WHERE A48 = %s AND A49 = %s
                """, (test_case['A48'], test_case['A49']))
                
                count = cursor.fetchone()['count']
                print(f"  {table_name}: {count}条记录")
        
    finally:
        cursor.close()
        conn.close()

def check_in_dict(cursor, value, dict_type, dict_name):
    """检查值是否在字典中"""
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM sys_dict 
        WHERE dict_type_code = %s 
        AND (dict_code = %s OR dict_name = %s)
    """, (dict_type, value, value))
    
    result = cursor.fetchone()
    exists = result['count'] > 0
    
    status = "✅ 存在" if exists else "❌ 不存在"
    print(f"    在{dict_name}字典中: {status}")

def main():
    """主函数"""
    print("医疗编码字典和规则检查")
    print("=" * 50)
    
    # 1. 检查医疗编码字典
    medical_dict_types = check_medical_code_dictionaries()
    
    # 2. 检查相关规则
    check_medical_code_rules()
    
    # 3. 检查测试数据
    check_test_case_data()
    
    print(f"\n=== 问题分析 ===")
    print("可能的问题:")
    print("1. Redis缓存只预加载了RC0xx类型字典，未包含医疗编码字典")
    print("2. 规则中的dict_types字段可能与实际字典类型不匹配")
    print("3. 医疗编码规则可能被错误分类或状态不正确")
    
    print(f"\n建议解决方案:")
    print("1. 扩展Redis缓存预加载，包含所有医疗编码字典")
    print("2. 检查并修正规则中的dict_types字段")
    print("3. 验证医疗编码规则的激活状态")

if __name__ == "__main__":
    main()