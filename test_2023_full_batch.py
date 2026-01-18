#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import pymysql
from datetime import datetime
import json

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

def check_system_status():
    """检查系统状态"""
    print("=== 检查系统状态 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 检查规则数量
        cursor.execute("SELECT COUNT(*) as total FROM kiro_qc_rule WHERE status = 'active'")
        rule_count = cursor.fetchone()['total']
        print(f"✅ 激活规则数量: {rule_count}")
        
        # 检查2023年数据量
        cursor.execute("""
            SELECT COUNT(*) as case_count
            FROM d_mr 
            WHERE B15 LIKE '2023/%'
        """)
        case_count = cursor.fetchone()['case_count']
        print(f"✅ 2023年病案数量: {case_count}")
        
        # 检查Redis缓存
        try:
            response = requests.get(f"{BASE_URL}/dict/cache/stats", timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    stats = result.get('data', {})
                    print(f"✅ Redis缓存: {stats.get('dictCacheCount', 0)}个字典")
                else:
                    print(f"⚠️  Redis缓存检查失败: {result.get('message', 'Unknown error')}")
            else:
                print(f"⚠️  Redis缓存检查失败: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Redis连接失败: {e}")
            return False
        
        return rule_count, case_count
        
    finally:
        cursor.close()
        conn.close()

def start_2023_batch_processing():
    """启动2023年批量处理"""
    print(f"\n=== 启动2023年批量处理 ===")
    
    # 清理之前的结果
    print("1. 清理之前的结果...")
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 删除2023年的质控结果
        cursor.execute("""
            DELETE FROM kiro_qc_case_result 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
        """)
        
        cursor.execute("""
            DELETE FROM kiro_qc_defect_detail 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
        """)
        
        conn.commit()
        print("✅ 清理完成")
        
    finally:
        cursor.close()
        conn.close()
    
    # 启动批量处理
    print("2. 启动批量处理...")
    
    batch_request = {
        "periodType": "year",
        "year": 2023
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(f"{BASE_URL}/qc/check/batch", 
                               json=batch_request,
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json().get('data', {})
            batch_key = result.get('batchKey', '')
            case_count = result.get('caseCount', 0)
            
            print(f"✅ 批量任务已启动")
            print(f"批次键: {batch_key}")
            print(f"病案数量: {case_count}")
            
            return batch_key, start_time
        else:
            print(f"❌ 批量任务启动失败: {response.status_code}")
            return None, None
    
    except Exception as e:
        print(f"❌ 批量任务启动异常: {e}")
        return None, None

def monitor_batch_progress(batch_key, start_time):
    """监控批量处理进度"""
    print(f"\n=== 监控批量处理进度 ===")
    
    last_progress = 0
    
    while True:
        try:
            response = requests.get(f"{BASE_URL}/qc/batch/status/{batch_key}", timeout=10)
            
            if response.status_code == 200:
                status = response.json().get('data', {})
                
                progress = status.get('progress', 0)
                processed_count = status.get('caseCount', 0)
                elapsed_seconds = status.get('elapsedSeconds', 0)
                batch_status = status.get('status', 'unknown')
                
                current_time = time.time()
                actual_elapsed = current_time - start_time
                
                if progress != last_progress:
                    print(f"进度: {progress}% ({processed_count}个病案), 已用时: {actual_elapsed:.0f}秒, 状态: {batch_status}")
                    last_progress = progress
                
                if batch_status == 'completed':
                    print(f"✅ 批量处理完成！")
                    print(f"总耗时: {actual_elapsed:.0f}秒 ({actual_elapsed/60:.1f}分钟)")
                    return True, actual_elapsed
                elif batch_status == 'failed':
                    print(f"❌ 批量处理失败")
                    return False, actual_elapsed
                
                time.sleep(10)  # 每10秒检查一次
            
            else:
                print(f"⚠️  状态查询失败: {response.status_code}")
                time.sleep(10)
        
        except Exception as e:
            print(f"⚠️  状态查询异常: {e}")
            time.sleep(10)

def analyze_batch_results():
    """分析批量处理结果"""
    print(f"\n=== 分析批量处理结果 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 总体统计
        print("1. 总体统计:")
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_cases,
                SUM(defect_count) as total_defects,
                AVG(defect_count) as avg_defects,
                AVG(final_score) as avg_score,
                MIN(final_score) as min_score,
                MAX(final_score) as max_score
            FROM kiro_qc_case_result 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
        """)
        
        overall_stats = cursor.fetchone()
        
        if overall_stats and overall_stats['total_cases']:
            print(f"  处理病案数: {overall_stats['total_cases']}")
            print(f"  总缺陷数: {overall_stats['total_defects']}")
            print(f"  平均缺陷数: {overall_stats['avg_defects']:.1f}")
            print(f"  平均得分: {overall_stats['avg_score']:.1f}")
            print(f"  最低得分: {overall_stats['min_score']:.1f}")
            print(f"  最高得分: {overall_stats['max_score']:.1f}")
        else:
            print("  未找到处理结果")
            return None
        
        # 2. 缺陷字段分析
        print(f"\n2. 缺陷字段分析:")
        
        cursor.execute("""
            SELECT 
                field_code,
                field_name,
                COUNT(*) as defect_count,
                COUNT(DISTINCT mr_key) as affected_cases
            FROM kiro_qc_defect_detail 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
            GROUP BY field_code, field_name
            ORDER BY defect_count DESC
            LIMIT 20
        """)
        
        field_stats = cursor.fetchall()
        
        print(f"  缺陷最多的20个字段:")
        print(f"  {'字段代码':<15} {'字段名称':<25} {'缺陷次数':<10} {'涉及病案'}")
        print("  " + "-" * 70)
        
        total_unique_fields = 0
        
        for field in field_stats:
            field_code = field['field_code'][:14]
            field_name = field['field_name'][:24] if field['field_name'] else '未知'
            defect_count = field['defect_count']
            affected_cases = field['affected_cases']
            
            print(f"  {field_code:<15} {field_name:<25} {defect_count:<10} {affected_cases}")
            total_unique_fields += 1
        
        # 统计总的唯一字段数
        cursor.execute("""
            SELECT COUNT(DISTINCT field_code) as unique_fields
            FROM kiro_qc_defect_detail 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
        """)
        
        unique_fields_total = cursor.fetchone()['unique_fields']
        print(f"\n  总计涉及字段数: {unique_fields_total}")
        
        # 3. 规则触发分析
        print(f"\n3. 规则触发分析:")
        
        cursor.execute("""
            SELECT 
                d.rule_id,
                d.rule_code,
                r.rule_type,
                r.dict_types,
                COUNT(*) as trigger_count,
                COUNT(DISTINCT d.mr_key) as affected_cases
            FROM kiro_qc_defect_detail d
            LEFT JOIN kiro_qc_rule r ON d.rule_id = r.id
            WHERE d.mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
            GROUP BY d.rule_id, d.rule_code, r.rule_type, r.dict_types
            ORDER BY trigger_count DESC
            LIMIT 20
        """)
        
        rule_stats = cursor.fetchall()
        
        print(f"  触发最多的20条规则:")
        print(f"  {'规则代码':<25} {'规则类型':<15} {'字典类型':<15} {'触发次数':<10} {'涉及病案'}")
        print("  " + "-" * 85)
        
        for rule in rule_stats:
            rule_code = rule['rule_code'][:24] if rule['rule_code'] else '未知'
            rule_type = rule['rule_type'][:14] if rule['rule_type'] else '未知'
            dict_types = rule['dict_types'][:14] if rule['dict_types'] else '无'
            trigger_count = rule['trigger_count']
            affected_cases = rule['affected_cases']
            
            print(f"  {rule_code:<25} {rule_type:<15} {dict_types:<15} {trigger_count:<10} {affected_cases}")
        
        # 统计总的触发规则数
        cursor.execute("""
            SELECT COUNT(DISTINCT rule_id) as unique_rules
            FROM kiro_qc_defect_detail 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
        """)
        
        unique_rules_total = cursor.fetchone()['unique_rules']
        print(f"\n  总计触发规则数: {unique_rules_total}")
        
        # 4. 医疗编码相关缺陷
        print(f"\n4. 医疗编码相关缺陷:")
        
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN field_code LIKE 'C01%' THEN '主要诊断编码'
                    WHEN field_code LIKE 'C02%' THEN '主要诊断中医编码'
                    WHEN field_code LIKE 'C04%' THEN '其他诊断编码'
                    WHEN field_code LIKE 'C21%' THEN '手术操作编码'
                    WHEN field_code LIKE 'C38%' THEN '其他手术编码'
                    WHEN field_code LIKE 'C43%' THEN '其他手术编码'
                    ELSE '其他医疗编码'
                END as code_type,
                COUNT(*) as defect_count,
                COUNT(DISTINCT mr_key) as affected_cases
            FROM kiro_qc_defect_detail 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
            AND (field_code LIKE 'C01%' OR field_code LIKE 'C02%' OR field_code LIKE 'C04%' 
                 OR field_code LIKE 'C21%' OR field_code LIKE 'C38%' OR field_code LIKE 'C43%')
            GROUP BY code_type
            ORDER BY defect_count DESC
        """)
        
        medical_code_stats = cursor.fetchall()
        
        if medical_code_stats:
            print(f"  医疗编码缺陷分布:")
            for stat in medical_code_stats:
                print(f"    {stat['code_type']}: {stat['defect_count']}个缺陷, 涉及{stat['affected_cases']}个病案")
        else:
            print(f"  未发现医疗编码相关缺陷")
        
        return {
            'total_cases': overall_stats['total_cases'],
            'total_defects': overall_stats['total_defects'],
            'avg_defects': overall_stats['avg_defects'],
            'unique_fields': unique_fields_total,
            'unique_rules': unique_rules_total,
            'medical_code_defects': len(medical_code_stats) > 0
        }
        
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    print("2023年完整规则集批量质控测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查系统状态
    system_check = check_system_status()
    if not system_check:
        print("❌ 系统状态检查失败")
        return
    
    rule_count, case_count = system_check
    
    # 2. 启动批量处理
    batch_result = start_2023_batch_processing()
    if not batch_result[0]:
        print("❌ 批量处理启动失败")
        return
    
    batch_key, start_time = batch_result
    
    # 3. 监控进度
    success, total_time = monitor_batch_progress(batch_key, start_time)
    
    if success:
        # 4. 分析结果
        analysis = analyze_batch_results()
        
        if analysis:
            # 5. 生成总结报告
            print(f"\n" + "=" * 60)
            print(f"📊 2023年批量质控完整报告")
            print(f"=" * 60)
            
            print(f"⏱️  处理性能:")
            print(f"   总耗时: {total_time:.0f}秒 ({total_time/60:.1f}分钟)")
            print(f"   平均每病案: {total_time/case_count:.1f}秒")
            print(f"   处理速度: {case_count*3600/total_time:.0f}病案/小时")
            
            print(f"\n🔍 质控效果:")
            print(f"   激活规则数: {rule_count}")
            print(f"   处理病案数: {analysis['total_cases']}")
            print(f"   总缺陷数: {analysis['total_defects']}")
            print(f"   平均缺陷数: {analysis['avg_defects']:.1f}个/病案")
            
            print(f"\n📋 覆盖范围:")
            print(f"   涉及字段数: {analysis['unique_fields']}")
            print(f"   触发规则数: {analysis['unique_rules']}")
            print(f"   规则触发率: {analysis['unique_rules']/rule_count*100:.1f}%")
            
            print(f"\n🏥 医疗编码验证:")
            if analysis['medical_code_defects']:
                print(f"   ✅ 成功检测到医疗编码相关缺陷")
            else:
                print(f"   ℹ️  未发现医疗编码缺陷（可能数据质量较好）")
            
            # 性能评级
            if total_time < 1800:  # 30分钟
                performance_grade = "🟢 优秀"
            elif total_time < 3600:  # 1小时
                performance_grade = "🟡 良好"
            elif total_time < 7200:  # 2小时
                performance_grade = "🟠 可接受"
            else:
                performance_grade = "🔴 需要优化"
            
            print(f"\n🎯 综合评价: {performance_grade}")
            
        else:
            print("❌ 结果分析失败")
    
    else:
        print("❌ 批量处理失败")

if __name__ == "__main__":
    main()