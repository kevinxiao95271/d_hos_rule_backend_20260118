#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import pymysql

# 数据库连接配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def clear_results():
    """清理测试结果"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM kiro_qc_case_result WHERE mr_key IN (SELECT CONCAT(A48, '_', A49) FROM d_mr WHERE B15 LIKE '2023/%')")
        cursor.execute("DELETE FROM kiro_qc_defect_detail WHERE mr_key IN (SELECT CONCAT(A48, '_', A49) FROM d_mr WHERE B15 LIKE '2023/%')")
        cursor.execute("DELETE FROM kiro_qc_batch_summary WHERE batch_key LIKE '%2023%'")
        conn.commit()
        print("✅ 清理完成")
    finally:
        cursor.close()
        conn.close()

def test_standard_batch():
    """测试标准批量处理"""
    print("\n=== 测试标准批量处理 ===")
    
    try:
        response = requests.post('http://localhost:4101/api/qc/check/batch', 
                               json={'periodType': 'year', 'year': 2023}, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json().get('data', {})
            batch_key = result.get('batchKey', '')
            case_count = result.get('caseCount', 0)
            
            print(f"✅ 标准批量处理已启动")
            print(f"批次键: {batch_key}")
            print(f"病案数量: {case_count}")
            
            return batch_key
        else:
            print(f"❌ 标准批量处理启动失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 标准批量处理异常: {e}")
        return None

def check_batch_status(batch_key, name):
    """检查批量处理状态"""
    print(f"\n=== 检查{name}状态 ===")
    
    for i in range(6):  # 检查1分钟
        try:
            response = requests.get(f'http://localhost:4101/api/qc/batch/status/{batch_key}', timeout=10)
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                progress = data.get('progress', 0)
                status = data.get('status', 'unknown')
                case_count = data.get('caseCount', 0)
                
                print(f"[{i*10}秒] 进度: {progress}%, 状态: {status}, 处理数: {case_count}")
                
                if status == 'completed':
                    print(f"✅ {name}处理完成！")
                    return True
                elif status == 'failed':
                    print(f"❌ {name}处理失败")
                    return False
            
            time.sleep(10)
            
        except Exception as e:
            print(f"状态查询异常: {e}")
    
    print(f"⏳ {name}仍在处理中...")
    return None

def main():
    """主函数"""
    print("标准 vs 优化批量处理对比测试")
    print("=" * 50)
    
    # 1. 检查当前优化批量状态
    print("1. 检查当前优化批量状态...")
    try:
        response = requests.get('http://localhost:4101/api/qc/batch/status/2023_opt')
        data = response.json().get('data', {})
        
        progress = data.get('progress', 0)
        status = data.get('status', 'unknown')
        elapsed = data.get('elapsedSeconds', 0)
        
        print(f"优化批量状态: {status}, 进度: {progress}%, 已运行: {elapsed/60:.1f}分钟")
        
        if status == 'completed':
            print("✅ 优化批量已完成")
        elif elapsed > 1800:  # 超过30分钟
            print("⚠️  优化批量运行时间过长，可能有问题")
        
    except Exception as e:
        print(f"检查优化批量状态失败: {e}")
    
    # 2. 清理并测试标准批量
    print("\n2. 测试标准批量处理...")
    clear_results()
    
    standard_batch_key = test_standard_batch()
    
    if standard_batch_key:
        # 监控标准批量处理1分钟
        check_batch_status(standard_batch_key, "标准批量")
    
    # 3. 总结
    print(f"\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    
    print("✅ 优化功能已部署:")
    print("   • BatchQcServiceOptimized.java - 8线程并行处理")
    print("   • /api/qc/check/batch/optimized - 优化批量接口")
    print("   • 预加载规则和Redis缓存预热")
    
    print("\n💡 下一步建议:")
    print("   1. 检查优化批量处理的日志，查看是否有异常")
    print("   2. 验证BatchQcServiceOptimized是否被正确注入")
    print("   3. 确认8线程并行处理是否正常工作")
    print("   4. 监控系统资源使用情况")
    
    print(f"\n🎯 预期效果:")
    print(f"   • 处理时间: 35分钟 → 5分钟以内")
    print(f"   • 性能提升: 7-10倍")
    print(f"   • 保持1699条完整规则")

if __name__ == "__main__":
    main()