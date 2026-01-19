#!/usr/bin/env python3
import requests
import json
import time

# API配置
BASE_URL = "http://localhost:4101"

def test_new_batch_qc():
    """测试新的批量质控"""
    print("🧪 测试新的批量质控")
    print("=" * 60)
    
    # 执行一个新的批量质控
    print("\n1. 🚀 启动新的批量质控...")
    try:
        response = requests.post(f"{BASE_URL}/api/qc/check/batch", json={
            "periodType": "month",
            "year": 2020,
            "month": 1
        }, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            
            print(f"✅ 批量质控启动成功")
            print(f"   批次键: {data.get('batchKey')}")
            print(f"   状态: {data.get('status')}")
            print(f"   进度: {data.get('progress', 0)}%")
            
            batch_key = data.get('batchKey')
            
            # 等待批量质控完成
            print(f"\n2. ⏳ 等待批量质控完成...")
            max_wait = 120  # 最多等待2分钟
            wait_time = 0
            
            while wait_time < max_wait:
                time.sleep(5)
                wait_time += 5
                
                # 查询状态
                status_response = requests.get(f"{BASE_URL}/api/qc/batch/status/{batch_key}", timeout=30)
                
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    status_data = status_result.get('data', {})
                    
                    status = status_data.get('status')
                    progress = status_data.get('progress', 0)
                    
                    print(f"   状态: {status}, 进度: {progress}% (等待 {wait_time}s)")
                    
                    if status == 'completed':
                        print(f"   ✅ 批量质控完成！")
                        
                        # 显示详细结果
                        print(f"\\n3. 📊 批量质控结果:")
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
                        
                        if cross_defect_count is not None and cross_defect_count > 0:
                            print(f"   ✅ 成功检出Cross规则违规！")
                        elif cross_defect_count is not None:
                            print(f"   ℹ️  未检出Cross规则违规（正常情况）")
                        else:
                            print(f"   ⚠️  Cross规则统计字段为空")
                        
                        break
                    elif status == 'failed':
                        print(f"   ❌ 批量质控失败")
                        break
                else:
                    print(f"   ⚠️  状态查询失败: {status_response.status_code}")
            
            if wait_time >= max_wait:
                print(f"   ⏰ 等待超时，批量质控可能仍在进行中")
                
        else:
            print(f"❌ 批量质控启动失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 批量质控异常: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 新批量质控测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_new_batch_qc()