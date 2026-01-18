#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自动生成的质控规则
"""

import requests
import pymysql
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

def get_sample_data(field_code, source_table):
    """从数据库获取样本数据"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 获取5条有值的记录
    cursor.execute(f"""
        SELECT A48, A49, {field_code}
        FROM {source_table}
        WHERE {field_code} IS NOT NULL AND {field_code} != ''
        LIMIT 5
    """)
    
    results = cursor.fetchall()
    conn.close()
    return results

def test_rule(rule_id, rule_code, field_code, source_table):
    """测试单个规则"""
    print(f"\n测试规则: {rule_code} ({field_code})")
    print("-" * 80)
    
    # 获取样本数据
    try:
        samples = get_sample_data(field_code, source_table)
        if not samples:
            print(f"  ⚠ 没有找到样本数据")
            return None
        
        print(f"  找到 {len(samples)} 条样本数据")
    except Exception as e:
        print(f"  ✗ 获取样本数据失败: {str(e)}")
        return None
    
    # 测试规则
    test_results = []
    for sample in samples:
        try:
            response = requests.post(
                f"{BASE_URL}/api/qc/rules/test",
                json={
                    "ruleId": rule_id,
                    "a48": sample['A48'],
                    "a49": sample['A49']
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['code'] == 200:
                    result = data['data']
                    test_results.append({
                        'a48': sample['A48'],
                        'a49': sample['A49'],
                        'value': sample[field_code],
                        'passed': result['passed'],
                        'message': result.get('message', '')
                    })
                else:
                    print(f"  ✗ API返回错误: {data.get('message', 'Unknown error')}")
            else:
                print(f"  ✗ HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"  ✗ 测试失败: {str(e)}")
    
    # 输出测试结果
    if test_results:
        passed_count = sum(1 for r in test_results if r['passed'])
        failed_count = len(test_results) - passed_count
        
        print(f"\n  测试结果: {passed_count} 通过, {failed_count} 失败")
        
        for i, result in enumerate(test_results, 1):
            status = "✓" if result['passed'] else "✗"
            print(f"    {i}. {status} A48={result['a48']}, A49={result['a49']}, 值={result['value']}")
            if not result['passed'] and result['message']:
                print(f"       消息: {result['message']}")
        
        return {
            'rule_code': rule_code,
            'field_code': field_code,
            'total': len(test_results),
            'passed': passed_count,
            'failed': failed_count
        }
    
    return None

def main():
    """主函数"""
    print("="*100)
    print("  测试自动生成的质控规则")
    print("="*100)
    
    # 连接数据库获取规则列表
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 获取前20条草稿规则进行测试
    cursor.execute("""
        SELECT id, rule_code, field_code, source_tables
        FROM kiro_qc_rule
        WHERE status = 'draft'
        ORDER BY id
        LIMIT 20
    """)
    
    rules = cursor.fetchall()
    conn.close()
    
    print(f"\n找到 {len(rules)} 条规则进行测试")
    
    # 测试每个规则
    test_summary = []
    for rule in rules:
        # 只取第一个源表
        source_table = rule['source_tables'].split(',')[0]
        
        result = test_rule(
            rule['id'],
            rule['rule_code'],
            rule['field_code'],
            source_table
        )
        
        if result:
            test_summary.append(result)
    
    # 输出汇总
    print("\n" + "="*100)
    print("测试汇总")
    print("="*100)
    
    if test_summary:
        total_tests = sum(r['total'] for r in test_summary)
        total_passed = sum(r['passed'] for r in test_summary)
        total_failed = sum(r['failed'] for r in test_summary)
        
        print(f"\n测试规则数: {len(test_summary)}")
        print(f"总测试次数: {total_tests}")
        print(f"通过: {total_passed} ({total_passed/total_tests*100:.1f}%)")
        print(f"失败: {total_failed} ({total_failed/total_tests*100:.1f}%)")
        
        print("\n各规则测试结果:")
        for r in test_summary:
            pass_rate = r['passed'] / r['total'] * 100 if r['total'] > 0 else 0
            print(f"  {r['rule_code']:40} {r['field_code']:15} {r['passed']}/{r['total']} ({pass_rate:.0f}%)")
    
    print("\n" + "="*100)
    print("测试完成！")
    print("="*100)

if __name__ == "__main__":
    main()
