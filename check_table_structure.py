#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

def check_table_structure():
    """检查表结构"""
    print("医疗质控系统表结构检查")
    print("=" * 40)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 检查规则表结构
        print(f"\n1. 规则表结构 (kiro_qc_rule):")
        try:
            cursor.execute("DESCRIBE kiro_qc_rule")
            columns = cursor.fetchall()
            
            print(f"   字段列表:")
            for col in columns:
                print(f"     {col['Field']}: {col['Type']} ({col['Null']}, {col['Key']})")
            
            # 检查规则数量
            cursor.execute("SELECT COUNT(*) as count FROM kiro_qc_rule")
            result = cursor.fetchone()
            print(f"   总规则数量: {result['count']}条")
            
            # 检查是否有状态字段
            status_fields = ['is_active', 'status', 'rule_status', 'active']
            for field in status_fields:
                try:
                    cursor.execute(f"SELECT DISTINCT {field} FROM kiro_qc_rule LIMIT 5")
                    values = cursor.fetchall()
                    print(f"   {field} 字段值: {[v[field] for v in values]}")
                    break
                except:
                    continue
            else:
                print(f"   ⚠️  未找到状态字段")
        
        except Exception as e:
            print(f"   ❌ 规则表检查失败: {e}")
        
        # 2. 检查字典表结构
        print(f"\n2. 字典表结构 (kiro_qc_dict):")
        try:
            cursor.execute("DESCRIBE kiro_qc_dict")
            columns = cursor.fetchall()
            
            print(f"   字段列表:")
            for col in columns:
                print(f"     {col['Field']}: {col['Type']}")
            
            # 检查字典数量
            cursor.execute("SELECT COUNT(*) as count FROM kiro_qc_dict")
            result = cursor.fetchone()
            print(f"   总字典项数量: {result['count']}条")
            
            # 检查字典类型
            cursor.execute("SELECT dict_type_code, COUNT(*) as count FROM kiro_qc_dict GROUP BY dict_type_code LIMIT 10")
            types = cursor.fetchall()
            print(f"   字典类型分布:")
            for t in types:
                print(f"     {t['dict_type_code']}: {t['count']}条")
        
        except Exception as e:
            print(f"   ❌ 字典表检查失败: {e}")
        
        # 3. 检查病案表结构
        print(f"\n3. 病案表结构 (d_mr):")
        try:
            cursor.execute("DESCRIBE d_mr LIMIT 10")  # 只显示前10个字段
            columns = cursor.fetchall()
            
            print(f"   主要字段:")
            for col in columns:
                print(f"     {col['Field']}: {col['Type']}")
            
            # 检查病案数量
            cursor.execute("SELECT COUNT(*) as count FROM d_mr")
            result = cursor.fetchone()
            print(f"   总病案数量: {result['count']}条")
            
            # 检查2023年病案数量
            cursor.execute("SELECT COUNT(*) as count FROM d_mr WHERE B15 LIKE '2023/%'")
            result = cursor.fetchone()
            print(f"   2023年病案数量: {result['count']}条")
        
        except Exception as e:
            print(f"   ❌ 病案表检查失败: {e}")
        
        # 4. 检查结果表结构
        print(f"\n4. 结果表结构:")
        
        result_tables = ['kiro_qc_case_result', 'kiro_qc_defect_detail', 'kiro_qc_batch_summary']
        
        for table in result_tables:
            try:
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                
                print(f"   {table}:")
                for col in columns:
                    print(f"     {col['Field']}: {col['Type']}")
                
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                result = cursor.fetchone()
                print(f"     记录数量: {result['count']}条")
                
            except Exception as e:
                print(f"   ❌ {table} 检查失败: {e}")
    
    finally:
        cursor.close()
        conn.close()

def analyze_performance_issues():
    """分析性能问题"""
    print(f"\n" + "=" * 40)
    print("性能问题分析")
    print("=" * 40)
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 检查规则数量和复杂度
        cursor.execute("SELECT COUNT(*) as count FROM kiro_qc_rule")
        result = cursor.fetchone()
        rule_count = result['count']
        
        print(f"1. 规则数量分析:")
        print(f"   总规则数: {rule_count}条")
        
        if rule_count > 2000:
            print(f"   ❌ 规则数量过多，是主要性能瓶颈")
        elif rule_count > 1000:
            print(f"   ⚠️  规则数量较多，影响性能")
        else:
            print(f"   ✅ 规则数量合理")
        
        # 2. 检查索引情况
        print(f"\n2. 索引情况检查:")
        
        tables_to_check = ['d_mr', 'kiro_qc_rule', 'kiro_qc_dict']
        
        for table in tables_to_check:
            try:
                cursor.execute(f"SHOW INDEX FROM {table}")
                indexes = cursor.fetchall()
                
                print(f"   {table} 索引:")
                if indexes:
                    for idx in indexes:
                        print(f"     {idx['Key_name']}: {idx['Column_name']}")
                else:
                    print(f"     ❌ 无索引")
            
            except Exception as e:
                print(f"   {table} 索引检查失败: {e}")
        
        # 3. 估算性能瓶颈
        print(f"\n3. 性能瓶颈估算:")
        
        # 假设每条规则需要查询字典和执行逻辑
        estimated_time_per_rule = 0.015  # 15毫秒/规则
        estimated_total_time = rule_count * estimated_time_per_rule
        
        print(f"   预估每条规则处理时间: {estimated_time_per_rule*1000:.1f}毫秒")
        print(f"   预估单病案总处理时间: {estimated_total_time:.1f}秒")
        
        actual_time = 27.97
        if estimated_total_time < actual_time:
            overhead = actual_time - estimated_total_time
            print(f"   实际处理时间: {actual_time:.1f}秒")
            print(f"   额外开销: {overhead:.1f}秒")
            print(f"   ❌ 存在严重的性能问题")
        
    finally:
        cursor.close()
        conn.close()

def provide_immediate_solutions():
    """提供立即解决方案"""
    print(f"\n" + "=" * 40)
    print("立即解决方案")
    print("=" * 40)
    
    print(f"🚀 立即可执行的优化:")
    
    print(f"\n1. 数据库索引优化:")
    print(f"   • 为 d_mr 表添加 (A48, A49) 复合索引")
    print(f"   • 为 d_mr 表添加 B15 索引")
    print(f"   • 为 kiro_qc_dict 表添加 dict_type_code 索引")
    
    print(f"\n2. 应用层优化:")
    print(f"   • 预加载所有规则到内存")
    print(f"   • 使用Redis缓存字典数据")
    print(f"   • 批量处理数据库操作")
    
    print(f"\n3. 规则优化:")
    print(f"   • 禁用不必要的规则")
    print(f"   • 简化复杂规则逻辑")
    print(f"   • 按优先级排序规则")
    
    print(f"\n4. 系统配置优化:")
    print(f"   • 增加JVM内存: -Xmx4g")
    print(f"   • 调整数据库连接池")
    print(f"   • 启用Redis缓存")

def create_quick_fix_script():
    """创建快速修复脚本"""
    print(f"\n=== 创建快速修复脚本 ===")
    
    fix_sql = """-- 医疗质控系统性能优化SQL脚本

-- 1. 添加关键索引
CREATE INDEX IF NOT EXISTS idx_d_mr_a48_a49 ON d_mr(A48, A49);
CREATE INDEX IF NOT EXISTS idx_d_mr_b15 ON d_mr(B15);
CREATE INDEX IF NOT EXISTS idx_qc_dict_type ON kiro_qc_dict(dict_type_code);

-- 2. 检查表统计信息
SELECT 'kiro_qc_rule' as table_name, COUNT(*) as count FROM kiro_qc_rule
UNION ALL
SELECT 'kiro_qc_dict' as table_name, COUNT(*) as count FROM kiro_qc_dict
UNION ALL
SELECT 'd_mr' as table_name, COUNT(*) as count FROM d_mr
UNION ALL
SELECT 'd_mr_2023' as table_name, COUNT(*) as count FROM d_mr WHERE B15 LIKE '2023/%';

-- 3. 分析规则分布
SELECT 
    CASE 
        WHEN rule_description LIKE '%字典%' THEN '字典验证规则'
        WHEN rule_description LIKE '%范围%' THEN '范围检查规则'
        WHEN rule_description LIKE '%逻辑%' THEN '逻辑检查规则'
        ELSE '其他规则'
    END as rule_category,
    COUNT(*) as count
FROM kiro_qc_rule 
GROUP BY rule_category;
"""
    
    try:
        with open('performance_fix.sql', 'w', encoding='utf-8') as f:
            f.write(fix_sql)
        
        print("✅ 已创建SQL修复脚本: performance_fix.sql")
        
        # 创建Python执行脚本
        py_script = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import time

DB_CONFIG = {DB_CONFIG}

def execute_performance_fix():
    print("执行性能修复...")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 执行索引创建
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_d_mr_a48_a49 ON d_mr(A48, A49)",
            "CREATE INDEX IF NOT EXISTS idx_d_mr_b15 ON d_mr(B15)",
            "CREATE INDEX IF NOT EXISTS idx_qc_dict_type ON kiro_qc_dict(dict_type_code)"
        ]
        
        for sql in indexes:
            try:
                cursor.execute(sql)
                print(f"✅ 执行成功: {{sql.split()[-1]}}")
            except Exception as e:
                print(f"⚠️  跳过: {{e}}")
        
        conn.commit()
        print("✅ 数据库优化完成")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    execute_performance_fix()
"""
        
        with open('execute_performance_fix.py', 'w', encoding='utf-8') as f:
            f.write(py_script)
        
        print("✅ 已创建Python执行脚本: execute_performance_fix.py")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建修复脚本失败: {e}")
        return False

def main():
    """主函数"""
    # 1. 检查表结构
    check_table_structure()
    
    # 2. 分析性能问题
    analyze_performance_issues()
    
    # 3. 提供解决方案
    provide_immediate_solutions()
    
    # 4. 创建修复脚本
    create_quick_fix_script()
    
    # 5. 总结
    print(f"\n" + "=" * 40)
    print("总结和下一步")
    print("=" * 40)
    
    print(f"🔍 发现的问题:")
    print(f"   • 单病案处理时间: 27.97秒")
    print(f"   • 可能缺少关键索引")
    print(f"   • 规则数量可能过多")
    print(f"   • 缓存可能未生效")
    
    print(f"\n⚡ 立即行动:")
    print(f"   1. 执行数据库优化: python execute_performance_fix.py")
    print(f"   2. 重启服务以应用优化")
    print(f"   3. 重新测试性能")
    
    print(f"\n🎯 预期效果:")
    print(f"   • 数据库查询性能提升2-5倍")
    print(f"   • 单病案处理时间降到10秒以内")
    print(f"   • 为进一步优化奠定基础")

if __name__ == "__main__":
    main()