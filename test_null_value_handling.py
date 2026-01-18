#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试空值处理逻辑
验证规则引擎是否正确处理字段为空的情况
"""

import pymysql
import requests
import json

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

def create_test_rules():
    """创建测试规则"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 删除旧的测试规则
    cursor.execute("DELETE FROM kiro_qc_rule WHERE rule_code LIKE 'TEST_NULL_%'")
    
    # 测试规则1：必填字段
    cursor.execute("""
        INSERT INTO kiro_qc_rule (
            rule_code, field_code, field_name, rule_type, canonical_expr,
            description, deduct_score, status, source_tables, dict_types
        ) VALUES (
            'TEST_NULL_REQUIRED', 'A01', '性别', 'value_check', 'A01 IN RC001',
            '性别必填，且必须在RC001字典范围内', 2, 'active', 'd_mr', 'RC001'
        )
    """)
    
    # 测试规则2：非必填字段
    cursor.execute("""
        INSERT INTO kiro_qc_rule (
            rule_code, field_code, field_name, rule_type, canonical_expr,
            description, deduct_score, status, source_tables, dict_types
        ) VALUES (
            'TEST_NULL_OPTIONAL', 'A02', '婚姻状况', 'value_check', 'A02 IN RC002',
            '婚姻状况必须在RC002字典范围内', 1, 'active', 'd_mr', 'RC002'
        )
    """)
    
    # 测试规则3：范围检查（必填）
    cursor.execute("""
        INSERT INTO kiro_qc_rule (
            rule_code, field_code, field_name, rule_type, canonical_expr,
            description, deduct_score, status, source_tables, dict_types
        ) VALUES (
            'TEST_NULL_RANGE_REQ', 'A16', '住院天数', 'range_check', 'A16 >= 0 AND A16 <= 365',
            '住院天数必填，应在0-365范围内', 2, 'active', 'd_mr', ''
        )
    """)
    
    # 测试规则4：范围检查（非必填）
    cursor.execute("""
        INSERT INTO kiro_qc_rule (
            rule_code, field_code, field_name, rule_type, canonical_expr,
            description, deduct_score, status, source_tables, dict_types
        ) VALUES (
            'TEST_NULL_RANGE_OPT', 'A04', '年龄', 'range_check', 'A04 >= 0 AND A04 <= 150',
            '年龄应在0-150范围内', 1, 'active', 'd_mr', ''
        )
    """)
    
    conn.commit()
    conn.close()
    
    print("✓ 测试规则创建成功")

def find_test_cases():
    """查找测试用例"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    test_cases = []
    
    # 场景1：A01为空（必填字段）
    cursor.execute("""
        SELECT A48, A49, A01, A02, A16, A04
        FROM d_mr
        WHERE (A01 IS NULL OR A01 = '')
        LIMIT 1
    """)
    case = cursor.fetchone()
    if case:
        test_cases.append({
            'name': '场景1：必填字段A01为空',
            'a48': case['A48'],
            'a49': case['A49'],
            'expected': '应报告缺陷：性别不能为空'
        })
    
    # 场景2：A02为空（非必填字段）
    cursor.execute("""
        SELECT A48, A49, A01, A02, A16, A04
        FROM d_mr
        WHERE (A02 IS NULL OR A02 = '')
        AND A01 IS NOT NULL AND A01 != ''
        LIMIT 1
    """)
    case = cursor.fetchone()
    if case:
        test_cases.append({
            'name': '场景2：非必填字段A02为空',
            'a48': case['A48'],
            'a49': case['A49'],
            'expected': '不应报告缺陷（跳过检查）'
        })
    
    # 场景3：A16为空（必填范围字段）
    cursor.execute("""
        SELECT A48, A49, A01, A02, A16, A04
        FROM d_mr
        WHERE (A16 IS NULL OR A16 = '')
        AND A01 IS NOT NULL AND A01 != ''
        LIMIT 1
    """)
    case = cursor.fetchone()
    if case:
        test_cases.append({
            'name': '场景3：必填范围字段A16为空',
            'a48': case['A48'],
            'a49': case['A49'],
            'expected': '应报告缺陷：住院天数不能为空'
        })
    
    # 场景4：A04为空（非必填范围字段）
    cursor.execute("""
        SELECT A48, A49, A01, A02, A16, A04
        FROM d_mr
        WHERE (A04 IS NULL OR A04 = '')
        AND A01 IS NOT NULL AND A01 != ''
        LIMIT 1
    """)
    case = cursor.fetchone()
    if case:
        test_cases.append({
            'name': '场景4：非必填范围字段A04为空',
            'a48': case['A48'],
            'a49': case['A49'],
            'expected': '不应报告缺陷（跳过检查）'
        })
    
    # 场景5：所有字段都有值
    cursor.execute("""
        SELECT A48, A49, A01, A02, A16, A04
        FROM d_mr
        WHERE A01 IS NOT NULL AND A01 != ''
        AND A02 IS NOT NULL AND A02 != ''
        AND A16 IS NOT NULL AND A16 != ''
        AND A04 IS NOT NULL AND A04 != ''
        LIMIT 1
    """)
    case = cursor.fetchone()
    if case:
        test_cases.append({
            'name': '场景5：所有字段都有值',
            'a48': case['A48'],
            'a49': case['A49'],
            'expected': '根据值域/范围检查结果报告缺陷'
        })
    
    conn.close()
    return test_cases

def run_qc_check(a48, a49):
    """执行质控检查"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/qc/check",
            json={
                "a48": a48,
                "a49": a49
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                return data['data']
        
        return None
    except Exception as e:
        print(f"  ✗ API调用失败: {str(e)}")
        return None

def main():
    """主函数"""
    print("="*100)
    print("  测试空值处理逻辑")
    print("="*100)
    
    # 创建测试规则
    print("\n步骤1：创建测试规则")
    create_test_rules()
    
    # 查找测试用例
    print("\n步骤2：查找测试用例")
    test_cases = find_test_cases()
    print(f"✓ 找到 {len(test_cases)} 个测试场景")
    
    # 执行测试
    print("\n步骤3：执行测试")
    print("="*100)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{case['name']}")
        print(f"  病案: A48={case['a48']}, A49={case['a49']}")
        print(f"  预期: {case['expected']}")
        
        result = run_qc_check(case['a48'], case['a49'])
        
        if result:
            defect_count = result.get('defectCount', 0)
            defects = result.get('defects', [])
            
            print(f"  结果: 发现 {defect_count} 个缺陷")
            
            if defects:
                for defect in defects:
                    print(f"    - {defect.get('fieldName', '未知字段')}: {defect.get('ruleDescription', '无描述')}")
            else:
                print(f"    无缺陷")
        else:
            print(f"  ✗ 测试失败")
    
    print("\n" + "="*100)
    print("测试完成！")
    print("="*100)
    print("\n请检查测试结果是否符合预期：")
    print("1. 必填字段为空时应报告缺陷")
    print("2. 非必填字段为空时不应报告缺陷")
    print("3. 字段有值时应进行值域/范围检查")

if __name__ == "__main__":
    main()
