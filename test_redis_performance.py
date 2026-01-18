#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import pymysql
from concurrent.futures import ThreadPoolExecutor
import statistics

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

def test_cache_loading():
    """测试缓存加载性能"""
    print("=== 测试Redis缓存加载性能 ===")
    
    try:
        # 1. 清除现有缓存
        print("1. 清除现有缓存...")
        response = requests.delete(f"{BASE_URL}/dict/cache")
        if response.status_code == 200:
            print("✅ 缓存清除成功")
        else:
            print(f"⚠️  缓存清除失败: {response.status_code}")
        
        # 2. 重新加载缓存并测试时间
        print("2. 重新加载缓存...")
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/dict/cache/reload")
        
        end_time = time.time()
        load_time = end_time - start_time
        
        if response.status_code == 200:
            print(f"✅ 缓存加载成功，耗时: {load_time:.2f}秒")
        else:
            print(f"❌ 缓存加载失败: {response.status_code}")
            return False
        
        # 3. 获取缓存统计
        print("3. 获取缓存统计...")
        response = requests.get(f"{BASE_URL}/dict/cache/stats")
        if response.status_code == 200:
            stats = response.json().get('data', {})
            print(f"字典缓存数量: {stats.get('dictCacheCount', 0)}")
            print(f"集合缓存数量: {stats.get('setCacheCount', 0)}")
            print(f"缓存过期时间: {stats.get('cacheExpireHours', 0)}小时")
        
        return True
        
    except Exception as e:
        print(f"❌ 缓存加载测试失败: {e}")
        return False

def test_single_dict_query_performance():
    """测试单次字典查询性能对比"""
    print(f"\n=== 测试单次字典查询性能对比 ===")
    
    test_dict_types = ['RC001', 'RC013', 'RC019', 'RC030', 'RC035']
    
    print("测试缓存查询性能:")
    cache_times = []
    
    for dict_type in test_dict_types:
        start_time = time.time()
        
        try:
            response = requests.get(f"{BASE_URL}/dict/type/{dict_type}")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            cache_times.append(response_time)
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                print(f"  {dict_type}: {len(data)}条记录, 响应时间: {response_time:.2f}ms")
            else:
                print(f"  {dict_type}: 请求失败 ({response.status_code})")
        
        except Exception as e:
            print(f"  {dict_type}: 请求异常 - {e}")
    
    if cache_times:
        avg_cache_time = statistics.mean(cache_times)
        print(f"\n缓存查询平均响应时间: {avg_cache_time:.2f}ms")
        return avg_cache_time
    
    return None

def test_validation_performance():
    """测试字典验证性能"""
    print(f"\n=== 测试字典验证性能 ===")
    
    # 测试数据
    test_cases = [
        {'dictTypeCode': 'RC001', 'value': '1'},  # 男
        {'dictTypeCode': 'RC001', 'value': '2'},  # 女
        {'dictTypeCode': 'RC013', 'value': '1'},  # 局麻
        {'dictTypeCode': 'RC019', 'value': '1'},  # 医嘱离院
        {'dictTypeCode': 'RC030', 'value': 'A'},  # A型血
        {'dictTypeCode': 'RC035', 'value': '01'}, # 汉族
    ]
    
    validation_times = []
    
    print("测试字典验证响应时间:")
    
    for test_case in test_cases:
        start_time = time.time()
        
        try:
            response = requests.post(f"{BASE_URL}/dict/validate", json=test_case)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            validation_times.append(response_time)
            
            if response.status_code == 200:
                is_valid = response.json().get('data', False)
                print(f"  {test_case['dictTypeCode']}:{test_case['value']} = {is_valid}, 响应时间: {response_time:.2f}ms")
            else:
                print(f"  {test_case['dictTypeCode']}:{test_case['value']}: 请求失败 ({response.status_code})")
        
        except Exception as e:
            print(f"  {test_case['dictTypeCode']}:{test_case['value']}: 请求异常 - {e}")
    
    if validation_times:
        avg_validation_time = statistics.mean(validation_times)
        print(f"\n字典验证平均响应时间: {avg_validation_time:.2f}ms")
        return avg_validation_time
    
    return None

def test_batch_performance():
    """测试批量处理性能提升"""
    print(f"\n=== 测试批量处理性能提升 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取2023年的一个测试病案
        cursor.execute("""
            SELECT A48, A49 
            FROM d_mr 
            WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
            LIMIT 1
        """)
        test_case = cursor.fetchone()
        
        if not test_case:
            print("❌ 未找到2023年测试数据")
            return
        
        print(f"测试病案: {test_case['A48']}_{test_case['A49']}")
        
        # 清理之前的结果
        mr_key = f"{test_case['A48']}_{test_case['A49']}"
        cursor.execute("DELETE FROM kiro_qc_case_result WHERE mr_key = %s", (mr_key,))
        cursor.execute("DELETE FROM kiro_qc_defect_detail WHERE mr_key = %s", (mr_key,))
        conn.commit()
        
        # 测试单个病案处理时间
        print("测试单个病案处理时间...")
        start_time = time.time()
        
        try:
            response = requests.post(f"{BASE_URL}/qc/check/single", 
                                   params={
                                       'a48': test_case['A48'],
                                       'a49': test_case['A49']
                                   },
                                   timeout=30)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"使用Redis缓存处理时间: {processing_time:.2f}秒")
            
            if response.status_code == 200:
                result = response.json().get('data', {})
                defect_count = result.get('defectCount', 0)
                final_score = result.get('finalScore', 0)
                
                print(f"检测到缺陷: {defect_count}个")
                print(f"最终得分: {final_score}")
                
                # 估算2023年全部处理时间
                cursor.execute("""
                    SELECT COUNT(*) as case_count
                    FROM d_mr 
                    WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
                """)
                case_count = cursor.fetchone()['case_count']
                
                estimated_total = processing_time * case_count
                print(f"估算2023年全部处理时间: {estimated_total:.0f}秒 ({estimated_total/60:.1f}分钟)")
                
                return processing_time
            
            else:
                print(f"处理失败: {response.status_code}")
        
        except Exception as e:
            print(f"测试异常: {e}")
    
    finally:
        cursor.close()
        conn.close()
    
    return None

def test_concurrent_performance():
    """测试并发查询性能"""
    print(f"\n=== 测试并发查询性能 ===")
    
    def query_dict(dict_type):
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/dict/type/{dict_type}")
            end_time = time.time()
            
            if response.status_code == 200:
                return (end_time - start_time) * 1000
            else:
                return None
        except:
            return None
    
    # 并发测试
    dict_types = ['RC001', 'RC013', 'RC019', 'RC030', 'RC035'] * 4  # 20个并发请求
    
    print(f"测试{len(dict_types)}个并发字典查询...")
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(query_dict, dict_types))
    
    end_time = time.time()
    
    successful_results = [r for r in results if r is not None]
    
    if successful_results:
        total_time = end_time - start_time
        avg_response_time = statistics.mean(successful_results)
        
        print(f"并发查询总时间: {total_time:.2f}秒")
        print(f"成功请求数: {len(successful_results)}/{len(dict_types)}")
        print(f"平均响应时间: {avg_response_time:.2f}ms")
        print(f"QPS: {len(successful_results)/total_time:.1f}")
    
    return successful_results

def compare_with_baseline():
    """与基准性能对比"""
    print(f"\n=== 性能对比总结 ===")
    
    # 基准数据（来自之前的测试）
    baseline_db_query = 82.81  # ms
    baseline_api_query = 118.09  # ms
    baseline_batch_time = 39.7  # seconds
    
    print("基准性能（无缓存）:")
    print(f"  数据库查询: {baseline_db_query:.2f}ms")
    print(f"  API查询: {baseline_api_query:.2f}ms")
    print(f"  2023年批量处理字典开销: {baseline_batch_time:.1f}秒")
    
    # 当前性能会在测试中获得
    print(f"\n当前性能（Redis缓存）:")
    print("  (将在测试中获得)")

if __name__ == "__main__":
    print("Redis缓存性能测试")
    print("请确保:")
    print("1. Redis服务已启动")
    print("2. 应用服务已启动 (java -jar target/qc-system-1.0.0.jar)")
    print("3. 已添加Redis依赖并重新编译")
    print()
    
    # 显示基准对比
    compare_with_baseline()
    
    # 测试缓存加载
    if test_cache_loading():
        
        # 测试单次查询性能
        cache_query_time = test_single_dict_query_performance()
        
        # 测试验证性能
        validation_time = test_validation_performance()
        
        # 测试批量处理性能
        batch_time = test_batch_performance()
        
        # 测试并发性能
        concurrent_results = test_concurrent_performance()
        
        # 性能提升总结
        print(f"\n=== 性能提升总结 ===")
        
        if cache_query_time:
            improvement = 118.09 / cache_query_time
            print(f"API查询性能提升: {improvement:.1f}x ({118.09:.2f}ms → {cache_query_time:.2f}ms)")
        
        if validation_time:
            print(f"字典验证响应时间: {validation_time:.2f}ms")
        
        if batch_time:
            batch_improvement = 39.7 / (batch_time * 96 / 5)  # 估算改进
            estimated_new_batch = batch_time * 96
            print(f"批量处理性能提升: {batch_improvement:.1f}x ({39.7:.1f}s → {estimated_new_batch:.1f}s)")
        
        if concurrent_results:
            avg_concurrent = statistics.mean(concurrent_results)
            print(f"并发查询平均响应时间: {avg_concurrent:.2f}ms")
    
    else:
        print("❌ 缓存测试失败，请检查Redis和应用服务状态")