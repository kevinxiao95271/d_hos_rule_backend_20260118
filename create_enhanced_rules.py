#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建增强的质控规则
自动识别字段所在表和字典类型
"""

import pymysql
import requests
import json
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

BASE_URL = "http://localhost:4101"

def search_field(field_code):
    """搜索字段所在的表"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/dict/field/search",
            params={"fieldCode": field_code}
        )
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200 and data['data']['foundInTables']:
                tables = [t['tableName'] for t in data['data']['foundInTables']]
                return ','.join(tables)
        return None
    except Exception as e:
        print(f"搜索字段 {field_code} 失败: {str(e)}")
        return None

def create_rule(conn, rule_data):
    """创建规则"""
    cursor = conn.cursor()
    
    sql = """
    INSERT INTO kiro_qc_rule (
        field_code, field_name, rule_type, rule_expression,
        error_message, score, status, source_tables, dict_types,
        created_at, updated_at
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
    )
    """
    
    try:
        cursor.execute(sql, (
            rule_data['field_code'],
            rule_data['field_name'],
            rule_data['rule_type'],
            rule_data['rule_expression'],
            rule_data['error_message'],
            rule_data['score'],
            rule_data['status'],
            rule_data['source_tables'],
            rule_data['dict_types']
        ))
        conn.commit()
        print(f"✓ 创建规则: {rule_data['field_name']} ({rule_data['field_code']})")
        return True
    except Exception as e:
        print(f"✗ 创建规则失败: {rule_data['field_name']} - {str(e)}")
        conn.rollback()
        return False

def main():
    """主函数"""
    print("="*80)
    print("  创建增强的质控规则")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 连接数据库
    conn = pymysql.connect(**DB_CONFIG)
    print("\n✓ 数据库连接成功")
    
    # 定义规则列表
    rules = [
        # 1. 其他手术操作3麻醉方式 - 交叉验证
        {
            'field_code': 'C43x03C',
            'field_name': '其他手术操作3麻醉方式',
            'rule_type': 'cross_check_null',
            'rule_expression': 'IF C43x03 IS_SURGERY THEN C43x03C NOT_NULL',
            'error_message': '其他手术操作3麻醉方式，其他手术及操作编码属性为手术时必填',
            'score': -0.5,
            'status': 'active',
            'source_tables': None,  # 将自动识别
            'dict_types': ''
        },
        # 2. 其他手术操作3麻醉方式 - 值域检查
        {
            'field_code': 'C43x03C',
            'field_name': '其他手术操作3麻醉方式',
            'rule_type': 'value_check',
            'rule_expression': 'C43x03C IN RC013',
            'error_message': '其他手术操作3麻醉方式取值不为空且不符合国家标准值域定义',
            'score': -0.5,
            'status': 'active',
            'source_tables': None,  # 将自动识别
            'dict_types': 'RC013'
        },
        # 3. 性别 - 值域检查
        {
            'field_code': 'A01',
            'field_name': '性别',
            'rule_type': 'value_check',
            'rule_expression': 'A01 IN RC001',
            'error_message': '性别代码必须在RC001字典范围内（0-未知，1-男，2-女，9-未说明）',
            'score': -2,
            'status': 'active',
            'source_tables': None,
            'dict_types': 'RC001'
        },
        # 4. 婚姻状况 - 值域检查
        {
            'field_code': 'A02',
            'field_name': '婚姻状况',
            'rule_type': 'value_check',
            'rule_expression': 'A02 IN RC002',
            'error_message': '婚姻状况代码必须在RC002字典范围内',
            'score': -1,
            'status': 'active',
            'source_tables': None,
            'dict_types': 'RC002'
        },
        # 5. 职业 - 值域检查
        {
            'field_code': 'A03',
            'field_name': '职业',
            'rule_type': 'value_check',
            'rule_expression': 'A03 IN RC003',
            'error_message': '职业代码必须在RC003字典范围内',
            'score': -1,
            'status': 'active',
            'source_tables': None,
            'dict_types': 'RC003'
        },
        # 6. 入院途径 - 值域检查
        {
            'field_code': 'A05',
            'field_name': '入院途径',
            'rule_type': 'value_check',
            'rule_expression': 'A05 IN RC026',
            'error_message': '入院途径代码必须在RC026字典范围内',
            'score': -1,
            'status': 'active',
            'source_tables': None,
            'dict_types': 'RC026'
        },
        # 7. 离院方式 - 值域检查
        {
            'field_code': 'A17',
            'field_name': '离院方式',
            'rule_type': 'value_check',
            'rule_expression': 'A17 IN RC019',
            'error_message': '离院方式代码必须在RC019字典范围内',
            'score': -2,
            'status': 'active',
            'source_tables': None,
            'dict_types': 'RC019'
        },
        # 8. ABO血型 - 值域检查
        {
            'field_code': 'A20',
            'field_name': 'ABO血型',
            'rule_type': 'value_check',
            'rule_expression': 'A20 IN RC030',
            'error_message': 'ABO血型代码必须在RC030字典范围内',
            'score': -1,
            'status': 'active',
            'source_tables': None,
            'dict_types': 'RC030'
        },
        # 9. Rh血型 - 值域检查
        {
            'field_code': 'A21',
            'field_name': 'Rh血型',
            'rule_type': 'value_check',
            'rule_expression': 'A21 IN RC031',
            'error_message': 'Rh血型代码必须在RC031字典范围内',
            'score': -1,
            'status': 'active',
            'source_tables': None,
            'dict_types': 'RC031'
        },
        # 10. 主要诊断编码 - 值域检查
        {
            'field_code': 'B01',
            'field_name': '主要诊断编码',
            'rule_type': 'value_check',
            'rule_expression': 'B01 IN RCJBBM',
            'error_message': '主要诊断编码必须在疾病编码字典（RCJBBM）范围内',
            'score': -4,
            'status': 'active',
            'source_tables': None,
            'dict_types': 'RCJBBM'
        },
        # 11. 主要诊断入院病情 - 值域检查
        {
            'field_code': 'B02',
            'field_name': '主要诊断入院病情',
            'rule_type': 'value_check',
            'rule_expression': 'B02 IN RC027',
            'error_message': '主要诊断入院病情代码必须在RC027字典范围内',
            'score': -2,
            'status': 'active',
            'source_tables': None,
            'dict_types': 'RC027'
        },
        # 12. 主要手术操作编码 - 值域检查
        {
            'field_code': 'C41x01',
            'field_name': '主要手术操作编码',
            'rule_type': 'value_check',
            'rule_expression': 'C41x01 IN operation_dict_v3',
            'error_message': '主要手术操作编码必须在手术编码字典（operation_dict_v3）范围内',
            'score': -4,
            'status': 'active',
            'source_tables': None,
            'dict_types': 'operation_dict_v3'
        },
        # 13. 主要手术操作麻醉方式 - 值域检查
        {
            'field_code': 'C41x01C',
            'field_name': '主要手术操作麻醉方式',
            'rule_type': 'value_check',
            'rule_expression': 'C41x01C IN RC013',
            'error_message': '主要手术操作麻醉方式必须在RC013字典范围内',
            'score': -1,
            'status': 'active',
            'source_tables': None,
            'dict_types': 'RC013'
        },
        # 14. 主要手术操作切口愈合等级 - 值域检查
        {
            'field_code': 'C41x01D',
            'field_name': '主要手术操作切口愈合等级',
            'rule_type': 'value_check',
            'rule_expression': 'C41x01D IN RC014',
            'error_message': '主要手术操作切口愈合等级必须在RC014字典范围内',
            'score': -1,
            'status': 'active',
            'source_tables': None,
            'dict_types': 'RC014'
        },
        # 15. 住院天数 - 范围检查
        {
            'field_code': 'A16',
            'field_name': '住院天数',
            'rule_type': 'range_check',
            'rule_expression': 'A16 >= 0 AND A16 <= 365',
            'error_message': '住院天数应在0-365天范围内',
            'score': -2,
            'status': 'active',
            'source_tables': None,
            'dict_types': ''
        },
        # 16. 年龄 - 范围检查
        {
            'field_code': 'A04',
            'field_name': '年龄',
            'rule_type': 'range_check',
            'rule_expression': 'A04 >= 0 AND A04 <= 150',
            'error_message': '年龄应在0-150岁范围内',
            'score': -2,
            'status': 'active',
            'source_tables': None,
            'dict_types': ''
        },
        # 17. 病案质量 - 值域检查
        {
            'field_code': 'A22',
            'field_name': '病案质量',
            'rule_type': 'value_check',
            'rule_expression': 'A22 IN RC011',
            'error_message': '病案质量代码必须在RC011字典范围内',
            'score': -2,
            'status': 'active',
            'source_tables': None,
            'dict_types': 'RC011'
        },
        # 18. 医疗付费方式 - 值域检查
        {
            'field_code': 'A23',
            'field_name': '医疗付费方式',
            'rule_type': 'value_check',
            'rule_expression': 'A23 IN RC032',
            'error_message': '医疗付费方式代码必须在RC032字典范围内',
            'score': -1,
            'status': 'active',
            'source_tables': None,
            'dict_types': 'RC032'
        },
        # 19. 出院31天内再住院计划 - 值域检查
        {
            'field_code': 'A19',
            'field_name': '出院31天内再住院计划',
            'rule_type': 'value_check',
            'rule_expression': 'A19 IN RC028',
            'error_message': '出院31天内再住院计划代码必须在RC028字典范围内',
            'score': -1,
            'status': 'active',
            'source_tables': None,
            'dict_types': 'RC028'
        },
        # 20. 民族 - 值域检查
        {
            'field_code': 'A06',
            'field_name': '民族',
            'rule_type': 'value_check',
            'rule_expression': 'A06 IN RC035',
            'error_message': '民族代码必须在RC035字典范围内',
            'score': -1,
            'status': 'active',
            'source_tables': None,
            'dict_types': 'RC035'
        }
    ]
    
    print(f"\n准备创建 {len(rules)} 条规则...")
    print("\n开始识别字段所在表...")
    
    # 识别每个字段所在的表
    for rule in rules:
        field_code = rule['field_code']
        print(f"\n正在搜索字段: {field_code} ({rule['field_name']})")
        
        source_tables = search_field(field_code)
        if source_tables:
            rule['source_tables'] = source_tables
            print(f"  ✓ 找到表: {source_tables}")
        else:
            print(f"  ✗ 未找到表，将使用默认值 d_mr")
            rule['source_tables'] = 'd_mr'
    
    print("\n" + "="*80)
    print("开始创建规则...")
    print("="*80)
    
    success_count = 0
    fail_count = 0
    
    for rule in rules:
        if create_rule(conn, rule):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "="*80)
    print("  规则创建完成")
    print("="*80)
    print(f"成功: {success_count} 条")
    print(f"失败: {fail_count} 条")
    print(f"总计: {len(rules)} 条")
    
    # 查询并显示所有规则
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT id, field_code, field_name, rule_type, status, 
               source_tables, dict_types, score
        FROM kiro_qc_rule
        ORDER BY id
    """)
    
    all_rules = cursor.fetchall()
    print(f"\n当前数据库中共有 {len(all_rules)} 条规则：")
    print("\n" + "-"*120)
    print(f"{'ID':<5} {'字段代码':<12} {'字段名称':<20} {'规则类型':<18} {'状态':<8} {'源表':<20} {'字典':<15} {'扣分':<6}")
    print("-"*120)
    
    for rule in all_rules:
        print(f"{rule['id']:<5} {rule['field_code']:<12} {rule['field_name']:<20} "
              f"{rule['rule_type']:<18} {rule['status']:<8} "
              f"{(rule['source_tables'] or ''):<20} {(rule['dict_types'] or ''):<15} {rule['score']:<6}")
    
    print("-"*120)
    
    conn.close()
    print("\n✓ 数据库连接已关闭")

if __name__ == "__main__":
    main()
