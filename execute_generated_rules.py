#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行自动生成的质控规则SQL
将214条高置信度规则插入数据库
"""

import pymysql
import sys

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def main():
    """主函数"""
    print("="*100)
    print("  执行自动生成的质控规则SQL")
    print("="*100)
    
    # 连接数据库
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("\n✓ 数据库连接成功")
    except Exception as e:
        print(f"\n✗ 数据库连接失败: {str(e)}")
        sys.exit(1)
    
    cursor = conn.cursor()
    
    # 读取SQL文件
    sql_file = 'auto_generated_rules_fixed.sql'
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        print(f"✓ 读取SQL文件: {sql_file}")
    except Exception as e:
        print(f"✗ 读取SQL文件失败: {str(e)}")
        conn.close()
        sys.exit(1)
    
    # 分割SQL语句
    sql_statements = []
    for statement in sql_content.split(';'):
        statement = statement.strip()
        if statement and not statement.startswith('--'):
            sql_statements.append(statement)
    
    print(f"✓ 解析到 {len(sql_statements)} 条SQL语句")
    
    # 执行SQL语句
    success_count = 0
    error_count = 0
    errors = []
    
    print("\n开始执行SQL语句...")
    for i, sql in enumerate(sql_statements, 1):
        try:
            cursor.execute(sql)
            success_count += 1
            if i % 20 == 0:
                print(f"  已执行 {i}/{len(sql_statements)} 条...")
        except Exception as e:
            error_count += 1
            # 提取字段代码用于错误报告
            field_code = "未知"
            if "field_code" in sql:
                try:
                    start = sql.index("'", sql.index("field_code")) + 1
                    end = sql.index("'", start)
                    field_code = sql[start:end]
                except:
                    pass
            errors.append({
                'index': i,
                'field_code': field_code,
                'error': str(e)
            })
    
    # 提交事务
    try:
        conn.commit()
        print(f"\n✓ 事务已提交")
    except Exception as e:
        print(f"\n✗ 提交事务失败: {str(e)}")
        conn.rollback()
        conn.close()
        sys.exit(1)
    
    # 输出结果
    print("\n" + "="*100)
    print("执行结果")
    print("="*100)
    print(f"\n成功: {success_count} 条")
    print(f"失败: {error_count} 条")
    
    if errors:
        print("\n失败详情:")
        for err in errors[:10]:  # 只显示前10个错误
            print(f"  [{err['index']}] {err['field_code']}: {err['error']}")
        if len(errors) > 10:
            print(f"  ... 还有 {len(errors) - 10} 个错误")
    
    # 查询插入的规则数量
    cursor.execute("SELECT COUNT(*) FROM kiro_qc_rule WHERE status = 'draft'")
    draft_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM kiro_qc_rule")
    total_count = cursor.fetchone()[0]
    
    print(f"\n数据库中的规则统计:")
    print(f"  草稿规则: {draft_count} 条")
    print(f"  总规则数: {total_count} 条")
    
    conn.close()
    print("\n✓ 数据库连接已关闭")
    
    print("\n" + "="*100)
    print("完成！")
    print("="*100)
    print("\n下一步操作建议：")
    print("1. 使用规则测试API验证规则效果")
    print("2. 查看测试结果，确认规则是否正确")
    print("3. 将验证通过的规则状态从 'draft' 改为 'active'")
    print("4. 可以使用以下SQL批量激活规则：")
    print("   UPDATE kiro_qc_rule SET status = 'active' WHERE status = 'draft' AND field_code IN ('A01', 'A02', ...);")

if __name__ == "__main__":
    main()
