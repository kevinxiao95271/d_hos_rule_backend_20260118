#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import pymysql
import statistics
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

def check_system_status():
    """检查系统状态"""
    print("=== 检查系统状态 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 检查规则数量
        cursor.execute("SELECT COUNT(*) as total FROM kiro_qc_rule WHERE status = 'active'")
        rule_count = cursor.fetchone()['total']
        print(f"✅ 激活规则数量: {rule_count}")
        
        # 2. 检查Redis缓存状态
        try:
            response = requests.get(f"{BASE_URL}/dict/cache/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json().get('data', {})
                print(f"✅ Redis缓存状态: {stats.get('dictCacheCount', 0)}个字典缓存")
            else:
                print(f"⚠️  Redis缓存状态检查失败")
        except Exception as e:
            print(f"❌ Redis缓存连接失败: {e}")
            return False
        
        # 3. 检查服务响应
        try:
            response = requests.get(f"{BASE_URL}/qc/rules/count", timeout=5)
            if response.status_code == 200:
                print(f"✅ 服务响应正常")
            else:
                print(f"⚠️  服务响应异常: {response.status_code}")
        except Exception as e:
            print(f"❌ 服务连接失败: {e}")
            return False
        
        return rule_count
        
    finally:
        cursor.close()
        conn.close()

def test_single_case_performance():
    """测试单个病案处理性能"""
    print(f"\n=== 测试单个病案处理性能 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取2023年的测试病案
        cursor.execute("""
            SELECT A48, A49 
            FROM d_mr 
            WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
            LIMIT 3
        """)
        test_cases = cursor.fetchall()
        
        if not test_cases:
            print("❌ 未找到2023年测试数据")
            return None
        
        print(f"测试{len(test_cases)}个病案...")
        
        processing_times = []
        defect_counts = []
        
        for i, case in enumerate(test_cases):
            print(f"\n测试病案 {i+1}: {case['A48']}_{case['A49']}")
            
            # 清理之前的结果
            mr_key = f"{case['A48']}_{case['A49']}"
            cursor.execute("DELETE FROM kiro_qc_case_result WHERE mr_key = %s", (mr_key,))
            cursor.execute("DELETE FROM kiro_qc_defect_detail WHERE mr_key = %s", (mr_key,))
            conn.commit()
            
            # 测试处理时间
            start_time = time.time()
            
            try:
                response = requests.post(f"{BASE_URL}/qc/check/single", 
                                       params={
                                           'a48': case['A48'],
                                           'a49': case['A49']
                                       },
                                       timeout=60)  # 增加超时时间
                
                end_time = time.time()
                processing_time = end_time - start_time
                processing_times.append(processing_time)
                
                print(f"  处理时间: {processing_time:.2f}秒")
                
                if response.status_code == 200:
                    result = response.json().get('data', {})
                    defect_count = result.get('defectCount', 0)
                    final_score = result.get('finalScore', 0)
                    defect_counts.append(defect_count)
                    
                    print(f"  检测到缺陷: {defect_count}个")
                    print(f"  最终得分: {final_score}")
                else:
                    print(f"  ❌ 处理失败: {response.status_code}")
            
            except Exception as e:
                print(f"  ❌ 处理异常: {e}")
        
        if processing_times:
            avg_time = statistics.mean(processing_times)
            max_time = max(processing_times)
            min_time = min(processing_times)
            
            print(f"\n📊 单病案处理性能统计:")
            print(f"  平均处理时间: {avg_time:.2f}秒")
            print(f"  最快处理时间: {min_time:.2f}秒")
            print(f"  最慢处理时间: {max_time:.2f}秒")
            
            if defect_counts:
                avg_defects = statistics.mean(defect_counts)
                print(f"  平均缺陷数量: {avg_defects:.1f}个")
            
            return avg_time
        
        return None
        
    finally:
        cursor.close()
        conn.close()

def estimate_batch_performance():
    """估算批量处理性能"""
    print(f"\n=== 估算批量处理性能 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取2023年病案总数
        cursor.execute("""
            SELECT COUNT(*) as case_count
            FROM d_mr 
            WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
        """)
        total_cases = cursor.fetchone()['case_count']
        
        print(f"2023年总病案数: {total_cases}")
        
        return total_cases
        
    finally:
        cursor.close()
        conn.close()

def analyze_rule_performance():
    """分析规则性能分布"""
    print(f"\n=== 分析规则性能分布 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 统计各类规则数量
        cursor.execute("""
            SELECT rule_type, COUNT(*) as count
            FROM kiro_qc_rule 
            WHERE status = 'active'
            GROUP BY rule_type
            ORDER BY count DESC
        """)
        rule_stats = cursor.fetchall()
        
        print("规则类型性能分析:")
        print(f"{'规则类型':<20} {'数量':<8} {'估算耗时':<12} {'性能影响'}")
        print("-" * 60)
        
        total_estimated_time = 0
        
        for stat in rule_stats:
            rule_type = stat['rule_type']
            count = stat['count']
            
            # 估算不同规则类型的性能开销
            if rule_type == 'value_check':
                # 字典验证，Redis缓存下很快
                estimated_ms = count * 1  # 1ms per rule
                impact = "低(Redis缓存)"
            elif rule_type in ['cross_check', 'cross_check_null']:
                # 交叉验证，需要查询多个字段
                estimated_ms = count * 2  # 2ms per rule
                impact = "中等"
            elif rule_type == 'range_check':
                # 范围检查，纯计算
                estimated_ms = count * 0.5  # 0.5ms per rule
                impact = "低"
            elif rule_type in ['length_check', 'legal_char_set']:
                # 字符串检查，纯计算
                estimated_ms = count * 0.3  # 0.3ms per rule
                impact = "很低"
            elif rule_type == 'date_check':
                # 日期检查，需要解析
                estimated_ms = count * 1.5  # 1.5ms per rule
                impact = "低-中等"
            else:
                # 其他规则
                estimated_ms = count * 1  # 1ms per rule
                impact = "中等"
            
            total_estimated_time += estimated_ms
            
            print(f"{rule_type:<20} {count:<8} {estimated_ms:<12.1f}ms {impact}")
        
        print("-" * 60)
        print(f"{'总计':<20} {sum(s['count'] for s in rule_stats):<8} {total_estimated_time:<12.1f}ms")
        
        return total_estimated_time / 1000  # 转换为秒
        
    finally:
        cursor.close()
        conn.close()

def performance_comparison():
    """性能对比分析"""
    print(f"\n=== 性能对比分析 ===")
    
    # 历史性能数据
    performance_history = {
        "原始系统(1699规则)": {"单病案": "~360秒", "批量": "不可用"},
        "核心规则(247规则)": {"单病案": "2-4秒", "批量": "4分钟"},
        "核心规则+Redis": {"单病案": "2.73秒", "批量": "4.4分钟"},
    }
    
    print("历史性能对比:")
    print(f"{'版本':<20} {'单病案处理':<15} {'2023年批量'}")
    print("-" * 50)
    
    for version, perf in performance_history.items():
        print(f"{version:<20} {perf['单病案']:<15} {perf['批量']}")
    
    return performance_history

def suggest_optimizations():
    """建议进一步的优化手段"""
    print(f"\n=== 进一步优化建议 ===")
    
    optimizations = [
        {
            "类别": "规则引擎优化",
            "建议": [
                "规则分层执行：先执行快速规则，再执行复杂规则",
                "规则并行化：将独立规则分组并行执行",
                "规则缓存：缓存规则执行结果，避免重复计算",
                "智能跳过：根据字段值快速跳过不适用的规则"
            ]
        },
        {
            "类别": "数据库优化",
            "建议": [
                "批量查询：一次查询获取病案所有相关数据",
                "索引优化：为常用查询字段添加复合索引",
                "连接池优化：调整数据库连接池参数",
                "读写分离：查询使用只读副本"
            ]
        },
        {
            "类别": "缓存策略优化",
            "建议": [
                "多级缓存：本地缓存+Redis缓存",
                "预热策略：启动时预加载热点数据",
                "缓存分区：按数据类型分区缓存",
                "异步更新：后台异步更新缓存数据"
            ]
        },
        {
            "类别": "架构优化",
            "建议": [
                "微服务拆分：将规则引擎独立为微服务",
                "异步处理：批量任务使用消息队列异步处理",
                "负载均衡：多实例部署支持水平扩展",
                "GPU加速：使用GPU并行处理大量规则"
            ]
        },
        {
            "类别": "算法优化",
            "建议": [
                "规则编译：将规则编译为字节码提升执行效率",
                "决策树：将规则组织为决策树减少判断次数",
                "位运算：使用位运算优化布尔逻辑",
                "SIMD指令：使用向量指令并行处理数据"
            ]
        }
    ]
    
    for opt in optimizations:
        print(f"\n🎯 {opt['类别']}:")
        for i, suggestion in enumerate(opt['建议'], 1):
            print(f"  {i}. {suggestion}")
    
    return optimizations

def main():
    """主测试函数"""
    print("=" * 60)
    print("完整规则集 + Redis缓存 基准测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查系统状态
    rule_count = check_system_status()
    if not rule_count:
        print("❌ 系统状态检查失败")
        return
    
    # 2. 测试单病案性能
    avg_processing_time = test_single_case_performance()
    
    # 3. 估算批量性能
    total_cases = estimate_batch_performance()
    
    # 4. 分析规则性能
    estimated_rule_time = analyze_rule_performance()
    
    # 5. 性能对比
    performance_comparison()
    
    # 6. 计算最终估算
    if avg_processing_time and total_cases:
        estimated_batch_time = avg_processing_time * total_cases
        estimated_batch_minutes = estimated_batch_time / 60
        
        print(f"\n📈 完整规则集性能估算:")
        print(f"  规则数量: {rule_count}")
        print(f"  单病案平均处理时间: {avg_processing_time:.2f}秒")
        print(f"  2023年病案总数: {total_cases}")
        print(f"  估算批量处理时间: {estimated_batch_minutes:.1f}分钟 ({estimated_batch_time:.0f}秒)")
        print(f"  理论规则执行时间: {estimated_rule_time:.2f}秒/病案")
        
        # 性能评估
        if estimated_batch_minutes < 10:
            performance_level = "🟢 优秀"
        elif estimated_batch_minutes < 30:
            performance_level = "🟡 良好"
        elif estimated_batch_minutes < 60:
            performance_level = "🟠 可接受"
        else:
            performance_level = "🔴 需要优化"
        
        print(f"  性能评级: {performance_level}")
    
    # 7. 优化建议
    suggest_optimizations()
    
    print(f"\n✅ 基准测试完成")

if __name__ == "__main__":
    main()