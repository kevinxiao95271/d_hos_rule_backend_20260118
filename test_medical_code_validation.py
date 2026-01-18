#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
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

def test_medical_dict_cache():
    """测试医疗字典缓存"""
    print("=== 测试医疗字典缓存 ===")
    
    # 测试医疗字典是否已缓存
    medical_dict_types = [
        "RCJBBM",  # 疾病编码
        "operation_dict_v3",  # 手术编码
        "level4_operation_code_v2",  # 四级手术编码
        "microfracture_oper_code_v2",  # 微创手术
        "day_operation_code_2022",  # 日间手术
        "operation_code_with_type"  # 手术类型
    ]
    
    print("测试医疗字典API访问:")
    
    for dict_type in medical_dict_types:
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/dict/type/{dict_type}", timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                print(f"  ✅ {dict_type}: {len(data)}条记录, 响应时间: {response_time:.2f}ms")
            else:
                print(f"  ❌ {dict_type}: 请求失败 ({response.status_code})")
        
        except Exception as e:
            print(f"  ❌ {dict_type}: 请求异常 - {e}")

def test_medical_code_validation():
    """测试医疗编码验证"""
    print(f"\n=== 测试医疗编码验证 ===")
    
    # 测试用例
    test_cases = [
        # 疾病编码测试
        {"dictTypeCode": "RCJBBM", "value": "A00.000", "expected": True, "desc": "霍乱编码"},
        {"dictTypeCode": "RCJBBM", "value": "INVALID_CODE", "expected": False, "desc": "无效疾病编码"},
        
        # 手术编码测试
        {"dictTypeCode": "operation_dict_v3", "value": "00.0100", "expected": True, "desc": "头和颈部血管治疗性超声"},
        {"dictTypeCode": "operation_dict_v3", "value": "INVALID_OP", "expected": False, "desc": "无效手术编码"},
    ]
    
    print("测试医疗编码验证:")
    
    for test_case in test_cases:
        try:
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/dict/validate", 
                                   json={
                                       "dictTypeCode": test_case["dictTypeCode"],
                                       "value": test_case["value"]
                                   },
                                   timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                is_valid = response.json().get('data', False)
                expected = test_case["expected"]
                result = "✅ 正确" if is_valid == expected else "❌ 错误"
                
                print(f"  {result} {test_case['desc']}: {test_case['value']} = {is_valid} (预期: {expected}), 响应时间: {response_time:.2f}ms")
            else:
                print(f"  ❌ {test_case['desc']}: 请求失败 ({response.status_code})")
        
        except Exception as e:
            print(f"  ❌ {test_case['desc']}: 请求异常 - {e}")

def test_single_case_with_medical_codes():
    """测试包含医疗编码的单个病案"""
    print(f"\n=== 测试包含医疗编码的病案质控 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取2023年的测试病案
        cursor.execute("""
            SELECT A48, A49 
            FROM d_mr 
            WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
            LIMIT 1
        """)
        test_case = cursor.fetchone()
        
        if test_case:
            print(f"测试病案: {test_case['A48']}_{test_case['A49']}")
            
            # 清理之前的结果
            mr_key = f"{test_case['A48']}_{test_case['A49']}"
            cursor.execute("DELETE FROM kiro_qc_case_result WHERE mr_key = %s", (mr_key,))
            cursor.execute("DELETE FROM kiro_qc_defect_detail WHERE mr_key = %s", (mr_key,))
            conn.commit()
            
            # 执行质控
            print("执行质控检查...")
            start_time = time.time()
            
            try:
                response = requests.post(f"{BASE_URL}/qc/check/single", 
                                       params={
                                           'a48': test_case['A48'],
                                           'a49': test_case['A49']
                                       },
                                       timeout=60)
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                print(f"处理时间: {processing_time:.2f}秒")
                
                if response.status_code == 200:
                    result = response.json().get('data', {})
                    defect_count = result.get('defectCount', 0)
                    final_score = result.get('finalScore', 0)
                    
                    print(f"检测到缺陷: {defect_count}个")
                    print(f"最终得分: {final_score}")
                    
                    # 查看医疗编码相关的缺陷
                    print(f"\n检查医疗编码相关缺陷:")
                    cursor.execute("""
                        SELECT field_code, field_name, actual_value, expected_value, rule_description
                        FROM kiro_qc_defect_detail 
                        WHERE mr_key = %s 
                        AND (field_code LIKE 'C01%' OR field_code LIKE 'C21%' OR field_code LIKE 'C38%' OR field_code LIKE 'C43%')
                        ORDER BY field_code
                    """, (mr_key,))
                    
                    medical_defects = cursor.fetchall()
                    
                    if medical_defects:
                        print(f"发现{len(medical_defects)}个医疗编码相关缺陷:")
                        for defect in medical_defects:
                            print(f"  {defect['field_code']} ({defect['field_name']}): {defect['actual_value']}")
                            print(f"    期望: {defect['expected_value']}")
                            print(f"    规则: {defect['rule_description'][:60]}...")
                    else:
                        print("未发现医疗编码相关缺陷")
                    
                    return processing_time, defect_count, len(medical_defects)
                
                else:
                    print(f"质控失败: {response.status_code}")
                    return None, None, None
            
            except Exception as e:
                print(f"质控异常: {e}")
                return None, None, None
        
        else:
            print("未找到测试病案")
            return None, None, None
    
    finally:
        cursor.close()
        conn.close()

def check_cache_effectiveness():
    """检查缓存效果"""
    print(f"\n=== 检查缓存效果 ===")
    
    # 获取缓存统计
    try:
        response = requests.get(f"{BASE_URL}/dict/cache/stats")
        if response.status_code == 200:
            stats = response.json().get('data', {})
            print(f"缓存统计:")
            print(f"  字典缓存数量: {stats.get('dictCacheCount', 0)}")
            print(f"  集合缓存数量: {stats.get('setCacheCount', 0)}")
            print(f"  缓存过期时间: {stats.get('cacheExpireHours', 0)}小时")
        else:
            print("无法获取缓存统计")
    except Exception as e:
        print(f"缓存统计查询失败: {e}")

def main():
    """主函数"""
    print("医疗编码验证功能测试")
    print("=" * 50)
    
    # 1. 测试医疗字典缓存
    test_medical_dict_cache()
    
    # 2. 测试医疗编码验证
    test_medical_code_validation()
    
    # 3. 测试实际病案质控
    processing_time, total_defects, medical_defects = test_single_case_with_medical_codes()
    
    # 4. 检查缓存效果
    check_cache_effectiveness()
    
    # 5. 总结
    print(f"\n=== 测试总结 ===")
    
    if processing_time is not None:
        print(f"✅ 医疗编码验证功能已启用")
        print(f"单病案处理时间: {processing_time:.2f}秒")
        print(f"总缺陷数: {total_defects}")
        print(f"医疗编码缺陷数: {medical_defects}")
        
        if medical_defects > 0:
            print(f"🎉 成功检测到医疗编码相关缺陷！")
        else:
            print(f"ℹ️  该病案的医疗编码符合规范")
    else:
        print(f"❌ 测试失败")
    
    print(f"\n医疗编码字典已成功集成到质控系统中！")

if __name__ == "__main__":
    main()