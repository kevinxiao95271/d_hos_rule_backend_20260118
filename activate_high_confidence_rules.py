#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
激活高置信度规则
将明确的字段规则从draft改为active
"""

import pymysql

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

# 明确的高置信度字段（已知字段）
HIGH_CONFIDENCE_FIELDS = [
    'A01',  # 性别
    'A02',  # 婚姻状况
    'A16',  # 住院天数
    'A17',  # 离院方式
    'A20',  # ABO血型
    'A22',  # 病案质量
    'C22x01C',  # 主要手术操作麻醉方式
]

# 麻醉方式字段（C43x##C模式）
ANESTHESIA_FIELDS = [f'C43x{i:02d}C' for i in range(1, 41)]

# 切口愈合等级字段（C42x##D模式）
INCISION_FIELDS = [f'C42x{i:02d}D' for i in range(1, 41)]

def main():
    """主函数"""
    print("="*100)
    print("  激活高置信度质控规则")
    print("="*100)
    
    # 连接数据库
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 合并所有要激活的字段
    fields_to_activate = HIGH_CONFIDENCE_FIELDS + ANESTHESIA_FIELDS + INCISION_FIELDS
    
    print(f"\n准备激活 {len(fields_to_activate)} 个字段的规则")
    print(f"  - 明确字段: {len(HIGH_CONFIDENCE_FIELDS)} 个")
    print(f"  - 麻醉方式字段: {len(ANESTHESIA_FIELDS)} 个")
    print(f"  - 切口愈合等级字段: {len(INCISION_FIELDS)} 个")
    
    # 构建SQL
    field_list = "', '".join(fields_to_activate)
    sql = f"""
        UPDATE kiro_qc_rule
        SET status = 'active'
        WHERE status = 'draft'
        AND field_code IN ('{field_list}')
    """
    
    # 执行更新
    try:
        cursor.execute(sql)
        affected_rows = cursor.rowcount
        conn.commit()
        print(f"\n✓ 成功激活 {affected_rows} 条规则")
    except Exception as e:
        print(f"\n✗ 激活失败: {str(e)}")
        conn.rollback()
        conn.close()
        return
    
    # 查询统计
    cursor.execute("SELECT status, COUNT(*) as count FROM kiro_qc_rule GROUP BY status")
    stats = cursor.fetchall()
    
    print("\n规则状态统计:")
    for status, count in stats:
        print(f"  {status}: {count} 条")
    
    # 查询已激活的规则详情
    cursor.execute("""
        SELECT field_code, field_name, rule_type, dict_types
        FROM kiro_qc_rule
        WHERE status = 'active'
        AND field_code IN ('{}')
        ORDER BY field_code
    """.format(field_list))
    
    active_rules = cursor.fetchall()
    
    print(f"\n已激活的规则详情 (前20条):")
    for i, (field_code, field_name, rule_type, dict_types) in enumerate(active_rules[:20], 1):
        print(f"  {i:2d}. {field_code:15} {field_name:30} {rule_type:15} {dict_types}")
    
    if len(active_rules) > 20:
        print(f"  ... 还有 {len(active_rules) - 20} 条规则")
    
    conn.close()
    
    print("\n" + "="*100)
    print("完成！")
    print("="*100)
    print("\n已激活的规则可以在质控检查中使用")
    print("剩余的draft规则需要人工审核后再激活")

if __name__ == "__main__":
    main()
