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

def test_dict_validation():
    """测试字典验证功能"""
    print("=== 测试字典验证功能 ===")
    
    # 1. 先找一个有C43x03C字段值为"-"的病案
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 查找有麻醉方式字段值为"-"的病案
        cursor.execute("""
            SELECT d.A48, d.A49, o.C43x03C
            FROM d_mr d
            JOIN d_mr_other_1_20 o ON d.A48 = o.A48 AND d.A49 = o.A49
            WHERE o.C43x03C = '-'
            LIMIT 1
        """)
        test_case = cursor.fetchone()
        
        if test_case:
            print(f"找到测试病案: {test_case['A48']}_{test_case['A49']}, C43x03C='{test_case['C43x03C']}'")
            
            # 2. 对这个病案进行质控检查
            response = requests.post(f"{BASE_URL}/qc/check/single", 
                                   params={
                                       'a48': test_case['A48'],
                                       'a49': test_case['A49']
                                   })
            
            print(f"质控检查状态: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"检查结果: {result.get('message', 'N/A')}")
                
                data = result.get('data', {})
                if data:
                    defects = data.get('defects', [])
                    print(f"发现缺陷数量: {len(defects)}")
                    
                    # 查找C43x03C相关的缺陷
                    c43_defects = [d for d in defects if d.get('fieldCode') == 'C43x03C']
                    print(f"C43x03C字段缺陷数量: {len(c43_defects)}")
                    
                    for defect in c43_defects:
                        print(f"  缺陷详情:")
                        print(f"    字段: {defect.get('fieldCode')} - {defect.get('fieldName')}")
                        print(f"    实际值: {defect.get('actualValue')}")
                        print(f"    期望值: {defect.get('expectedValue')}")
                        print(f"    规则描述: {defect.get('ruleDescription')}")
                        print(f"    扣分: {defect.get('deductScore')}")
                else:
                    print("未返回检查数据")
            else:
                print(f"检查失败: {response.text}")
        
        # 3. 查找有有效麻醉方式值的病案
        cursor.execute("""
            SELECT d.A48, d.A49, o.C43x03C
            FROM d_mr d
            JOIN d_mr_other_1_20 o ON d.A48 = o.A48 AND d.A49 = o.A49
            WHERE o.C43x03C IN ('01', '02', '03', '0302')
            LIMIT 1
        """)
        valid_case = cursor.fetchone()
        
        if valid_case:
            print(f"\n找到有效值测试病案: {valid_case['A48']}_{valid_case['A49']}, C43x03C='{valid_case['C43x03C']}'")
            
            # 对这个病案进行质控检查
            response = requests.post(f"{BASE_URL}/qc/check/single", 
                                   params={
                                       'a48': valid_case['A48'],
                                       'a49': valid_case['A49']
                                   })
            
            print(f"质控检查状态: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                data = result.get('data', {})
                if data:
                    defects = data.get('defects', [])
                    c43_defects = [d for d in defects if d.get('fieldCode') == 'C43x03C']
                    print(f"C43x03C字段缺陷数量: {len(c43_defects)} (应该为0，因为值有效)")
                    
                    if c43_defects:
                        print("意外发现缺陷:")
                        for defect in c43_defects:
                            print(f"  {defect.get('fieldCode')}: {defect.get('actualValue')} -> {defect.get('expectedValue')}")
    
    finally:
        cursor.close()
        conn.close()

def test_rc013_dict():
    """测试RC013字典查询"""
    print("\n=== 测试RC013字典查询 ===")
    
    response = requests.get(f"{BASE_URL}/dict/type/RC013")
    print(f"字典查询状态: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        data = result.get('data', [])
        print(f"RC013字典项数量: {len(data)}")
        
        # 显示前几个字典项
        for i, item in enumerate(data[:5]):
            print(f"  {item.get('dictCode')}: {item.get('dictName')}")
        
        # 检查是否包含"-"
        dash_items = [item for item in data if item.get('dictCode') == '-']
        print(f"字典中是否包含'-': {'是' if dash_items else '否'}")

if __name__ == "__main__":
    test_rc013_dict()
    test_dict_validation()