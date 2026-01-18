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

def debug_single_case_scoring():
    """调试单个病案的计分"""
    print("=== 调试单个病案计分 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 选择一个病案进行详细分析
        cursor.execute("""
            SELECT mr_key, defect_count, total_deduct, final_score
            FROM kiro_qc_case_result 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
            ORDER BY defect_count DESC
            LIMIT 1
        """)
        
        case = cursor.fetchone()
        mr_key = case['mr_key']
        
        print(f"分析病案: {mr_key}")
        print(f"缺陷数: {case['defect_count']}")
        print(f"总扣分: {case['total_deduct']}")
        print(f"最终得分: {case['final_score']}")
        
        # 查看该病案的缺陷明细
        cursor.execute("""
            SELECT 
                d.rule_id,
                d.rule_code,
                d.field_code,
                d.deduct_score as detail_deduct,
                r.deduct_score as rule_deduct
            FROM kiro_qc_defect_detail d
            LEFT JOIN kiro_qc_rule r ON d.rule_id = r.id
            WHERE d.mr_key = %s
            ORDER BY d.deduct_score DESC
            LIMIT 10
        """, (mr_key,))
        
        defects = cursor.fetchall()
        
        print(f"\n缺陷明细（前10条）:")
        manual_total = 0
        for defect in defects:
            detail_deduct = float(defect['detail_deduct'])
            rule_deduct = float(defect['rule_deduct']) if defect['rule_deduct'] else 0
            manual_total += rule_deduct
            
            print(f"  规则{defect['rule_id']}: 字段{defect['field_code']}")
            print(f"    明细扣分: {detail_deduct}, 规则扣分: {rule_deduct}")
        
        # 计算所有缺陷的总扣分
        cursor.execute("""
            SELECT 
                COUNT(*) as total_defects,
                SUM(d.deduct_score) as detail_total,
                SUM(r.deduct_score) as rule_total
            FROM kiro_qc_defect_detail d
            LEFT JOIN kiro_qc_rule r ON d.rule_id = r.id
            WHERE d.mr_key = %s
        """, (mr_key,))
        
        totals = cursor.fetchone()
        
        print(f"\n总计算:")
        print(f"  总缺陷数: {totals['total_defects']}")
        print(f"  明细表总扣分: {totals['detail_total']}")
        print(f"  规则表总扣分: {totals['rule_total']}")
        
        # 手动计算最终得分
        rule_total = float(totals['rule_total']) if totals['rule_total'] else 0
        manual_final_score = max(0, 100 - rule_total)
        
        print(f"\n手动计算:")
        print(f"  100 - {rule_total} = {manual_final_score}")
        print(f"  数据库中的得分: {case['final_score']}")
        
        if rule_total > 100:
            print(f"  ❌ 问题：总扣分({rule_total})超过100分，导致得分为0")
            print(f"  建议：调整扣分标准或计分逻辑")
        
        return {
            'mr_key': mr_key,
            'total_defects': totals['total_defects'],
            'rule_total': rule_total,
            'manual_final_score': manual_final_score,
            'db_final_score': float(case['final_score'])
        }
        
    finally:
        cursor.close()
        conn.close()

def analyze_scoring_distribution():
    """分析扣分分布"""
    print("\n=== 分析扣分分布 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 统计每个病案的扣分情况
        cursor.execute("""
            SELECT 
                d.mr_key,
                COUNT(*) as defect_count,
                SUM(r.deduct_score) as total_deduct,
                100 - SUM(r.deduct_score) as calculated_score
            FROM kiro_qc_defect_detail d
            LEFT JOIN kiro_qc_rule r ON d.rule_id = r.id
            WHERE d.mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
            GROUP BY d.mr_key
            ORDER BY total_deduct DESC
            LIMIT 10
        """)
        
        cases = cursor.fetchall()
        
        print("病案扣分排行（前10）:")
        over_100_count = 0
        
        for case in cases:
            mr_key = case['mr_key']
            defect_count = case['defect_count']
            total_deduct = float(case['total_deduct']) if case['total_deduct'] else 0
            calculated_score = float(case['calculated_score']) if case['calculated_score'] else 0
            
            if total_deduct > 100:
                over_100_count += 1
                status = "❌ 超标"
            else:
                status = "✅ 正常"
            
            print(f"  {mr_key}: {defect_count}缺陷, 扣{total_deduct:.1f}分, 得分{max(0, calculated_score):.1f} {status}")
        
        # 统计总体情况
        cursor.execute("""
            SELECT 
                COUNT(*) as total_cases,
                AVG(total_deduct) as avg_deduct,
                MAX(total_deduct) as max_deduct,
                MIN(total_deduct) as min_deduct,
                SUM(CASE WHEN total_deduct > 100 THEN 1 ELSE 0 END) as over_100_cases
            FROM (
                SELECT 
                    d.mr_key,
                    SUM(r.deduct_score) as total_deduct
                FROM kiro_qc_defect_detail d
                LEFT JOIN kiro_qc_rule r ON d.rule_id = r.id
                WHERE d.mr_key IN (
                    SELECT CONCAT(A48, '_', A49) 
                    FROM d_mr 
                    WHERE B15 LIKE '2023/%'
                )
                GROUP BY d.mr_key
            ) t
        """)
        
        stats = cursor.fetchone()
        
        print(f"\n总体统计:")
        print(f"  总病案数: {stats['total_cases']}")
        print(f"  平均扣分: {stats['avg_deduct']:.1f}")
        print(f"  最高扣分: {stats['max_deduct']:.1f}")
        print(f"  最低扣分: {stats['min_deduct']:.1f}")
        print(f"  超100分病案: {stats['over_100_cases']} ({stats['over_100_cases']/stats['total_cases']*100:.1f}%)")
        
        return stats
        
    finally:
        cursor.close()
        conn.close()

def suggest_scoring_fix():
    """建议计分修复方案"""
    print("\n=== 建议计分修复方案 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 分析规则扣分分布
        cursor.execute("""
            SELECT 
                deduct_score,
                COUNT(*) as rule_count
            FROM kiro_qc_rule 
            WHERE status = 'active'
            GROUP BY deduct_score
            ORDER BY deduct_score DESC
        """)
        
        rule_stats = cursor.fetchall()
        
        print("当前规则扣分分布:")
        total_rules = 0
        high_score_rules = 0
        
        for stat in rule_stats:
            deduct_score = float(stat['deduct_score'])
            rule_count = stat['rule_count']
            total_rules += rule_count
            
            if deduct_score >= 2.0:
                high_score_rules += rule_count
            
            print(f"  扣分 {deduct_score}: {rule_count}条规则")
        
        print(f"\n高扣分规则(≥2分): {high_score_rules}/{total_rules} ({high_score_rules/total_rules*100:.1f}%)")
        
        # 建议方案
        print(f"\n💡 修复建议:")
        
        if high_score_rules > total_rules * 0.1:  # 超过10%的规则扣分≥2
            print(f"1. 降低扣分标准:")
            print(f"   • 将4分规则降为1分")
            print(f"   • 将2分规则降为0.5分")
            print(f"   • 将1分规则降为0.2分")
            print(f"   • 保持0.5分规则不变")
        
        print(f"2. 调整计分逻辑:")
        print(f"   • 设置最大扣分上限（如50分）")
        print(f"   • 使用加权扣分（重要规则权重高）")
        print(f"   • 按缺陷类型分类计分")
        
        print(f"3. 分级质控:")
        print(f"   • A级缺陷：严重问题，扣分较多")
        print(f"   • B级缺陷：一般问题，扣分适中")
        print(f"   • C级缺陷：轻微问题，扣分较少")
        
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    print("调试质控计分问题")
    print("=" * 40)
    print(f"调试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 调试单个病案
    case_result = debug_single_case_scoring()
    
    # 2. 分析扣分分布
    stats = analyze_scoring_distribution()
    
    # 3. 建议修复方案
    suggest_scoring_fix()
    
    print(f"\n" + "=" * 40)
    print("🔍 问题诊断结果")
    print("=" * 40)
    
    print(f"核心问题：")
    if case_result['rule_total'] > 100:
        print(f"  ❌ 单个病案扣分过高（{case_result['rule_total']:.1f}分）")
        print(f"  ❌ 平均扣分{stats['avg_deduct']:.1f}分，远超100分上限")
        print(f"  ❌ {stats['over_100_cases']}/{stats['total_cases']}个病案扣分超100分")
    
    print(f"\n解决方案：")
    print(f"  1. 立即方案：降低所有规则扣分（除以5或10）")
    print(f"  2. 长期方案：重新设计扣分标准和计分逻辑")
    print(f"  3. 业务方案：与医院确认合理的扣分标准")

if __name__ == "__main__":
    main()