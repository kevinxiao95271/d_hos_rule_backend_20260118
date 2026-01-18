#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

BASE_URL = "http://localhost:4101/api"

def test_2023_batch_qc():
    """测试2023年批量质控"""
    print("=== 2023年批量质控测试 ===")
    
    # 1. 启动2023年批量质控
    batch_data = {
        "startDate": "2023-01-01",
        "endDate": "2023-12-31",
        "batchType": "year"
    }
    
    print("启动2023年批量质控...")
    response = requests.post(f"{BASE_URL}/qc/check/batch", json=batch_data)
    print(f"批量质控启动状态: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"启动结果: {result.get('message', 'N/A')}")
        
        # 2. 等待处理完成
        print("等待批量质控处理完成...")
        max_wait = 60  # 最多等待60秒
        wait_count = 0
        
        while wait_count < max_wait:
            time.sleep(2)
            wait_count += 2
            
            # 检查批量状态
            status_response = requests.get(f"{BASE_URL}/qc/batch/status/2023")
            if status_response.status_code == 200:
                status_data = status_response.json().get('data', {})
                status = status_data.get('status', 'unknown')
                progress = status_data.get('progress', 0)
                
                print(f"处理进度: {progress}%, 状态: {status}")
                
                if status == 'completed':
                    print("批量质控处理完成!")
                    break
                elif status == 'failed':
                    print("批量质控处理失败!")
                    return
            
            if wait_count >= max_wait:
                print("等待超时，继续查看结果...")
                break
        
        # 3. 获取批量汇总结果
        print("\n=== 获取2023年批量汇总结果 ===")
        summary_response = requests.post(f"{BASE_URL}/qc/result/batch/summary", json=batch_data)
        
        if summary_response.status_code == 200:
            summary_data = summary_response.json().get('data', {})
            print(f"病案总数: {summary_data.get('caseCount', 0)}")
            print(f"总缺陷数: {summary_data.get('totalDefectCount', 0)}")
            print(f"平均缺陷: {summary_data.get('avgDefect', 0)}")
            print(f"平均得分: {summary_data.get('avgScore', 0)}")
        
        # 4. 获取批量明细结果（前10个病案）
        print("\n=== 获取2023年批量明细结果（前10个） ===")
        cases_response = requests.post(f"{BASE_URL}/qc/result/batch/cases", json=batch_data)
        
        if cases_response.status_code == 200:
            cases_data = cases_response.json().get('data', [])
            print(f"获取到病案明细: {len(cases_data)}个")
            
            # 统计规则违规情况
            rule_violations = {}
            field_violations = {}
            
            for i, case in enumerate(cases_data[:10]):  # 只看前10个
                print(f"\n病案 {i+1}: {case.get('mrKey', 'N/A')}")
                print(f"  缺陷数: {case.get('defectCount', 0)}, 得分: {case.get('finalScore', 0)}")
                
                defects = case.get('allDefects', [])
                for defect in defects:
                    rule_code = defect.get('ruleCode', 'unknown')
                    field_code = defect.get('fieldCode', 'unknown')
                    
                    # 统计规则违规
                    if rule_code not in rule_violations:
                        rule_violations[rule_code] = {
                            'count': 0,
                            'description': defect.get('ruleDescription', ''),
                            'field': field_code
                        }
                    rule_violations[rule_code]['count'] += 1
                    
                    # 统计字段违规
                    if field_code not in field_violations:
                        field_violations[field_code] = 0
                    field_violations[field_code] += 1
            
            # 5. 输出统计结果
            print(f"\n=== 规则违规统计（前10个病案） ===")
            sorted_rules = sorted(rule_violations.items(), key=lambda x: x[1]['count'], reverse=True)
            
            for rule_code, info in sorted_rules:
                print(f"{rule_code}: {info['count']}次违规")
                print(f"  字段: {info['field']}")
                print(f"  描述: {info['description'][:50]}...")
            
            print(f"\n=== 字段违规统计（前10个病案） ===")
            sorted_fields = sorted(field_violations.items(), key=lambda x: x[1], reverse=True)
            
            for field_code, count in sorted_fields:
                print(f"{field_code}: {count}次违规")
        
        else:
            print(f"获取批量明细失败: {cases_response.status_code}")
            print(f"错误信息: {cases_response.text}")
    
    else:
        print(f"批量质控启动失败: {response.status_code}")
        print(f"错误信息: {response.text}")

if __name__ == "__main__":
    test_2023_batch_qc()