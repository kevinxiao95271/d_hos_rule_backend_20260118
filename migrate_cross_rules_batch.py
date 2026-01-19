#!/usr/bin/env python3
import pymysql
import re
import json
from datetime import datetime

# 数据库配置
db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def analyze_cross_rule_type(rule_code, description):
    """分析Cross规则类型"""
    desc_lower = description.lower()
    
    # 字段配对
    if any(keyword in desc_lower for keyword in ['为空', '不为空', '同时有值', '同时为空', '配对']):
        return 'field_pair'
    
    # 年龄相关
    elif any(keyword in desc_lower for keyword in ['岁', '年龄', '儿童', '成人', '周岁', '天']):
        return 'age_diagnosis'
    
    # 性别相关
    elif any(keyword in desc_lower for keyword in ['男性', '女性', '性别', '妇科']):
        return 'age_gender'
    
    # 条件必填
    elif any(keyword in desc_lower for keyword in ['必填', '属性为', '时必', '当']):
        return 'conditional_required'
    
    # 输血相关
    elif any(keyword in desc_lower for keyword in ['输血', '血液', '血费']):
        return 'transfusion_logic'
    
    # 日期一致性
    elif any(keyword in desc_lower for keyword in ['日期', '时间', '一致']):
        return 'date_consistency'
    
    # 默认逻辑检查
    else:
        return 'logic_check'

def extract_involved_fields(rule_code, description, field_code):
    """提取涉及的字段"""
    involved_fields = [field_code]
    
    # 从描述中提取其他字段
    field_pattern = r'[A-Z]\d+[A-Za-z]*(?:x\d+[A-Za-z]*)?'
    found_fields = re.findall(field_pattern, description)
    
    for field in found_fields:
        if field not in involved_fields and field != field_code:
            involved_fields.append(field)
    
    return involved_fields

def determine_severity(cross_type, deduct_score):
    """确定严重程度"""
    if deduct_score >= 3.0:
        return 'high'
    elif deduct_score >= 1.0:
        return 'medium'
    else:
        return 'low'

def migrate_cross_rules_batch():
    """批量迁移Cross规则"""
    print("🚀 批量迁移Cross规则")
    print("=" * 80)
    
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # 1. 获取所有需要迁移的Cross规则
        print("1. 获取需要迁移的Cross规则...")
        cursor.execute("""
            SELECT id, rule_code, description, field_code, deduct_score, status
            FROM kiro_qc_rule 
            WHERE LOWER(rule_code) LIKE '%cross%'
            ORDER BY rule_code
        """)
        
        cross_rules = cursor.fetchall()
        print(f"   找到 {len(cross_rules)} 条Cross规则需要迁移")
        
        if not cross_rules:
            print("   没有找到需要迁移的规则")
            return
        
        # 2. 检查目标表是否存在
        cursor.execute("SHOW TABLES LIKE 'kiro_qc_rule_cross'")
        if not cursor.fetchone():
            print("   ❌ kiro_qc_rule_cross表不存在，请先创建")
            return
        
        # 3. 批量迁移
        print("\n2. 开始批量迁移...")
        
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        for rule in cross_rules:
            rule_id, rule_code, description, field_code, deduct_score, status = rule
            
            try:
                # 检查是否已经存在
                new_rule_code = f"RULE_CROSS_{rule_code.replace('_cross_check', '').replace('cross_check', '').upper()}"
                
                cursor.execute("""
                    SELECT COUNT(*) FROM kiro_qc_rule_cross 
                    WHERE rule_code = %s
                """, (new_rule_code,))
                
                if cursor.fetchone()[0] > 0:
                    skipped_count += 1
                    continue
                
                # 分析规则类型和涉及字段
                cross_type = analyze_cross_rule_type(rule_code, description)
                involved_fields = extract_involved_fields(rule_code, description, field_code)
                severity = determine_severity(cross_type, deduct_score or 0)
                
                # 插入到Cross规则表
                cursor.execute("""
                    INSERT INTO kiro_qc_rule_cross (
                        rule_code, description, cross_type, primary_field, 
                        related_fields, deduct_score, status, severity,
                        created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    new_rule_code,
                    description,
                    cross_type,
                    field_code,
                    json.dumps([{"field": f, "name": f} for f in involved_fields[1:]]) if len(involved_fields) > 1 else '[]',
                    deduct_score or 0,
                    status,
                    severity,
                    datetime.now(),
                    datetime.now()
                ))
                
                migrated_count += 1
                
                if migrated_count % 50 == 0:
                    print(f"   已迁移 {migrated_count} 条规则...")
                
            except Exception as e:
                error_count += 1
                print(f"   ❌ 迁移规则失败 {rule_code}: {e}")
        
        # 提交事务
        conn.commit()
        
        print(f"\n3. 迁移完成:")
        print(f"   成功迁移: {migrated_count} 条")
        print(f"   跳过重复: {skipped_count} 条")
        print(f"   迁移失败: {error_count} 条")
        print(f"   总计处理: {len(cross_rules)} 条")
        
        # 4. 验证迁移结果
        print(f"\n4. 验证迁移结果:")
        cursor.execute("SELECT COUNT(*) FROM kiro_qc_rule_cross")
        total_cross_rules = cursor.fetchone()[0]
        print(f"   Cross规则表总数: {total_cross_rules} 条")
        
        # 按类型统计
        cursor.execute("""
            SELECT cross_type, COUNT(*) 
            FROM kiro_qc_rule_cross 
            GROUP BY cross_type 
            ORDER BY COUNT(*) DESC
        """)
        
        type_stats = cursor.fetchall()
        print(f"   按类型分布:")
        for cross_type, count in type_stats:
            print(f"     {cross_type}: {count} 条")
        
        cursor.close()
        conn.close()
        
        return {
            'migrated': migrated_count,
            'skipped': skipped_count,
            'errors': error_count,
            'total': len(cross_rules)
        }
        
    except Exception as e:
        print(f"❌ 批量迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def update_rule_engine_for_large_cross_rules():
    """更新规则引擎以处理大量Cross规则"""
    print(f"\n🔧 优化建议：处理大量Cross规则")
    print("=" * 80)
    
    print(f"由于发现了大量Cross规则，建议进行以下优化:")
    
    print(f"\n1. 性能优化:")
    print(f"   - 增加Cross规则缓存时间")
    print(f"   - 实现规则分批加载")
    print(f"   - 添加规则执行优先级")
    print(f"   - 优化数据库查询")
    
    print(f"\n2. 内存管理:")
    print(f"   - 实现规则懒加载")
    print(f"   - 添加规则LRU缓存")
    print(f"   - 定期清理无用规则")
    
    print(f"\n3. 前端适配:")
    print(f"   - 实现Cross规则分页展示")
    print(f"   - 添加规则类型过滤")
    print(f"   - 优化大量违规的展示性能")
    
    print(f"\n4. 监控告警:")
    print(f"   - 监控Cross规则执行时间")
    print(f"   - 统计规则触发频率")
    print(f"   - 设置性能阈值告警")

def create_optimized_cross_rule_config():
    """创建优化的Cross规则配置"""
    config = """
# Cross规则优化配置

## 缓存配置
cross.rules.cache.ttl=10m
cross.rules.cache.max-size=1000
cross.rules.lazy-loading=true

## 性能配置
cross.rules.batch-size=100
cross.rules.max-concurrent=10
cross.rules.timeout=30s

## 前端配置
cross.defects.page-size=20
cross.defects.max-display=100
cross.defects.group-by-type=true
"""
    
    with open('cross_rules_optimization.properties', 'w', encoding='utf-8') as f:
        f.write(config)
    
    print(f"\n✅ 已生成优化配置文件: cross_rules_optimization.properties")

def main():
    print("🚀 Cross规则大规模迁移")
    
    # 执行批量迁移
    result = migrate_cross_rules_batch()
    
    if result:
        # 提供优化建议
        update_rule_engine_for_large_cross_rules()
        
        # 创建优化配置
        create_optimized_cross_rule_config()
        
        print(f"\n" + "=" * 80)
        print("📊 迁移总结")
        print("=" * 80)
        
        print(f"🎯 迁移结果:")
        print(f"   成功迁移: {result['migrated']} 条")
        print(f"   跳过重复: {result['skipped']} 条")
        print(f"   迁移失败: {result['errors']} 条")
        print(f"   迁移成功率: {result['migrated']/(result['total']-result['skipped'])*100:.1f}%")
        
        print(f"\n⚠️  重要提醒:")
        print(f"   - Cross规则数量庞大，需要优化性能")
        print(f"   - 前端需要适配大量Cross规则的展示")
        print(f"   - 建议分阶段启用Cross规则")
        print(f"   - 需要监控系统性能影响")
        
        print(f"\n🔄 下一步:")
        print(f"   1. 重新编译并重启服务")
        print(f"   2. 测试大量Cross规则的性能")
        print(f"   3. 更新前端文档")
        print(f"   4. 实施性能优化措施")

if __name__ == "__main__":
    main()