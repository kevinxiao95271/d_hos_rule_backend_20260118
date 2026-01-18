import requests
import json
import time

BASE_URL = "http://localhost:4101/api/qc"

def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

print("=" * 80)
print("医疗病案质控系统API自动测试")
print("=" * 80)
print(f"基础URL: {BASE_URL}\n")

try:
    # 1. 测试获取规则列表
    print_section("1. 测试获取规则列表")
    response = requests.get(f"{BASE_URL}/rules")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"规则数量: {len(data.get('data', []))}")
        if data.get('data'):
            print(f"第一条规则: {data['data'][0]['ruleCode']} - {data['data'][0]['description'][:50]}...")
    
    # 2. 测试单个病案质控
    print_section("2. 测试单个病案质控 (A48=19079841, A49=1)")
    response = requests.post(f"{BASE_URL}/check/single", params={"a48": "19079841", "a49": "1"})
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 200:
            result = data['data']
            print(f"病案: {result['mrKey']}")
            print(f"最终得分: {result['finalScore']}")
            print(f"缺陷数: {result['defectCount']}")
            print(f"总扣分: {result['totalDeduct']}")
    
    # 3. 测试获取单个病案结果
    print_section("3. 测试获取单个病案质控结果")
    response = requests.get(f"{BASE_URL}/result/case", params={"a48": "19079841", "a49": "1"})
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 200:
            result = data['data']
            print(f"病案: {result['mrKey']}, 得分: {result['finalScore']}, 缺陷数: {result['defectCount']}")
            if result.get('defectsByField'):
                print(f"按字段分组的缺陷数: {len(result['defectsByField'])}")
    
    # 4. 测试批量质控 - 2020年1月
    print_section("4. 测试批量质控 - 2020年1月")
    request_data = {"periodType": "month", "year": 2020, "month": 1}
    response = requests.post(f"{BASE_URL}/check/batch", json=request_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 200:
            result = data['data']
            print(f"周期: {result['year']}年{result['month']}月")
            print(f"病案数量: {result['caseCount']}")
            print(f"总缺陷数: {result['totalDefectCount']}")
            print(f"平均缺陷: {result['avgDefect']}")
            print(f"平均得分: {result['avgScore']}")
            print(f"状态: {result['status']}")
    
    # 5. 测试获取批量质控汇总
    print_section("5. 测试获取批量质控汇总 - 2020年1月")
    response = requests.post(f"{BASE_URL}/result/batch/summary", json=request_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 200:
            result = data['data']
            print(f"病案数量: {result['caseCount']}")
            print(f"总缺陷数: {result['totalDefectCount']}")
            print(f"平均缺陷: {result['avgDefect']}")
            print(f"平均得分: {result['avgScore']}")
    
    # 6. 测试获取批量质控明细列表（前5条）
    print_section("6. 测试获取批量质控明细列表 - 2020年1月（前5条）")
    response = requests.post(f"{BASE_URL}/result/batch/cases", json=request_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 200:
            cases = data['data'][:5]
            print(f"总数: {len(data['data'])} 条，显示前5条:")
            for case in cases:
                print(f"  {case['mrKey']}: 得分={case['finalScore']}, 缺陷数={case['defectCount']}")
    
    # 7. 测试批量质控 - 2023年
    print_section("7. 测试批量质控 - 2023年")
    request_data_2023 = {"periodType": "year", "year": 2023}
    response = requests.post(f"{BASE_URL}/check/batch", json=request_data_2023)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 200:
            result = data['data']
            print(f"周期: {result['year']}年")
            print(f"病案数量: {result['caseCount']}")
            print(f"总缺陷数: {result['totalDefectCount']}")
            print(f"平均缺陷: {result['avgDefect']}")
            print(f"平均得分: {result['avgScore']}")
    
    # 8. 测试批量质控 - 2020年全年
    print_section("8. 测试批量质控 - 2020年全年")
    request_data_2020 = {"periodType": "year", "year": 2020}
    response = requests.post(f"{BASE_URL}/check/batch", json=request_data_2020)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 200:
            result = data['data']
            print(f"周期: {result['year']}年")
            print(f"病案数量: {result['caseCount']}")
            print(f"总缺陷数: {result['totalDefectCount']}")
            print(f"平均缺陷: {result['avgDefect']}")
            print(f"平均得分: {result['avgScore']}")
    
    print("\n" + "=" * 80)
    print("所有测试完成！")
    print("=" * 80)
    print("\nSwagger文档地址: http://localhost:4101/swagger-ui/index.html")
    
except requests.exceptions.ConnectionError:
    print("\n错误: 无法连接到后端服务，请确保服务已启动在 http://localhost:4101")
except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()
