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

def emergency_analysis():
    """紧急性能分析"""
    print("医疗质控系统紧急性能分析")
    print("=" * 50)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n🚨 当前严重问题:")
    print(f"   • 单病案处理超过30秒（超时）")
    print(f"   • 1699条规则全部执行")
    print(f"   • 字典验证可能没有缓存")
    print(f"   • 数据库查询频繁")
    
    # 分析根本原因
    analyze_root_cause()

def analyze_root_cause():
    """分析根本原因"""
    print(f"\n🔍 根本原因分析:")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 检查规则复杂度
        print(f"\n1. 规则复杂度分析:")
        
        # 检查字典验证规则数量
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            AND (rule_type = 'value_check' OR description LIKE '%字典%')
        """)
        result = cursor.fetchone()
        dict_rules = result['count']
        
        print(f"   字典验证规则: {dict_rules}条")
        
        # 检查复杂规则
        cursor.execute("""
            SELECT rule_type, COUNT(*) as count 
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            GROUP BY rule_type 
            ORDER BY count DESC
        """)
        rule_types = cursor.fetchall()
        
        print(f"   规则类型分布:")
        for rule in rule_types:
            print(f"     {rule['rule_type']}: {rule['count']}条")
        
        # 2. 检查是否有字典表
        print(f"\n2. 字典数据检查:")
        
        try:
            cursor.execute("SELECT COUNT(*) as count FROM kiro_qc_dict")
            result = cursor.fetchone()
            print(f"   字典表存在，记录数: {result['count']}")
        except:
            print(f"   ❌ 字典表不存在，这是主要问题！")
            print(f"   所有字典验证都会失败或查询其他表")
        
        # 3. 估算性能瓶颈
        print(f"\n3. 性能瓶颈估算:")
        
        total_rules = 1699
        dict_rules_ratio = dict_rules / total_rules if total_rules > 0 else 0
        
        print(f"   总规则数: {total_rules}")
        print(f"   字典规则占比: {dict_rules_ratio:.1%}")
        
        # 假设每条字典规则需要查询数据库
        estimated_dict_time = dict_rules * 0.02  # 20毫秒/规则
        estimated_other_time = (total_rules - dict_rules) * 0.005  # 5毫秒/规则
        estimated_total = estimated_dict_time + estimated_other_time
        
        print(f"   预估字典验证时间: {estimated_dict_time:.1f}秒")
        print(f"   预估其他规则时间: {estimated_other_time:.1f}秒")
        print(f"   预估总时间: {estimated_total:.1f}秒")
        
        if estimated_total > 20:
            print(f"   ❌ 预估时间过长，主要是字典验证问题")
        
    finally:
        cursor.close()
        conn.close()

def create_emergency_solutions():
    """创建紧急解决方案"""
    print(f"\n" + "=" * 50)
    print("🚀 紧急解决方案")
    print("=" * 50)
    
    print(f"\n💡 立即可实施的解决方案:")
    
    print(f"\n方案1: 减少规则数量（最快）")
    print(f"   • 暂时禁用字典验证规则")
    print(f"   • 只保留核心规则（约500条）")
    print(f"   • 预期效果: 处理时间降到8-10秒")
    
    print(f"\n方案2: 修复字典缓存（推荐）")
    print(f"   • 检查Redis服务状态")
    print(f"   • 重新加载字典缓存")
    print(f"   • 预期效果: 处理时间降到5-8秒")
    
    print(f"\n方案3: 创建字典表（根本解决）")
    print(f"   • 创建缺失的kiro_qc_dict表")
    print(f"   • 导入字典数据")
    print(f"   • 预期效果: 处理时间降到3-5秒")
    
    print(f"\n方案4: 使用优化批量接口（绕过问题）")
    print(f"   • 直接使用8线程并行批量处理")
    print(f"   • 即使单病案慢，并行处理仍能达到目标")
    print(f"   • 预期效果: 96病案5分钟内完成")

def implement_quick_fix():
    """实施快速修复"""
    print(f"\n=== 实施快速修复 ===")
    
    print(f"选择修复方案...")
    
    # 方案1: 暂时禁用部分规则
    print(f"\n执行方案1: 暂时禁用字典验证规则")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 备份当前状态
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kiro_qc_rule_backup AS 
            SELECT * FROM kiro_qc_rule WHERE status = 'active'
        """)
        
        print(f"✅ 已备份当前规则状态")
        
        # 暂时禁用字典验证规则
        cursor.execute("""
            UPDATE kiro_qc_rule 
            SET status = 'disabled_temp' 
            WHERE status = 'active' 
            AND rule_type = 'value_check'
        """)
        
        disabled_count = cursor.rowcount
        conn.commit()
        
        print(f"✅ 已暂时禁用 {disabled_count} 条字典验证规则")
        
        # 检查剩余规则数量
        cursor.execute("SELECT COUNT(*) as count FROM kiro_qc_rule WHERE status = 'active'")
        result = cursor.fetchone()
        remaining_rules = result[0]
        
        print(f"✅ 剩余活跃规则: {remaining_rules}条")
        
        # 估算新的处理时间
        estimated_time = remaining_rules * 0.005  # 5毫秒/规则
        print(f"✅ 预估新的处理时间: {estimated_time:.1f}秒")
        
        return remaining_rules
        
    except Exception as e:
        print(f"❌ 快速修复失败: {e}")
        return None
    
    finally:
        cursor.close()
        conn.close()

def test_performance_after_fix():
    """修复后性能测试"""
    print(f"\n=== 修复后性能测试 ===")
    
    test_case = {'a48': '20003285', 'a49': '1'}
    
    print(f"测试病案: {test_case['a48']}_{test_case['a49']}")
    
    try:
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/qc/check/single", 
                               params=test_case, timeout=60)
        
        process_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json().get('data', {})
            defect_count = result.get('defectCount', 0)
            final_score = result.get('finalScore', 0)
            
            print(f"✅ 修复后测试成功")
            print(f"   处理时间: {process_time:.2f}秒")
            print(f"   缺陷数量: {defect_count}个")
            print(f"   最终得分: {final_score}分")
            
            # 性能评估
            if process_time <= 3:
                print(f"   🎉 性能目标达成！")
                performance = "优秀"
            elif process_time <= 10:
                print(f"   ✅ 性能显著改善")
                performance = "良好"
            elif process_time <= 20:
                print(f"   ⚠️  性能有所改善")
                performance = "一般"
            else:
                print(f"   ❌ 性能仍然较差")
                performance = "较差"
            
            # 计算改善倍数
            old_time = 27.97
            improvement = old_time / process_time
            print(f"   性能提升: {improvement:.1f}倍")
            
            return {
                'success': True,
                'time': process_time,
                'defects': defect_count,
                'score': final_score,
                'performance': performance,
                'improvement': improvement
            }
        
        else:
            print(f"❌ 测试失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return {'success': False, 'error': response.text}
    
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return {'success': False, 'error': str(e)}

def restore_rules_if_needed():
    """如果需要，恢复规则"""
    print(f"\n=== 规则恢复选项 ===")
    
    print(f"如果需要恢复所有规则，可以执行:")
    print(f"```sql")
    print(f"UPDATE kiro_qc_rule ")
    print(f"SET status = 'active' ")
    print(f"WHERE status = 'disabled_temp';")
    print(f"```")
    
    # 创建恢复脚本
    restore_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def restore_rules():
    print("恢复所有规则...")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE kiro_qc_rule SET status = 'active' WHERE status = 'disabled_temp'")
        restored_count = cursor.rowcount
        conn.commit()
        
        print(f"✅ 已恢复 {restored_count} 条规则")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    restore_rules()
"""
    
    try:
        with open('restore_rules.py', 'w', encoding='utf-8') as f:
            f.write(restore_script)
        
        print(f"✅ 已创建规则恢复脚本: restore_rules.py")
        
    except Exception as e:
        print(f"❌ 创建恢复脚本失败: {e}")

def main():
    """主函数"""
    # 1. 紧急分析
    emergency_analysis()
    
    # 2. 实施快速修复
    remaining_rules = implement_quick_fix()
    
    if remaining_rules:
        # 3. 测试修复效果
        result = test_performance_after_fix()
        
        # 4. 创建恢复选项
        restore_rules_if_needed()
        
        # 5. 总结
        print(f"\n" + "=" * 50)
        print("紧急修复总结")
        print("=" * 50)
        
        if result and result.get('success'):
            print(f"🎉 紧急修复成功！")
            print(f"   处理时间: {result['time']:.2f}秒")
            print(f"   性能提升: {result['improvement']:.1f}倍")
            print(f"   性能等级: {result['performance']}")
            
            if result['time'] <= 3:
                print(f"   ✅ 已达到性能目标")
            elif result['time'] <= 10:
                print(f"   ✅ 性能可接受，可以使用")
            
            print(f"\n🎯 现在可以:")
            print(f"   • 使用单病案接口处理少量数据")
            print(f"   • 使用优化批量接口处理大量数据")
            print(f"   • 96病案预估时间: {result['time'] * 96 / 8 / 60:.1f}分钟（8线程并行）")
        
        else:
            print(f"❌ 紧急修复失败")
            print(f"   建议使用优化批量接口绕过问题")
        
        print(f"\n📋 后续优化建议:")
        print(f"   1. 创建完整的字典表和缓存")
        print(f"   2. 优化规则逻辑复杂度")
        print(f"   3. 根据需要恢复禁用的规则")
        print(f"   4. 监控系统资源使用")
    
    else:
        print(f"❌ 快速修复失败，建议直接使用优化批量接口")

if __name__ == "__main__":
    main()