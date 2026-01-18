#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pymysql
import json

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

def test_complete_rule_system():
    """测试完整的规则系统"""
    print("=== 测试完整的规则系统 ===")
    
    # 1. 检查规则加载情况
    print("1. 检查规则加载情况...")
    response = requests.get(f"{BASE_URL}/qc/rules")
    if response.status_code == 200:
        rules = response.json().get('data', [])
        print(f"系统加载的规则总数: {len(rules)}")
        
        # 按规则类型统计
        rule_type_stats = {}
        for rule in rules:
            rule_type = rule.get('ruleType', 'unknown')
            if rule_type not in rule_type_stats:
                rule_type_stats[rule_type] = 0
            rule_type_stats[rule_type] += 1
        
        print("规则类型分布:")
        for rule_type, count in sorted(rule_type_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {rule_type}: {count}条规则")
    
    # 2. 测试2020年数据的全面质控
    print(f"\n2. 测试2020年数据的全面质控...")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 找一个2020年的病案进行测试
        cursor.execute("""
            SELECT m.A48, m.A49
            FROM d_mr m
            WHERE YEAR(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = 2020
            LIMIT 1
        """)
        case_2020 = cursor.fetchone()
        
        if case_2020:
            print(f"2020年测试病案: {case_2020['A48']}_{case_2020['A49']}")
            
            # 进行质控检查
            response = requests.post(f"{BASE_URL}/qc/check/single", 
                                   params={
                                       'a48': case_2020['A48'],
                                       'a49': case_2020['A49']
                                   })
            
            if response.status_code == 200:
                result = response.json().get('data', {})
                defects = result.get('allDefects', [])
                
                print(f"检测到缺陷数量: {len(defects)}")
                print(f"最终得分: {result.get('finalScore', 0)}")
                
                # 按规则类型统计缺陷
                defect_type_stats = {}
                for defect in defects:
                    rule_code = defect.get('ruleCode', '')
                    
                    # 推断规则类型
                    if 'range_check' in rule_code:
                        rule_type = 'range_check'
                    elif 'cross_check_null' in rule_code:
                        rule_type = 'cross_check_null'
                    elif 'cross_check' in rule_code:
                        rule_type = 'cross_check'
                    elif 'value_check' in rule_code:
                        rule_type = 'value_check'
                    elif 'length_check' in rule_code:
                        rule_type = 'length_check'
                    elif 'date_check' in rule_code:
                        rule_type = 'date_check'
                    elif 'null_check' in rule_code:
                        rule_type = 'null_check'
                    elif 'RULE_' in rule_code and 'RC0' in rule_code:
                        rule_type = 'dict_validation'
                    else:
                        rule_type = 'other'
                    
                    if rule_type not in defect_type_stats:
                        defect_type_stats[rule_type] = 0
                    defect_type_stats[rule_type] += 1
                
                print(f"\n缺陷类型分布:")
                for defect_type, count in sorted(defect_type_stats.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {defect_type}: {count}个缺陷")
                
                # 显示前10个缺陷详情
                print(f"\n前10个缺陷详情:")
                for i, defect in enumerate(defects[:10], 1):
                    print(f"{i:2d}. {defect.get('fieldCode')} ({defect.get('ruleCode')})")
                    print(f"     实际值: '{defect.get('actualValue')}'")
                    print(f"     期望值: {defect.get('expectedValue')}")
                    print(f"     扣分: {defect.get('deductScore')}")
            
            else:
                print(f"质控检查失败: {response.status_code}")
        
        # 3. 测试2023年数据对比
        print(f"\n3. 测试2023年数据对比...")
        
        cursor.execute("""
            SELECT m.A48, m.A49
            FROM d_mr m
            WHERE YEAR(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = 2023
            LIMIT 1
        """)
        case_2023 = cursor.fetchone()
        
        if case_2023:
            print(f"2023年测试病案: {case_2023['A48']}_{case_2023['A49']}")
            
            response = requests.post(f"{BASE_URL}/qc/check/single", 
                                   params={
                                       'a48': case_2023['A48'],
                                       'a49': case_2023['A49']
                                   })
            
            if response.status_code == 200:
                result = response.json().get('data', {})
                defects = result.get('allDefects', [])
                
                print(f"2023年缺陷数量: {len(defects)}")
                print(f"2023年最终得分: {result.get('finalScore', 0)}")
        
        # 4. 统计规则覆盖的字段
        print(f"\n4. 统计规则覆盖的字段...")
        
        cursor.execute("""
            SELECT COUNT(DISTINCT field_code) as covered_fields,
                   COUNT(*) as total_rules
            FROM kiro_qc_rule
            WHERE status = 'active'
        """)
        coverage_stats = cursor.fetchone()
        
        print(f"规则覆盖统计:")
        print(f"  覆盖字段数: {coverage_stats['covered_fields']}")
        print(f"  总规则数: {coverage_stats['total_rules']}")
        
        # 统计各表的字段覆盖情况
        tables = ['d_mr', 'd_mr_other_1_20', 'd_mr_other_21_40', 'd_mr_other_f']
        
        print(f"\n各表字段覆盖情况:")
        for table in tables:
            # 获取表的总字段数
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            total_columns = len(cursor.fetchall())
            
            # 获取有规则覆盖的字段数
            cursor.execute("""
                SELECT COUNT(DISTINCT field_code) as covered_fields
                FROM kiro_qc_rule
                WHERE status = 'active' 
                  AND (source_tables = %s OR source_tables LIKE %s)
            """, (table, f"%{table}%"))
            covered_result = cursor.fetchone()
            covered_fields = covered_result['covered_fields'] if covered_result else 0
            
            coverage_rate = (covered_fields / total_columns * 100) if total_columns > 0 else 0
            print(f"  {table}: {covered_fields}/{total_columns} ({coverage_rate:.1f}%)")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_complete_rule_system()