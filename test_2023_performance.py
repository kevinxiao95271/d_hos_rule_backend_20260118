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

def test_2023_performance():
    """测试2023年数据处理性能"""
    print("=== 测试2023年数据处理性能 ===")
    
    # 1. 先检查2023年数据量
    print("1. 检查2023年数据量...")
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute("""
            SELECT COUNT(*) as case_count
            FROM d_mr 
            WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
        """)
        result = cursor.fetchone()
        case_count = result['case_count']
        print(f"2023年病案数量: {case_count}")
        
        # 2. 测试单个病案处理时间
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
            cursor.execute("DELETE FROM kiro_qc_case_result WHERE mr_key = %s", (f"{test_case['A48']}_{test_case['A49']}",))
            cursor.execute("DELETE FROM kiro_qc_defect_detail WHERE mr_key = %s", (f"{test_case['A48']}_{test_case['A49']}",))
            conn.commit()
            
            # 测试处理时间
            start_time = time.time()
            
            response = requests.post(f"{BASE_URL}/qc/check/single", 
                                   params={
                                       'a48': test_case['A48'],
                                       'a49': test_case['A49']
                                   },
                                   timeout=300)  # 5分钟超时
            
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
                print(f"\n估算2023年全部{case_count}个病案处理时间: {estimated_batch_time:.0f}秒 ({estimated_batch_time/60:.1f}分钟)")
                
                if estimated_batch_time > 600:  # 超过10分钟
                    print("⚠️  警告: 预计处理时间过长，需要性能优化！")
                
            else:
                print(f"单个病案处理失败: {response.status_code}")
                print(f"错误信息: {response.text}")
        
        # 3. 测试小批量处理（前5个病案）
        print(f"\n3. 测试小批量处理性能...")
        
        cursor.execute("""
            SELECT A48, A49 
            FROM d_mr 
            WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
            LIMIT 5
        """)
        small_batch = cursor.fetchall()
        
        if small_batch:
            print(f"测试5个病案的处理时间...")
            
            total_start = time.time()
            success_count = 0
            
            for i, case in enumerate(small_batch, 1):
                print(f"  处理病案 {i}/5: {case['A48']}_{case['A49']}")
                
                case_start = time.time()
                
                try:
                    response = requests.post(f"{BASE_URL}/qc/check/single", 
                                           params={
                                               'a48': case['A48'],
                                               'a49': case['A49']
                                           },
                                           timeout=120)  # 2分钟超时
                    
                    case_end = time.time()
                    case_time = case_end - case_start
                    
                    if response.status_code == 200:
                        result = response.json().get('data', {})
                        defects = result.get('defectCount', 0)
                        print(f"    处理时间: {case_time:.2f}秒, 缺陷: {defects}个")
                        success_count += 1
                    else:
                        print(f"    处理失败: {response.status_code}")
                
                except Exception as e:
                    print(f"    处理异常: {e}")
            
            total_end = time.time()
            total_time = total_end - total_start
            
            print(f"\n小批量处理结果:")
            print(f"  总时间: {total_time:.2f}秒")
            print(f"  成功处理: {success_count}/5个病案")
            print(f"  平均时间: {total_time/5:.2f}秒/病案")
            
            # 基于小批量结果重新估算
            if success_count > 0:
                avg_time_per_case = total_time / success_count
                estimated_total = avg_time_per_case * case_count
                print(f"  重新估算全部处理时间: {estimated_total:.0f}秒 ({estimated_total/60:.1f}分钟)")
        
        # 4. 分析性能瓶颈
        print(f"\n4. 性能分析...")
        
        # 检查规则数量
        cursor.execute("SELECT COUNT(*) as rule_count FROM kiro_qc_rule WHERE status = 'active'")
        rule_result = cursor.fetchone()
        rule_count = rule_result['rule_count']
        
        print(f"当前激活规则数量: {rule_count}")
        print(f"理论计算复杂度: {case_count} × {rule_count} = {case_count * rule_count:,} 次规则检查")
        
        # 检查最近的缺陷记录数量
        cursor.execute("""
            SELECT COUNT(*) as recent_defects
            FROM kiro_qc_defect_detail 
            WHERE created_time > DATE_SUB(NOW(), INTERVAL 1 HOUR)
        """)
        defect_result = cursor.fetchone()
        recent_defects = defect_result['recent_defects'] if defect_result else 0
        
        print(f"最近1小时产生的缺陷记录: {recent_defects}")
        
    finally:
        cursor.close()
        conn.close()

def suggest_optimizations():
    """建议性能优化方案"""
    print(f"\n=== 性能优化建议 ===")
    
    print("🚀 立即可实施的优化:")
    print("1. 规则分级: 将规则按重要性分为核心规则和扩展规则")
    print("2. 批量优化: 改进批量处理逻辑，减少数据库往返")
    print("3. 索引优化: 为常用查询字段添加数据库索引")
    print("4. 缓存机制: 缓存字典数据和规则数据")
    
    print(f"\n⚡ 进阶优化方案:")
    print("1. 异步处理: 将质控处理改为异步任务")
    print("2. 并行处理: 支持多线程并行处理病案")
    print("3. 规则引擎优化: 优化规则匹配算法")
    print("4. 数据库连接池: 优化数据库连接管理")
    
    print(f"\n🎯 建议的处理策略:")
    print("1. 核心规则集: 保留最重要的200-300条规则用于日常质控")
    print("2. 完整规则集: 1699条规则用于深度质控或专项检查")
    print("3. 分层处理: 先跑核心规则，有问题的病案再跑完整规则")

if __name__ == "__main__":
    test_2023_performance()
    suggest_optimizations()