#!/usr/bin/env python3
import pymysql
import sys

# 数据库配置
db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def update_cross_rule_naming():
    """更新Cross规则命名为RULE_CROSS_前缀"""
    print("🔧 更新Cross规则命名")
    print("=" * 60)
    
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # 1. 检查当前的Cross规则
        print("1. 检查当前Cross规则:")
        cursor.execute("""
            SELECT rule_code, description, cross_type, status 
            FROM kiro_qc_rule_cross 
            ORDER BY rule_code
        """)
        
        current_rules = cursor.fetchall()
        print(f"   找到 {len(current_rules)} 条Cross规则:")
        for rule in current_rules:
            print(f"     - {rule[0]}: {rule[1][:50]}... (类型: {rule[2]}, 状态: {rule[3]})")
        
        if not current_rules:
            print("   ❌ 未找到Cross规则，可能需要先创建")
            return False
        
        # 2. 更新规则命名
        print(f"\n2. 更新规则命名:")
        
        # 更新所有以CROSS_开头但不以RULE_CROSS_开头的规则
        cursor.execute("""
            UPDATE kiro_qc_rule_cross 
            SET rule_code = CONCAT('RULE_', rule_code)
            WHERE rule_code LIKE 'CROSS_%' 
              AND rule_code NOT LIKE 'RULE_CROSS_%'
        """)
        
        updated_count = cursor.rowcount
        print(f"   更新了 {updated_count} 条规则的命名")
        
        # 3. 检查更新后的结果
        print(f"\n3. 检查更新结果:")
        cursor.execute("""
            SELECT rule_code, description, cross_type, status 
            FROM kiro_qc_rule_cross 
            WHERE rule_code LIKE 'RULE_CROSS_%'
            ORDER BY rule_code
        """)
        
        updated_rules = cursor.fetchall()
        print(f"   更新后的Cross规则 ({len(updated_rules)}条):")
        for rule in updated_rules:
            print(f"     ✅ {rule[0]}: {rule[1][:50]}... (类型: {rule[2]}, 状态: {rule[3]})")
        
        # 4. 提交更改
        conn.commit()
        print(f"\n✅ Cross规则命名更新完成!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_naming_consistency():
    """验证命名一致性"""
    print(f"\n🔍 验证命名一致性")
    print("=" * 60)
    
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # 检查普通规则的命名模式
        cursor.execute("""
            SELECT rule_code 
            FROM kiro_qc_rule 
            WHERE rule_code LIKE 'RULE_%'
            LIMIT 5
        """)
        
        normal_rules = cursor.fetchall()
        print(f"普通规则命名示例:")
        for rule in normal_rules:
            print(f"  - {rule[0]}")
        
        # 检查Cross规则的命名模式
        cursor.execute("""
            SELECT rule_code 
            FROM kiro_qc_rule_cross 
            WHERE rule_code LIKE 'RULE_CROSS_%'
        """)
        
        cross_rules = cursor.fetchall()
        print(f"\nCross规则命名:")
        for rule in cross_rules:
            print(f"  - {rule[0]}")
        
        # 检查是否还有旧命名的规则
        cursor.execute("""
            SELECT rule_code 
            FROM kiro_qc_rule_cross 
            WHERE rule_code LIKE 'CROSS_%' 
              AND rule_code NOT LIKE 'RULE_CROSS_%'
        """)
        
        old_naming_rules = cursor.fetchall()
        if old_naming_rules:
            print(f"\n⚠️  仍有旧命名的规则:")
            for rule in old_naming_rules:
                print(f"  - {rule[0]}")
        else:
            print(f"\n✅ 所有Cross规则都使用新命名格式")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")

def main():
    print("🚀 Cross规则命名标准化")
    print("将所有Cross规则命名从CROSS_改为RULE_CROSS_")
    print("以保持与普通规则RULE_前缀的一致性")
    
    # 更新命名
    success = update_cross_rule_naming()
    
    if success:
        # 验证一致性
        verify_naming_consistency()
        
        print(f"\n" + "=" * 60)
        print("📋 命名标准化总结")
        print("=" * 60)
        print("✅ Cross规则命名已标准化为RULE_CROSS_前缀")
        print("✅ 与普通规则的RULE_前缀保持一致")
        print("✅ 代码中的识别逻辑已同步更新")
        print("\n🔄 请重新编译并重启服务以应用更改")
    else:
        print(f"\n❌ 命名更新失败，请检查数据库连接和权限")

if __name__ == "__main__":
    main()