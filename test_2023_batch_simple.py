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

def start_batch_processing():
    """启动批量处理"""
    print("=== 启动2023年批量处理 ===")
    
    # 简单清理
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 删除2023年的质控结果（简化版）
        cursor.execute("DELETE FROM kiro_qc_case_result WHERE mr_key LIKE '%2023%'")
        cursor.execute("DELETE FROM kiro_qc_defect_detail WHERE mr_key LIKE '%2023%'")
        conn.commit()
        print("✅ 清理完成")
        
    except Exception as e:
        print(f"⚠️  清理警告: {e}")
    
    finally:
        cursor.close()
        conn.close()
    
    # 启动批量处理
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
            
            return batch_key, start_time, case_count
        else:
            print(f"❌ 批量任务启动失败: {response.status_code}")
            print(f"响应: {response.text}")
            return None, None, None
    
    except Exception as e:
        print(f"❌ 批量任务启动异常: {e}")
        return None, None, None

def monitor_progress(batch_key, start_time):
    """监控进度"""
    print(f"\n=== 监控批量处理进度 ===")
    
    last_progress = 0
    
    while True:
        try:
            response = requests.get(f"{BASE_URL}/qc/batch/status/{batch_key}", timeout=10)
            
            if response.status_code == 200:
                status = response.json().get('data', {})
                
                progress = status.get('progress', 0)
                processed_count = status.get('caseCount', 0)
                batch_status = status.get('status', 'unknown')
                
                current_time = time.time()
                actual_elapsed = current_time - start_time
                
                if progress != last_progress or progress % 10 == 0:
                    print(f"进度: {progress}% ({processed_count}个病案), 已用时: {actual_elapsed:.0f}秒 ({actual_elapsed/60:.1f}分钟), 状态: {batch_status}")
                    last_progress = progress
                
                if batch_status == 'completed':
                    print(f"✅ 批量处理完成！")
                    print(f"总耗时: {actual_elapsed:.0f}秒 ({actual_elapsed/60:.1f}分钟)")
                    return True, actual_elapsed
                elif batch_status == 'failed':
                    print(f"❌ 批量处理失败")
                    return False, actual_elapsed
                
                time.sleep(15)  # 每15秒检查一次
            
            else:
                print(f"⚠️  状态查询失败: {response.status_code}")
                time.sleep(15)
        
        except Exception as e:
            print(f"⚠️  状态查询异常: {e}")
            time.sleep(15)

def analyze_results():
    """分析结果"""
    print(f"\n=== 分析批量处理结果 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 总体统计
        cursor.execute("""
            SELECT 
                COUNT(*) as total_cases,
                SUM(defect_count) as total_defects,
                AVG(defect_count) as avg_defects,
                AVG(final_score) as avg_score
            FROM kiro_qc_case_result 
        """)
        
        overall = cursor.fetchone()
        
        if overall and overall['total_cases']:
            print(f"📊 总体统计:")
            print(f"  处理病案数: {overall['total_cases']}")
            print(f"  总缺陷数: {overall['total_defects']}")
            print(f"  平均缺陷数: {overall['avg_defects']:.1f}")
            print(f"  平均得分: {overall['avg_score']:.1f}")
        else:
            print("❌ 未找到处理结果")
            return None
        
        # 2. 字段统计
        cursor.execute("""
            SELECT COUNT(DISTINCT field_code) as unique_fields
            FROM kiro_qc_defect_detail 
        """)
        
        field_count = cursor.fetchone()['unique_fields']
        
        # 3. 规则统计
        cursor.execute("""
            SELECT COUNT(DISTINCT rule_id) as unique_rules
            FROM kiro_qc_defect_detail 
        """)
        
        rule_count = cursor.fetchone()['unique_rules']
        
        # 4. 缺陷最多的字段
        cursor.execute("""
            SELECT 
                field_code,
                field_name,
                COUNT(*) as defect_count
            FROM kiro_qc_defect_detail 
            GROUP BY field_code, field_name
            ORDER BY defect_count DESC
            LIMIT 10
        """)
        
        top_fields = cursor.fetchall()
        
        print(f"\n📋 覆盖统计:")
        print(f"  涉及字段数: {field_count}")
        print(f"  触发规则数: {rule_count}")
        
        print(f"\n🔍 缺陷最多的10个字段:")
        for i, field in enumerate(top_fields, 1):
            field_name = field['field_name'][:20] if field['field_name'] else '未知'
            print(f"  {i:2d}. {field['field_code']:<12} {field_name:<20} {field['defect_count']}个缺陷")
        
        # 5. 触发最多的规则
        cursor.execute("""
            SELECT 
                d.rule_code,
                r.rule_type,
                COUNT(*) as trigger_count
            FROM kiro_qc_defect_detail d
            LEFT JOIN kiro_qc_rule r ON d.rule_id = r.id
            GROUP BY d.rule_code, r.rule_type
            ORDER BY trigger_count DESC
            LIMIT 10
        """)
        
        top_rules = cursor.fetchall()
        
        print(f"\n⚡ 触发最多的10条规则:")
        for i, rule in enumerate(top_rules, 1):
            rule_code = rule['rule_code'][:25] if rule['rule_code'] else '未知'
            rule_type = rule['rule_type'] if rule['rule_type'] else '未知'
            print(f"  {i:2d}. {rule_code:<25} ({rule_type:<15}) {rule['trigger_count']}次")
        
        # 6. 医疗编码缺陷
        cursor.execute("""
            SELECT COUNT(*) as medical_defects
            FROM kiro_qc_defect_detail 
            WHERE field_code LIKE 'C01%' OR field_code LIKE 'C21%' 
               OR field_code LIKE 'C38%' OR field_code LIKE 'C43%'
        """)
        
        medical_defects = cursor.fetchone()['medical_defects']
        
        print(f"\n🏥 医疗编码缺陷: {medical_defects}个")
        
        return {
            'total_cases': overall['total_cases'],
            'total_defects': overall['total_defects'],
            'avg_defects': overall['avg_defects'],
            'unique_fields': field_count,
            'unique_rules': rule_count,
            'medical_defects': medical_defects
        }
        
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    print("2023年完整规则集批量质控测试")
    print("=" * 50)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 启动批量处理
    result = start_batch_processing()
    if not result[0]:
        return
    
    batch_key, start_time, case_count = result
    
    # 监控进度
    success, total_time = monitor_progress(batch_key, start_time)
    
    if success:
        # 分析结果
        analysis = analyze_results()
        
        if analysis:
            print(f"\n" + "=" * 50)
            print(f"📊 2023年批量质控完整报告")
            print(f"=" * 50)
            
            print(f"⏱️  处理性能:")
            print(f"   总耗时: {total_time:.0f}秒 ({total_time/60:.1f}分钟)")
            print(f"   病案数量: {case_count}")
            print(f"   平均每病案: {total_time/case_count:.1f}秒")
            
            print(f"\n🔍 质控效果:")
            print(f"   总缺陷数: {analysis['total_defects']}")
            print(f"   平均缺陷数: {analysis['avg_defects']:.1f}个/病案")
            print(f"   涉及字段数: {analysis['unique_fields']}")
            print(f"   触发规则数: {analysis['unique_rules']}")
            print(f"   医疗编码缺陷: {analysis['medical_defects']}个")
            
            # 性能评级
            if total_time < 1800:  # 30分钟
                grade = "🟢 优秀"
            elif total_time < 3600:  # 1小时
                grade = "🟡 良好"
            else:
                grade = "🔴 需要优化"
            
            print(f"\n🎯 性能评级: {grade}")
            
            if analysis['medical_defects'] > 0:
                print(f"✅ 医疗编码验证功能正常工作！")
            
        print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()