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

def test_optimized_2023_performance():
    """测试优化后的2023年数据处理性能"""
    print("=== 测试优化后的2023年数据处理性能 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 检查当前规则数量
        print("1. 检查当前规则数量...")
        cursor.execute("SELECT COUNT(*) as count FROM kiro_qc_rule WHERE status = 'active'")
        rule_count = cursor.fetchone()['count']
        print(f"当前激活规则数: {rule_count}")
        
        # 2. 检查2023年数据量
        cursor.execute("""
            SELECT COUNT(*) as case_count
            FROM d_mr 
            WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
        """)
        case_count = cursor.fetchone()['case_count']
        print(f"2023年病案数量: {case_count}")
        
        # 3. 测试单个病案处理时间
        print(f"\n2. 测试单个病案处理时间...")
        
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
            
            # 测试处理时间
            start_time = time.time()
            
            response = requests.post(f"{BASE_URL}/qc/check/single", 
                                   params={
                                       'a48': test_case['A48'],
                                       'a49': test_case['A49']
                                   },
                                   timeout=60)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"单个病案处理时间: {processing_time:.2f}秒")
            
            if response.status_code == 200:
                result = response.json().get('data', {})
                defect_count = result.get('defectCount', 0)
                final_score = result.get('finalScore', 0)
                
                print(f"检测到缺陷: {defect_count}个")
                print(f"最终得分: {final_score}")
                
                # 估算批量处理时间
                estimated_batch_time = processing_time * case_count
                print(f"\n估算2023年全部{case_count}个病案处理时间:")
                print(f"  总时间: {estimated_batch_time:.0f}秒")
                print(f"  约: {estimated_batch_time/60:.1f}分钟")
                
                if estimated_batch_time < 180:  # 3分钟内
                    print("✅ 性能优秀！处理时间很快")
                elif estimated_batch_time < 600:  # 10分钟内
                    print("✅ 性能良好，可接受")
                else:
                    print("⚠️  仍需进一步优化")
                
                # 4. 测试批量处理（前3个病案）
                print(f"\n3. 测试小批量处理...")
                
                cursor.execute("""
                    SELECT A48, A49 
                    FROM d_mr 
                    WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
                    LIMIT 3
                """)
                batch_cases = cursor.fetchall()
                
                batch_start = time.time()
                batch_success = 0
                
                for i, case in enumerate(batch_cases, 1):
                    print(f"  处理病案 {i}/3: {case['A48']}_{case['A49']}")
                    
                    try:
                        response = requests.post(f"{BASE_URL}/qc/check/single", 
                                               params={
                                                   'a48': case['A48'],
                                                   'a49': case['A49']
                                               },
                                               timeout=30)
                        
                        if response.status_code == 200:
                            result = response.json().get('data', {})
                            defects = result.get('defectCount', 0)
                            score = result.get('finalScore', 0)
                            print(f"    结果: {defects}个缺陷, 得分{score}")
                            batch_success += 1
                        else:
                            print(f"    失败: {response.status_code}")
                    
                    except Exception as e:
                        print(f"    异常: {e}")
                
                batch_end = time.time()
                batch_time = batch_end - batch_start
                
                print(f"\n小批量处理结果:")
                print(f"  总时间: {batch_time:.2f}秒")
                print(f"  成功: {batch_success}/3个病案")
                print(f"  平均: {batch_time/3:.2f}秒/病案")
                
                # 基于实际批量测试重新估算
                if batch_success > 0:
                    real_avg = batch_time / batch_success
                    real_estimate = real_avg * case_count
                    print(f"  实际估算全部处理时间: {real_estimate:.0f}秒 ({real_estimate/60:.1f}分钟)")
            
            else:
                print(f"单个病案处理失败: {response.status_code}")
                print(f"错误信息: {response.text}")
        
        # 5. 性能对比
        print(f"\n4. 性能优化效果:")
        print(f"  规则数量: 1532 → {rule_count} (减少{(1532-rule_count)/1532*100:.1f}%)")
        print(f"  预期性能提升: ~{1532/rule_count:.1f}倍")
        
    finally:
        cursor.close()
        conn.close()

def test_2023_batch_qc():
    """测试2023年批量质控"""
    print(f"\n=== 测试2023年批量质控 ===")
    
    batch_data = {
        "startDate": "2023-01-01",
        "endDate": "2023-12-31",
        "batchType": "year"
    }
    
    print("启动2023年批量质控...")
    start_time = time.time()
    
    try:
        response = requests.post(f"{BASE_URL}/qc/check/batch", 
                               json=batch_data,
                               timeout=600)  # 10分钟超时
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"批量质控完成时间: {total_time:.2f}秒 ({total_time/60:.1f}分钟)")
        
        if response.status_code == 200:
            result = response.json()
            print(f"批量质控结果: {result.get('message', 'N/A')}")
            
            # 等待一下再查询结果
            time.sleep(2)
            
            # 查询批量结果
            summary_response = requests.post(f"{BASE_URL}/qc/result/batch/summary", json=batch_data)
            if summary_response.status_code == 200:
                summary = summary_response.json().get('data', {})
                print(f"批量汇总:")
                print(f"  病案数: {summary.get('caseCount', 0)}")
                print(f"  缺陷数: {summary.get('totalDefectCount', 0)}")
                print(f"  平均缺陷: {summary.get('avgDefect', 0)}")
                print(f"  平均得分: {summary.get('avgScore', 0)}")
        
        else:
            print(f"批量质控失败: {response.status_code}")
            print(f"错误: {response.text}")
    
    except Exception as e:
        print(f"批量质控异常: {e}")

if __name__ == "__main__":
    test_optimized_2023_performance()
    
    # 询问是否测试批量处理
    print(f"\n是否测试2023年批量质控？(y/n): ", end="")
    choice = input().lower()
    if choice == 'y':
        test_2023_batch_qc()