#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time

BASE_URL = "http://localhost:4101"

def test_simple_status():
    """简单状态测试"""
    print("🔍 测试服务状态...")
    try:
        response = requests.get(f"{BASE_URL}/api/qc/status", timeout=3)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 状态测试失败: {e}")
        return False

def test_simple_qc():
    """简单QC测试"""
    print("🔍 测试简单QC...")
    try:
        params = {'a48': '19063452', 'a49': '1'}
        print(f"请求参数: {params}")
        
        response = requests.post(
            f"{BASE_URL}/api/qc/check/single",
            params=params,
            timeout=5
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"成功: {result.get('success')}")
            if result.get('success'):
                data = result.get('data', {})
                violations = data.get('violations', [])
                print(f"违规数: {len(violations)}")
                
                # 只显示跨字段违规
                cross_violations = [v for v in violations if v.get('ruleCode', '').startswith('CROSS_')]
                print(f"跨字段违规数: {len(cross_violations)}")
                
                for violation in cross_violations[:2]:
                    print(f"  - {violation.get('ruleCode')}")
            else:
                print(f"失败原因: {result.get('message')}")
        else:
            print(f"响应: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ QC测试失败: {e}")

def main():
    print("🚀 简单跨字段规则测试")
    
    if test_simple_status():
        print("✅ 服务状态正常")
        time.sleep(1)
        test_simple_qc()
    else:
        print("❌ 服务状态异常")

if __name__ == "__main__":
    main()