#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import time
import requests
from collections import defaultdict

# 数据库连接配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def analyze_dict_usage():
    """分析字典查询的使用情况"""
    print("=== 分析字典查询使用情况 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 统计RC0xx字典类型的数据量
        print("1. RC0xx字典数据量统计:")
        cursor.execute("""
            SELECT dict_type_code, COUNT(*) as dict_count
            FROM sys_dict 
            WHERE dict_type_code LIKE 'RC%'
            GROUP BY dict_type_code
            ORDER BY dict_count DESC
        """)
        
        rc_stats = cursor.fetchall()
        total_rc_records = 0
        
        for stat in rc_stats:
            print(f"  {stat['dict_type_code']}: {stat['dict_count']}条")
            total_rc_records += stat['dict_count']
        
        print(f"RC0xx总记录数: {total_rc_records}")
        
        # 2. 统计活跃规则中涉及的字典类型
        print(f"\n2. 活跃规则中的字典验证:")
        cursor.execute("""
            SELECT dict_types, COUNT(*) as rule_count
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            AND rule_type = 'value_check'
            AND dict_types IS NOT NULL
            GROUP BY dict_types
            ORDER BY rule_count DESC
        """)
        
        dict_usage = cursor.fetchall()
        
        for usage in dict_usage:
            print(f"  {usage['dict_types']}: {usage['rule_count']}条规则")
        
        # 3. 测试单次字典查询性能
        print(f"\n3. 单次字典查询性能测试:")
        
        test_dict_types = ['RC001', 'RC013', 'RC019', 'RC030', 'RC035']
        
        for dict_type in test_dict_types:
            start_time = time.time()
            cursor.execute("SELECT dict_code FROM sys_dict WHERE dict_type_code = %s", (dict_type,))
            results = cursor.fetchall()
            end_time = time.time()
            
            query_time = (end_time - start_time) * 1000  # 毫秒
            print(f"  {dict_type}: {len(results)}条记录, 查询时间: {query_time:.2f}ms")
        
        # 4. 模拟批量处理中的字典查询
        print(f"\n4. 模拟批量处理字典查询:")
        
        # 获取2023年的几个测试病案
        cursor.execute("""
            SELECT A48, A49 
            FROM d_mr 
            WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
            LIMIT 5
        """)
        test_cases = cursor.fetchall()
        
        print(f"测试{len(test_cases)}个病案的字典查询性能...")
        
        total_queries = 0
        total_time = 0
        
        for case in test_cases:
            case_start = time.time()
            
            # 模拟一个病案需要的字典查询（基于当前活跃规则）
            for dict_type in ['RC001', 'RC013', 'RC019', 'RC030', 'RC035']:
                query_start = time.time()
                cursor.execute("SELECT dict_code FROM sys_dict WHERE dict_type_code = %s", (dict_type,))
                cursor.fetchall()
                query_end = time.time()
                
                total_queries += 1
                total_time += (query_end - query_start)
            
            case_end = time.time()
            case_time = (case_end - case_start) * 1000
            print(f"  病案 {case['A48']}_{case['A49']}: {case_time:.2f}ms")
        
        avg_query_time = (total_time / total_queries) * 1000
        print(f"\n平均单次字典查询时间: {avg_query_time:.2f}ms")
        print(f"总查询次数: {total_queries}")
        print(f"总查询时间: {total_time * 1000:.2f}ms")
        
        # 5. 估算2023年全部处理的字典查询开销
        cursor.execute("""
            SELECT COUNT(*) as case_count
            FROM d_mr 
            WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
        """)
        total_cases = cursor.fetchone()['case_count']
        
        # 假设每个病案平均需要查询5个字典类型
        estimated_queries = total_cases * 5
        estimated_time = estimated_queries * (avg_query_time / 1000)
        
        print(f"\n5. 2023年全部处理估算:")
        print(f"总病案数: {total_cases}")
        print(f"估算字典查询次数: {estimated_queries}")
        print(f"估算字典查询总时间: {estimated_time:.2f}秒 ({estimated_time/60:.1f}分钟)")
        
        return {
            'total_rc_records': total_rc_records,
            'avg_query_time_ms': avg_query_time,
            'estimated_total_time_sec': estimated_time
        }
        
    finally:
        cursor.close()
        conn.close()

def test_api_dict_performance():
    """测试API字典查询性能"""
    print(f"\n=== 测试API字典查询性能 ===")
    
    BASE_URL = "http://localhost:4101/api"
    
    test_dict_types = ['RC001', 'RC013', 'RC019', 'RC030', 'RC035']
    
    print("测试API字典查询响应时间:")
    
    total_time = 0
    
    for dict_type in test_dict_types:
        start_time = time.time()
        
        try:
            response = requests.get(f"{BASE_URL}/dict/type/{dict_type}", timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            total_time += response_time
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                print(f"  {dict_type}: {len(data)}条记录, 响应时间: {response_time:.2f}ms")
            else:
                print(f"  {dict_type}: 请求失败 ({response.status_code})")
        
        except Exception as e:
            print(f"  {dict_type}: 请求异常 - {e}")
    
    avg_api_time = total_time / len(test_dict_types)
    print(f"\n平均API响应时间: {avg_api_time:.2f}ms")
    
    return avg_api_time

if __name__ == "__main__":
    # 分析字典使用情况
    stats = analyze_dict_usage()
    
    # 测试API性能
    try:
        api_time = test_api_dict_performance()
        
        print(f"\n=== 性能分析总结 ===")
        print(f"RC0xx字典总记录数: {stats['total_rc_records']}")
        print(f"数据库查询平均时间: {stats['avg_query_time_ms']:.2f}ms")
        print(f"API查询平均时间: {api_time:.2f}ms")
        print(f"2023年批量处理字典查询开销: {stats['estimated_total_time_sec']:.1f}秒")
        
        if stats['estimated_total_time_sec'] > 30:
            print(f"\n⚠️  字典查询开销较大，建议引入Redis缓存")
        else:
            print(f"\n✅ 字典查询性能可接受")
            
    except Exception as e:
        print(f"API测试失败: {e}")
        print("请确保服务已启动 (java -jar target/qc-system-1.0.0.jar)")