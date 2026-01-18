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

def diagnose_scoring_issue():
    """诊断计分问题"""
    print("=== 诊断质控计分问题 ===")
    print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 检查规则的扣分设置
        print("\n1. 检查规则扣分设置:")
        cursor.execute("""
            SELECT 
                deduct_score,
                COUNT(*) as rule_count
            FROM kiro_qc_rule 
            WHERE status = 'active'
            GROUP BY deduct_score
            ORDER BY deduct_score DESC
        """)
        
        deduct_stats = cursor.fetchall()
        
        print("扣分分布:")
        total_rules = 0
        zero_score_rules = 0
        
        for stat in deduct_stats:
            deduct_score = float(stat['deduct_score'])
            rule_count = stat['rule_count']
            total_rules += rule_count
            
            if deduct_score == 0:
                zero_score_rules = rule_count
            
            print(f"  扣分 {deduct_score}: {rule_count}条规则")
        
        print(f"\n总规则数: {total_rules}")
        print(f"零扣分规则: {zero_score_rules} ({zero_score_rules/total_rules*100:.1f}%)")
        
        # 2. 检查缺陷明细中的扣分
        print("\n2. 检查缺陷明细扣分:")
        cursor.execute("""
            SELECT 
                deduct_score,
                COUNT(*) as defect_count
            FROM kiro_qc_defect_detail 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
            GROUP BY deduct_score
            ORDER BY deduct_score DESC
            LIMIT 10
        """)
        
        defect_deduct_stats = cursor.fetchall()
        
        print("缺陷扣分分布:")
        total_defects = 0
        zero_deduct_defects = 0
        
        for stat in defect_deduct_stats:
            deduct_score = float(stat['deduct_score'])
            defect_count = stat['defect_count']
            total_defects += defect_count
            
            if deduct_score == 0:
                zero_deduct_defects = defect_count
            
            print(f"  扣分 {deduct_score}: {defect_count}个缺陷")
        
        print(f"\n总缺陷数: {total_defects}")
        print(f"零扣分缺陷: {zero_deduct_defects} ({zero_deduct_defects/total_defects*100:.1f}%)")
        
        # 3. 检查病案结果表的计分
        print("\n3. 检查病案结果计分:")
        cursor.execute("""
            SELECT 
                mr_key,
                defect_count,
                total_deduct,
                final_score
            FROM kiro_qc_case_result 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
            ORDER BY defect_count DESC
            LIMIT 5
        """)
        
        case_results = cursor.fetchall()
        
        print("病案计分详情:")
        for result in case_results:
            mr_key = result['mr_key']
            defect_count = result['defect_count']
            total_deduct = float(result['total_deduct'])
            final_score = float(result['final_score'])
            
            print(f"  {mr_key}: {defect_count}缺陷, 总扣分:{total_deduct}, 最终得分:{final_score}")
        
        # 4. 手动计算一个病案的扣分
        if case_results:
            sample_mr_key = case_results[0]['mr_key']
            print(f"\n4. 手动验证病案 {sample_mr_key} 的计分:")
            
            cursor.execute("""
                SELECT 
                    rule_id,
                    rule_code,
                    field_code,
                    deduct_score
                FROM kiro_qc_defect_detail 
                WHERE mr_key = %s
                ORDER BY deduct_score DESC
                LIMIT 10
            """, (sample_mr_key,))
            
            sample_defects = cursor.fetchall()
            
            manual_total_deduct = 0
            print("缺陷扣分明细:")
            
            for defect in sample_defects:
                deduct_score = float(defect['deduct_score'])
                manual_total_deduct += deduct_score
                
                print(f"    规则{defect['rule_id']} ({defect['rule_code']}): 字段{defect['field_code']}, 扣分{deduct_score}")
            
            print(f"\n手动计算总扣分: {manual_total_deduct}")
            
            # 计算应该的最终得分
            expected_final_score = max(0, 100 - manual_total_deduct)
            actual_final_score = case_results[0]['final_score']
            
            print(f"预期最终得分: {expected_final_score}")
            print(f"实际最终得分: {actual_final_score}")
            
            if abs(expected_final_score - actual_final_score) > 0.01:
                print("❌ 计分逻辑有问题！")
            else:
                print("✅ 计分逻辑正确")
        
        # 5. 检查规则引擎的计分逻辑
        print("\n5. 分析计分问题原因:")
        
        if zero_score_rules > total_rules * 0.8:
            print("❌ 主要问题：大部分规则扣分为0")
            print("   建议：检查规则导入时的扣分设置")
        
        if zero_deduct_defects > total_defects * 0.8:
            print("❌ 主要问题：缺陷明细中扣分为0")
            print("   建议：检查规则引擎计分逻辑")
        
        # 6. 检查具体的规则类型扣分
        print("\n6. 按规则类型检查扣分:")
        cursor.execute("""
            SELECT 
                r.rule_type,
                AVG(r.deduct_score) as avg_deduct,
                COUNT(*) as rule_count,
                SUM(CASE WHEN r.deduct_score = 0 THEN 1 ELSE 0 END) as zero_count
            FROM kiro_qc_rule r
            WHERE r.status = 'active'
            GROUP BY r.rule_type
            ORDER BY avg_deduct DESC
        """)
        
        rule_type_stats = cursor.fetchall()
        
        print("规则类型扣分统计:")
        for stat in rule_type_stats:
            rule_type = stat['rule_type']
            avg_deduct = float(stat['avg_deduct'])
            rule_count = stat['rule_count']
            zero_count = stat['zero_count']
            zero_rate = zero_count / rule_count * 100
            
            print(f"  {rule_type}: 平均扣分{avg_deduct:.2f}, {rule_count}条规则, {zero_count}条零扣分({zero_rate:.1f}%)")
        
        return {
            'total_rules': total_rules,
            'zero_score_rules': zero_score_rules,
            'total_defects': total_defects,
            'zero_deduct_defects': zero_deduct_defects
        }
        
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    print("质控计分问题诊断")
    print("=" * 40)
    
    result = diagnose_scoring_issue()
    
    print(f"\n" + "=" * 40)
    print("📊 诊断总结")
    print("=" * 40)
    
    print(f"规则扣分问题:")
    print(f"  总规则数: {result['total_rules']}")
    print(f"  零扣分规则: {result['zero_score_rules']} ({result['zero_score_rules']/result['total_rules']*100:.1f}%)")
    
    print(f"\n缺陷扣分问题:")
    print(f"  总缺陷数: {result['total_defects']}")
    print(f"  零扣分缺陷: {result['zero_deduct_defects']} ({result['zero_deduct_defects']/result['total_defects']*100:.1f}%)")
    
    # 判断主要问题
    if result['zero_score_rules'] > result['total_rules'] * 0.8:
        print(f"\n🔍 主要问题：规则扣分设置问题")
        print(f"   大部分规则的扣分为0，需要修复规则表中的deduct_score字段")
    elif result['zero_deduct_defects'] > result['total_defects'] * 0.8:
        print(f"\n🔍 主要问题：规则引擎计分逻辑问题")
        print(f"   规则扣分正常，但缺陷明细中扣分为0，需要检查RuleEngineService")
    else:
        print(f"\n🔍 问题复杂：需要进一步分析")

if __name__ == "__main__":
    main()