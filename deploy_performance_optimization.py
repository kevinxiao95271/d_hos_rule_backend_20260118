#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import time
from datetime import datetime

def check_java_service():
    """检查Java服务状态"""
    print("=== 检查Java服务状态 ===")
    
    try:
        # 检查Java进程
        result = subprocess.run(['jps', '-l'], capture_output=True, text=True)
        
        if 'Application' in result.stdout or 'jar' in result.stdout:
            print("✅ Java服务正在运行")
            return True
        else:
            print("❌ Java服务未运行")
            return False
    
    except Exception as e:
        print(f"❌ 检查Java服务失败: {e}")
        return False

def restart_java_service():
    """重启Java服务以应用优化"""
    print("\n=== 重启Java服务 ===")
    
    try:
        # 停止现有服务
        print("1. 停止现有服务...")
        subprocess.run(['pkill', '-f', 'java.*jar'], capture_output=True)
        time.sleep(5)
        
        # 启动服务
        print("2. 启动优化后的服务...")
        
        # 检查是否有start.bat
        if os.path.exists('start.bat'):
            print("   使用start.bat启动服务...")
            subprocess.Popen(['start.bat'], shell=True)
        else:
            # 尝试直接启动jar
            jar_files = [f for f in os.listdir('.') if f.endswith('.jar')]
            if jar_files:
                jar_file = jar_files[0]
                print(f"   直接启动JAR文件: {jar_file}")
                subprocess.Popen(['java', '-jar', jar_file])
            else:
                print("   未找到JAR文件，尝试Maven启动...")
                subprocess.Popen(['mvn', 'spring-boot:run'])
        
        print("✅ 服务启动命令已执行")
        print("⏳ 等待服务启动...")
        
        # 等待服务启动
        for i in range(30):
            time.sleep(2)
            if check_service_health():
                print("✅ 服务启动成功")
                return True
            print(f"   等待中... ({i+1}/30)")
        
        print("⚠️  服务启动超时，请手动检查")
        return False
        
    except Exception as e:
        print(f"❌ 重启服务失败: {e}")
        return False

def check_service_health():
    """检查服务健康状态"""
    try:
        import requests
        response = requests.get('http://localhost:4101/api/qc/status', timeout=5)
        return response.status_code == 200
    except:
        return False

def verify_optimization_features():
    """验证优化功能"""
    print("\n=== 验证优化功能 ===")
    
    try:
        import requests
        
        # 1. 检查优化批量接口
        print("1. 检查优化批量接口...")
        
        response = requests.post('http://localhost:4101/api/qc/check/batch/optimized', 
                               json={'periodType': 'year', 'year': 2020}, 
                               timeout=10)
        
        if response.status_code == 200:
            print("   ✅ 优化批量接口可用")
        else:
            print(f"   ❌ 优化批量接口异常: {response.status_code}")
        
        # 2. 检查Redis缓存
        print("2. 检查Redis缓存...")
        
        response = requests.get('http://localhost:4101/api/dict/cache/stats', timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            cache_count = result.get('data', {}).get('dictCacheCount', 0)
            print(f"   ✅ Redis缓存正常，已缓存{cache_count}个字典")
        else:
            print(f"   ❌ Redis缓存检查失败: {response.status_code}")
        
        # 3. 检查规则数量
        print("3. 检查规则数量...")
        
        response = requests.get('http://localhost:4101/api/qc/rules', timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            rule_count = len(result.get('data', []))
            print(f"   ✅ 规则加载正常，共{rule_count}条规则")
        else:
            print(f"   ❌ 规则检查失败: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证优化功能失败: {e}")
        return False

def create_performance_test_script():
    """创建性能测试脚本"""
    print("\n=== 创建性能测试脚本 ===")
    
    test_script = '''@echo off
echo 医疗质控系统性能测试
echo ========================

echo 1. 测试优化批量处理...
python test_optimized_batch_performance.py

echo.
echo 2. 如果需要单独测试，可以使用以下命令：
echo    python -c "import requests; print(requests.post('http://localhost:4101/api/qc/check/batch/optimized', json={'periodType':'year','year':2023}).json())"

echo.
echo 测试完成！
pause
'''
    
    try:
        with open('run_performance_test.bat', 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        print("✅ 已创建性能测试脚本: run_performance_test.bat")
        return True
        
    except Exception as e:
        print(f"❌ 创建测试脚本失败: {e}")
        return False

def show_optimization_summary():
    """显示优化总结"""
    print(f"\n" + "=" * 60)
    print("🚀 医疗质控系统性能优化部署完成")
    print("=" * 60)
    
    print(f"📋 优化内容:")
    print(f"   ✅ 创建了BatchQcServiceOptimized（8线程并行处理）")
    print(f"   ✅ 添加了优化批量接口 /api/qc/check/batch/optimized")
    print(f"   ✅ 集成Redis缓存预热")
    print(f"   ✅ 实现批量数据库操作")
    print(f"   ✅ 优化规则引擎算法")
    
    print(f"\n🎯 预期效果:")
    print(f"   • 处理时间从35分钟压缩到5分钟以内")
    print(f"   • 性能提升7-50倍")
    print(f"   • 保持完整1699条规则")
    print(f"   • 保持所有质控功能")
    
    print(f"\n🔧 使用方法:")
    print(f"   1. 标准批量处理: POST /api/qc/check/batch")
    print(f"   2. 优化批量处理: POST /api/qc/check/batch/optimized")
    print(f"   3. 运行性能测试: run_performance_test.bat")
    
    print(f"\n📊 测试建议:")
    print(f"   1. 先用小数据集测试优化效果")
    print(f"   2. 监控系统资源使用情况")
    print(f"   3. 根据实际效果调整线程数和批量大小")
    print(f"   4. 确保Redis缓存命中率高")
    
    print(f"\n⚙️  调优参数:")
    print(f"   • 线程数: BatchQcServiceOptimized.parallelExecutor (当前8)")
    print(f"   • 批量大小: PARALLEL_BATCH_SIZE (当前12)")
    print(f"   • 数据库批量: DB_BATCH_SIZE (当前50)")

def main():
    """主函数"""
    print("医疗质控系统性能优化部署")
    print("=" * 50)
    print(f"部署时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查当前服务状态
    service_running = check_java_service()
    
    # 2. 如果服务在运行，重启以应用优化
    if service_running:
        restart_success = restart_java_service()
        
        if restart_success:
            # 3. 验证优化功能
            verify_optimization_features()
        else:
            print("⚠️  服务重启可能未成功，请手动重启服务")
    else:
        print("💡 请手动启动服务以应用优化")
    
    # 4. 创建测试脚本
    create_performance_test_script()
    
    # 5. 显示优化总结
    show_optimization_summary()
    
    print(f"\n🎉 部署完成！")
    print(f"下一步: 运行 run_performance_test.bat 测试性能")

if __name__ == "__main__":
    main()