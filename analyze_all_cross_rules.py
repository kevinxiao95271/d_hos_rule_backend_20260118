#!/usr/bin/env python3
import pymysql
import re

# 数据库配置
db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def analyze_all_cross_rules():
    """分析所有可能的Cross规则"""
    print("🔍 分析所有Cross规则")
    print("=" * 80)
    
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # 1. 检查kiro_qc_rule_cross表中的规则
        print("1. 检查专门的Cross规则表:")
        cursor.execute("SELECT COUNT(*) FROM kiro_qc_rule_cross")
        cross_table_count = cursor.fetchone()[0]
        print(f"   kiro_qc_rule_cross表中的规则: {cross_table_count}条")
        
        # 2. 检查普通规则表中包含cross关键词的规则
        print("\n2. 检查普通规则表中的cross相关规则:")
        
        # 查找规则代码包含cross的规则
        cursor.execute("""
            SELECT rule_code, description, field_code, status 
            FROM kiro_qc_rule 
            WHERE LOWER(rule_code) LIKE '%cross%' 
            ORDER BY rule_code
        """)
        
        cross_code_rules = cursor.fetchall()
        print(f"   规则代码包含'cross'的规则: {len(cross_code_rules)}条")
        
        if cross_code_rules:
            print("   示例规则:")
            for rule in cross_code_rules[:10]:  # 显示前10条
                print(f"     - {rule[0]}: {rule[1][:60]}... (字段: {rule[2]}, 状态: {rule[3]})")
            if len(cross_code_rules) > 10:
                print(f"     ... 还有 {len(cross_code_rules) - 10} 条规则")
        
        # 查找描述包含cross或跨字段的规则
        cursor.execute("""
            SELECT rule_code, description, field_code, status 
            FROM kiro_qc_rule 
            WHERE (LOWER(description) LIKE '%cross%' 
               OR description LIKE '%跨字段%'
               OR description LIKE '%配对%'
               OR description LIKE '%同时%'
               OR description LIKE '%一致%')
            AND LOWER(rule_code) NOT LIKE '%cross%'
            ORDER BY rule_code
        """)
        
        cross_desc_rules = cursor.fetchall()
        print(f"\n   描述包含跨字段逻辑的规则: {len(cross_desc_rules)}条")
        
        if cross_desc_rules:
            print("   示例规则:")
            for rule in cross_desc_rules[:10]:
                print(f"     - {rule[0]}: {rule[1][:60]}... (字段: {rule[2]})")
            if len(cross_desc_rules) > 10:
                print(f"     ... 还有 {len(cross_desc_rules) - 10} 条规则")
        
        # 3. 分析规则类型
        print("\n3. 分析可能的Cross规则类型:")
        
        # 字段配对类型
        cursor.execute("""
            SELECT COUNT(*) FROM kiro_qc_rule 
            WHERE (description LIKE '%为空%' AND description LIKE '%不为空%')
               OR (description LIKE '%同时有值%')
               OR (description LIKE '%同时为空%')
               OR (description LIKE '%配对%')
        """)
        field_pair_count = cursor.fetchone()[0]
        print(f"   字段配对类型: ~{field_pair_count}条")
        
        # 年龄相关
        cursor.execute("""
            SELECT COUNT(*) FROM kiro_qc_rule 
            WHERE description LIKE '%岁%' 
               OR description LIKE '%年龄%'
               OR description LIKE '%儿童%'
               OR description LIKE '%成人%'
        """)
        age_related_count = cursor.fetchone()[0]
        print(f"   年龄相关类型: ~{age_related_count}条")
        
        # 性别相关
        cursor.execute("""
            SELECT COUNT(*) FROM kiro_qc_rule 
            WHERE description LIKE '%男性%' 
               OR description LIKE '%女性%'
               OR description LIKE '%性别%'
               OR description LIKE '%妇科%'
        """)
        gender_related_count = cursor.fetchone()[0]
        print(f"   性别相关类型: ~{gender_related_count}条")
        
        # 条件必填
        cursor.execute("""
            SELECT COUNT(*) FROM kiro_qc_rule 
            WHERE description LIKE '%时必填%' 
               OR description LIKE '%属性为%'
               OR description LIKE '%条件%'
        """)
        conditional_count = cursor.fetchone()[0]
        print(f"   条件必填类型: ~{conditional_count}条")
        
        # 4. 总体统计
        total_potential_cross = len(cross_code_rules) + len(cross_desc_rules)
        print(f"\n4. 总体统计:")
        print(f"   专门Cross规则表: {cross_table_count}条")
        print(f"   普通表中的潜在Cross规则: {total_potential_cross}条")
        print(f"   总计: {cross_table_count + total_potential_cross}条")
        
        # 5. 详细分析一些典型的cross规则
        print(f"\n5. 典型Cross规则分析:")
        
        cursor.execute("""
            SELECT rule_code, description, field_code 
            FROM kiro_qc_rule 
            WHERE LOWER(rule_code) LIKE '%cross%' 
            ORDER BY rule_code
            LIMIT 20
        """)
        
        sample_rules = cursor.fetchall()
        
        rule_patterns = {
            'field_pair': 0,
            'age_related': 0,
            'gender_related': 0,
            'conditional': 0,
            'logic_check': 0
        }
        
        for rule in sample_rules:
            rule_code, description, field_code = rule
            desc_lower = description.lower()
            
            if any(keyword in desc_lower for keyword in ['为空', '不为空', '同时', '配对']):
                rule_patterns['field_pair'] += 1
            elif any(keyword in desc_lower for keyword in ['岁', '年龄', '儿童', '成人']):
                rule_patterns['age_related'] += 1
            elif any(keyword in desc_lower for keyword in ['男性', '女性', '性别', '妇科']):
                rule_patterns['gender_related'] += 1
            elif any(keyword in desc_lower for keyword in ['必填', '属性', '条件']):
                rule_patterns['conditional'] += 1
            else:
                rule_patterns['logic_check'] += 1
        
        print(f"   规则模式分布 (基于前20条样本):")
        for pattern, count in rule_patterns.items():
            print(f"     {pattern}: {count}条")
        
        cursor.close()
        conn.close()
        
        return {
            'cross_table_count': cross_table_count,
            'cross_code_rules': len(cross_code_rules),
            'cross_desc_rules': len(cross_desc_rules),
            'total_potential': total_potential_cross + cross_table_count
        }
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_cross_rule_samples():
    """获取Cross规则样本"""
    print(f"\n🔬 获取Cross规则样本")
    print("=" * 80)
    
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # 获取不同类型的样本
        samples = {}
        
        # 1. 字段配对样本
        cursor.execute("""
            SELECT rule_code, description, field_code 
            FROM kiro_qc_rule 
            WHERE (description LIKE '%为空%' AND description LIKE '%不为空%')
               OR description LIKE '%同时有值%'
               OR description LIKE '%同时为空%'
            LIMIT 5
        """)
        samples['field_pair'] = cursor.fetchall()
        
        # 2. 年龄相关样本
        cursor.execute("""
            SELECT rule_code, description, field_code 
            FROM kiro_qc_rule 
            WHERE description LIKE '%岁%' 
               OR description LIKE '%年龄%'
               OR description LIKE '%儿童%'
            LIMIT 5
        """)
        samples['age_related'] = cursor.fetchall()
        
        # 3. 性别相关样本
        cursor.execute("""
            SELECT rule_code, description, field_code 
            FROM kiro_qc_rule 
            WHERE description LIKE '%男性%' 
               OR description LIKE '%女性%'
               OR description LIKE '%妇科%'
            LIMIT 5
        """)
        samples['gender_related'] = cursor.fetchall()
        
        # 4. 条件必填样本
        cursor.execute("""
            SELECT rule_code, description, field_code 
            FROM kiro_qc_rule 
            WHERE description LIKE '%时必填%' 
               OR description LIKE '%属性为%'
            LIMIT 5
        """)
        samples['conditional'] = cursor.fetchall()
        
        # 显示样本
        for category, rules in samples.items():
            if rules:
                print(f"\n📋 {category} 样本:")
                for rule in rules:
                    print(f"   - {rule[0]}")
                    print(f"     字段: {rule[2]}")
                    print(f"     描述: {rule[1][:80]}...")
                    print()
        
        cursor.close()
        conn.close()
        
        return samples
        
    except Exception as e:
        print(f"❌ 获取样本失败: {e}")
        return {}

def recommend_cross_rule_migration():
    """推荐Cross规则迁移策略"""
    print(f"\n💡 Cross规则迁移建议")
    print("=" * 80)
    
    print(f"基于分析结果，建议采用以下迁移策略:")
    
    print(f"\n1. 立即迁移 (高优先级):")
    print(f"   - 规则代码明确包含'cross'的规则")
    print(f"   - 描述明确提到'跨字段'、'配对'的规则")
    print(f"   - 涉及多个字段逻辑关系的规则")
    
    print(f"\n2. 逐步迁移 (中优先级):")
    print(f"   - 年龄与诊断相关的逻辑规则")
    print(f"   - 性别与诊断相关的逻辑规则")
    print(f"   - 条件必填类型的规则")
    
    print(f"\n3. 评估后迁移 (低优先级):")
    print(f"   - 复杂的业务逻辑规则")
    print(f"   - 需要重新设计的规则")
    
    print(f"\n🔧 迁移工具建议:")
    print(f"   - 创建自动化迁移脚本")
    print(f"   - 批量转换规则格式")
    print(f"   - 验证迁移后的规则正确性")
    print(f"   - 保留原规则作为备份")

def main():
    print("🚀 全面Cross规则分析")
    
    # 分析所有Cross规则
    stats = analyze_all_cross_rules()
    
    if stats:
        # 获取样本
        get_cross_rule_samples()
        
        # 推荐迁移策略
        recommend_cross_rule_migration()
        
        print(f"\n" + "=" * 80)
        print("📊 分析总结")
        print("=" * 80)
        
        print(f"🎯 Cross规则现状:")
        print(f"   专门Cross规则表: {stats['cross_table_count']}条")
        print(f"   普通表中包含'cross'的规则: {stats['cross_code_rules']}条")
        print(f"   普通表中描述涉及跨字段的规则: {stats['cross_desc_rules']}条")
        print(f"   总计潜在Cross规则: {stats['total_potential']}条")
        
        print(f"\n💡 建议:")
        if stats['total_potential'] > 100:
            print(f"   ⚠️  发现大量潜在Cross规则，建议:")
            print(f"   1. 创建批量迁移工具")
            print(f"   2. 分阶段迁移，优先处理明确的Cross规则")
            print(f"   3. 建立Cross规则管理流程")
            print(f"   4. 更新前端文档，说明可能的大量Cross规则")
        else:
            print(f"   ✅ Cross规则数量适中，可以逐步迁移")

if __name__ == "__main__":
    main()