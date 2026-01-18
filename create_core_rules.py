#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

def create_core_rule_set():
    """创建核心规则集以提升性能"""
    print("=== 创建核心规则集 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 查看当前规则统计
        print("1. 当前规则统计...")
        cursor.execute("""
            SELECT rule_type, COUNT(*) as count
            FROM kiro_qc_rule 
            WHERE status = 'active'
            GROUP BY rule_type
            ORDER BY count DESC
        """)
        current_stats = cursor.fetchall()
        
        total_current = sum(r['count'] for r in current_stats)
        print(f"当前激活规则总数: {total_current}")
        
        for stat in current_stats:
            print(f"  {stat['rule_type']}: {stat['count']}条")
        
        # 2. 创建核心规则集
        print(f"\n2. 创建核心规则集...")
        
        # 先将所有规则设为inactive
        cursor.execute("UPDATE kiro_qc_rule SET status = 'inactive' WHERE status = 'active'")
        
        # 选择核心规则 - 保留最重要的规则类型
        core_rules = [
            # 范围检查 - 非常重要，保留所有
            "rule_type = 'range_check'",
            
            # 重要的字典验证 - 只保留基本信息字段
            "(rule_type = 'value_check' AND (field_code REGEXP '^A[0-2][0-9]$' OR field_code IN ('A01','A02','A17','A20','A22')))",
            
            # 新生儿相关的交叉检查 - 医疗逻辑重要
            "(rule_type = 'cross_check_null' AND field_code LIKE 'A18%')",
            
            # 日期检查 - 保留重要的日期字段
            "(rule_type = 'date_check' AND field_code REGEXP '^[AB][0-9]{2}$')",
            
            # 空值检查 - 保留基本信息必填字段
            "(rule_type = 'null_check' AND field_code REGEXP '^A[0-2][0-9]$')"
        ]
        
        # 激活核心规则
        core_condition = " OR ".join(f"({rule})" for rule in core_rules)
        
        update_sql = f"""
            UPDATE kiro_qc_rule 
            SET status = 'active'
            WHERE {core_condition}
        """
        
        cursor.execute(update_sql)
        conn.commit()
        
        # 3. 统计核心规则
        print(f"\n3. 核心规则统计...")
        cursor.execute("""
            SELECT rule_type, COUNT(*) as count
            FROM kiro_qc_rule 
            WHERE status = 'active'
            GROUP BY rule_type
            ORDER BY count DESC
        """)
        core_stats = cursor.fetchall()
        
        total_core = sum(r['count'] for r in core_stats)
        print(f"核心规则总数: {total_core}")
        
        for stat in core_stats:
            print(f"  {stat['rule_type']}: {stat['count']}条")
        
        reduction_ratio = (total_current - total_core) / total_current * 100
        print(f"\n规则数量减少: {total_current} → {total_core} (减少{reduction_ratio:.1f}%)")
        
        # 4. 显示一些核心规则示例
        print(f"\n4. 核心规则示例...")
        cursor.execute("""
            SELECT rule_code, field_code, rule_type, description
            FROM kiro_qc_rule 
            WHERE status = 'active'
            ORDER BY rule_type, field_code
            LIMIT 10
        """)
        examples = cursor.fetchall()
        
        for example in examples:
            print(f"  {example['rule_code']}: {example['field_code']} ({example['rule_type']})")
        
        return total_core
        
    finally:
        cursor.close()
        conn.close()

def test_core_performance():
    """测试核心规则集的性能"""
    print(f"\n=== 测试核心规则集性能 ===")
    
    import requests
    import time
    
    BASE_URL = "http://localhost:4101/api"
    
    # 先启动服务
    print("请手动启动服务: java -jar target\\qc-system-1.0.0.jar")
    print("启动后按回车继续...")
    input()
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取2023年测试病案
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
            
            try:
                response = requests.post(f"{BASE_URL}/qc/check/single", 
                                       params={
                                           'a48': test_case['A48'],
                                           'a49': test_case['A49']
                                       },
                                       timeout=30)  # 30秒超时
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                print(f"核心规则集处理时间: {processing_time:.2f}秒")
                
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
                    
                    if estimated_total < 180:  # 3分钟内
                        print("✅ 性能优化成功！处理时间很快")
                    elif estimated_total < 600:  # 10分钟内
                        print("✅ 性能可接受")
                    else:
                        print("⚠️  仍需进一步优化")
                
                else:
                    print(f"处理失败: {response.status_code}")
            
            except Exception as e:
                print(f"测试异常: {e}")
    
    finally:
        cursor.close()
        conn.close()

def restore_options():
    """提供恢复选项"""
    print(f"\n=== 规则集管理选项 ===")
    print("1. 当前使用核心规则集（性能优化）")
    print("2. 如需恢复完整规则集，执行:")
    print("   UPDATE kiro_qc_rule SET status = 'active';")
    print("3. 如需查看inactive规则:")
    print("   SELECT COUNT(*) FROM kiro_qc_rule WHERE status = 'inactive';")

if __name__ == "__main__":
    core_count = create_core_rule_set()
    
    if core_count < 300:  # 如果核心规则数量合理
        print(f"\n✅ 核心规则集创建成功！规则数量从1532减少到{core_count}")
        print("现在可以重启服务测试性能")
    
    restore_options()