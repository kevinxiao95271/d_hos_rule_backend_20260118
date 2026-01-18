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

def analyze_2023_vs_2020():
    """分析2023年与2020年数据的差异"""
    print("=== 分析2023年与2020年数据差异 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 对比2020年和2023年的质控结果
        print("1. 对比2020年和2023年质控结果...")
        
        for year in [2020, 2023]:
            cursor.execute("""
                SELECT COUNT(*) as total_cases,
                       SUM(defect_count) as total_defects,
                       AVG(defect_count) as avg_defects,
                       AVG(final_score) as avg_score
                FROM kiro_qc_case_result 
                WHERE check_year = %s
            """, (year,))
            stats = cursor.fetchone()
            
            if stats and stats['total_cases'] > 0:
                print(f"{year}年: {stats['total_cases']}个病案, {stats['total_defects']}个缺陷, 平均{stats['avg_defects']:.2f}个缺陷/病案, 平均得分{stats['avg_score']:.2f}")
            else:
                print(f"{year}年: 无数据")
        
        # 2. 检查2023年数据中字典字段的实际值
        print(f"\n2. 检查2023年数据中字典字段的实际值...")
        
        # 检查一些关键字典字段在2023年的数据分布
        dict_fields = [
            ('A02', 'RC002', '婚姻状况'),
            ('A17', 'RC019', '离院方式'),
            ('A20', 'RC030', 'ABO血型'),
            ('A22', 'RC011', '病案质量')
        ]
        
        for field_code, dict_type, field_name in dict_fields:
            cursor.execute(f"""
                SELECT m.{field_code}, COUNT(*) as count
                FROM d_mr m
                WHERE YEAR(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = 2023
                  AND m.{field_code} IS NOT NULL 
                  AND m.{field_code} != ''
                GROUP BY m.{field_code}
                ORDER BY count DESC
                LIMIT 5
            """)
            values = cursor.fetchall()
            
            print(f"\n{field_code} ({field_name}) 在2023年的值分布:")
            if values:
                for value in values:
                    print(f"  '{value[field_code]}': {value['count']}条记录")
            else:
                print("  无数据或全为空值")
        
        # 3. 检查2023年麻醉方式字段的值分布
        print(f"\n3. 检查2023年麻醉方式字段的值分布...")
        cursor.execute("""
            SELECT o.C43x03C, COUNT(*) as count
            FROM d_mr m
            JOIN d_mr_other_1_20 o ON m.A48 = o.A48 AND m.A49 = o.A49
            WHERE YEAR(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = 2023
              AND o.C43x03C IS NOT NULL 
              AND o.C43x03C != ''
            GROUP BY o.C43x03C
            ORDER BY count DESC
            LIMIT 10
        """)
        anesthesia_values = cursor.fetchall()
        
        print("C43x03C (麻醉方式3) 在2023年的值分布:")
        if anesthesia_values:
            for value in anesthesia_values:
                print(f"  '{value['C43x03C']}': {value['count']}条记录")
        else:
            print("  无数据或全为空值")
        
        # 4. 检查2020年的相同字段对比
        print(f"\n4. 对比2020年的字典字段值分布...")
        
        cursor.execute("""
            SELECT m.A02, COUNT(*) as count
            FROM d_mr m
            WHERE YEAR(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = 2020
              AND m.A02 IS NOT NULL 
              AND m.A02 != ''
            GROUP BY m.A02
            ORDER BY count DESC
            LIMIT 5
        """)
        a02_2020 = cursor.fetchall()
        
        print("A02 (婚姻状况) 在2020年的值分布:")
        if a02_2020:
            for value in a02_2020:
                print(f"  '{value['A02']}': {value['count']}条记录")
        
        # 5. 检查规则是否正确加载
        print(f"\n5. 检查字典验证规则是否正确加载...")
        cursor.execute("""
            SELECT rule_code, field_code, dict_types, status
            FROM kiro_qc_rule
            WHERE dict_types IS NOT NULL 
              AND dict_types != ''
              AND status = 'active'
            ORDER BY field_code
            LIMIT 10
        """)
        dict_rules = cursor.fetchall()
        
        print("字典验证规则:")
        for rule in dict_rules:
            print(f"  {rule['rule_code']}: {rule['field_code']} -> {rule['dict_types']} ({rule['status']})")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    analyze_2023_vs_2020()