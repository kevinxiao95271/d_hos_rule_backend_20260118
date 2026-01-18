import requests
import json
import time

def test_service():
    """测试服务是否可用"""
    try:
        response = requests.get("http://localhost:4101/api/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def run_qc_test():
    """运行质控测试"""
    print("🔄 运行质控测试...")
    
    try:
        # 运行小批量质控
        payload = {"year": 2023, "limit": 5}
        response = requests.post(
            "http://localhost:4101/api/qc/batch",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 质控批次启动成功: {result.get('batchKey', 'N/A')}")
            return True
        else:
            print(f"❌ 质控批次启动失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 质控测试失败: {e}")
        return False

def check_ethnicity_results():
    """检查民族字段结果"""
    print("🔍 检查民族字段结果...")
    
    try:
        # 获取字段统计
        response = requests.get("http://localhost:4101/api/qc/field-stats", timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            
            ethnicity_stats = []
            for stat in stats:
                field_code = stat.get('fieldCode', '')
                field_name = stat.get('fieldName', '')
                
                if 'A19C' in field_code or '民族' in field_name:
                    ethnicity_stats.append(stat)
            
            if ethnicity_stats:
                print("📊 民族字段统计:")
                for stat in ethnicity_stats:
                    print(f"  字段: {stat.get('fieldCode')} ({stat.get('fieldName')})")
                    print(f"  缺陷数: {stat.get('defectCount', 0)}")
                    print(f"  规则数: {stat.get('ruleCount', 0)}")
            else:
                print("✅ 未发现民族字段缺陷 (数据正确)")
                
        else:
            print(f"⚠️  无法获取字段统计: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 检查结果失败: {e}")

def check_case_defects():
    """检查病案445583_1的缺陷"""
    print("🔍 检查病案445583_1的缺陷...")
    
    try:
        response = requests.get("http://localhost:4101/api/qc/case-defects/445583_1", timeout=10)
        
        if response.status_code == 200:
            defects = response.json()
            
            ethnicity_defects = []
            for defect in defects:
                rule_code = defect.get('ruleCode', '')
                field_code = defect.get('fieldCode', '')
                field_name = defect.get('fieldName', '')
                
                if 'RC035' in rule_code or 'A19C' in field_code or '民族' in field_name:
                    ethnicity_defects.append(defect)
            
            if ethnicity_defects:
                print("⚠️  发现民族相关缺陷:")
                for defect in ethnicity_defects:
                    print(f"  规则: {defect.get('ruleCode')}")
                    print(f"  字段: {defect.get('fieldCode')} ({defect.get('fieldName')})")
                    print(f"  实际值: '{defect.get('actualValue')}'")
                    print(f"  期望值: {defect.get('expectedValue')}")
                    
                    # 检查是否还是旧的错误
                    if defect.get('ruleCode') == 'RULE_A01_RC035':
                        print("  ❌ 仍然显示旧的规则代码!")
                    elif defect.get('actualValue') and 'ABS' in str(defect.get('actualValue')):
                        print("  ❌ 仍然显示错误的实际值!")
                    else:
                        print("  ✅ 规则代码和实际值看起来正确")
            else:
                print("✅ 病案445583_1无民族相关缺陷 (预期结果)")
                
        else:
            print(f"⚠️  无法获取病案缺陷: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 检查病案缺陷失败: {e}")

def main():
    print("=" * 60)
    print("快速民族字段修复验证")
    print("=" * 60)
    
    # 等待服务启动
    print("⏳ 等待Spring Boot服务启动...")
    max_wait = 120  # 最多等待2分钟
    wait_time = 0
    
    while wait_time < max_wait:
        if test_service():
            print("✅ 服务已启动")
            break
        print(f"  等待中... ({wait_time}s/{max_wait}s)")
        time.sleep(5)
        wait_time += 5
    else:
        print("❌ 服务启动超时")
        return
    
    # 运行测试
    if run_qc_test():
        print("\n⏳ 等待质控完成...")
        time.sleep(10)
        
        check_ethnicity_results()
        check_case_defects()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    print("\n📋 验证要点:")
    print("✅ 规则代码应该是 RULE_A19C_RC035")
    print("✅ 字段代码应该是 A19C")
    print("✅ 实际值应该是 '1' (汉族)")
    print("✅ 由于'1'是有效值，应该无违规记录")

if __name__ == "__main__":
    main()