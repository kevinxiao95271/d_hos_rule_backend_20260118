#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:4101/api"

def check_optimization_status():
    """检查优化状态"""
    print("医疗质控系统优化效果检查")
    print("=" * 40)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查服务状态
    print("\n1. 检查服务状态...")
    try:
        response = requests.get(f"{BASE_URL}/qc/status", timeout=5)
        if response.status_code == 200:
            print("✅ 服务正常运行")
        else:
            print(f"❌ 服务异常: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 服务连接失败: {e}")
        return
    
    # 2. 检查优化接口是否可用
    print("\n2. 检查优化接口...")
    try:
        # 用一个简单的请求测试接口
        response = requests.post(f"{BASE_URL}/qc/check/batch/optimized", 
                               json={'periodType': 'year', 'year': 2019},  # 用2019年，数据更少
                               timeout=5)
        
        if response.status_code == 200:
            print("✅ 优化接口可用")
            result = response.json().get('data', {})
            case_count = result.get('caseCount', 0)
            print(f"   2019年病案数量: {case_count}个")
        elif response.status_code == 404:
            print("❌ 优化接口不存在")
            print("   需要检查 BatchQcServiceOptimized 是否正确部署")
        else:
            print(f"⚠️  优化接口响应异常: {response.status_code}")
    
    except Exception as e:
        print(f"❌ 优化接口测试失败: {e}")
    
    # 3. 检查当前批次状态
    print("\n3. 检查当前批次状态...")
    
    batch_keys = ['2020_opt', '2023_opt', '2019_opt']
    
    for batch_key in batch_keys:
        try:
            response = requests.get(f"{BASE_URL}/qc/batch/status/{batch_key}", timeout=5)
            
            if response.status_code == 200:
                status = response.json().get('data', {})
                progress = status.get('progress', 0)
                batch_status = status.get('status', 'unknown')
                case_count = status.get('caseCount', 0)
                
                print(f"   批次 {batch_key}:")
                print(f"     状态: {batch_status}")
                print(f"     进度: {progress}%")
                print(f"     已处理: {case_count}个病案")
                
                if batch_status == 'processing' and progress > 0:
                    print(f"     ✅ 正在处理中，有进展")
                elif batch_status == 'processing' and progress == 0:
                    print(f"     ⚠️  处理中但无进展")
                elif batch_status == 'completed':
                    print(f"     ✅ 已完成")
                elif batch_status == 'failed':
                    print(f"     ❌ 处理失败")
            
            else:
                print(f"   批次 {batch_key}: 无状态信息")
        
        except Exception as e:
            print(f"   批次 {batch_key}: 查询异常 - {e}")
    
    # 4. 测试单个病案性能
    print("\n4. 测试单个病案性能...")
    test_single_case_performance()
    
    # 5. 给出建议
    print("\n" + "=" * 40)
    print("📋 优化建议")
    print("=" * 40)
    
    print("✅ 已完成的优化:")
    print("   • BatchQcServiceOptimized.java - 8线程并行处理")
    print("   • 预加载规则到内存")
    print("   • Redis缓存字典验证")
    print("   • 批量数据库操作")
    print("   • 优化接口: POST /api/qc/check/batch/optimized")
    
    print("\n🎯 使用建议:")
    print("   1. 使用优化接口处理大批量数据")
    print("   2. 监控系统资源使用（CPU、内存）")
    print("   3. 如果性能仍不理想，可以调整线程数")
    
    print("\n⚙️  调优参数（在 BatchQcServiceOptimized.java 中）:")
    print("   • 线程池大小: 当前8，可根据CPU核心数调整")
    print("   • 并行批量大小: 当前12，可调整为16或20")
    print("   • 数据库批量大小: 当前50，可调整为100")

def test_single_case_performance():
    """测试单个病案性能"""
    try:
        # 测试单个病案处理时间
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/qc/check", 
                               json={
                                   'a48': '20003285',
                                   'a49': '1'
                               }, timeout=30)
        
        process_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json().get('data', {})
            defect_count = result.get('defectCount', 0)
            final_score = result.get('finalScore', 0)
            
            print(f"   单病案测试结果:")
            print(f"     处理时间: {process_time:.2f}秒")
            print(f"     缺陷数量: {defect_count}个")
            print(f"     最终得分: {final_score}分")
            
            if process_time <= 3:
                print(f"     ✅ 性能优秀！")
            elif process_time <= 5:
                print(f"     ✅ 性能良好")
            else:
                print(f"     ⚠️  性能需要进一步优化")
        
        else:
            print(f"   单病案测试失败: {response.status_code}")
    
    except Exception as e:
        print(f"   单病案测试异常: {e}")

if __name__ == "__main__":
    check_optimization_status()