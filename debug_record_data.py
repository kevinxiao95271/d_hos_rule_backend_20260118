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

def debug_record_data():
    """调试记录数据获取"""
    print("=== 调试记录数据获取 ===")
    
    # 1. 直接查询数据库
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 查找有C43x03C字段值为"-"的病案
        cursor.execute("""
            SELECT m.A48, m.A49, m.B15, o.C43x03C
            FROM d_mr m
            LEFT JOIN d_mr_other_1_20 o ON m.A48 = o.A48 AND m.A49 = o.A49
            WHERE o.C43x03C = '-'
            LIMIT 1
        """)
        test_case = cursor.fetchone()
        
        if test_case:
            print(f"数据库查询结果: {test_case}")
            a48, a49 = test_case['A48'], test_case['A49']
            
            # 2. 测试规则试运行API，看看能否检测到违规
            rule_test_data = {
                "ruleId": None,  # 需要找到C43x03C的规则ID
                "a48": a48,
                "a49": a49,
                "limit": 10
            }
            
            # 先获取C43x03C的规则ID
            response = requests.get(f"{BASE_URL}/qc/rules/search?fieldCode=C43x03C")
            if response.status_code == 200:
                rules = response.json().get('data', [])
                if rules:
                    rule_id = rules[0].get('id')
                    rule_test_data['ruleId'] = rule_id
                    
                    print(f"找到规则ID: {rule_id}")
                    
                    # 测试规则
                    response = requests.post(f"{BASE_URL}/qc/rules/test", json=rule_test_data)
                    print(f"规则测试状态: {response.status_code}")
                    if response.status_code == 200:
                        result = response.json()
                        print(f"规则测试结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    else:
                        print(f"规则测试失败: {response.text}")
                else:
                    print("未找到C43x03C相关规则")
            
            # 3. 直接测试单个病案质控
            print(f"\n=== 测试单个病案质控: {a48}_{a49} ===")
            response = requests.post(f"{BASE_URL}/qc/check/single", 
                                   params={'a48': a48, 'a49': a49})
            
            print(f"质控检查状态: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"质控结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            else:
                print(f"质控检查失败: {response.text}")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    debug_record_data()