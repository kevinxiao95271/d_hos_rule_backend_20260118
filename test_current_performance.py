#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import json
import pymysql
from datetime import datetime

# 数据库连接配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

BASE_URL = "http://localhost:4101/api"

def clear_previous_results():
    """清理之前的测试结果"""
    print("=== 清理之前的测试结果 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 清理2023年的质控结果
        cursor.execute("""
            DELETE FROM kiro_qc_case_result 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
        """)
        
        cursor.execute("""
            DELETE FROM kiro_qc_defect_detail 
            WHERE mr_key IN (
                SELECT CONCAT(A48, '_', A49) 
                FROM d_mr 
                WHERE B15 LIKE '2023/%'
            )
        """)
        
        # 清理批次汇总
        cursor.execute("DELETE FROM kiro_qc_batch_summary WHERE batch_key LIKE '%2023%'")
        
        conn.commit()
        
        print("✅ 清理完成")
        
    finally:
        cursor.close()
        conn.close()

def test_current_batch_performance():
    """测试当前批量处理性能"""
    print("\n=== 测试当前批量处理性能 ===")
    
    # 启动批量处理
    start_time = time.time()
    
    try:
        response = requests.post(f"{BASE_URL}/qc/check/batch", 
                               json={
                                   'periodType': 'year',
                                   'year': 2023
                               }, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 批量处理启动失败: {response.status_code}")
            print(f"响应: {response.text}")
            return None
        
        result = response.json().get('data', {})
        batch_key = result.get('batchKey', '')
        case_count = result.get('caseCount', 0)
        
        print(f"✅ 批量处理已启动")
        print(f"批次键: {batch_key}")
        print(f"病案数量: {case_count}")
        
        # 监控进度（只监控5分钟，看看能处理多少）
        return monitor_batch_progress_limited(batch_key, start_time, case_count)
        
    except Exception as e:
        print(f"❌ 批量处理异常: {e}")
        return None

def monitor_batch_progress_limited(batch_key, start_time, total_cases):
    """监控批量处理进度（限时5分钟）"""
    print(f"\n=== 监控处理进度（限时5分钟测试） ===")
    
    max_wait = 300  # 5分钟
    wait_time = 0
    last_progress = 0
    
    while wait_time < max_wait:
        time.sleep(10)
        wait_time += 10
        
        try:
            response = requests.get(f"{BASE_URL}/qc/batch/status/{batch_key}", timeout=10)
            
            if response.status_code == 200:
                status = response.json().get('data', {})
                progress = status.get('progress', 0)
                batch_status = status.get('status', 'unknown')
                processed_count = status.get('caseCount', 0)
                
                current_time = time.time() - start_time
                
                if progress != last_progress or wait_time % 30 == 0:  # 每30秒或进度变化时输出
                    print(f"  进度: {progress}% ({processed_count}个病案), 已用时: {current_time/60:.1f}分钟, 状态: {batch_status}")
                    last_progress = progress
                
                if batch_status == 'completed':
                    total_time = time.time() - start_time
                    
                    print(f"  ✅ 处理完成！")
                    print(f"  总耗时: {total_time/60:.1f}分钟")
                    print(f"  平均每病案: {total_time/processed_count:.2f}秒")
                    
                    return {
                        'completed': True,
                        'total_time': total_time,
                        'total_minutes': total_time / 60,
                        'case_count': processed_count,
                        'avg_per_case': total_time / processed_count,
                        'success': True
                    }
                
                elif batch_status == 'failed':
                    print(f"  ❌ 处理失败")
                    return {'success': False, 'reason': 'batch_failed'}
            
            else:
                print(f"    状态查询失败: {response.status_code}")
        
        except Exception as e:
            print(f"    状态查询异常: {e}")
    
    # 5分钟时间到，计算当前性能
    current_time = time.time() - start_time
    
    try:
        response = requests.get(f"{BASE_URL}/qc/batch/status/{batch_key}", timeout=10)
        if response.status_code == 200:
            status = response.json().get('data', {})
            progress = status.get('progress', 0)
            processed_count = status.get('caseCount', 0)
            
            print(f"  ⏰ 5分钟测试结束")
            print(f"  当前进度: {progress}% ({processed_count}个病案)")
            print(f"  已用时: {current_time/60:.1f}分钟")
            
            if processed_count > 0:
                avg_per_case = current_time / processed_count
                estimated_total_time = avg_per_case * total_cases
                
                print(f"  平均每病案: {avg_per_case:.2f}秒")
                print(f"  预估总时间: {estimated_total_time/60:.1f}分钟")
                
                return {
                    'completed': False,
                    'partial_time': current_time,
                    'partial_minutes': current_time / 60,
                    'processed_count': processed_count,
                    'total_cases': total_cases,
                    'progress': progress,
                    'avg_per_case': avg_per_case,
                    'estimated_total_minutes': estimated_total_time / 60,
                    'success': True
                }
            
    except Exception as e:
        print(f"    最终状态查询异常: {e}")
    
    return {'success': False, 'reason': 'timeout'}

def analyze_performance_and_optimization():
    """分析性能并给出优化建议"""
    print(f"\n" + "=" * 60)
    print("📊 性能分析和优化建议")
    print("=" * 60)
    
    print(f"🔍 当前性能瓶颈分析:")
    print(f"   • 单线程顺序处理病案")
    print(f"   • 每个病案重复查询规则")
    print(f"   • 逐条插入数据库结果")
    print(f"   • 字典验证重复查询数据库")
    
    print(f"\n🚀 已实现的优化方案:")
    print(f"   ✅ BatchQcServiceOptimized.java - 8线程并行处理")
    print(f"   ✅ 预加载所有规则到内存")
    print(f"   ✅ Redis缓存预热")
    print(f"   ✅ 批量数据库操作")
    print(f"   ✅ 优化的批量接口 /api/qc/check/batch/optimized")
    
    print(f"\n📋 部署优化的步骤:")
    print(f"   1. 重新编译项目: mvn clean compile")
    print(f"   2. 重新打包: mvn package")
    print(f"   3. 重启服务")
    print(f"   4. 测试优化接口: POST /api/qc/check/batch/optimized")
    
    print(f"\n⚡ 预期优化效果:")
    print(f"   • 处理时间: 从35分钟 → 5分钟以内")
    print(f"   • 性能提升: 7-10倍")
    print(f"   • 并行处理: 8个病案同时处理")
    print(f"   • 缓存加速: Redis字典验证")

def create_deployment_guide():
    """创建部署指南"""
    print(f"\n=== 创建部署指南 ===")
    
    guide = """# 医疗质控系统性能优化部署指南

## 优化内容
1. **BatchQcServiceOptimized.java** - 8线程并行批量处理服务
2. **优化的QcController接口** - /api/qc/check/batch/optimized
3. **QcService优化方法** - batchCheckOptimized()

## 部署步骤

### 1. 停止当前服务
```bash
# 找到Java进程
jps -l

# 停止服务（替换PID）
kill <PID>
```

### 2. 重新编译和打包
```bash
# 清理和编译
mvn clean compile

# 打包
mvn package -DskipTests

# 或者直接运行
mvn spring-boot:run
```

### 3. 启动服务
```bash
# 使用JAR文件启动
java -jar target/medical-qc-*.jar

# 或使用start.bat（如果存在）
start.bat
```

### 4. 验证优化功能
```bash
# 检查服务状态
curl http://localhost:4101/api/qc/status

# 测试优化批量接口
curl -X POST http://localhost:4101/api/qc/check/batch/optimized \\
  -H "Content-Type: application/json" \\
  -d '{"periodType":"year","year":2023}'
```

## 性能对比测试

### 标准版本
```bash
POST /api/qc/check/batch
```

### 优化版本
```bash
POST /api/qc/check/batch/optimized
```

## 预期效果
- **处理时间**: 35分钟 → 5分钟
- **性能提升**: 7-10倍
- **并发处理**: 8线程并行
- **规则完整性**: 保持1699条规则

## 调优参数
在BatchQcServiceOptimized.java中可调整：
- `parallelExecutor`: 线程池大小（当前8）
- `PARALLEL_BATCH_SIZE`: 并行批量大小（当前12）
- `DB_BATCH_SIZE`: 数据库批量大小（当前50）

## 监控建议
1. 监控CPU使用率（应该更高，因为并行处理）
2. 监控内存使用（预加载规则会增加内存使用）
3. 监控数据库连接数
4. 监控Redis缓存命中率
"""
    
    try:
        with open('OPTIMIZATION_DEPLOYMENT_GUIDE.md', 'w', encoding='utf-8') as f:
            f.write(guide)
        
        print("✅ 已创建部署指南: OPTIMIZATION_DEPLOYMENT_GUIDE.md")
        return True
        
    except Exception as e:
        print(f"❌ 创建部署指南失败: {e}")
        return False

def main():
    """主函数"""
    print("医疗质控系统当前性能测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 清理之前的结果
    clear_previous_results()
    
    # 2. 测试当前性能（5分钟限时）
    result = test_current_batch_performance()
    
    # 3. 分析结果
    if result and result.get('success'):
        print(f"\n" + "=" * 60)
        print("📊 当前性能测试结果")
        print("=" * 60)
        
        if result.get('completed'):
            print(f"✅ 完整处理完成")
            print(f"   总耗时: {result['total_minutes']:.1f}分钟")
            print(f"   处理病案: {result['case_count']}个")
            print(f"   平均每病案: {result['avg_per_case']:.2f}秒")
        else:
            print(f"⏱️  5分钟部分测试结果")
            print(f"   已处理: {result['processed_count']}/{result['total_cases']}个病案 ({result['progress']:.1f}%)")
            print(f"   已用时: {result['partial_minutes']:.1f}分钟")
            print(f"   平均每病案: {result['avg_per_case']:.2f}秒")
            print(f"   预估总时间: {result['estimated_total_minutes']:.1f}分钟")
            
            if result['estimated_total_minutes'] > 30:
                print(f"   ❌ 预估时间过长，急需优化！")
            elif result['estimated_total_minutes'] > 10:
                print(f"   ⚠️  预估时间较长，建议优化")
            else:
                print(f"   ✅ 预估时间可接受")
    
    # 4. 分析性能和优化建议
    analyze_performance_and_optimization()
    
    # 5. 创建部署指南
    create_deployment_guide()
    
    print(f"\n🎯 下一步行动:")
    print(f"   1. 按照 OPTIMIZATION_DEPLOYMENT_GUIDE.md 部署优化")
    print(f"   2. 重新编译和重启服务")
    print(f"   3. 测试优化后的性能")
    print(f"   4. 对比性能提升效果")

if __name__ == "__main__":
    main()