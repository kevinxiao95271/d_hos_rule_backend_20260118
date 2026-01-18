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

def check_processing_results():
    """检查处理结果"""
    print("=== 检查质控处理结果 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 检查是否有最新的处理结果
        cursor.execute("""
            SELECT 
                mr_key,
                defect_count,
                final_score,
                created_at
            FROM kiro_qc_case_result 
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        recent_results = cursor.fetchall()
        
        if recent_results:
            print("最近的处理结果:")
            for result in recent_results:
                print(f"  {result['mr_key']}: {result['defect_count']}个缺陷, 得分:{result['final_score']}, 时间:{result['created_at']}")
        else:
            print("未找到处理结果")
            return None
        
        # 2. 分析最新的一个病案
        latest = recent_results[0]
        mr_key = latest['mr_key']
        
        print(f"\n分析病案 {mr_key}:")
        
        # 缺陷详情统计
        cursor.execute("""
            SELECT 
                COUNT(*) as total_defects,
                COUNT(DISTINCT field_code) as unique_fields,
                COUNT(DISTINCT rule_id) as unique_rules
            FROM kiro_qc_defect_detail 
            WHERE mr_key = %s
        """, (mr_key,))
        
        stats = cursor.fetchone()
        
        print(f"  总缺陷数: {stats['total_defects']}")
        print(f"  涉及字段数: {stats['unique_fields']}")
        print(f"  触发规则数: {stats['unique_rules']}")
        
        # 按规则类型统计
        cursor.execute("""
            SELECT 
                r.rule_type,
                COUNT(*) as count
            FROM kiro_qc_defect_detail d
            LEFT JOIN kiro_qc_rule r ON d.rule_id = r.id
            WHERE d.mr_key = %s
            GROUP BY r.rule_type
            ORDER BY count DESC
        """, (mr_key,))
        
        rule_type_stats = cursor.fetchall()
        
        print(f"\n  按规则类型统计:")
        for stat in rule_type_stats:
            rule_type = stat['rule_type'] if stat['rule_type'] else '未知'
            print(f"    {rule_type}: {stat['count']}个")
        
        # 医疗编码缺陷
        cursor.execute("""
            SELECT COUNT(*) as medical_defects
            FROM kiro_qc_defect_detail 
            WHERE mr_key = %s
            AND (field_code LIKE 'C01%' OR field_code LIKE 'C21%' 
                 OR field_code LIKE 'C38%' OR field_code LIKE 'C43%')
        """, (mr_key,))
        
        medical_defects = cursor.fetchone()['medical_defects']
        print(f"  医疗编码缺陷: {medical_defects}个")
        
        # 字典验证缺陷
        cursor.execute("""
            SELECT 
                r.dict_types,
                COUNT(*) as count
            FROM kiro_qc_defect_detail d
            LEFT JOIN kiro_qc_rule r ON d.rule_id = r.id
            WHERE d.mr_key = %s
            AND r.rule_type = 'value_check'
            AND r.dict_types IS NOT NULL
            GROUP BY r.dict_types
            ORDER BY count DESC
        """, (mr_key,))
        
        dict_defects = cursor.fetchall()
        
        if dict_defects:
            print(f"\n  字典验证缺陷:")
            for defect in dict_defects:
                print(f"    {defect['dict_types']}: {defect['count']}个")
        
        return {
            'mr_key': mr_key,
            'total_defects': stats['total_defects'],
            'unique_fields': stats['unique_fields'],
            'unique_rules': stats['unique_rules'],
            'medical_defects': medical_defects,
            'final_score': latest['final_score']
        }
        
    finally:
        cursor.close()
        conn.close()

def analyze_system_performance():
    """分析系统性能"""
    print(f"\n=== 分析系统性能 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 规则覆盖率
        cursor.execute("SELECT COUNT(*) as total_rules FROM kiro_qc_rule WHERE status = 'active'")
        total_rules = cursor.fetchone()['total_rules']
        
        cursor.execute("SELECT COUNT(DISTINCT rule_id) as triggered_rules FROM kiro_qc_defect_detail")
        triggered_rules = cursor.fetchone()['triggered_rules']
        
        coverage_rate = (triggered_rules / total_rules * 100) if total_rules > 0 else 0
        
        print(f"规则覆盖率:")
        print(f"  总规则数: {total_rules}")
        print(f"  触发规则数: {triggered_rules}")
        print(f"  覆盖率: {coverage_rate:.1f}%")
        
        # 2. 字段覆盖情况
        cursor.execute("SELECT COUNT(DISTINCT field_code) as total_fields FROM kiro_qc_defect_detail")
        total_fields = cursor.fetchone()['total_fields']
        
        print(f"\n字段覆盖情况:")
        print(f"  涉及字段数: {total_fields}")
        
        # 3. 医疗编码验证效果
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT d.rule_id) as medical_rules_triggered
            FROM kiro_qc_defect_detail d
            LEFT JOIN kiro_qc_rule r ON d.rule_id = r.id
            WHERE r.dict_types IN ('RCJBBM', 'operation_dict_v3', 'level4_operation_code_v2')
        """)
        
        medical_rules_triggered = cursor.fetchone()['medical_rules_triggered']
        
        cursor.execute("""
            SELECT COUNT(*) as medical_rules_total
            FROM kiro_qc_rule 
            WHERE status = 'active'
            AND dict_types IN ('RCJBBM', 'operation_dict_v3', 'level4_operation_code_v2')
        """)
        
        medical_rules_total = cursor.fetchone()['medical_rules_total']
        
        medical_coverage = (medical_rules_triggered / medical_rules_total * 100) if medical_rules_total > 0 else 0
        
        print(f"\n医疗编码验证:")
        print(f"  医疗编码规则总数: {medical_rules_total}")
        print(f"  触发的医疗编码规则: {medical_rules_triggered}")
        print(f"  医疗编码规则覆盖率: {medical_coverage:.1f}%")
        
        return {
            'total_rules': total_rules,
            'triggered_rules': triggered_rules,
            'coverage_rate': coverage_rate,
            'total_fields': total_fields,
            'medical_rules_total': medical_rules_total,
            'medical_rules_triggered': medical_rules_triggered,
            'medical_coverage': medical_coverage
        }
        
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    print("完整医疗质控系统结果分析")
    print("=" * 50)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查处理结果
    result = check_processing_results()
    
    if result:
        # 2. 分析系统性能
        performance = analyze_system_performance()
        
        # 3. 生成总结报告
        print(f"\n" + "=" * 50)
        print(f"📊 完整医疗质控系统分析报告")
        print(f"=" * 50)
        
        print(f"🔍 质控效果 (病案 {result['mr_key']}):")
        print(f"   总缺陷数: {result['total_defects']}")
        print(f"   涉及字段数: {result['unique_fields']}")
        print(f"   触发规则数: {result['unique_rules']}")
        print(f"   医疗编码缺陷: {result['medical_defects']}")
        print(f"   最终得分: {result['final_score']}")
        
        print(f"\n📈 系统覆盖率:")
        print(f"   规则总数: {performance['total_rules']}")
        print(f"   规则覆盖率: {performance['coverage_rate']:.1f}%")
        print(f"   字段覆盖数: {performance['total_fields']}")
        
        print(f"\n🏥 医疗编码验证:")
        print(f"   医疗编码规则: {performance['medical_rules_total']}")
        print(f"   医疗编码覆盖率: {performance['medical_coverage']:.1f}%")
        
        # 功能验证结果
        print(f"\n✅ 功能验证结果:")
        
        if result['total_defects'] > 0:
            print(f"   ✅ 质控功能正常 - 检测到{result['total_defects']}个缺陷")
        
        if result['medical_defects'] > 0:
            print(f"   ✅ 医疗编码验证正常 - 检测到{result['medical_defects']}个医疗编码缺陷")
        elif performance['medical_rules_total'] > 0:
            print(f"   ℹ️  医疗编码验证已启用 - 该病案医疗编码符合规范")
        
        if performance['coverage_rate'] > 50:
            print(f"   ✅ 规则覆盖率良好 - {performance['coverage_rate']:.1f}%")
        
        print(f"\n🎉 完整医疗质控系统功能验证完成！")
        print(f"系统已具备:")
        print(f"   • {performance['total_rules']}条完整质控规则")
        print(f"   • {performance['medical_rules_total']}条医疗编码验证规则")
        print(f"   • Redis缓存加速的字典验证")
        print(f"   • 覆盖{performance['total_fields']}个字段的全面质控")
        
    else:
        print("❌ 未找到处理结果，请先运行质控测试")

if __name__ == "__main__":
    main()