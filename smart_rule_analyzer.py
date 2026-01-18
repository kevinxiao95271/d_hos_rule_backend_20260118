#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能质控规则分析器
扫描数据库表字段，智能识别和生成质控规则
"""

import pymysql
import requests
import json
import re
from datetime import datetime
from collections import defaultdict

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

# 明确语义的字段映射
KNOWN_FIELDS = {
    'A48': {'name': '病案号', 'required': True, 'type': 'identifier'},
    'A49': {'name': '住院次数', 'required': True, 'type': 'identifier'},
    'A01': {'name': '性别', 'dict': 'RC001', 'required': True},
    'A02': {'name': '婚姻状况', 'dict': 'RC002'},
    'A03': {'name': '职业', 'dict': 'RC003'},
    'A04': {'name': '年龄', 'range': (0, 150)},
    'A05': {'name': '入院途径', 'dict': 'RC026'},
    'A06': {'name': '民族', 'dict': 'RC035'},
    'A16': {'name': '住院天数', 'range': (0, 365)},
    'A17': {'name': '离院方式', 'dict': 'RC019', 'required': True},
    'A19': {'name': '出院31天内再住院计划', 'dict': 'RC028'},
    'A20': {'name': 'ABO血型', 'dict': 'RC030'},
    'A21': {'name': 'Rh血型', 'dict': 'RC031'},
    'A22': {'name': '病案质量', 'dict': 'RC011'},
    'A23': {'name': '医疗付费方式', 'dict': 'RC032'},
    'B01': {'name': '主要诊断编码', 'dict': 'RCJBBM', 'required': True},
    'B02': {'name': '主要诊断入院病情', 'dict': 'RC027'},
    'B15': {'name': '出院日期', 'type': 'date'},
}

# 字段名称模式识别
FIELD_PATTERNS = {
    r'.*麻醉方式.*': 'RC013',
    r'.*切口愈合.*': 'RC014',
    r'.*诊断编码.*': 'RCJBBM',
    r'.*手术.*编码.*': 'operation_dict_v3',
    r'.*入院病情.*': 'RC027',
}

def get_table_columns(conn, table_name):
    """获取表的所有列"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(f"""
        SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{DB_CONFIG['database']}'
        AND TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
    """)
    return cursor.fetchall()

def search_field_api(field_code):
    """使用API搜索字段所在的表"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/dict/field/search",
            params={"fieldCode": field_code},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                return data['data']
        return None
    except Exception as e:
        print(f"  ⚠ API搜索失败: {str(e)}")
        return None

def get_dict_types():
    """获取所有字典类型"""
    try:
        response = requests.get(f"{BASE_URL}/api/dict/types", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                return data['data']
        return []
    except:
        return []

def analyze_field(field_code, field_comment, search_result):
    """分析字段并生成规则建议"""
    suggestions = []
    
    # 1. 检查是否是已知字段
    if field_code in KNOWN_FIELDS:
        field_info = KNOWN_FIELDS[field_code]
        
        if 'dict' in field_info:
            suggestions.append({
                'type': 'value_check',
                'confidence': 'HIGH',
                'field_name': field_info['name'],
                'dict_type': field_info['dict'],
                'required': field_info.get('required', False),
                'reason': '明确的字典字段'
            })
        
        if 'range' in field_info:
            suggestions.append({
                'type': 'range_check',
                'confidence': 'HIGH',
                'field_name': field_info['name'],
                'range': field_info['range'],
                'reason': '明确的范围字段'
            })
        
        return suggestions
    
    # 2. 根据字段注释推断
    if field_comment:
        for pattern, dict_type in FIELD_PATTERNS.items():
            if re.match(pattern, field_comment):
                suggestions.append({
                    'type': 'value_check',
                    'confidence': 'MEDIUM',
                    'field_name': field_comment,
                    'dict_type': dict_type,
                    'reason': f'字段注释匹配模式: {pattern}'
                })
    
    # 3. 根据字段代码模式推断
    # 手术相关字段
    if re.match(r'C\d+x\d+$', field_code):
        suggestions.append({
            'type': 'value_check',
            'confidence': 'MEDIUM',
            'field_name': field_comment or f'手术操作{field_code}',
            'dict_type': 'operation_dict_v3',
            'reason': '手术操作编码字段模式'
        })
    
    # 麻醉方式字段
    if re.match(r'C\d+x\d+C$', field_code):
        suggestions.append({
            'type': 'value_check',
            'confidence': 'HIGH',
            'field_name': field_comment or f'麻醉方式{field_code}',
            'dict_type': 'RC013',
            'reason': '麻醉方式字段模式（以C结尾）'
        })
    
    # 切口愈合等级字段
    if re.match(r'C\d+x\d+D$', field_code):
        suggestions.append({
            'type': 'value_check',
            'confidence': 'HIGH',
            'field_name': field_comment or f'切口愈合等级{field_code}',
            'dict_type': 'RC014',
            'reason': '切口愈合等级字段模式（以D结尾）'
        })
    
    # 诊断相关字段
    if re.match(r'B\d+$', field_code) and field_code != 'B15':
        suggestions.append({
            'type': 'value_check',
            'confidence': 'MEDIUM',
            'field_name': field_comment or f'诊断{field_code}',
            'dict_type': 'RCJBBM',
            'reason': '诊断编码字段模式'
        })
    
    return suggestions

def main():
    """主函数"""
    print("="*100)
    print("  智能质控规则分析器")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)
    
    # 连接数据库
    conn = pymysql.connect(**DB_CONFIG)
    print("\n✓ 数据库连接成功")
    
    # 获取字典类型列表
    print("\n正在获取字典类型列表...")
    dict_types = get_dict_types()
    print(f"✓ 获取到 {len(dict_types)} 种字典类型")
    
    # 要扫描的表
    tables = ['d_mr', 'd_mr_other_1_20', 'd_mr_other_21_40', 'd_mr_other_f']
    
    all_fields = {}
    field_locations = defaultdict(list)
    
    print("\n" + "="*100)
    print("第一步：扫描所有表的字段")
    print("="*100)
    
    for table in tables:
        print(f"\n正在扫描表: {table}")
        columns = get_table_columns(conn, table)
        print(f"  找到 {len(columns)} 个字段")
        
        for col in columns:
            field_code = col['COLUMN_NAME']
            field_comment = col['COLUMN_COMMENT'] or ''
            
            if field_code not in all_fields:
                all_fields[field_code] = {
                    'comment': field_comment,
                    'data_type': col['DATA_TYPE']
                }
            
            field_locations[field_code].append(table)
    
    print(f"\n✓ 总共发现 {len(all_fields)} 个唯一字段")
    
    print("\n" + "="*100)
    print("第二步：分析字段并生成规则建议")
    print("="*100)
    
    high_confidence_rules = []
    medium_confidence_rules = []
    low_confidence_rules = []
    
    for field_code, field_info in sorted(all_fields.items()):
        # 跳过系统字段
        if field_code in ['id', 'created_at', 'updated_at']:
            continue
        
        # 使用API搜索字段
        search_result = search_field_api(field_code)
        
        # 分析字段
        suggestions = analyze_field(field_code, field_info['comment'], search_result)
        
        if not suggestions:
            continue
        
        # 确定字段所在的表
        tables_found = field_locations[field_code]
        source_tables = ','.join(tables_found)
        
        # 只有一个位置的字段更可靠
        location_confidence = 'HIGH' if len(tables_found) == 1 else 'MEDIUM'
        
        for suggestion in suggestions:
            rule_info = {
                'field_code': field_code,
                'field_name': suggestion['field_name'],
                'rule_type': suggestion['type'],
                'confidence': suggestion['confidence'],
                'location_confidence': location_confidence,
                'source_tables': source_tables,
                'dict_type': suggestion.get('dict_type', ''),
                'range': suggestion.get('range'),
                'reason': suggestion['reason'],
                'tables_count': len(tables_found)
            }
            
            # 综合置信度
            if suggestion['confidence'] == 'HIGH' and location_confidence == 'HIGH':
                high_confidence_rules.append(rule_info)
            elif suggestion['confidence'] == 'HIGH' or location_confidence == 'HIGH':
                medium_confidence_rules.append(rule_info)
            else:
                low_confidence_rules.append(rule_info)
    
    # 输出分析结果
    print("\n" + "="*100)
    print("分析结果汇总")
    print("="*100)
    
    print(f"\n高置信度规则: {len(high_confidence_rules)} 条（建议直接使用）")
    print(f"中置信度规则: {len(medium_confidence_rules)} 条（建议人工审核）")
    print(f"低置信度规则: {len(low_confidence_rules)} 条（仅供参考）")
    
    # 详细输出高置信度规则
    if high_confidence_rules:
        print("\n" + "="*100)
        print("【高置信度规则】- 建议直接使用")
        print("="*100)
        
        for i, rule in enumerate(high_confidence_rules, 1):
            print(f"\n{i}. 字段: {rule['field_code']} - {rule['field_name']}")
            print(f"   规则类型: {rule['rule_type']}")
            print(f"   源表: {rule['source_tables']} (出现在{rule['tables_count']}个表)")
            if rule['dict_type']:
                print(f"   字典类型: {rule['dict_type']}")
            if rule['range']:
                print(f"   范围: {rule['range'][0]} - {rule['range'][1]}")
            print(f"   原因: {rule['reason']}")
            
            # 生成规则SQL
            if rule['rule_type'] == 'value_check' and rule['dict_type']:
                print(f"\n   建议规则表达式: {rule['field_code']} IN {rule['dict_type']}")
                print(f"   建议错误消息: {rule['field_name']}必须在{rule['dict_type']}字典范围内")
            elif rule['rule_type'] == 'range_check' and rule['range']:
                print(f"\n   建议规则表达式: {rule['field_code']} >= {rule['range'][0]} AND {rule['field_code']} <= {rule['range'][1]}")
                print(f"   建议错误消息: {rule['field_name']}应在{rule['range'][0]}-{rule['range'][1]}范围内")
    
    # 输出中置信度规则
    if medium_confidence_rules:
        print("\n" + "="*100)
        print("【中置信度规则】- 建议人工审核")
        print("="*100)
        
        for i, rule in enumerate(medium_confidence_rules[:20], 1):  # 只显示前20条
            print(f"\n{i}. 字段: {rule['field_code']} - {rule['field_name']}")
            print(f"   规则类型: {rule['rule_type']}")
            print(f"   源表: {rule['source_tables']} (出现在{rule['tables_count']}个表)")
            if rule['dict_type']:
                print(f"   字典类型: {rule['dict_type']}")
            print(f"   原因: {rule['reason']}")
            print(f"   ⚠ 建议: 请人工确认字段语义和字典类型是否正确")
    
    # 保存分析结果到文件
    output_file = 'rule_analysis_result.json'
    result = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_fields': len(all_fields),
            'high_confidence': len(high_confidence_rules),
            'medium_confidence': len(medium_confidence_rules),
            'low_confidence': len(low_confidence_rules)
        },
        'high_confidence_rules': high_confidence_rules,
        'medium_confidence_rules': medium_confidence_rules,
        'low_confidence_rules': low_confidence_rules
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 分析结果已保存到: {output_file}")
    
    # 生成可直接使用的规则SQL
    print("\n" + "="*100)
    print("生成规则创建SQL")
    print("="*100)
    
    sql_file = 'auto_generated_rules.sql'
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write("-- 自动生成的质控规则\n")
        f.write(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"-- 高置信度规则: {len(high_confidence_rules)} 条\n\n")
        
        for rule in high_confidence_rules:
            if rule['rule_type'] == 'value_check' and rule['dict_type']:
                expression = f"{rule['field_code']} IN {rule['dict_type']}"
                message = f"{rule['field_name']}必须在{rule['dict_type']}字典范围内"
                score = 2 if 'required' in rule['reason'] else 1
                rule_code = f"RULE_{rule['field_code']}_{rule['dict_type']}"
                
                sql = f"""INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    '{rule_code}', '{rule['field_code']}', '{rule['field_name']}', 'value_check', '{expression}',
    '{message}', {score}, 'draft', '{rule['source_tables']}', '{rule['dict_type']}',
    NOW(), NOW()
);\n\n"""
                f.write(sql)
            
            elif rule['rule_type'] == 'range_check' and rule['range']:
                expression = f"{rule['field_code']} >= {rule['range'][0]} AND {rule['field_code']} <= {rule['range'][1]}"
                message = f"{rule['field_name']}应在{rule['range'][0]}-{rule['range'][1]}范围内"
                rule_code = f"RULE_{rule['field_code']}_RANGE"
                
                sql = f"""INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    '{rule_code}', '{rule['field_code']}', '{rule['field_name']}', 'range_check', '{expression}',
    '{message}', 2, 'draft', '{rule['source_tables']}', '',
    NOW(), NOW()
);\n\n"""
                f.write(sql)
    
    print(f"✓ 规则SQL已保存到: {sql_file}")
    print(f"  包含 {len(high_confidence_rules)} 条高置信度规则")
    print(f"  状态: draft（草稿），可在测试后改为active")
    
    conn.close()
    print("\n✓ 数据库连接已关闭")
    
    print("\n" + "="*100)
    print("分析完成！")
    print("="*100)
    print("\n下一步操作建议：")
    print("1. 查看 rule_analysis_result.json 了解详细分析结果")
    print("2. 查看 auto_generated_rules.sql 中的高置信度规则")
    print("3. 执行SQL创建规则（状态为draft）")
    print("4. 使用规则测试API验证规则效果")
    print("5. 确认无误后将规则状态改为active")

if __name__ == "__main__":
    main()
