#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
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

BASE_URL = "http://localhost:4101/api"

def check_2023_results():
    """检查2023年质控结果"""
    print("=== 检查2023年质控结果 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 检查批量汇总表
        print("1. 检查批量汇总结果...")
        cursor.execute("""
            SELECT * FROM kiro_qc_batch_summary 
            WHERE batch_key LIKE '2023%'
            ORDER BY start_time DESC
            LIMIT 5
        """)
        summaries = cursor.fetchall()
        
        if summaries:
            print(f"找到2023年批量汇总记录: {len(summaries)}条")
            for summary in summaries:
                print(f"  {summary['batch_key']}: {summary['case_count']}个病案, {summary['total_defect_count']}个缺陷, 平均得分{summary['avg_score']}")
        else:
            print("未找到2023年批量汇总记录")
        
        # 2. 检查病案结果表
        print("\n2. 检查2023年病案质控结果...")
        cursor.execute("""
            SELECT COUNT(*) as total_cases,
                   SUM(defect_count) as total_defects,
                   AVG(defect_count) as avg_defects,
                   AVG(final_score) as avg_score,
                   MIN(final_score) as min_score,
                   MAX(final_score) as max_score
            FROM kiro_qc_case_result 
            WHERE check_year = 2023
        """)
        case_stats = cursor.fetchone()
        
        if case_stats and case_stats['total_cases'] > 0:
            print(f"2023年病案统计:")
            print(f"  总病案数: {case_stats['total_cases']}")
            print(f"  总缺陷数: {case_stats['total_defects']}")
            print(f"  平均缺陷: {case_stats['avg_defects']:.2f}")
            print(f"  平均得分: {case_stats['avg_score']:.2f}")
            print(f"  最低得分: {case_stats['min_score']}")
            print(f"  最高得分: {case_stats['max_score']}")
        else:
            print("未找到2023年病案质控结果")
        
        # 3. 检查缺陷详情统计
        print("\n3. 检查2023年缺陷规则统计...")
        cursor.execute("""
            SELECT d.rule_code, d.field_code, d.rule_description,
                   COUNT(*) as violation_count,
                   COUNT(DISTINCT d.mr_key) as affected_cases
            FROM kiro_qc_defect_detail d
            JOIN kiro_qc_case_result c ON d.mr_key = c.mr_key
            WHERE c.check_year = 2023
            GROUP BY d.rule_code, d.field_code, d.rule_description
            ORDER BY violation_count DESC
            LIMIT 20
        """)
        rule_stats = cursor.fetchall()
        
        if rule_stats:
            print(f"2023年规则违规统计（前20个）:")
            for i, stat in enumerate(rule_stats, 1):
                print(f"{i:2d}. {stat['rule_code']} ({stat['field_code']})")
                print(f"     违规次数: {stat['violation_count']}, 影响病案: {stat['affected_cases']}")
                print(f"     规则描述: {stat['rule_description'][:60]}...")
        else:
            print("未找到2023年缺陷统计")
        
        # 4. 检查字段违规统计
        print("\n4. 检查2023年字段违规统计...")
        cursor.execute("""
            SELECT d.field_code, d.field_name,
                   COUNT(*) as violation_count,
                   COUNT(DISTINCT d.mr_key) as affected_cases
            FROM kiro_qc_defect_detail d
            JOIN kiro_qc_case_result c ON d.mr_key = c.mr_key
            WHERE c.check_year = 2023
            GROUP BY d.field_code, d.field_name
            ORDER BY violation_count DESC
            LIMIT 15
        """)
        field_stats = cursor.fetchall()
        
        if field_stats:
            print(f"2023年字段违规统计（前15个）:")
            for i, stat in enumerate(field_stats, 1):
                print(f"{i:2d}. {stat['field_code']} ({stat['field_name']})")
                print(f"     违规次数: {stat['violation_count']}, 影响病案: {stat['affected_cases']}")
        else:
            print("未找到2023年字段违规统计")
        
        # 5. 查看几个具体的违规病案
        print("\n5. 查看2023年违规病案示例...")
        cursor.execute("""
            SELECT c.mr_key, c.a48, c.a49, c.defect_count, c.final_score
            FROM kiro_qc_case_result c
            WHERE c.check_year = 2023 AND c.defect_count > 0
            ORDER BY c.defect_count DESC
            LIMIT 5
        """)
        sample_cases = cursor.fetchall()
        
        if sample_cases:
            print(f"违规病案示例:")
            for case in sample_cases:
                print(f"  {case['mr_key']}: {case['defect_count']}个缺陷, 得分{case['final_score']}")
                
                # 查看这个病案的具体缺陷
                cursor.execute("""
                    SELECT field_code, rule_code, actual_value, expected_value, rule_description
                    FROM kiro_qc_defect_detail
                    WHERE mr_key = %s
                    LIMIT 3
                """, (case['mr_key'],))
                defects = cursor.fetchall()
                
                for defect in defects:
                    print(f"    - {defect['field_code']}: {defect['actual_value']} -> {defect['expected_value']}")
                    print(f"      规则: {defect['rule_description'][:50]}...")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_2023_results()