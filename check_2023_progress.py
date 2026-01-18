#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
from datetime import datetime
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

def check_progress():
    """检查2023年批量处理进度"""
    print("=== 检查2023年批量处理进度 ===")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 检查2023年病案总数
        cursor.execute("SELECT COUNT(*) as total FROM d_mr WHERE B15 LIKE '2023/%'")
        total_cases = cursor.fetchone()['total']
        print(f"2023年病案总数: {total_cases}")
        
        # 2. 检查已处理的病案数
        cursor.execute("""
            SELECT COUNT(*) as processed 
            FROM kiro_qc_case_result 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
        """)
        processed_cases = cursor.fetchone()['processed']
        print(f"已处理病案数: {processed_cases}")
        
        if total_cases > 0:
            progress = (processed_cases / total_cases) * 100
            print(f"处理进度: {progress:.1f}%")
        
        # 3. 检查最新处理的病案
        cursor.execute("""
            SELECT mr_key, defect_count, final_score, check_time
            FROM kiro_qc_case_result 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
            ORDER BY check_time DESC
            LIMIT 5
        """)
        
        recent_results = cursor.fetchall()
        
        if recent_results:
            print(f"\n最新处理的病案:")
            for result in recent_results:
                print(f"  {result['mr_key']}: {result['defect_count']}个缺陷, 得分:{result['final_score']:.1f}, 时间:{result['check_time']}")
        
        # 4. 检查缺陷统计
        if processed_cases > 0:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_defects,
                    COUNT(DISTINCT field_code) as unique_fields,
                    COUNT(DISTINCT rule_id) as unique_rules
                FROM kiro_qc_defect_detail 
                WHERE mr_key IN (
                    SELECT CONCAT(A48, '_', A49) 
                    FROM d_mr 
                    WHERE B15 LIKE '2023/%'
                )
            """)
            
            defect_stats = cursor.fetchone()
            
            print(f"\n缺陷统计:")
            print(f"  总缺陷数: {defect_stats['total_defects']}")
            print(f"  涉及字段数: {defect_stats['unique_fields']}")
            print(f"  触发规则数: {defect_stats['unique_rules']}")
            
            # 5. 医疗编码缺陷
            cursor.execute("""
                SELECT COUNT(*) as medical_defects
                FROM kiro_qc_defect_detail 
                WHERE mr_key IN (
                    SELECT CONCAT(A48, '_', A49) 
                    FROM d_mr 
                    WHERE B15 LIKE '2023/%'
                )
                AND (field_code LIKE 'C01%' OR field_code LIKE 'C21%' 
                     OR field_code LIKE 'C38%' OR field_code LIKE 'C43%')
            """)
            
            medical_defects = cursor.fetchone()['medical_defects']
            print(f"  医疗编码缺陷: {medical_defects}")
        
        return {
            'total_cases': total_cases,
            'processed_cases': processed_cases,
            'progress': progress if total_cases > 0 else 0,
            'is_complete': processed_cases >= total_cases
        }
        
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    result = check_progress()
    
    if result['is_complete']:
        print(f"\n✅ 2023年批量处理已完成！")
        print(f"处理了 {result['processed_cases']}/{result['total_cases']} 个病案")
    elif result['processed_cases'] > 0:
        print(f"\n⏳ 2023年批量处理进行中...")
        print(f"已处理 {result['processed_cases']}/{result['total_cases']} 个病案 ({result['progress']:.1f}%)")
        print(f"预计还需要一些时间完成剩余 {result['total_cases'] - result['processed_cases']} 个病案")
    else:
        print(f"\n⏸️  2023年批量处理尚未开始或遇到问题")
        print(f"总共需要处理 {result['total_cases']} 个病案")

if __name__ == "__main__":
    main()