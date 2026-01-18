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

def recheck_2023_complete():
    """重新检查2023年完整质控结果"""
    print("=== 重新检查2023年完整质控结果 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 重新统计2023年所有规则违规情况
        print("1. 2023年所有规则违规统计:")
        cursor.execute("""
            SELECT d.rule_code, d.field_code, d.rule_description,
                   COUNT(*) as violation_count,
                   COUNT(DISTINCT d.mr_key) as affected_cases
            FROM kiro_qc_defect_detail d
            JOIN kiro_qc_case_result c ON d.mr_key = c.mr_key
            WHERE c.check_year = 2023
            GROUP BY d.rule_code, d.field_code, d.rule_description
            ORDER BY violation_count DESC
        """)
        all_rules = cursor.fetchall()
        
        print(f"2023年共有 {len(all_rules)} 种规则检测出违规:")
        for i, rule in enumerate(all_rules, 1):
            print(f"{i:2d}. {rule['rule_code']} ({rule['field_code']})")
            print(f"     违规次数: {rule['violation_count']}, 影响病案: {rule['affected_cases']}")
            print(f"     规则描述: {rule['rule_description'][:60]}...")
        
        # 2. 按规则类型分类统计
        print(f"\n2. 按规则类型分类:")
        
        range_rules = [r for r in all_rules if 'range_check' in r['rule_code']]
        dict_rules = [r for r in all_rules if 'RULE_' in r['rule_code'] and 'RC0' in r['rule_code']]
        other_rules = [r for r in all_rules if r not in range_rules and r not in dict_rules]
        
        print(f"范围检查规则 (range_check): {len(range_rules)}个")
        for rule in range_rules:
            print(f"  - {rule['rule_code']}: {rule['violation_count']}次违规")
        
        print(f"\n字典验证规则 (RC0xx): {len(dict_rules)}个")
        for rule in dict_rules:
            print(f"  - {rule['rule_code']}: {rule['violation_count']}次违规")
        
        print(f"\n其他规则: {len(other_rules)}个")
        for rule in other_rules:
            print(f"  - {rule['rule_code']}: {rule['violation_count']}次违规")
        
        # 3. 检查是否所有2023年病案都有字典违规
        print(f"\n3. 检查2023年病案字典违规分布:")
        cursor.execute("""
            SELECT c.mr_key, c.defect_count,
                   COUNT(CASE WHEN d.rule_code LIKE '%RC0%' THEN 1 END) as dict_defects,
                   COUNT(CASE WHEN d.rule_code LIKE '%range_check%' THEN 1 END) as range_defects
            FROM kiro_qc_case_result c
            LEFT JOIN kiro_qc_defect_detail d ON c.mr_key = d.mr_key
            WHERE c.check_year = 2023
            GROUP BY c.mr_key, c.defect_count
            ORDER BY c.defect_count DESC
            LIMIT 10
        """)
        case_breakdown = cursor.fetchall()
        
        print("病案缺陷分布（前10个）:")
        for case in case_breakdown:
            print(f"  {case['mr_key']}: 总缺陷{case['defect_count']}, 字典缺陷{case['dict_defects']}, 范围缺陷{case['range_defects']}")
        
        # 4. 总结
        total_violations = sum(r['violation_count'] for r in all_rules)
        dict_violations = sum(r['violation_count'] for r in dict_rules)
        range_violations = sum(r['violation_count'] for r in range_rules)
        
        print(f"\n4. 2023年质控总结:")
        print(f"总违规次数: {total_violations}")
        print(f"字典违规: {dict_violations} ({dict_violations/total_violations*100:.1f}%)")
        print(f"范围违规: {range_violations} ({range_violations/total_violations*100:.1f}%)")
        print(f"其他违规: {total_violations - dict_violations - range_violations}")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    recheck_2023_complete()