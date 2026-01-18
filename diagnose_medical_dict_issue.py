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

def diagnose_dict_types_issue():
    """诊断字典类型问题"""
    print("=== 诊断字典类型问题 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 查看字典验证规则的dict_types分布
        print("1. 字典验证规则的dict_types分布:")
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN dict_types IS NULL OR dict_types = '' THEN '空值'
                    ELSE dict_types 
                END as dict_type_display,
                COUNT(*) as count
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            AND rule_type = 'value_check'
            GROUP BY dict_types
            ORDER BY count DESC
        """)
        
        dict_stats = cursor.fetchall()
        
        for stat in dict_stats:
            print(f"  {stat['dict_type_display']}: {stat['count']}条规则")
        
        # 2. 查看空dict_types的规则示例
        print(f"\n2. 空dict_types的规则示例:")
        cursor.execute("""
            SELECT rule_code, field_code, field_name, description
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            AND rule_type = 'value_check'
            AND (dict_types IS NULL OR dict_types = '')
            LIMIT 10
        """)
        
        empty_rules = cursor.fetchall()
        
        for rule in empty_rules:
            print(f"  {rule['rule_code']}: {rule['field_code']} - {rule['field_name']}")
            desc = rule['description'][:80] + "..." if len(rule['description']) > 80 else rule['description']
            print(f"    描述: {desc}")
        
        # 3. 检查是否有医疗编码相关的描述
        print(f"\n3. 检查医疗编码相关的规则:")
        cursor.execute("""
            SELECT rule_code, field_code, description, dict_types
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            AND rule_type = 'value_check'
            AND (description LIKE '%编码%' OR description LIKE '%ICD%' OR description LIKE '%手术%' OR description LIKE '%诊断%')
            LIMIT 10
        """)
        
        medical_rules = cursor.fetchall()
        
        for rule in medical_rules:
            dict_type = rule['dict_types'] if rule['dict_types'] else '空'
            print(f"  {rule['rule_code']}: {rule['field_code']}")
            print(f"    字典类型: {dict_type}")
            desc = rule['description'][:60] + "..." if len(rule['description']) > 60 else rule['description']
            print(f"    描述: {desc}")
        
        return len(empty_rules)
        
    finally:
        cursor.close()
        conn.close()

def check_medical_dict_availability():
    """检查医疗字典可用性"""
    print(f"\n=== 检查医疗字典可用性 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        medical_dicts = [
            "level4_operation_code_v2",
            "operation_dict_v3", 
            "RCJBBM",
            "microfracture_oper_code_v2",
            "day_operation_code_2022",
            "operation_code_with_type"
        ]
        
        print("医疗字典数据量:")
        for dict_type in medical_dicts:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM sys_dict 
                WHERE dict_type_code = %s
            """, (dict_type,))
            
            count = cursor.fetchone()['count']
            print(f"  {dict_type}: {count}条")
        
        return medical_dicts
        
    finally:
        cursor.close()
        conn.close()

def fix_medical_dict_rules():
    """修复医疗字典规则"""
    print(f"\n=== 修复医疗字典规则 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 定义字段到字典类型的映射
        field_dict_mapping = [
            # 疾病编码相关
            ("C01%", "RCJBBM", "主要诊断ICD编码"),
            ("C02%", "RCJBBM", "主要诊断中医疾病编码"),
            ("C03%", "RCJBBM", "主要诊断中医证候编码"),
            ("C04%", "RCJBBM", "其他诊断ICD编码"),
            ("C05%", "RCJBBM", "其他诊断中医疾病编码"),
            ("C06%", "RCJBBM", "其他诊断中医证候编码"),
            
            # 手术编码相关
            ("C21%", "operation_dict_v3", "手术及操作编码"),
            ("C38%", "operation_dict_v3", "其他手术操作编码"),
            ("C43%", "operation_dict_v3", "其他手术操作编码"),
        ]
        
        updated_count = 0
        
        for field_pattern, dict_type, description in field_dict_mapping:
            # 查找匹配的规则
            cursor.execute("""
                SELECT rule_id, rule_code, field_code
                FROM kiro_qc_rule 
                WHERE status = 'active' 
                AND rule_type = 'value_check'
                AND field_code LIKE %s
                AND (dict_types IS NULL OR dict_types = '')
            """, (field_pattern,))
            
            rules = cursor.fetchall()
            
            if rules:
                print(f"\n修复{description}相关规则:")
                
                for rule in rules:
                    # 更新dict_types
                    cursor.execute("""
                        UPDATE kiro_qc_rule 
                        SET dict_types = %s
                        WHERE rule_id = %s
                    """, (dict_type, rule['rule_id']))
                    
                    print(f"  {rule['rule_code']}: {rule['field_code']} -> {dict_type}")
                    updated_count += 1
        
        conn.commit()
        print(f"\n✅ 已修复 {updated_count} 条规则的dict_types字段")
        
        return updated_count
        
    finally:
        cursor.close()
        conn.close()

def update_redis_cache_for_medical_dicts():
    """更新Redis缓存以包含医疗字典"""
    print(f"\n=== 更新Redis缓存配置 ===")
    
    # 修改DictCacheService以包含医疗字典
    medical_dict_types = [
        "level4_operation_code_v2",
        "operation_dict_v3", 
        "RCJBBM",
        "microfracture_oper_code_v2",
        "day_operation_code_2022",
        "operation_code_with_type"
    ]
    
    print("需要添加到Redis缓存的医疗字典:")
    for dict_type in medical_dict_types:
        print(f"  - {dict_type}")
    
    print(f"\n修改建议:")
    print("1. 修改DictCacheService.getAllRcDictTypes()方法")
    print("2. 将方法重命名为getAllDictTypes()并包含医疗字典")
    print("3. 重启服务以重新加载缓存")
    
    return medical_dict_types

def main():
    """主函数"""
    print("医疗字典规则问题诊断和修复")
    print("=" * 50)
    
    # 1. 诊断问题
    empty_count = diagnose_dict_types_issue()
    
    # 2. 检查字典可用性
    medical_dicts = check_medical_dict_availability()
    
    # 3. 修复规则
    if empty_count > 0:
        print(f"\n发现{empty_count}条规则的dict_types为空，开始修复...")
        updated_count = fix_medical_dict_rules()
        
        if updated_count > 0:
            print(f"✅ 成功修复{updated_count}条规则")
        else:
            print("⚠️  未找到需要修复的医疗编码规则")
    
    # 4. 更新缓存配置
    update_redis_cache_for_medical_dicts()
    
    print(f"\n=== 总结 ===")
    print("问题根源: 规则生成时dict_types字段未正确设置")
    print("解决方案:")
    print("1. ✅ 修复规则表中的dict_types字段")
    print("2. 🔄 需要修改DictCacheService包含医疗字典")
    print("3. 🔄 需要重启服务重新加载缓存")
    print("4. 🔄 需要重新测试医疗编码验证")

if __name__ == "__main__":
    main()