import requests
import json
import time

print("测试重启后的应用...")

# 1. 检查服务状态
try:
    response = requests.get("http://localhost:4101/api/health", timeout=5)
    if response.status_code == 200:
        print("✅ 服务运行正常")
    else:
        print(f"⚠️  服务响应: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ 服务未启动: {e}")
    exit(1)

# 2. 运行单个病案测试
print("\n运行单个病案测试...")
try:
    payload = {
        "year": 2023,
        "limit": 1,
        "a48": "445583",
        "a49": "1"
    }
    
    response = requests.post(
        "http://localhost:4101/api/qc/batch",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 质控批次启动成功: {result.get('batchKey', 'N/A')}")
        
        # 等待处理完成
        time.sleep(5)
        
        # 获取缺陷详情
        defect_response = requests.get(
            "http://localhost:4101/api/qc/case-defects/445583_1",
            timeout=10
        )
        
        if defect_response.status_code == 200:
            defects = defect_response.json()
            print(f"\n病案445583_1的缺陷详情:")
            
            ethnicity_defects = []
            for defect in defects:
                rule_code = defect.get('ruleCode', '')
                field_code = defect.get('fieldCode', '')
                field_name = defect.get('fieldName', '')
                actual_value = defect.get('actualValue', '')
                expected_value = defect.get('expectedValue', '')
                
                if 'RC035' in rule_code or 'A19C' in field_code or 'A01' in field_code or '民族' in field_name:
                    ethnicity_defects.append(defect)
                    print(f"  民族相关缺陷:")
                    print(f"    规则代码: {rule_code}")
                    print(f"    字段代码: {field_code}")
                    print(f"    字段名称: {field_name}")
                    print(f"    实际值: '{actual_value}'")
                    print(f"    期望值: {expected_value}")
                    print()
            
            if not ethnicity_defects:
                print("  ✅ 无民族相关缺陷 (说明A19C='1'是有效值)")
            
            # 显示所有缺陷的概览
            print(f"\n总缺陷数: {len(defects)}")
            if len(defects) > 0:
                print("所有缺陷字段:")
                for defect in defects[:5]:  # 只显示前5个
                    print(f"  {defect.get('fieldCode')} ({defect.get('fieldName')}): {defect.get('ruleCode')}")
                if len(defects) > 5:
                    print(f"  ... 还有 {len(defects) - 5} 个缺陷")
        else:
            print(f"❌ 获取缺陷详情失败: {defect_response.status_code}")
            
    else:
        print(f"❌ 质控批次失败: {response.status_code}")
        print(f"响应: {response.text}")
        
except Exception as e:
    print(f"❌ 测试失败: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)