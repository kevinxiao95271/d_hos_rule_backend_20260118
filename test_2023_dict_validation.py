#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
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

def test_2023_dict_validation():
    """测试2023年字典验证"""
    print("=== 测试2023年字典验证 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 找一个2023年的病案，检查其字典字段值
        cursor.execute("""
            SELECT m.A48, m.A49, m.A02, m.A17, m.A20, m.A22
            FROM d_mr m
            WHERE YEAR(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = 2023
            LIMIT 1
        """)
        case_2023 = cursor.fetchone()
        
        if case_2023:
            print(f"2023年测试病案: {case_2023['A48']}_{case_2023['A49']}")
            print(f"  A02 (婚姻状况): '{case_2023['A02']}'")
            print(f"  A17 (离院方式): '{case_2023['A17']}'")
            print(f"  A20 (ABO血型): '{case_2023['A20']}'")
            print(f"  A22 (病案质量): '{case_2023['A22']}'")
            
            # 2. 检查这些值是否在对应字典中
            dict_checks = [
                ('A02', 'RC002', case_2023['A02']),
                ('A17', 'RC019', case_2023['A17']),
                ('A20', 'RC030', case_2023['A20']),
                ('A22', 'RC011', case_2023['A22'])
            ]
            
            print(f"\n检查字典验证:")
            for field, dict_type, value in dict_checks:
                if value:
                    cursor.execute("""
                        SELECT COUNT(*) as count
                        FROM sys_dict
                        WHERE dict_type_code = %s 
                          AND (dict_code = %s OR dict_name = %s)
                    """, (dict_type, value, value))
                    result = cursor.fetchone()
                    
                    is_valid = result['count'] > 0
                    print(f"  {field} -> {dict_type}: '{value}' {'✓有效' if is_valid else '✗无效'}")
            
            # 3. 对这个病案进行质控检查
            print(f"\n对病案 {case_2023['A48']}_{case_2023['A49']} 进行质控检查:")
            response = requests.post(f"{BASE_URL}/qc/check/single", 
                                   params={
                                       'a48': case_2023['A48'],
                                       'a49': case_2023['A49']
                                   })
            
            if response.status_code == 200:
                result = response.json().get('data', {})
                defects = result.get('allDefects', [])
                
                print(f"检测到缺陷数量: {len(defects)}")
                
                # 查找字典相关的缺陷
                dict_defects = [d for d in defects if any(dict_type in d.get('ruleCode', '') for dict_type in ['RC002', 'RC019', 'RC030', 'RC011'])]
                
                print(f"字典相关缺陷: {len(dict_defects)}")
                for defect in dict_defects:
                    print(f"  {defect.get('fieldCode')}: {defect.get('actualValue')} -> {defect.get('expectedValue')}")
                
                # 显示所有缺陷
                print(f"所有缺陷:")
                for defect in defects:
                    print(f"  {defect.get('fieldCode')} ({defect.get('ruleCode')}): {defect.get('actualValue')}")
            
            else:
                print(f"质控检查失败: {response.status_code}")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_2023_dict_validation()