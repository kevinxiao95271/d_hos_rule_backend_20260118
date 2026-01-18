import requests
import json

BASE_URL = "http://localhost:4101/api/qc"

def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

print("=" * 80)
print("规则管理功能测试")
print("=" * 80)

try:
    # 1. 获取所有规则
    print_section("1. 获取所有规则")
    response = requests.get(f"{BASE_URL}/rules")
    data = response.json()
    print(f"状态码: {response.status_code}")
    print(f"规则总数: {len(data['data'])}")
    for rule in data['data']:
        print(f"  - {rule['ruleCode']}: {rule['status']}")
    
    # 2. 按状态获取规则 - active
    print_section("2. 获取已完善规则 (active)")
    response = requests.get(f"{BASE_URL}/rules/status/active")
    data = response.json()
    print(f"状态码: {response.status_code}")
    print(f"已完善规则数: {len(data['data'])}")
    
    # 3. 按状态获取规则 - draft
    print_section("3. 获取未完善规则 (draft)")
    response = requests.get(f"{BASE_URL}/rules/status/draft")
    data = response.json()
    print(f"状态码: {response.status_code}")
    print(f"未完善规则数: {len(data['data'])}")
    
    # 4. 搜索规则（带状态筛选）
    print_section("4. 搜索规则（active + 关键词'新生儿'）")
    response = requests.get(f"{BASE_URL}/rules/search", params={"status": "active", "keyword": "新生儿"})
    data = response.json()
    print(f"状态码: {response.status_code}")
    print(f"搜索结果: {len(data['data'])}条")
    
    # 5. 获取单个规则详情
    print_section("5. 获取规则详情 (ID=1)")
    response = requests.get(f"{BASE_URL}/rules/1")
    data = response.json()
    print(f"状态码: {response.status_code}")
    if data['code'] == 200:
        rule = data['data']
        print(f"规则编码: {rule['ruleCode']}")
        print(f"字段名称: {rule['fieldName']}")
        print(f"规则类型: {rule['ruleType']}")
        print(f"扣分: {rule['deductScore']}")
        print(f"状态: {rule['status']}")
        print(f"描述: {rule['description']}")
    
    # 6. 规则试运行 - 测试单个病案
    print_section("6. 规则试运行 - 测试单个病案")
    test_request = {
        "ruleId": 3,  # A18x01_range_check
        "a48": "19079841",
        "a49": "1",
        "limit": 5
    }
    response = requests.post(f"{BASE_URL}/rules/test", json=test_request)
    data = response.json()
    print(f"状态码: {response.status_code}")
    if data['code'] == 200:
        result = data['data']
        print(f"规则编码: {result['ruleCode']}")
        print(f"测试记录数: {result['totalRecords']}")
        print(f"违规数量: {result['violationCount']}")
        print(f"违规率: {result['violationRate']:.2f}%")
        print(f"违规明细:")
        for v in result['violations']:
            print(f"  - 病案: {v['mrKey']}, 字段: {v['fieldCode']}")
            print(f"    实际值: {v['actualValue']}, 预期值: {v['expectedValue']}")
    
    # 7. 规则试运行 - 测试批量数据
    print_section("7. 规则试运行 - 测试2020年1月数据")
    test_request = {
        "ruleId": 3,
        "year": 2020,
        "month": 1,
        "limit": 5
    }
    response = requests.post(f"{BASE_URL}/rules/test", json=test_request)
    data = response.json()
    print(f"状态码: {response.status_code}")
    if data['code'] == 200:
        result = data['data']
        print(f"测试记录数: {result['totalRecords']}")
        print(f"违规数量: {result['violationCount']}")
        print(f"违规率: {result['violationRate']:.2f}%")
    
    # 8. 更新规则状态 - 将规则1改为draft
    print_section("8. 更新规则状态 (ID=1, status=draft)")
    response = requests.put(f"{BASE_URL}/rules/1/status", params={"status": "draft"})
    data = response.json()
    print(f"状态码: {response.status_code}")
    print(f"结果: {data['message']}")
    
    # 9. 验证状态更新
    print_section("9. 验证状态更新")
    response = requests.get(f"{BASE_URL}/rules/1")
    data = response.json()
    if data['code'] == 200:
        print(f"规则1当前状态: {data['data']['status']}")
    
    # 10. 恢复规则状态为active
    print_section("10. 恢复规则状态 (ID=1, status=active)")
    response = requests.put(f"{BASE_URL}/rules/1/status", params={"status": "active"})
    data = response.json()
    print(f"状态码: {response.status_code}")
    print(f"结果: {data['message']}")
    
    print("\n" + "=" * 80)
    print("所有测试完成！")
    print("=" * 80)
    print("\n新增接口:")
    print("  - GET  /api/qc/rules/status/{status} - 按状态获取规则")
    print("  - GET  /api/qc/rules/{id} - 获取规则详情")
    print("  - GET  /api/qc/rules/search?status=xxx - 搜索规则（支持状态筛选）")
    print("  - PUT  /api/qc/rules - 更新规则")
    print("  - PUT  /api/qc/rules/{id}/status - 更新规则状态")
    print("  - POST /api/qc/rules/test - 规则试运行")
    
except requests.exceptions.ConnectionError:
    print("\n错误: 无法连接到后端服务，请确保服务已启动在 http://localhost:4101")
except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()
