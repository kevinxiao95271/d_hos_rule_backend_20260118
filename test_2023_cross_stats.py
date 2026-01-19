#!/usr/bin/env python3
import requests
import json
import time

# API配置
BASE_URL = "http://localhost:4101"

def test_2023_cross_stats():
    """测试2023年数据的Cross规则统计"""
    print("🧪 测试2023年Cross规则统计")
    print("=" * 60)
    
    # 1. 先测试单个病案
    print("\n1. 🔍 测试单个2023年病案...")
    try:
        response = requests.post(f"{BASE_URL}/api/qc/check/single", 
                               params={"a48": "2023001", "a49": "001"}, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            
            print(f"✅ 单病案质控成功")
            print(f"   病案键: {data.get('mrKey')}")
            print(f"   总违规数: {data.get('defectCount', 0)}")
            print(f"   Cross违规数: {data.get('crossDefectCount', 0)}")
            print(f"   Cross扣分: {data.get('crossTotalDeduct', 0)}")
            
        else:
            print(f"❌ 单病案质控失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 单病案质控异常: {e}")
    
    # 2. 执行2023年批量质控（数据量较少）
    print("\n2. 🚀 启动2023年批量质控...")
    try:
        response = requests.post(f"{BASE_URL}/api/qc/check/batch", json={
            "periodType": "year",
            "year": 2023
        }, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            
            print(f"✅ 批量质控启动成功")
            print(f"   批次键: {data.get('batchKey')}")
            print(f"   状态: {data.get('status')}")
            
            batch_key = data.get('batchKey')
            
            # 等待完成（2023年数据少，应该很快）
            print(f"\n3. ⏳ 等待批量质控完成...")
            max_wait = 60  # 最多等待1分钟
            wait_time = 0
            
            while wait_time < max_wait:
                time.sleep(3)
                wait_time += 3
                
                # 查询状态
                status_response = requests.get(f"{BASE_URL}/api/qc/batch/status/{batch_key}", timeout=30)
                
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    status_data = status_result.get('data', {})
                    
                    status = status_data.get('status')
                    progress = status_data.get('progress', 0)
                    case_count = status_data.get('caseCount', 0)
                    
                    print(f"   状态: {status}, 进度: {progress}%, 病案数: {case_count} (等待 {wait_time}s)")
                    
                    if status == 'completed':
                        print(f"   ✅ 批量质控完成！")
                        
                        # 显示详细结果
                        print(f"\\n4. 📊 2023年批量质控结果:")
                        print(f"   📋 基本统计:")
                        print(f"     - 处理病案数: {status_data.get('caseCount', 0)}")
                        print(f"     - 总违规数: {status_data.get('totalDefectCount', 0)}")
                        print(f"     - 平均违规数: {status_data.get('avgDefect', 0)}")
                        print(f"     - 平均得分: {status_data.get('avgScore', 0)}")
                        
                        # 检查Cross规则统计
                        cross_defect_count = status_data.get('crossDefectCount')
                        cross_total_deduct = status_data.get('crossTotalDeduct')
                        avg_cross_defect = status_data.get('avgCrossDefect')
                        
                        print(f"   🎯 Cross规则统计:")
                        print(f"     - Cross违规总数: {cross_defect_count}")
                        print(f"     - Cross总扣分: {cross_total_deduct}")
                        print(f"     - 平均Cross违规数: {avg_cross_defect}")
                        
                        # 计算统计
                        total_defects = status_data.get('totalDefectCount', 0)
                        if total_defects > 0 and cross_defect_count is not None:
                            cross_ratio = (cross_defect_count / total_defects) * 100
                            print(f"     - Cross规则占比: {cross_ratio:.1f}%")
                        
                        if cross_defect_count is not None and cross_defect_count > 0:
                            print(f"   ✅ 成功检出 {cross_defect_count} 个Cross规则违规！")
                            print(f"   💡 Cross规则系统正常工作")
                        elif cross_defect_count is not None:
                            print(f"   ℹ️  未检出Cross规则违规（可能是正常情况）")
                        else:
                            print(f"   ⚠️  Cross规则统计字段为空，可能需要检查代码")
                        
                        break
                    elif status == 'failed':
                        print(f"   ❌ 批量质控失败")
                        break
                else:
                    print(f"   ⚠️  状态查询失败: {status_response.status_code}")
            
            if wait_time >= max_wait:
                print(f"   ⏰ 等待超时")
                
        else:
            print(f"❌ 批量质控启动失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 批量质控异常: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 2023年Cross规则统计测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_2023_cross_stats()