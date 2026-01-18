#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

def restore_all_rules():
    """恢复所有规则到active状态"""
    print("=== 恢复所有规则到active状态 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 查看当前规则状态
        print("1. 当前规则状态统计:")
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM kiro_qc_rule 
            GROUP BY status
            ORDER BY count DESC
        """)
        current_status = cursor.fetchall()
        
        for stat in current_status:
            print(f"  {stat['status']}: {stat['count']}条")
        
        # 2. 恢复所有规则
        print(f"\n2. 恢复所有规则...")
        cursor.execute("UPDATE kiro_qc_rule SET status = 'active'")
        updated_count = cursor.rowcount
        conn.commit()
        
        print(f"✅ 已恢复 {updated_count} 条规则")
        
        # 3. 验证恢复结果
        print(f"\n3. 恢复后规则统计:")
        cursor.execute("""
            SELECT rule_type, COUNT(*) as count
            FROM kiro_qc_rule 
            WHERE status = 'active'
            GROUP BY rule_type
            ORDER BY count DESC
        """)
        restored_stats = cursor.fetchall()
        
        total_active = 0
        for stat in restored_stats:
            print(f"  {stat['rule_type']}: {stat['count']}条")
            total_active += stat['count']
        
        print(f"\n总计激活规则: {total_active}条")
        
        # 4. 显示规则类型分布
        print(f"\n4. 规则类型详细分布:")
        cursor.execute("""
            SELECT rule_type, 
                   COUNT(*) as total_count,
                   COUNT(CASE WHEN dict_types IS NOT NULL THEN 1 END) as dict_rules,
                   COUNT(CASE WHEN dict_types IS NULL THEN 1 END) as non_dict_rules
            FROM kiro_qc_rule 
            WHERE status = 'active'
            GROUP BY rule_type
            ORDER BY total_count DESC
        """)
        detailed_stats = cursor.fetchall()
        
        print(f"{'规则类型':<20} {'总数':<8} {'字典规则':<10} {'非字典规则':<10}")
        print("-" * 60)
        
        for stat in detailed_stats:
            print(f"{stat['rule_type']:<20} {stat['total_count']:<8} {stat['dict_rules']:<10} {stat['non_dict_rules']:<10}")
        
        return total_active
        
    finally:
        cursor.close()
        conn.close()

def analyze_performance_impact():
    """分析性能影响"""
    print(f"\n=== 分析性能影响 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 统计字典验证规则数量
        cursor.execute("""
            SELECT COUNT(*) as dict_rule_count
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            AND rule_type = 'value_check'
            AND dict_types IS NOT NULL
        """)
        dict_rule_count = cursor.fetchone()['dict_rule_count']
        
        # 统计涉及的字典类型
        cursor.execute("""
            SELECT DISTINCT dict_types
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            AND rule_type = 'value_check'
            AND dict_types IS NOT NULL
        """)
        dict_types = cursor.fetchall()
        
        unique_dict_types = set()
        for dt in dict_types:
            if dt['dict_types']:
                unique_dict_types.add(dt['dict_types'])
        
        print(f"字典验证规则数量: {dict_rule_count}")
        print(f"涉及的字典类型数量: {len(unique_dict_types)}")
        print(f"主要字典类型: {', '.join(list(unique_dict_types)[:10])}")
        
        # 估算性能影响
        print(f"\n性能影响估算:")
        print(f"- 每个病案可能触发的字典验证: ~{dict_rule_count}次")
        print(f"- Redis缓存命中情况下单次验证: ~1ms")
        print(f"- 估算每病案字典验证总时间: ~{dict_rule_count}ms")
        
        return dict_rule_count
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # 恢复所有规则
    total_rules = restore_all_rules()
    
    # 分析性能影响
    dict_rules = analyze_performance_impact()
    
    print(f"\n=== 恢复完成 ===")
    print(f"✅ 总规则数: {total_rules}")
    print(f"✅ 字典规则数: {dict_rules}")
    print(f"✅ 所有规则已恢复为active状态")
    print(f"\n下一步: 重启服务并进行完整规则集基准测试")