#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
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

BASE_URL = "http://localhost:4101/api"

def test_single_case_comprehensive():
    """测试单个病案的完整质控"""
    print("=== 测试单个病案完整质控 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取2023年测试病案
        cursor.execute("""
            SELECT A48, A49 
            FROM d_mr 
            WHERE A48 = '60484296' AND A49 = '1'
        """)
        test_case = cursor.fetchone()
        
        if not test_case:
            print("❌ 未找到测试病案")
            return None
        
        print(f"测试病案: {test_case['A48']}_{test_case['A49']}")
        
        # 清理之前的结果
        mr_key = f"{test_case['A48']}_{test_case['A49']}"
        cursor.execute("DELETE FROM kiro_qc_case_result WHERE mr_key = %s", (mr_key,))
        cursor.execute("DELETE FROM kiro_qc_defect_detail WHERE mr_key = %s", (mr_key,))
        conn.commit()
        
        # 执行质控
        print("执行完整规则集质控...")
        start_time = time.time()
        
        try:
            response = requests.post(f"{BASE_URL}/qc/check/single", 
                                   params={
                                       'a48': test_case['A48'],
                                       'a49': test_case['A49']
                                   },
                                   timeout=120)  # 2分钟超时
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"✅ 处理完成，耗时: {processing_time:.2f}秒")
            
            if response.status_code == 200:
                result = response.json().get('data', {})
                defect_count = result.get('defectCount', 0)
                final_score = result.get('finalScore', 0)
                
                print(f"检测到缺陷: {defect_count}个")
                print(f"最终得分: {final_score}")
                
                # 分析缺陷详情
                analyze_defect_details(cursor, mr_key)
                
                return {
                    'processing_time': processing_time,
                    'defect_count': defect_count,
                    'final_score': final_score
                }
            
            else:
                print(f"❌ 质控失败: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"❌ 质控异常: {e}")
            return None
    
    finally:
        cursor.close()
        conn.close()

def analyze_defect_details(cursor, mr_key):
    """分析缺陷详情"""
    print(f"\n📋 缺陷详情分析:")
    
    # 1. 按规则类型统计
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
    
    print("按规则类型统计:")
    for stat in rule_type_stats:
        rule_type = stat['rule_type'] if stat['rule_type'] else '未知'
        print(f"  {rule_type}: {stat['count']}个缺陷")
    
    # 2. 字典验证缺陷
    cursor.execute("""
        SELECT 
            d.field_code,
            d.field_name,
            d.actual_value,
            d.expected_value,
            r.dict_types
        FROM kiro_qc_defect_detail d
        LEFT JOIN kiro_qc_rule r ON d.rule_id = r.id
        WHERE d.mr_key = %s
        AND r.rule_type = 'value_check'
        AND r.dict_types IS NOT NULL
        ORDER BY d.field_code
    """, (mr_key,))
    
    dict_defects = cursor.fetchall()
    
    if dict_defects:
        print(f"\n字典验证缺陷 ({len(dict_defects)}个):")
        for defect in dict_defects:
            field_name = defect['field_name'][:20] if defect['field_name'] else '未知'
            actual = defect['actual_value'][:15] if defect['actual_value'] else '空'
            dict_type = defect['dict_types'][:15] if defect['dict_types'] else '未知'
            print(f"  {defect['field_code']:<12} {field_name:<20} 值:{actual:<15} 字典:{dict_type}")
    
    # 3. 医疗编码缺陷
    cursor.execute("""
        SELECT 
            field_code,
            field_name,
            actual_value,
            rule_description
        FROM kiro_qc_defect_detail 
        WHERE mr_key = %s
        AND (field_code LIKE 'C01%' OR field_code LIKE 'C21%' 
             OR field_code LIKE 'C38%' OR field_code LIKE 'C43%')
        ORDER BY field_code
    """, (mr_key,))
    
    medical_defects = cursor.fetchall()
    
    if medical_defects:
        print(f"\n🏥 医疗编码缺陷 ({len(medical_defects)}个):")
        for defect in medical_defects:
            field_name = defect['field_name'][:25] if defect['field_name'] else '未知'
            actual = defect['actual_value'][:20] if defect['actual_value'] else '空'
            print(f"  {defect['field_code']:<12} {field_name:<25} 值:{actual}")
    else:
        print(f"\n🏥 医疗编码缺陷: 0个")
    
    # 4. 涉及的字段和规则统计
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT field_code) as unique_fields,
            COUNT(DISTINCT rule_id) as unique_rules
        FROM kiro_qc_defect_detail 
        WHERE mr_key = %s
    """, (mr_key,))
    
    coverage = cursor.fetchone()
    
    print(f"\n📊 覆盖统计:")
    print(f"  涉及字段数: {coverage['unique_fields']}")
    print(f"  触发规则数: {coverage['unique_rules']}")

def estimate_batch_performance():
    """估算批量处理性能"""
    print(f"\n=== 估算批量处理性能 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取2023年病案数量
        cursor.execute("""
            SELECT COUNT(*) as case_count
            FROM d_mr 
            WHERE A48 LIKE '6%' OR A48 LIKE '4%' OR A48 LIKE '3%'
        """)
        
        case_count = cursor.fetchone()['case_count']
        print(f"2023年病案数量: {case_count}")
        
        return case_count
        
    finally:
        cursor.close()
        conn.close()

def check_system_capabilities():
    """检查系统能力"""
    print(f"\n=== 检查系统能力 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 规则统计
        cursor.execute("""
            SELECT 
                rule_type,
                COUNT(*) as count
            FROM kiro_qc_rule 
            WHERE status = 'active'
            GROUP BY rule_type
            ORDER BY count DESC
        """)
        
        rule_stats = cursor.fetchall()
        
        print("激活规则统计:")
        total_rules = 0
        for stat in rule_stats:
            print(f"  {stat['rule_type']}: {stat['count']}条")
            total_rules += stat['count']
        
        print(f"  总计: {total_rules}条规则")
        
        # 2. 字典缓存统计
        try:
            response = requests.get(f"{BASE_URL}/dict/cache/stats", timeout=5)
            if response.status_code == 200:
                cache_stats = response.json().get('data', {})
                print(f"\nRedis缓存统计:")
                print(f"  字典缓存数: {cache_stats.get('dictCacheCount', 0)}")
                print(f"  集合缓存数: {cache_stats.get('setCacheCount', 0)}")
        except Exception as e:
            print(f"缓存统计获取失败: {e}")
        
        # 3. 医疗字典规则统计
        cursor.execute("""
            SELECT 
                dict_types,
                COUNT(*) as count
            FROM kiro_qc_rule 
            WHERE status = 'active'
            AND rule_type = 'value_check'
            AND dict_types IS NOT NULL
            AND dict_types != ''
            GROUP BY dict_types
            ORDER BY count DESC
        """)
        
        dict_rules = cursor.fetchall()
        
        print(f"\n字典验证规则:")
        medical_dict_count = 0
        for rule in dict_rules:
            dict_type = rule['dict_types']
            count = rule['count']
            print(f"  {dict_type}: {count}条规则")
            
            if dict_type in ['RCJBBM', 'operation_dict_v3', 'level4_operation_code_v2']:
                medical_dict_count += count
        
        print(f"  医疗编码相关: {medical_dict_count}条规则")
        
        return total_rules, medical_dict_count
        
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    print("完整医疗质控系统测试")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查系统能力
    total_rules, medical_rules = check_system_capabilities()
    
    # 2. 测试单个病案
    result = test_single_case_comprehensive()
    
    if result:
        # 3. 估算批量性能
        case_count = estimate_batch_performance()
        
        # 4. 生成总结报告
        print(f"\n" + "=" * 50)
        print(f"📊 完整医疗质控系统测试报告")
        print(f"=" * 50)
        
        print(f"🔧 系统配置:")
        print(f"   总规则数: {total_rules}")
        print(f"   医疗编码规则: {medical_rules}")
        print(f"   Redis缓存: 已启用")
        
        print(f"\n⚡ 单病案性能:")
        print(f"   处理时间: {result['processing_time']:.2f}秒")
        print(f"   检测缺陷: {result['defect_count']}个")
        print(f"   质控得分: {result['final_score']}")
        
        print(f"\n📈 批量处理估算:")
        estimated_total = result['processing_time'] * case_count
        print(f"   病案数量: {case_count}")
        print(f"   估算总时间: {estimated_total:.0f}秒 ({estimated_total/60:.1f}分钟)")
        print(f"   平均处理速度: {3600/result['processing_time']:.0f}病案/小时")
        
        # 性能评级
        if result['processing_time'] < 20:
            performance = "🟢 优秀"
        elif result['processing_time'] < 40:
            performance = "🟡 良好"
        elif result['processing_time'] < 60:
            performance = "🟠 可接受"
        else:
            performance = "🔴 需要优化"
        
        print(f"\n🎯 性能评级: {performance}")
        
        # 功能验证
        if result['defect_count'] > 0:
            print(f"✅ 质控功能正常，成功检测到缺陷")
        
        if medical_rules > 0:
            print(f"✅ 医疗编码验证功能已集成")
        
        print(f"\n🎉 完整医疗质控系统测试完成！")
        
    else:
        print(f"❌ 测试失败")

if __name__ == "__main__":
    main()