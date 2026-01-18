import requests
import json
import time

print("🎯 民族字段修复最终测试")
print("=" * 50)

base_url = "http://localhost:4101"

# 1. 检查民族相关规则
print("\n1. 检查民族相关规则...")
try:
    response = requests.get(f"{base_url}/api/qc/rules", timeout=10)
    if response.status_code == 200:
        rules_data = response.text
        print(f"✅ 规则API响应正常 (长度: {len(rules_data)})")
        
        # 检查是否包含民族相关规则
        if 'A19C' in rules_data and 'RC035' in rules_data:
            print("✅ 发现A19C和RC035相关规则")
        if 'RULE_A19C_RC035' in rules_data:
            print("✅ 发现RULE_A19C_RC035规则")
        if 'A19C_value_check' in rules_data:
            print("✅ 发现A19C_value_check规则")
            
    else:
        print(f"❌ 规则API失败: HTTP {response.status_code}")
        
except Exception as e:
    print(f"❌ 规则API异常: {e}")

# 2. 运行质控批次
print("\n2. 运行质控批次...")
try:
    payload = {
        "year": 2023,
        "limit": 10  # 小批量测试
    }
    
    response = requests.post(
        f"{base_url}/api/qc/batch",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        batch_key = result.get('batchKey', 'N/A')
        print(f"✅ 质控批次启动成功: {batch_key}")
        
        # 等待批次完成
        print("⏳ 等待质控完成...")
        time.sleep(15)
        
        # 检查批次状态
        try:
            status_response = requests.get(f"{base_url}/api/qc/batch/{batch_key}/status", timeout=10)
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"📊 批次状态: {status.get('status', 'unknown')}")
                print(f"📊 处理病案: {status.get('caseCount', 0)}")
                print(f"📊 缺陷总数: {status.get('totalDefectCount', 0)}")
            else:
                print(f"⚠️  无法获取批次状态: HTTP {status_response.status_code}")
        except:
            print("⚠️  批次状态检查失败")
            
    else:
        print(f"❌ 质控批次启动失败: HTTP {response.status_code}")
        print(f"响应: {response.text}")
        
except Exception as e:
    print(f"❌ 质控批次异常: {e}")

# 3. 检查病案445583_1的结果
print("\n3. 检查病案445583_1的质控结果...")
try:
    response = requests.get(f"{base_url}/api/qc/case/445583_1/defects", timeout=10)
    
    if response.status_code == 200:
        defects = response.json()
        
        if isinstance(defects, list):
            print(f"📋 病案445583_1共有 {len(defects)} 个缺陷")
            
            # 查找民族相关缺陷
            ethnicity_defects = []
            for defect in defects:
                if isinstance(defect, dict):
                    rule_code = defect.get('ruleCode', '')
                    field_code = defect.get('fieldCode', '')
                    field_name = defect.get('fieldName', '')
                    
                    if ('RC035' in rule_code or 'A19C' in field_code or 
                        '民族' in field_name or 'A01' in rule_code):
                        ethnicity_defects.append(defect)
            
            if ethnicity_defects:
                print("⚠️  发现民族相关缺陷:")
                for defect in ethnicity_defects:
                    print(f"   规则: {defect.get('ruleCode')}")
                    print(f"   字段: {defect.get('fieldCode')} ({defect.get('fieldName')})")
                    print(f"   实际值: '{defect.get('actualValue')}'")
                    print(f"   期望值: {defect.get('expectedValue')}")
                    
                    # 检查修复效果
                    if defect.get('ruleCode') == 'RULE_A01_RC035':
                        print("   ❌ 仍然使用旧的规则代码!")
                    elif 'ABS' in str(defect.get('actualValue', '')):
                        print("   ❌ 仍然显示错误的实际值!")
                    else:
                        print("   ✅ 规则代码和实际值看起来正确")
                    print()
            else:
                print("✅ 病案445583_1无民族相关缺陷 (预期结果)")
                print("   这意味着A19C='1'被正确识别为有效的民族代码")
        else:
            print(f"⚠️  缺陷数据格式异常: {type(defects)}")
            
    else:
        print(f"⚠️  无法获取病案缺陷: HTTP {response.status_code}")
        
except Exception as e:
    print(f"❌ 病案缺陷检查异常: {e}")

print("\n" + "=" * 50)
print("🎯 测试完成")
print("=" * 50)

print("\n📋 修复验证要点:")
print("✅ 规则代码应该是 RULE_A19C_RC035 (不是 RULE_A01_RC035)")
print("✅ 字段代码应该是 A19C (不是 A01)")
print("✅ 实际值应该是 '1' (不是 'ABS478045')")
print("✅ 由于'1'是有效的民族代码，应该无违规记录")

print("\n🎉 如果看到'无民族相关缺陷'，说明修复成功!")