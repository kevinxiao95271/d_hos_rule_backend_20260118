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

def get_sample_cases(year, limit=10):
    """获取指定年份的样本病案"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 查询指定年份的病案，按时间排序取前N条
        query = f"""
        SELECT CONCAT(A48, '_', A49) as mr_key, A49 as mr_no, A02 as pat_name, B15 as in_date, B16 as out_date
        FROM d_mr 
        WHERE B15 LIKE '{year}/%'
        ORDER BY B15 
        LIMIT {limit}
        """
        
        cursor.execute(query)
        cases = cursor.fetchall()
        
        print(f"📋 找到 {len(cases)} 个{year}年的样本病案:")
        for i, case in enumerate(cases, 1):
            in_date = case['in_date'] if case['in_date'] else '未知'
            out_date = case['out_date'] if case['out_date'] else '未知'
            pat_name = case['pat_name'][:3] + '***' if case['pat_name'] else '未知'
            print(f"  {i:2d}. {case['mr_key']} | {case['mr_no']} | {pat_name} | {in_date} ~ {out_date}")
        
        return [case['mr_key'] for case in cases]
        
    finally:
        cursor.close()
        conn.close()

def clean_test_results(mr_keys):
    """清理测试病案的质控结果"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        if mr_keys:
            # 构建IN条件
            placeholders = ','.join(['%s'] * len(mr_keys))
            
            # 删除质控结果
            cursor.execute(f"DELETE FROM kiro_qc_case_result WHERE mr_key IN ({placeholders})", mr_keys)
            result_count = cursor.rowcount
            
            cursor.execute(f"DELETE FROM kiro_qc_defect_detail WHERE mr_key IN ({placeholders})", mr_keys)
            detail_count = cursor.rowcount
            
            conn.commit()
            print(f"✅ 清理完成: {result_count}个病案结果, {detail_count}个缺陷详情")
        
    except Exception as e:
        print(f"⚠️  清理警告: {e}")
    
    finally:
        cursor.close()
        conn.close()

def test_single_case(mr_key):
    """测试单个病案"""
    try:
        response = requests.post(f"{BASE_URL}/qc/check/single", 
                               json={"mrKey": mr_key},
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json().get('data', {})
            defect_count = result.get('defectCount', 0)
            final_score = result.get('finalScore', 0)
            
            return True, defect_count, final_score
        else:
            print(f"❌ 病案 {mr_key} 质控失败: {response.status_code}")
            return False, 0, 0
    
    except Exception as e:
        print(f"❌ 病案 {mr_key} 质控异常: {e}")
        return False, 0, 0

def test_batch_cases(mr_keys, test_name):
    """批量测试病案"""
    print(f"\n=== {test_name} ===")
    print(f"测试病案数量: {len(mr_keys)}")
    
    # 清理之前的结果
    clean_test_results(mr_keys)
    
    start_time = time.time()
    success_count = 0
    total_defects = 0
    total_score = 0
    
    for i, mr_key in enumerate(mr_keys, 1):
        print(f"处理 {i}/{len(mr_keys)}: {mr_key}", end=" ... ")
        
        success, defects, score = test_single_case(mr_key)
        
        if success:
            success_count += 1
            total_defects += defects
            total_score += score
            print(f"✅ {defects}个缺陷, 得分{score}")
        else:
            print(f"❌ 失败")
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    # 统计结果
    print(f"\n📊 {test_name} 结果:")
    print(f"  成功率: {success_count}/{len(mr_keys)} ({success_count/len(mr_keys)*100:.1f}%)")
    print(f"  总耗时: {elapsed:.1f}秒")
    print(f"  平均耗时: {elapsed/len(mr_keys):.1f}秒/病案")
    
    if success_count > 0:
        print(f"  总缺陷数: {total_defects}")
        print(f"  平均缺陷: {total_defects/success_count:.1f}个/病案")
        print(f"  平均得分: {total_score/success_count:.1f}")
    
    return success_count == len(mr_keys), elapsed, total_defects

def analyze_detailed_results(mr_keys):
    """分析详细结果"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        if not mr_keys:
            return
        
        placeholders = ','.join(['%s'] * len(mr_keys))
        
        # 1. 字段覆盖统计
        cursor.execute(f"""
            SELECT 
                field_code,
                field_name,
                COUNT(*) as defect_count
            FROM kiro_qc_defect_detail 
            WHERE mr_key IN ({placeholders})
            GROUP BY field_code, field_name
            ORDER BY defect_count DESC
            LIMIT 10
        """, mr_keys)
        
        fields = cursor.fetchall()
        
        # 2. 规则触发统计
        cursor.execute(f"""
            SELECT 
                d.rule_code,
                r.rule_type,
                COUNT(*) as trigger_count
            FROM kiro_qc_defect_detail d
            LEFT JOIN kiro_qc_rule r ON d.rule_id = r.id
            WHERE d.mr_key IN ({placeholders})
            GROUP BY d.rule_code, r.rule_type
            ORDER BY trigger_count DESC
            LIMIT 10
        """, mr_keys)
        
        rules = cursor.fetchall()
        
        # 3. 医疗编码缺陷
        cursor.execute(f"""
            SELECT COUNT(*) as medical_defects
            FROM kiro_qc_defect_detail 
            WHERE mr_key IN ({placeholders})
              AND (field_code LIKE 'C01%' OR field_code LIKE 'C21%' 
                   OR field_code LIKE 'C38%' OR field_code LIKE 'C43%')
        """, mr_keys)
        
        medical_defects = cursor.fetchone()['medical_defects']
        
        print(f"\n🔍 详细分析:")
        
        if fields:
            print(f"  缺陷最多的字段:")
            for field in fields[:5]:
                field_name = field['field_name'][:15] if field['field_name'] else '未知'
                print(f"    {field['field_code']:<12} {field_name:<15} {field['defect_count']}个")
        
        if rules:
            print(f"  触发最多的规则:")
            for rule in rules[:5]:
                rule_code = rule['rule_code'][:20] if rule['rule_code'] else '未知'
                rule_type = rule['rule_type'] if rule['rule_type'] else '未知'
                print(f"    {rule_code:<20} ({rule_type:<10}) {rule['trigger_count']}次")
        
        print(f"  医疗编码缺陷: {medical_defects}个")
        
        return len(fields), len(rules), medical_defects
        
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数 - 渐进式测试"""
    print("渐进式批量质控测试")
    print("=" * 50)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试年份
    test_year = 2023
    
    # 第一阶段：10条数据快速验证
    print(f"\n🚀 第一阶段：快速验证（10条数据）")
    sample_10 = get_sample_cases(test_year, 10)
    
    if not sample_10:
        print("❌ 未找到测试数据")
        return
    
    success_10, time_10, defects_10 = test_batch_cases(sample_10, "10条数据测试")
    
    if not success_10:
        print("❌ 10条数据测试失败，请检查系统配置")
        return
    
    # 分析10条数据的结果
    fields_10, rules_10, medical_10 = analyze_detailed_results(sample_10)
    
    print(f"\n✅ 第一阶段通过！")
    print(f"  字段覆盖: {fields_10}个")
    print(f"  规则触发: {rules_10}个")
    print(f"  医疗编码: {medical_10}个缺陷")
    
    # 询问是否继续50条测试
    print(f"\n🤔 是否继续50条数据测试？")
    print(f"  预计耗时: {time_10 * 5:.0f}秒 ({time_10 * 5 / 60:.1f}分钟)")
    
    # 自动继续（可以改为手动确认）
    continue_test = True
    
    if continue_test:
        # 第二阶段：50条数据完整验证
        print(f"\n🚀 第二阶段：完整验证（50条数据）")
        sample_50 = get_sample_cases(test_year, 50)
        
        success_50, time_50, defects_50 = test_batch_cases(sample_50, "50条数据测试")
        
        if success_50:
            # 分析50条数据的结果
            fields_50, rules_50, medical_50 = analyze_detailed_results(sample_50)
            
            print(f"\n✅ 第二阶段通过！")
            print(f"  字段覆盖: {fields_50}个")
            print(f"  规则触发: {rules_50}个")
            print(f"  医疗编码: {medical_50}个缺陷")
            
            # 性能对比
            print(f"\n📈 性能对比:")
            print(f"  10条平均: {time_10/10:.1f}秒/病案")
            print(f"  50条平均: {time_50/50:.1f}秒/病案")
            
            if time_50/50 <= time_10/10 * 1.2:  # 允许20%的性能波动
                print(f"  ✅ 性能稳定")
            else:
                print(f"  ⚠️  性能有所下降")
            
            # 询问是否进行更大规模测试
            if time_50 < 300:  # 5分钟内完成50条
                print(f"\n🎯 系统性能良好，可以考虑更大规模测试")
                print(f"  建议测试规模: 200-500条")
                print(f"  预计耗时: {time_50/50*200/60:.0f}-{time_50/50*500/60:.0f}分钟")
            else:
                print(f"\n⚠️  系统性能需要优化后再进行大规模测试")
        
        else:
            print(f"❌ 第二阶段失败，建议检查系统稳定性")
    
    else:
        print(f"\n⏸️  测试暂停，10条数据验证已完成")
    
    print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()