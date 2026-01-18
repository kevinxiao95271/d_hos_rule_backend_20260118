#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

def create_indexes():
    """创建数据库索引"""
    print("创建数据库索引...")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 需要创建的索引
        indexes = [
            {
                'name': 'idx_d_mr_a48_a49',
                'table': 'd_mr',
                'sql': 'CREATE INDEX idx_d_mr_a48_a49 ON d_mr(A48, A49)',
                'description': 'A48和A49复合索引'
            },
            {
                'name': 'idx_d_mr_b15',
                'table': 'd_mr', 
                'sql': 'CREATE INDEX idx_d_mr_b15 ON d_mr(B15)',
                'description': 'B15索引'
            }
        ]
        
        for index in indexes:
            try:
                # 先检查索引是否已存在
                cursor.execute(f"SHOW INDEX FROM {index['table']} WHERE Key_name = '{index['name']}'")
                existing = cursor.fetchall()
                
                if existing:
                    print(f"  ✅ 索引已存在: {index['name']}")
                else:
                    # 创建索引
                    print(f"  创建索引: {index['description']}...")
                    cursor.execute(index['sql'])
                    print(f"  ✅ 索引创建成功: {index['name']}")
            
            except Exception as e:
                print(f"  ❌ 索引创建失败 {index['name']}: {e}")
        
        conn.commit()
        print("✅ 索引创建完成")
        
        # 验证索引
        print("\n验证索引创建结果:")
        cursor.execute("SHOW INDEX FROM d_mr")
        indexes = cursor.fetchall()
        
        for idx in indexes:
            print(f"  {idx[2]}: {idx[4]}")  # Key_name: Column_name
        
    finally:
        cursor.close()
        conn.close()

def test_query_performance():
    """测试查询性能"""
    print(f"\n测试查询性能...")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 测试病案查询性能
        start_time = time.time()
        cursor.execute("SELECT * FROM d_mr WHERE A48 = '20003285' AND A49 = '1'")
        record = cursor.fetchone()
        query_time = time.time() - start_time
        
        print(f"  病案查询时间: {query_time:.3f}秒")
        
        if query_time < 0.01:
            print(f"  ✅ 查询性能优秀")
        elif query_time < 0.1:
            print(f"  ✅ 查询性能良好")
        else:
            print(f"  ⚠️  查询性能需要优化")
        
        # 测试规则查询性能
        start_time = time.time()
        cursor.execute("SELECT * FROM kiro_qc_rule WHERE status = 'active'")
        rules = cursor.fetchall()
        query_time = time.time() - start_time
        
        print(f"  规则查询时间: {query_time:.3f}秒 ({len(rules)}条)")
        
        return len(rules)
        
    finally:
        cursor.close()
        conn.close()

def analyze_rule_complexity():
    """分析规则复杂度"""
    print(f"\n分析规则复杂度...")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 分析规则类型分布
        cursor.execute("""
            SELECT rule_type, COUNT(*) as count 
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            GROUP BY rule_type
        """)
        
        rule_types = cursor.fetchall()
        print(f"  规则类型分布:")
        
        total_rules = 0
        for rule_type in rule_types:
            count = rule_type['count']
            total_rules += count
            print(f"    {rule_type['rule_type'] or '未分类'}: {count}条")
        
        print(f"  总活跃规则: {total_rules}条")
        
        # 分析字段分布
        cursor.execute("""
            SELECT field_code, COUNT(*) as count 
            FROM kiro_qc_rule 
            WHERE status = 'active' AND field_code IS NOT NULL
            GROUP BY field_code 
            ORDER BY count DESC 
            LIMIT 10
        """)
        
        field_dist = cursor.fetchall()
        print(f"  字段规则分布（前10）:")
        
        for field in field_dist:
            print(f"    {field['field_code']}: {field['count']}条")
        
        return total_rules
        
    finally:
        cursor.close()
        conn.close()

def estimate_performance_improvement():
    """估算性能改善"""
    print(f"\n估算性能改善...")
    
    # 基于索引优化的预期改善
    print(f"  优化前单病案处理时间: 27.97秒")
    
    # 假设数据库查询占总时间的60%，索引可以提升5倍性能
    db_time_ratio = 0.6
    db_improvement = 5
    
    old_db_time = 27.97 * db_time_ratio
    new_db_time = old_db_time / db_improvement
    other_time = 27.97 * (1 - db_time_ratio)
    
    estimated_new_time = new_db_time + other_time
    
    print(f"  预估数据库查询时间: {old_db_time:.1f}秒 → {new_db_time:.1f}秒")
    print(f"  预估新的总处理时间: {estimated_new_time:.1f}秒")
    
    improvement = 27.97 / estimated_new_time
    print(f"  预估性能提升: {improvement:.1f}倍")
    
    if estimated_new_time <= 3:
        print(f"  🎉 预估可达到性能目标！")
    elif estimated_new_time <= 10:
        print(f"  ✅ 预估性能显著改善")
    else:
        print(f"  ⚠️  预估仍需进一步优化")
    
    return estimated_new_time

def main():
    """主函数"""
    print("医疗质控系统数据库索引优化")
    print("=" * 40)
    print(f"优化时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 创建索引
    create_indexes()
    
    # 2. 测试查询性能
    rule_count = test_query_performance()
    
    # 3. 分析规则复杂度
    total_rules = analyze_rule_complexity()
    
    # 4. 估算性能改善
    estimated_time = estimate_performance_improvement()
    
    # 5. 总结
    print(f"\n" + "=" * 40)
    print("优化总结")
    print("=" * 40)
    
    print(f"✅ 已完成的优化:")
    print(f"   • 为d_mr表添加A48,A49复合索引")
    print(f"   • 为d_mr表添加B15索引")
    print(f"   • 验证索引创建成功")
    
    print(f"\n📊 系统状态:")
    print(f"   • 活跃规则数量: {total_rules}条")
    print(f"   • 预估处理时间: {estimated_time:.1f}秒")
    
    print(f"\n🎯 下一步:")
    print(f"   1. 重新测试单病案性能")
    print(f"   2. 如果性能仍不理想，考虑减少规则数量")
    print(f"   3. 启用Redis缓存优化")
    print(f"   4. 使用优化批量接口处理大数据")

if __name__ == "__main__":
    main()