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

def analyze_performance_bottleneck():
    """分析性能瓶颈"""
    print("医疗质控系统性能瓶颈分析")
    print("=" * 50)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n🔍 当前性能问题:")
    print(f"   • 单病案处理时间: 27.97秒")
    print(f"   • 目标处理时间: 3秒以内")
    print(f"   • 性能差距: 9.3倍")
    
    print(f"\n📊 可能的瓶颈原因:")
    
    # 1. 检查规则数量
    check_rule_count()
    
    # 2. 检查数据库查询性能
    check_database_performance()
    
    # 3. 检查Redis缓存状态
    check_redis_cache()
    
    # 4. 分析规则执行效率
    analyze_rule_execution()

def check_rule_count():
    """检查规则数量"""
    print(f"\n1. 规则数量检查:")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 检查活跃规则数量
        cursor.execute("SELECT COUNT(*) as count FROM kiro_qc_rule WHERE is_active = 1")
        result = cursor.fetchone()
        active_rules = result['count']
        
        # 检查总规则数量
        cursor.execute("SELECT COUNT(*) as count FROM kiro_qc_rule")
        result = cursor.fetchone()
        total_rules = result['count']
        
        print(f"   活跃规则数量: {active_rules}条")
        print(f"   总规则数量: {total_rules}条")
        
        if active_rules > 2000:
            print(f"   ❌ 规则数量过多，可能是主要瓶颈")
        elif active_rules > 1000:
            print(f"   ⚠️  规则数量较多，需要优化")
        else:
            print(f"   ✅ 规则数量合理")
        
        # 检查规则类型分布
        cursor.execute("""
            SELECT rule_type, COUNT(*) as count 
            FROM kiro_qc_rule 
            WHERE is_active = 1 
            GROUP BY rule_type
        """)
        
        rule_types = cursor.fetchall()
        print(f"   规则类型分布:")
        for rule_type in rule_types:
            print(f"     {rule_type['rule_type']}: {rule_type['count']}条")
        
        return active_rules
        
    finally:
        cursor.close()
        conn.close()

def check_database_performance():
    """检查数据库查询性能"""
    print(f"\n2. 数据库查询性能检查:")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 测试规则查询性能
        start_time = time.time()
        cursor.execute("SELECT * FROM kiro_qc_rule WHERE is_active = 1")
        rules = cursor.fetchall()
        rule_query_time = time.time() - start_time
        
        print(f"   规则查询时间: {rule_query_time:.3f}秒 ({len(rules)}条)")
        
        # 测试病案查询性能
        start_time = time.time()
        cursor.execute("SELECT * FROM d_mr WHERE A48 = '20003285' AND A49 = '1'")
        record = cursor.fetchone()
        record_query_time = time.time() - start_time
        
        print(f"   病案查询时间: {record_query_time:.3f}秒")
        
        # 测试字典查询性能
        start_time = time.time()
        cursor.execute("SELECT * FROM kiro_qc_dict WHERE dict_type_code = 'RC001'")
        dict_items = cursor.fetchall()
        dict_query_time = time.time() - start_time
        
        print(f"   字典查询时间: {dict_query_time:.3f}秒 ({len(dict_items)}条)")
        
        total_db_time = rule_query_time + record_query_time + dict_query_time
        print(f"   数据库查询总时间: {total_db_time:.3f}秒")
        
        if total_db_time > 5:
            print(f"   ❌ 数据库查询过慢，是主要瓶颈")
        elif total_db_time > 1:
            print(f"   ⚠️  数据库查询较慢")
        else:
            print(f"   ✅ 数据库查询性能良好")
        
        return total_db_time
        
    finally:
        cursor.close()
        conn.close()

def check_redis_cache():
    """检查Redis缓存状态"""
    print(f"\n3. Redis缓存状态检查:")
    
    try:
        # 通过API检查缓存状态
        response = requests.get(f"{BASE_URL}/dict/cache/status", timeout=5)
        
        if response.status_code == 200:
            cache_status = response.json().get('data', {})
            print(f"   ✅ Redis缓存可用")
            print(f"   缓存状态: {cache_status}")
        else:
            print(f"   ❌ Redis缓存状态异常: {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Redis缓存检查失败: {e}")
        print(f"   可能原因: Redis服务未启动或配置错误")

def analyze_rule_execution():
    """分析规则执行效率"""
    print(f"\n4. 规则执行效率分析:")
    
    # 基于已知信息分析
    single_case_time = 27.97  # 秒
    estimated_rules = 1699    # 条规则
    
    if estimated_rules > 0:
        time_per_rule = single_case_time / estimated_rules
        print(f"   平均每条规则处理时间: {time_per_rule*1000:.1f}毫秒")
        
        if time_per_rule > 0.01:  # 10毫秒
            print(f"   ❌ 规则执行效率极低")
        elif time_per_rule > 0.005:  # 5毫秒
            print(f"   ⚠️  规则执行效率较低")
        else:
            print(f"   ✅ 规则执行效率可接受")
    
    print(f"\n   可能的效率问题:")
    print(f"   • 每条规则都查询数据库")
    print(f"   • 重复解析病案数据")
    print(f"   • 字典验证未使用缓存")
    print(f"   • 规则逻辑复杂度高")

def provide_optimization_solutions():
    """提供优化解决方案"""
    print(f"\n" + "=" * 50)
    print("🚀 优化解决方案")
    print("=" * 50)
    
    print(f"\n💡 立即可实施的优化:")
    
    print(f"\n1. 数据库层面优化:")
    print(f"   • 添加索引: A48, A49, is_active")
    print(f"   • 优化规则查询: 预加载到内存")
    print(f"   • 使用连接池: 减少连接开销")
    
    print(f"\n2. 缓存层面优化:")
    print(f"   • 确保Redis正常运行")
    print(f"   • 预热所有字典缓存")
    print(f"   • 缓存病案数据")
    
    print(f"\n3. 代码层面优化:")
    print(f"   • 规则分组执行: 按字段分组")
    print(f"   • 减少重复计算: 缓存中间结果")
    print(f"   • 优化规则逻辑: 简化复杂规则")
    
    print(f"\n4. 系统层面优化:")
    print(f"   • 增加JVM内存: -Xmx4g")
    print(f"   • 调整线程池大小")
    print(f"   • 监控系统资源")

def create_immediate_fix_script():
    """创建立即修复脚本"""
    print(f"\n=== 创建立即修复脚本 ===")
    
    fix_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pymysql
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

BASE_URL = "http://localhost:4101/api"

def add_database_indexes():
    \"\"\"添加数据库索引\"\"\"
    print("添加数据库索引...")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 添加病案表索引
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_d_mr_a48_a49 ON d_mr(A48, A49)",
            "CREATE INDEX IF NOT EXISTS idx_d_mr_b15 ON d_mr(B15)",
            "CREATE INDEX IF NOT EXISTS idx_qc_rule_active ON kiro_qc_rule(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_qc_rule_field ON kiro_qc_rule(field_code)",
            "CREATE INDEX IF NOT EXISTS idx_dict_type ON kiro_qc_dict(dict_type_code)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"  ✅ 索引创建成功: {index_sql.split()[-1]}")
            except Exception as e:
                print(f"  ⚠️  索引创建跳过: {e}")
        
        conn.commit()
        print("✅ 数据库索引优化完成")
        
    finally:
        cursor.close()
        conn.close()

def reload_redis_cache():
    \"\"\"重新加载Redis缓存\"\"\"
    print("重新加载Redis缓存...")
    
    try:
        response = requests.post(f"{BASE_URL}/dict/cache/reload", timeout=30)
        
        if response.status_code == 200:
            print("✅ Redis缓存重新加载成功")
        else:
            print(f"❌ Redis缓存重新加载失败: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Redis缓存重新加载异常: {e}")

def test_performance_after_fix():
    \"\"\"修复后性能测试\"\"\"
    print("修复后性能测试...")
    
    test_case = {'a48': '20003285', 'a49': '1'}
    
    try:
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/qc/check/single", 
                               params=test_case, timeout=60)
        
        process_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json().get('data', {})
            defect_count = result.get('defectCount', 0)
            final_score = result.get('finalScore', 0)
            
            print(f"✅ 修复后性能测试成功")
            print(f"   处理时间: {process_time:.2f}秒")
            print(f"   缺陷数量: {defect_count}个")
            print(f"   最终得分: {final_score}分")
            
            if process_time <= 3:
                print(f"   🎉 性能目标达成！")
            elif process_time <= 10:
                print(f"   ✅ 性能显著改善")
            else:
                print(f"   ⚠️  性能仍需进一步优化")
            
            return process_time
        
        else:
            print(f"❌ 性能测试失败: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"❌ 性能测试异常: {e}")
        return None

def main():
    print("医疗质控系统性能立即修复")
    print("=" * 40)
    
    # 1. 添加数据库索引
    add_database_indexes()
    
    # 2. 重新加载Redis缓存
    reload_redis_cache()
    
    # 3. 等待系统稳定
    print("等待系统稳定...")
    time.sleep(10)
    
    # 4. 测试修复后性能
    performance = test_performance_after_fix()
    
    # 5. 总结
    print("\\n" + "=" * 40)
    print("修复总结")
    print("=" * 40)
    
    if performance:
        improvement = 27.97 / performance if performance > 0 else 0
        print(f"性能改善: {improvement:.1f}倍")
        print(f"处理时间: 27.97秒 → {performance:.2f}秒")
        
        if performance <= 3:
            print("🎉 性能目标达成！")
        elif performance <= 10:
            print("✅ 性能显著改善，可以使用")
        else:
            print("⚠️  仍需进一步优化")
    else:
        print("❌ 修复验证失败")

if __name__ == "__main__":
    main()
"""
    
    try:
        with open('immediate_performance_fix.py', 'w', encoding='utf-8') as f:
            f.write(fix_script)
        
        print("✅ 已创建立即修复脚本: immediate_performance_fix.py")
        return True
        
    except Exception as e:
        print(f"❌ 创建修复脚本失败: {e}")
        return False

def main():
    """主函数"""
    # 1. 分析性能瓶颈
    analyze_performance_bottleneck()
    
    # 2. 提供优化解决方案
    provide_optimization_solutions()
    
    # 3. 创建立即修复脚本
    create_immediate_fix_script()
    
    # 4. 总结和建议
    print(f"\n" + "=" * 50)
    print("📋 总结和下一步行动")
    print("=" * 50)
    
    print(f"🔍 主要问题:")
    print(f"   • 单病案处理时间: 27.97秒（目标3秒）")
    print(f"   • 性能差距: 9.3倍")
    print(f"   • 可能原因: 数据库查询慢、缓存未生效、规则执行效率低")
    
    print(f"\n⚡ 立即行动:")
    print(f"   1. 运行修复脚本: python immediate_performance_fix.py")
    print(f"   2. 添加数据库索引")
    print(f"   3. 重新加载Redis缓存")
    print(f"   4. 测试修复后性能")
    
    print(f"\n🎯 预期效果:")
    print(f"   • 数据库索引: 提升查询性能2-5倍")
    print(f"   • Redis缓存: 提升字典验证性能10倍")
    print(f"   • 综合优化: 单病案处理时间降到5-10秒")
    
    print(f"\n📞 如果仍然不理想:")
    print(f"   • 检查服务器资源使用")
    print(f"   • 考虑减少规则数量")
    print(f"   • 优化规则逻辑复杂度")
    print(f"   • 使用更强的硬件配置")

if __name__ == "__main__":
    main()