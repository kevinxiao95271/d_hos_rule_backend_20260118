#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import pymysql
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

def check_batch_status():
    """检查当前批量处理状态"""
    print("=== 检查批量处理状态 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 查询所有批量任务状态
        cursor.execute("""
            SELECT batch_key, status, progress, case_count, 
                   start_time, end_time, 
                   TIMESTAMPDIFF(SECOND, start_time, NOW()) as elapsed_seconds
            FROM kiro_qc_batch_summary 
            WHERE batch_key LIKE '%2023%'
            ORDER BY start_time DESC
            LIMIT 10
        """)
        
        batches = cursor.fetchall()
        
        if not batches:
            print("❌ 没有找到2023年的批量任务")
            return
        
        print(f"找到 {len(batches)} 个批量任务:")
        print("-" * 80)
        
        for batch in batches:
            batch_key = batch['batch_key']
            status = batch['status']
            progress = batch['progress']
            case_count = batch['case_count']
            elapsed = batch['elapsed_seconds'] or 0
            
            print(f"批次键: {batch_key}")
            print(f"状态: {status}, 进度: {progress}%, 病案数: {case_count}")
            print(f"已运行: {elapsed//60}分{elapsed%60}秒")
            print(f"开始时间: {batch['start_time']}")
            print(f"结束时间: {batch['end_time']}")
            
            # 检查是否是优化批量
            if '_opt' in batch_key:
                print("🔍 这是优化批量任务")
                if status == 'processing' and elapsed > 300:  # 超过5分钟
                    print("⚠️  优化批量运行时间异常长")
                    check_optimized_batch_details(batch_key)
            
            print("-" * 80)
    
    finally:
        cursor.close()
        conn.close()

def check_optimized_batch_details(batch_key):
    """检查优化批量的详细信息"""
    print(f"\n=== 检查优化批量详情: {batch_key} ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 检查是否有病案结果
        cursor.execute("""
            SELECT COUNT(*) as case_count
            FROM kiro_qc_case_result 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
        """)
        case_results = cursor.fetchone()['case_count']
        
        # 检查是否有缺陷明细
        cursor.execute("""
            SELECT COUNT(*) as defect_count
            FROM kiro_qc_defect_detail 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
        """)
        defect_results = cursor.fetchone()['defect_count']
        
        print(f"病案结果数: {case_results}")
        print(f"缺陷明细数: {defect_results}")
        
        if case_results == 0 and defect_results == 0:
            print("❌ 优化批量没有产生任何结果，可能存在以下问题:")
            print("   1. BatchQcServiceOptimized未被正确调用")
            print("   2. 并行处理线程池出现异常")
            print("   3. 数据库事务回滚")
            print("   4. 规则引擎处理异常")
        
    finally:
        cursor.close()
        conn.close()

def test_optimized_api():
    """测试优化API是否可用"""
    print("\n=== 测试优化API ===")
    
    try:
        # 测试优化批量接口
        response = requests.post(
            'http://localhost:4101/api/qc/check/batch/optimized',
            json={'periodType': 'year', 'year': 2023},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            batch_key = data.get('batchKey', '')
            case_count = data.get('caseCount', 0)
            
            print(f"✅ 优化API响应正常")
            print(f"批次键: {batch_key}")
            print(f"病案数: {case_count}")
            
            # 等待几秒后检查状态
            time.sleep(5)
            
            status_response = requests.get(
                f'http://localhost:4101/api/qc/batch/status/{batch_key}',
                timeout=10
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json().get('data', {})
                print(f"5秒后状态: {status_data.get('status')}, 进度: {status_data.get('progress')}%")
            
        else:
            print(f"❌ 优化API响应异常: {response.status_code}")
            print(f"响应内容: {response.text}")
    
    except Exception as e:
        print(f"❌ 优化API测试失败: {e}")

def check_service_health():
    """检查服务健康状态"""
    print("\n=== 检查服务健康状态 ===")
    
    try:
        # 检查基本API
        response = requests.get('http://localhost:4101/api/qc/rules', timeout=5)
        if response.status_code == 200:
            rules = response.json().get('data', [])
            active_rules = [r for r in rules if r.get('status') == 'active']
            print(f"✅ 服务正常，活跃规则数: {len(active_rules)}")
        else:
            print(f"❌ 服务异常: {response.status_code}")
    
    except Exception as e:
        print(f"❌ 服务连接失败: {e}")

def suggest_fixes():
    """建议修复方案"""
    print("\n=== 修复建议 ===")
    
    print("🔧 立即检查项:")
    print("1. 检查Spring Boot应用日志:")
    print("   tail -f logs/application.log | grep -i 'BatchQcServiceOptimized\\|error\\|exception'")
    
    print("\n2. 验证服务注入:")
    print("   在QcService.batchCheckOptimized()方法开头添加:")
    print("   log.info(\"BatchQcServiceOptimized注入状态: {}\", batchQcServiceOptimized != null);")
    
    print("\n3. 检查线程池状态:")
    print("   在BatchQcServiceOptimized中添加线程池监控日志")
    
    print("\n🚀 快速修复方案:")
    print("1. 减少并行线程数 (8 → 2)")
    print("2. 减少批量大小 (12 → 5)")
    print("3. 添加详细异常捕获和日志")
    print("4. 使用同步处理验证逻辑正确性")
    
    print("\n⚡ 临时优化方案:")
    print("如果并行处理问题复杂，可以先实现:")
    print("1. 增加数据库批量操作大小 (50 → 100)")
    print("2. 优化Redis缓存预热")
    print("3. 减少不必要的数据库查询")
    print("预计可实现3-5倍性能提升 (35分钟 → 7-12分钟)")

def main():
    """主函数"""
    print("医疗质控系统优化批量处理诊断工具")
    print("=" * 60)
    
    check_batch_status()
    test_optimized_api()
    check_service_health()
    suggest_fixes()
    
    print("\n" + "=" * 60)
    print("📊 诊断完成")

if __name__ == "__main__":
    main()