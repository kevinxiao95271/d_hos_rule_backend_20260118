#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:4101"

def debug_single_qc_api():
    """调试单个QC API的响应结构"""
    print("🔍 调试单个QC API响应结构")
    
    # 测试参数
    params = {
        'a48': '19063452',
        'a49': '1'
    }
    
    try:
        print(f"请求URL: {BASE_URL}/api/qc/check/single")
        print(f"请求参数: {params}")
        
        response = requests.post(
            f"{BASE_URL}/api/qc/check/single",
            params=params,
            timeout=10
        )
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"\n完整响应JSON:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                # 分析响应结构
                print(f"\n📊 响应结构分析:")
                print(f"- code: {result.get('code')}")
                print(f"- message: {result.get('message')}")
                print(f"- success: {result.get('success')}")
                
                data = result.get('data')
                if data:
                    print(f"- data类型: {type(data)}")
                    if isinstance(data, dict):
                        print(f"- data键: {list(data.keys())}")
                        
                        violations = data.get('violations', [])
                        print(f"- violations数量: {len(violations)}")
                        
                        if violations:
                            print(f"- 前3个violations:")
                            for i, v in enumerate(violations[:3]):
                                print(f"  {i+1}. {v.get('ruleCode', 'N/A')}: {v.get('ruleDescription', 'N/A')[:50]}...")
                                
                            # 检查cross规则
                            cross_violations = [v for v in violations if v.get('ruleCode', '').startswith('CROSS_')]
                            print(f"- cross规则违规数: {len(cross_violations)}")
                            
                            if cross_violations:
                                print(f"- cross规则详情:")
                                for v in cross_violations[:3]:
                                    print(f"  - {v.get('ruleCode')}: {v.get('fieldCode')} = '{v.get('actualValue')}'")
                        else:
                            print(f"- 无违规记录")
                    else:
                        print(f"- data内容: {data}")
                else:
                    print(f"- 无data字段")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"原始响应: {response.text}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_rules_api():
    """测试规则API，看看有多少cross规则"""
    print(f"\n🔍 检查系统中的cross规则")
    
    try:
        response = requests.get(f"{BASE_URL}/api/qc/rules", timeout=5)
        if response.status_code == 200:
            result = response.json()
            rules = result.get('data', [])
            
            cross_rules = [r for r in rules if r.get('ruleCode', '').startswith('CROSS_')]
            print(f"总规则数: {len(rules)}")
            print(f"cross规则数: {len(cross_rules)}")
            
            if cross_rules:
                print(f"cross规则示例:")
                for rule in cross_rules[:5]:
                    print(f"  - {rule.get('ruleCode')}: {rule.get('ruleDescription', '')[:60]}...")
                    print(f"    状态: {rule.get('status')}, 字段: {rule.get('fieldCode')}")
            else:
                print("❌ 未找到cross规则!")
                
        else:
            print(f"❌ 规则API请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 规则API异常: {e}")

def main():
    print("🚀 Cross规则API调试")
    print("=" * 60)
    
    # 先检查规则
    test_rules_api()
    
    # 再调试QC API
    debug_single_qc_api()

if __name__ == "__main__":
    main()