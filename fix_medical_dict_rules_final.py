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

def check_table_structure():
    """检查表结构"""
    print("=== 检查kiro_qc_rule表结构 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute("DESCRIBE kiro_qc_rule")
        columns = cursor.fetchall()
        
        print("表字段:")
        for col in columns:
            print(f"  {col['Field']} - {col['Type']}")
        
        return [col['Field'] for col in columns]
        
    finally:
        cursor.close()
        conn.close()

def fix_medical_dict_rules():
    """修复医疗字典规则"""
    print(f"\n=== 修复医疗字典规则 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 修复诊断编码规则 - 应该使用RCJBBM而不是RC013
        print("1. 修复诊断编码规则...")
        
        # 查找错误使用RC013的诊断编码规则
        cursor.execute("""
            SELECT id, rule_code, field_code, dict_types
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            AND rule_type = 'value_check'
            AND dict_types = 'RC013'
            AND (field_code LIKE 'C01%' OR field_code LIKE 'C02%' OR field_code LIKE 'C03%' 
                 OR field_code LIKE 'C04%' OR field_code LIKE 'C05%' OR field_code LIKE 'C06%')
        """)
        
        wrong_diagnosis_rules = cursor.fetchall()
        
        if wrong_diagnosis_rules:
            print(f"发现{len(wrong_diagnosis_rules)}条错误的诊断编码规则:")
            
            for rule in wrong_diagnosis_rules:
                print(f"  修复: {rule['rule_code']} ({rule['field_code']}) RC013 -> RCJBBM")
                
                cursor.execute("""
                    UPDATE kiro_qc_rule 
                    SET dict_types = 'RCJBBM'
                    WHERE id = %s
                """, (rule['id'],))
        
        # 2. 修复手术编码规则 - 应该使用operation_dict_v3
        print(f"\n2. 修复手术编码规则...")
        
        # 查找空dict_types的手术编码规则
        cursor.execute("""
            SELECT id, rule_code, field_code, description
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            AND rule_type = 'value_check'
            AND (dict_types IS NULL OR dict_types = '')
            AND (field_code LIKE 'C21%' OR field_code LIKE 'C38%' OR field_code LIKE 'C43%')
        """)
        
        surgery_rules = cursor.fetchall()
        
        if surgery_rules:
            print(f"发现{len(surgery_rules)}条手术编码规则需要修复:")
            
            for rule in surgery_rules:
                print(f"  修复: {rule['rule_code']} ({rule['field_code']}) 空 -> operation_dict_v3")
                
                cursor.execute("""
                    UPDATE kiro_qc_rule 
                    SET dict_types = 'operation_dict_v3'
                    WHERE id = %s
                """, (rule['id'],))
        
        # 3. 修复其他标准字典规则
        print(f"\n3. 修复其他标准字典规则...")
        
        # 标准字典映射
        standard_dict_mapping = [
            ('A12C', 'RC001', '性别'),
            ('A19C', 'RC035', '民族'),
            ('A21C', 'RC002', '婚姻'),
            ('A38C', 'RC003', '职业'),
            ('A46C', 'RC032', '医疗付费方式'),
            ('A33C', 'RC033', '联系人关系'),
            ('F01', 'RC027', '入院时情况'),
        ]
        
        for field_code, dict_type, description in standard_dict_mapping:
            cursor.execute("""
                SELECT id, rule_code
                FROM kiro_qc_rule 
                WHERE status = 'active' 
                AND rule_type = 'value_check'
                AND field_code = %s
                AND (dict_types IS NULL OR dict_types = '')
            """, (field_code,))
            
            rules = cursor.fetchall()
            
            for rule in rules:
                print(f"  修复: {rule['rule_code']} ({field_code}) 空 -> {dict_type} ({description})")
                
                cursor.execute("""
                    UPDATE kiro_qc_rule 
                    SET dict_types = %s
                    WHERE id = %s
                """, (dict_type, rule['id']))
        
        conn.commit()
        
        # 4. 验证修复结果
        print(f"\n4. 验证修复结果...")
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
        
        updated_stats = cursor.fetchall()
        
        print("修复后的字典类型分布:")
        for stat in updated_stats:
            print(f"  {stat['dict_type_display']}: {stat['count']}条规则")
        
        return True
        
    finally:
        cursor.close()
        conn.close()

def update_dict_cache_service():
    """更新字典缓存服务以包含医疗字典"""
    print(f"\n=== 更新字典缓存服务 ===")
    
    # 修改DictCacheService.java
    cache_service_path = "src/main/java/com/medical/qc/service/DictCacheService.java"
    
    print("需要修改DictCacheService.java:")
    print("1. 修改getAllRcDictTypes()方法")
    print("2. 添加医疗编码字典类型")
    
    # 新的字典类型列表
    new_dict_types = """
    private List<String> getAllDictTypes() {
        // 获取所有需要缓存的字典类型
        List<Map<String, Object>> results = dictMapper.queryDicts(null, null, null);
        return results.stream()
            .map(row -> row.get("dict_type_code").toString())
            .filter(type -> type.startsWith("RC") || 
                           type.equals("level4_operation_code_v2") ||
                           type.equals("operation_dict_v3") ||
                           type.equals("RCJBBM") ||
                           type.equals("microfracture_oper_code_v2") ||
                           type.equals("day_operation_code_2022") ||
                           type.equals("operation_code_with_type"))
            .distinct()
            .collect(Collectors.toList());
    }
    """
    
    print("建议的代码修改:")
    print(new_dict_types)
    
    return True

def main():
    """主函数"""
    print("修复医疗字典规则问题")
    print("=" * 50)
    
    # 1. 检查表结构
    columns = check_table_structure()
    
    if 'id' not in columns:
        print("❌ 表中没有id字段，无法进行修复")
        return
    
    # 2. 修复规则
    success = fix_medical_dict_rules()
    
    if success:
        print("✅ 规则修复完成")
        
        # 3. 更新缓存服务
        update_dict_cache_service()
        
        print(f"\n=== 下一步操作 ===")
        print("1. 手动修改DictCacheService.java文件")
        print("2. 重新编译应用: mvn clean package -DskipTests")
        print("3. 重启服务")
        print("4. 测试医疗编码验证功能")
    else:
        print("❌ 规则修复失败")

if __name__ == "__main__":
    main()