import requests
import json
import time

BASE_URL = "http://localhost:4101/api/qc"

def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def test_get_rules():
    print_section("1. 测试获取规则列表")
    response = requests.get(f"{BASE_URL}/rules")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return data

def test_search_rules():
    print_section("2. 测试搜索规则")
    response = requests.get(f"{BASE_URL}/rules/search", params={"keyword": "新生儿"})
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

def test_single_case():
    print_section("3. 测试单个病案质控")
    # 使用2020年的数据
    response = requests.post(f"{BASE_URL}/check/single", params={"a48": "19079841", "a49": "1"})
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return data

def test_get_case_result():
    print_section("4. 测试获取单个病案质控结果")
    response = requests.get(f"{BASE_URL}/result/case", params={"a48": "19079841", "a49": "1"})
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

def test_batch_check_2020_jan():
    print_section("5. 测试批量质控 - 2020年1月")
    request_data = {
        "periodType": "month",
        "year": 2020,
        "month": 1
    }
    response = requests.post(f"{BASE_URL}/check/batch", json=request_data)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return data

def test_batch_check_2023():
    print_section("6. 测试批量质控 - 2023年")
    request_data = {
        "periodType": "year",
        "year": 2023
    }
    response = requests.post(f"{BASE_URL}/check/batch", json=request_data)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return data

def test_batch_check_2020():
    print_section("7. 测试批量质控 - 2020年全年")
    request_data = {
        "periodType": "year",
        "year": 2020
    }
    response = requests.post(f"{BASE_URL}/check/batch", json=request_data)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return data

def test_get_batch_summary():
    print_section("8. 测试获取批量质控汇总 - 2020年1月")
    request_data = {
        "periodType": "month",
        "year": 2020,
        "month": 1
    }
    response = requests.post(f"{BASE_URL}/result/batch/summary", json=request_data)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

def test_get_batch_cases():
    print_section("9. 测试获取批量质控明细列表 - 2020年1月（前5条）")
    request_data = {
        "periodType": "month",
        "year": 2020,
        "month": 1
    }
    response = requests.post(f"{BASE_URL}/result/batch/cases", json=request_data)
    print(f"状态码: {response.status_code}")
    data = response.json()
    if data.get('code') == 200 and data.get('data'):
        cases = data['data'][:5]  # 只显示前5条
        print(f"总数: {len(data['data'])} 条，显示前5条:")
        for case in cases:
            print(f"\n病案: {case['mrKey']}")
            print(f"  得分: {case['finalScore']}, 缺陷数: {case['defectCount']}, 扣分: {case['totalDeduct']}")
            if case.get('defectsByField'):
                print(f"  按字段分组的缺陷:")
                for field, defects in list(case['defectsByField'].items())[:3]:
                    print(f"    {field}: {len(defects)} 个缺陷")

if __name__ == "__main__":
    print("=" * 80)
    print("医疗病案质控系统API测试")
    print("=" * 80)
    print(f"基础URL: {BASE_URL}")
    print("请确保后端服务已启动在 http://localhost:4101")
    print("\n按回车键开始测试...")
    input()
    
    try:
        # 测试规则接口
        test_get_rules()
        test_search_rules()
        
        # 测试单个病案
        test_single_case()
        test_get_case_result()
        
        # 测试批量质控
        test_batch_check_2020_jan()
        time.sleep(2)
        test_get_batch_summary()
        test_get_batch_cases()
        
        # 测试2023年
        test_batch_check_2023()
        
        # 测试2020年全年
        test_batch_check_2020()
        
        print("\n" + "=" * 80)
        print("所有测试完成！")
        print("=" * 80)
        
    except requests.exceptions.ConnectionError:
        print("\n错误: 无法连接到后端服务，请确保服务已启动在 http://localhost:4101")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
