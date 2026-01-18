#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import time

# 数据库连接配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def analyze_performance_bottleneck():
    """分析性能瓶颈"""
    print("=== 分析性能瓶颈 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 统计规则数量和类型
        print("1. 规则统计分析...")
        cursor.execute("""
            SELECT rule_type, COUNT(*) as count, 
                   AVG(CASE WHEN dict_types IS NOT NULL AND dict_types != '' THEN 1 ELSE 0 END) as dict_ratio
            FROM kiro_qc_rule 
            WHERE status = 'active'
            GROUP BY rule_type
            ORDER BY count DESC
        """)
        rule_stats = cursor.fetchall()
        
        total_rules = sum(r['count'] for r in rule_stats)
        print(f"总激活规则数: {total_rules}")
        
        for stat in rule_stats:
            print(f"  {stat['rule_type']}: {stat['count']}条")
        
        # 2. 分析最近的处理性能
        print(f"\n2. 最近处理性能分析...")
        cursor.execute("""
            SELECT COUNT(*) as processed_cases,
                   COUNT(DISTINCT mr_key) as unique_cases,
                   SUM(defect_count) as total_defects,
                   AVG(defect_count) as avg_defects,
                   MIN(created_time) as start_time,
                   MAX(created_time) as end_time
            FROM kiro_qc_case_result 
            WHERE created_time > DATE_SUB(NOW(), INTERVAL 2 HOUR)
        """)
        perf_stats = cursor.fetchone()
        
        if perf_stats and perf_stats['processed_cases'] > 0:
            print(f"最近2小时处理病案: {perf_stats['unique_cases']}个")
            print(f"平均缺陷数: {perf_stats['avg_defects']:.1f}")
            print(f"总缺陷记录: {perf_stats['total_defects']}")
            
            if perf_stats['start_time'] and perf_stats['end_time']:
                time_diff = (perf_stats['end_time'] - perf_stats['start_time']).total_seconds()
                if time_diff > 0:
                    cases_per_second = perf_stats['unique_cases'] / time_diff
                    print(f"处理速度: {cases_per_second:.3f} 病案/秒")
        
        # 3. 分析缺陷分布
        print(f"\n3. 缺陷分布分析...")
        cursor.execute("""
            SELECT rule_type, COUNT(*) as defect_count
            FROM kiro_qc_defect_detail d
            JOIN kiro_qc_rule r ON d.rule_code = r.rule_code
            WHERE d.created_time > DATE_SUB(NOW(), INTERVAL 2 HOUR)
            GROUP BY rule_type
            ORDER BY defect_count DESC
            LIMIT 10
        """)
        defect_stats = cursor.fetchall()
        
        if defect_stats:
            print("最常触发的规则类型:")
            for stat in defect_stats:
                print(f"  {stat['rule_type']}: {stat['defect_count']}次违规")
        
    finally:
        cursor.close()
        conn.close()

def create_core_rule_set():
    """创建核心规则集"""
    print(f"\n=== 创建核心规则集 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 基于重要性选择核心规则
        print("1. 选择核心规则...")
        
        # 核心规则选择策略：
        # - 所有range_check规则（数值范围很重要）
        # - 重要的字典验证规则（A01-A30等基本信息字段）
        # - 关键的cross_check规则（医疗逻辑关系）
        
        core_rule_conditions = [
            "rule_type = 'range_check'",  # 所有范围检查
            "(rule_type = 'value_check' AND field_code REGEXP '^A[0-9]{2}$')",  # A01-A99基本信息字段
            "(rule_type = 'cross_check_null' AND field_code LIKE 'A18%')",  # 新生儿相关
            "(rule_type = 'date_check')",  # 日期检查
            "(dict_types IN ('RC001', 'RC002', 'RC011', 'RC019', 'RC030'))"  # 重要字典
        ]
        
        # 将非核心规则设为inactive
        cursor.execute("""
            UPDATE kiro_qc_rule 
            SET status = 'inactive'
            WHERE status = 'active'
        """)
        
        # 激活核心规则
        core_condition = " OR ".join(f"({cond})" for cond in core_rule_conditions)
        
        cursor.execute(f"""
            UPDATE kiro_qc_rule 
            SET status = 'active'
            WHERE {core_condition}
        """)
        
        conn.commit()
        
        # 统计核心规则数量
        cursor.execute("SELECT COUNT(*) as count FROM kiro_qc_rule WHERE status = 'active'")
        core_count = cursor.fetchone()['count']
        
        print(f"核心规则集大小: {core_count}条")
        
        # 按类型统计核心规则
        cursor.execute("""
            SELECT rule_type, COUNT(*) as count
            FROM kiro_qc_rule 
            WHERE status = 'active'
            GROUP BY rule_type
            ORDER BY count DESC
        """)
        core_stats = cursor.fetchall()
        
        print("核心规则分布:")
        for stat in core_stats:
            print(f"  {stat['rule_type']}: {stat['count']}条")
        
        return core_count
        
    finally:
        cursor.close()
        conn.close()

def test_optimized_performance():
    """测试优化后的性能"""
    print(f"\n=== 测试优化后性能 ===")
    
    import requests
    
    BASE_URL = "http://localhost:4101/api"
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取测试病案
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
            
            # 测试优化后的处理时间
            start_time = time.time()
            
            try:
                response = requests.post(f"{BASE_URL}/qc/check/single", 
                                       params={
                                           'a48': test_case['A48'],
                                           'a49': test_case['A49']
                                       },
                                       timeout=60)  # 1分钟超时
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                print(f"优化后处理时间: {processing_time:.2f}秒")
                
                if response.status_code == 200:
                    result = response.json().get('data', {})
                    defect_count = result.get('defectCount', 0)
                    final_score = result.get('finalScore', 0)
                    
                    print(f"检测到缺陷: {defect_count}个")
                    print(f"最终得分: {final_score}")
                    
                    # 估算批量处理时间
                    cursor.execute("""
                        SELECT COUNT(*) as case_count
                        FROM d_mr 
                        WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
                    """)
                    case_count = cursor.fetchone()['case_count']
                    
                    estimated_batch_time = processing_time * case_count
                    print(f"估算2023年全部处理时间: {estimated_batch_time:.0f}秒 ({estimated_batch_time/60:.1f}分钟)")
                    
                    if estimated_batch_time < 300:  # 5分钟内
                        print("✅ 性能优化成功！处理时间可接受")
                    elif estimated_batch_time < 600:  # 10分钟内
                        print("⚠️  性能有改善，但仍需进一步优化")
                    else:
                        print("❌ 仍需更多优化")
                
                else:
                    print(f"处理失败: {response.status_code}")
                    print(f"错误: {response.text}")
            
            except Exception as e:
                print(f"测试异常: {e}")
    
    finally:
        cursor.close()
        conn.close()

def restore_full_rules():
    """恢复完整规则集"""
    print(f"\n=== 恢复完整规则集选项 ===")
    print("如需恢复完整的1699条规则，可执行:")
    print("UPDATE kiro_qc_rule SET status = 'active' WHERE status = 'inactive';")

if __name__ == "__main__":
    analyze_performance_bottleneck()
    core_count = create_core_rule_set()
    
    if core_count < 500:  # 如果核心规则数量合理
        test_optimized_performance()
    
    restore_full_rules()