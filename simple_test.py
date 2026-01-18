#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import requests

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

def test_db_connection():
    """测试数据库连接"""
    print("测试数据库连接...")
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 查询2023年病案数量
        cursor.execute("SELECT COUNT(*) as count FROM d_mr WHERE B15 LIKE '2023/%'")
        result = cursor.fetchone()
        print(f"✅ 数据库连接成功，2023年病案数: {result['count']}")
        
        # 获取前5条2023年病案
        cursor.execute("""
            SELECT CONCAT(A48, '_', A49) as mr_key, A49 as mr_no, A02 as pat_name, B15 as in_date
            FROM d_mr 
            WHERE B15 LIKE '2023/%'
            ORDER BY B15 
            LIMIT 5
        """)
        cases = cursor.fetchall()
        
        print("前5条2023年病案:")
        for i, case in enumerate(cases, 1):
            pat_name = case['pat_name'][:3] + '***' if case['pat_name'] else '未知'
            print(f"  {i}. {case['mr_key']} | {case['mr_no']} | {pat_name} | {case['in_date']}")
        
        cursor.close()
        conn.close()
        return cases
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return []

def test_api_connection():
    """测试API连接"""
    print("\n测试API连接...")
    try:
        response = requests.get(f"{BASE_URL}/qc/status", timeout=10)
        if response.status_code == 200:
            print("✅ API连接成功")
            return True
        else:
            print(f"❌ API返回错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

def test_single_case_api(mr_key):
    """测试单个病案质控API"""
    print(f"\n测试病案质控: {mr_key}")
    try:
        response = requests.post(f"{BASE_URL}/qc/check/single", 
                               json={"mrKey": mr_key},
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json().get('data', {})
            defect_count = result.get('defectCount', 0)
            final_score = result.get('finalScore', 0)
            print(f"✅ 质控成功: {defect_count}个缺陷, 得分{final_score}")
            return True
        else:
            print(f"❌ 质控失败: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ 质控异常: {e}")
        return False

def main():
    print("简单系统测试")
    print("=" * 30)
    
    # 1. 测试数据库连接
    cases = test_db_connection()
    if not cases:
        print("数据库测试失败，退出")
        return
    
    # 2. 测试API连接
    if not test_api_connection():
        print("API测试失败，退出")
        return
    
    # 3. 测试单个病案质控
    test_case = cases[0]['mr_key']
    if test_single_case_api(test_case):
        print(f"\n✅ 系统测试通过！可以进行批量测试")
        print(f"建议测试病案: {[case['mr_key'] for case in cases[:3]]}")
    else:
        print(f"\n❌ 单个病案测试失败，请检查系统配置")

if __name__ == "__main__":
    main()