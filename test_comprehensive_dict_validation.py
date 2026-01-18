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

def test_comprehensive_dict_validation():
    """测试全面的字典验证功能"""
    print("=== 测试全面的字典验证功能 ===")
    
    # 1. 检查规则加载情况
    print("1. 检查规则加载情况...")
    response = requests.get(f"{BASE_URL}/qc/rules")
    if response.status_code == 200:
        rules = response.json().get('data', [])
        dict_rules = [r for r in rules if r.get('dictTypes')]
        print(f"总规则数: {len(rules)}")
        print(f"字典规则数: {len(dict_rules)}")
        
        # 按字典类型统计
        dict_stats = {}
        for rule in dict_rules:
            dict_type = rule.get('dictTypes')
            if dict_type not in dict_stats:
                dict_stats[dict_type] = 0
            dict_stats[dict_type] += 1
        
        print("字典规则分布:")
        for dict_type, count in sorted(dict_stats.items()):
            print(f"  {dict_type}: {count}个规则")
    
    # 2. 测试2020年数据（应该有更多违规）
    print(f"\n2. 测试2020年数据的字典验证...")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 找一个2020年的病案进行测试
        cursor.execute("""
            SELECT m.A48, m.A49, m.A01, m.A02, m.A16, m.A17, m.A20, m.A22, m.A26, m.A27, m.A32
            FROM d_mr m
            WHERE YEAR(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = 2020
            LIMIT 1
        """)
        case_2020 = cursor.fetchone()
        
        if case_2020:
            print(f"2020年测试病案: {case_2020['A48']}_{case_2020['A49']}")
            
            # 显示字段值
            dict_fields = ['A01', 'A02', 'A16', 'A17', 'A20', 'A22', 'A26', 'A27', 'A32']
            for field in dict_fields:
                value = case_2020.get(field)
                if value:
                    print(f"  {field}: '{value}'")
            
            # 进行质控检查
            response = requests.post(f"{BASE_URL}/qc/check/single", 
                                   params={
                                       'a48': case_2020['A48'],
                                       'a49': case_2020['A49']
                                   })
            
            if response.status_code == 200:
                result = response.json().get('data', {})
                defects = result.get('allDefects', [])
                
                print(f"\n检测到缺陷数量: {len(defects)}")
                
                # 统计字典相关缺陷
                dict_defects = [d for d in defects if 'RC0' in d.get('ruleCode', '')]
                range_defects = [d for d in defects if 'range_check' in d.get('ruleCode', '')]
                other_defects = [d for d in defects if d not in dict_defects and d not in range_defects]
                
                print(f"字典验证缺陷: {len(dict_defects)}")
                print(f"范围检查缺陷: {len(range_defects)}")
                print(f"其他缺陷: {len(other_defects)}")
                
                # 显示字典缺陷详情
                if dict_defects:
                    print(f"\n字典验证缺陷详情:")
                    for defect in dict_defects:
                        print(f"  {defect.get('fieldCode')} ({defect.get('ruleCode')})")
                        print(f"    实际值: '{defect.get('actualValue')}'")
                        print(f"    期望值: {defect.get('expectedValue')}")
                
                # 显示范围检查缺陷
                if range_defects:
                    print(f"\n范围检查缺陷:")
                    for defect in range_defects:
                        print(f"  {defect.get('fieldCode')}: {defect.get('actualValue')} -> {defect.get('expectedValue')}")
            
            else:
                print(f"质控检查失败: {response.status_code}")
        
        # 3. 测试2023年数据对比
        print(f"\n3. 测试2023年数据对比...")
        
        cursor.execute("""
            SELECT m.A48, m.A49, m.A01, m.A02, m.A16, m.A17, m.A20, m.A22, m.A26, m.A27, m.A32
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
                dict_defects = [d for d in defects if 'RC0' in d.get('ruleCode', '')]
                
                print(f"2023年缺陷数量: {len(defects)} (字典缺陷: {len(dict_defects)})")
        
        # 4. 测试麻醉方式字段
        print(f"\n4. 测试麻醉方式字段验证...")
        
        cursor.execute("""
            SELECT m.A48, m.A49, o.C43x01C, o.C43x02C, o.C43x03C
            FROM d_mr m
            JOIN d_mr_other_1_20 o ON m.A48 = o.A48 AND m.A49 = o.A49
            WHERE YEAR(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = 2020
              AND (o.C43x01C IS NOT NULL OR o.C43x02C IS NOT NULL OR o.C43x03C IS NOT NULL)
            LIMIT 1
        """)
        anesthesia_case = cursor.fetchone()
        
        if anesthesia_case:
            print(f"麻醉方式测试病案: {anesthesia_case['A48']}_{anesthesia_case['A49']}")
            print(f"  C43x01C: '{anesthesia_case['C43x01C']}'")
            print(f"  C43x02C: '{anesthesia_case['C43x02C']}'")
            print(f"  C43x03C: '{anesthesia_case['C43x03C']}'")
            
            response = requests.post(f"{BASE_URL}/qc/check/single", 
                                   params={
                                       'a48': anesthesia_case['A48'],
                                       'a49': anesthesia_case['A49']
                                   })
            
            if response.status_code == 200:
                result = response.json().get('data', {})
                defects = result.get('allDefects', [])
                anesthesia_defects = [d for d in defects if 'C43x' in d.get('fieldCode', '') and 'RC013' in d.get('ruleCode', '')]
                
                print(f"麻醉方式缺陷数量: {len(anesthesia_defects)}")
                for defect in anesthesia_defects:
                    print(f"  {defect.get('fieldCode')}: '{defect.get('actualValue')}' -> {defect.get('expectedValue')}")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_comprehensive_dict_validation()