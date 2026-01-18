#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
from datetime import datetime

# 数据库连接配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def analyze_negative_scores():
    """分析负扣分规则"""
    print("=== 分析负扣分规则 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 查看负扣分规则的详情
        cursor.execute("""
            SELECT 
                rule_code,
                field_code,
                rule_type,
                deduct_score,
                description
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            AND deduct_score < 0
            ORDER BY deduct_score ASC
            LIMIT 10
        """)
        
        negative_rules = cursor.fetchall()
        
        print("负扣分规则示例:")
        for rule in negative_rules:
            print(f"  {rule['rule_code']}: {rule['field_code']}, 扣分{rule['deduct_score']}, 类型{rule['rule_type']}")
            if rule['description']:
                desc = rule['description'][:50] + "..." if len(rule['description']) > 50 else rule['description']
                print(f"    描述: {desc}")
        
        # 统计负扣分规则数量
        cursor.execute("""
            SELECT 
                deduct_score,
                COUNT(*) as count
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            AND deduct_score < 0
            GROUP BY deduct_score
            ORDER BY deduct_score ASC
        """)
        
        negative_stats = cursor.fetchall()
        
        print(f"\n负扣分统计:")
        total_negative = 0
        for stat in negative_stats:
            count = stat['count']
            total_negative += count
            print(f"  扣分 {stat['deduct_score']}: {count}条规则")
        
        print(f"总负扣分规则数: {total_negative}")
        
        return total_negative
        
    finally:
        cursor.close()
        conn.close()

def fix_deduct_scores():
    """修复扣分设置"""
    print("\n=== 修复扣分设置 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 方案1：将所有负扣分转为正扣分
        print("1. 将负扣分转为正扣分...")
        
        cursor.execute("""
            UPDATE kiro_qc_rule 
            SET deduct_score = ABS(deduct_score)
            WHERE status = 'active' 
            AND deduct_score < 0
        """)
        
        updated_count = cursor.rowcount
        conn.commit()
        
        print(f"✅ 已修复 {updated_count} 条规则的扣分")
        
        # 验证修复结果
        cursor.execute("""
            SELECT 
                deduct_score,
                COUNT(*) as count
            FROM kiro_qc_rule 
            WHERE status = 'active'
            GROUP BY deduct_score
            ORDER BY deduct_score DESC
        """)
        
        fixed_stats = cursor.fetchall()
        
        print(f"\n修复后扣分分布:")
        for stat in fixed_stats:
            print(f"  扣分 {stat['deduct_score']}: {stat['count']}条规则")
        
        return updated_count
        
    finally:
        cursor.close()
        conn.close()

def recalculate_case_scores():
    """重新计算病案得分"""
    print("\n=== 重新计算病案得分 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取2023年所有病案
        cursor.execute("""
            SELECT DISTINCT mr_key
            FROM kiro_qc_case_result 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
        """)
        
        case_keys = [row['mr_key'] for row in cursor.fetchall()]
        
        print(f"需要重新计算 {len(case_keys)} 个病案的得分")
        
        updated_cases = 0
        
        for mr_key in case_keys:
            # 重新计算该病案的总扣分
            cursor.execute("""
                SELECT 
                    COUNT(*) as defect_count,
                    COALESCE(SUM(r.deduct_score), 0) as total_deduct
                FROM kiro_qc_defect_detail d
                LEFT JOIN kiro_qc_rule r ON d.rule_id = r.id
                WHERE d.mr_key = %s
            """, (mr_key,))
            
            result = cursor.fetchone()
            defect_count = result['defect_count']
            total_deduct = float(result['total_deduct'])
            
            # 计算最终得分
            final_score = max(0, 100 - total_deduct)
            
            # 更新病案结果
            cursor.execute("""
                UPDATE kiro_qc_case_result 
                SET 
                    defect_count = %s,
                    total_deduct = %s,
                    final_score = %s,
                    check_time = NOW()
                WHERE mr_key = %s
            """, (defect_count, total_deduct, final_score, mr_key))
            
            updated_cases += 1
            
            if updated_cases % 10 == 0:
                print(f"  已更新 {updated_cases}/{len(case_keys)} 个病案")
        
        conn.commit()
        
        print(f"✅ 已重新计算 {updated_cases} 个病案的得分")
        
        # 验证修复结果
        cursor.execute("""
            SELECT 
                COUNT(*) as total_cases,
                AVG(final_score) as avg_score,
                MIN(final_score) as min_score,
                MAX(final_score) as max_score,
                SUM(CASE WHEN final_score = 0 THEN 1 ELSE 0 END) as zero_score_cases
            FROM kiro_qc_case_result 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
        """)
        
        stats = cursor.fetchone()
        
        print(f"\n修复后得分统计:")
        print(f"  总病案数: {stats['total_cases']}")
        print(f"  平均得分: {stats['avg_score']:.2f}")
        print(f"  最低得分: {stats['min_score']:.2f}")
        print(f"  最高得分: {stats['max_score']:.2f}")
        print(f"  零分病案: {stats['zero_score_cases']}")
        
        return stats
        
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    print("修复质控计分逻辑")
    print("=" * 40)
    print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 分析负扣分问题
    negative_count = analyze_negative_scores()
    
    if negative_count > 0:
        print(f"\n发现 {negative_count} 条负扣分规则，这可能是导致计分错误的原因")
        
        # 2. 修复扣分设置
        fixed_count = fix_deduct_scores()
        
        if fixed_count > 0:
            # 3. 重新计算病案得分
            stats = recalculate_case_scores()
            
            print(f"\n" + "=" * 40)
            print("🎉 计分逻辑修复完成！")
            print("=" * 40)
            
            print(f"修复内容:")
            print(f"  • 修复了 {fixed_count} 条负扣分规则")
            print(f"  • 重新计算了 {stats['total_cases']} 个病案得分")
            print(f"  • 平均得分从 0.0 提升到 {stats['avg_score']:.2f}")
            
            if stats['zero_score_cases'] == 0:
                print(f"  ✅ 所有病案都有合理得分")
            else:
                print(f"  ⚠️  仍有 {stats['zero_score_cases']} 个病案得分为0（可能缺陷过多）")
        
    else:
        print(f"\n未发现负扣分规则，问题可能在其他地方")

if __name__ == "__main__":
    main()