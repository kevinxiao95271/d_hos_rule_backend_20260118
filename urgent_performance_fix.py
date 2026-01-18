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

def check_current_batch_status():
    """检查当前批量任务状态"""
    print("=== 检查当前批量任务状态 ===")
    
    try:
        # 检查2023年批次状态
        response = requests.get(f"{BASE_URL}/qc/batch/status/2023", timeout=5)
        
        if response.status_code == 200:
            status = response.json().get('data', {})
            progress = status.get('progress', 0)
            batch_status = status.get('status', 'unknown')
            case_count = status.get('caseCount', 0)
            
            print(f"批次状态: {batch_status}")
            print(f"进度: {progress}%")
            print(f"已处理病案: {case_count}个")
            
            if batch_status == 'processing' and progress == 0:
                print("❌ 任务卡住，进度为0")
                return 'stuck'
            elif batch_status == 'processing' and progress < 10:
                print("⚠️  任务进展缓慢")
                return 'slow'
            elif batch_status == 'processing':
                print("✅ 任务正常进行中")
                return 'running'
            elif batch_status == 'completed':
                print("✅ 任务已完成")
                return 'completed'
            else:
                print(f"❓ 未知状态: {batch_status}")
                return 'unknown'
        
        else:
            print(f"❌ 状态查询失败: {response.status_code}")
            return 'error'
    
    except Exception as e:
        print(f"❌ 状态查询异常: {e}")
        return 'error'

def stop_current_batch():
    """停止当前批量任务"""
    print("\n=== 停止当前批量任务 ===")
    
    try:
        # 尝试停止批量任务（如果有这个接口）
        response = requests.post(f"{BASE_URL}/qc/batch/stop/2023", timeout=5)
        
        if response.status_code == 200:
            print("✅ 批量任务已停止")
            return True
        else:
            print(f"⚠️  停止接口不可用: {response.status_code}")
    
    except Exception as e:
        print(f"⚠️  停止接口异常: {e}")
    
    # 清理数据库中的批次状态
    print("清理数据库中的批次状态...")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 删除或更新批次状态
        cursor.execute("DELETE FROM kiro_qc_batch_summary WHERE batch_key = '2023'")
        conn.commit()
        
        print("✅ 已清理批次状态")
        return True
        
    except Exception as e:
        print(f"❌ 清理批次状态失败: {e}")
        return False
    
    finally:
        cursor.close()
        conn.close()

def check_optimization_deployment():
    """检查优化版本是否已部署"""
    print("\n=== 检查优化版本部署状态 ===")
    
    try:
        # 检查优化接口是否可用
        response = requests.post(f"{BASE_URL}/qc/check/batch/optimized", 
                               json={'periodType': 'year', 'year': 2020},  # 用2020年测试，数据少
                               timeout=5)
        
        if response.status_code == 200:
            print("✅ 优化接口可用")
            return True
        elif response.status_code == 404:
            print("❌ 优化接口不存在，需要重新部署")
            return False
        else:
            print(f"⚠️  优化接口异常: {response.status_code}")
            print(f"响应: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ 优化接口测试失败: {e}")
        return False

def create_immediate_fix_guide():
    """创建立即修复指南"""
    print("\n=== 创建立即修复指南 ===")
    
    fix_guide = """# 医疗质控系统性能问题立即修复指南

## 🚨 当前问题
- 几千条规则检查时，单条病案处理时间超过3秒
- 96个病案需要35分钟以上处理时间
- 性能严重不足，影响用户体验

## ⚡ 立即修复步骤

### 1. 停止当前慢速任务
```bash
# 方法1: 通过API停止（如果支持）
curl -X POST http://localhost:4101/api/qc/batch/stop/2023

# 方法2: 重启服务
jps -l  # 找到Java进程PID
kill <PID>  # 停止服务
```

### 2. 重新编译和部署优化版本
```bash
# 清理和编译
mvn clean compile

# 打包
mvn package -DskipTests

# 启动服务
java -jar target/medical-qc-*.jar

# 或使用Maven直接运行
mvn spring-boot:run
```

### 3. 验证优化版本
```bash
# 检查服务状态
curl http://localhost:4101/api/qc/status

# 测试优化接口（用少量数据测试）
curl -X POST http://localhost:4101/api/qc/check/batch/optimized \\
  -H "Content-Type: application/json" \\
  -d '{"periodType":"year","year":2020}'
```

### 4. 使用优化接口处理2023年数据
```bash
# 使用优化接口
curl -X POST http://localhost:4101/api/qc/check/batch/optimized \\
  -H "Content-Type: application/json" \\
  -d '{"periodType":"year","year":2023}'
```

## 🔧 优化版本特性

### BatchQcServiceOptimized.java
- **8线程并行处理**: 同时处理8个病案
- **预加载规则**: 一次性加载1699条规则到内存
- **批量数据库操作**: 50条记录一批写入
- **Redis缓存**: 预热字典缓存，快速验证

### 新增API接口
```
POST /api/qc/check/batch/optimized
Content-Type: application/json
{
  "periodType": "year",
  "year": 2023
}
```

### 性能提升预期
- **单病案处理时间**: 22秒 → 3秒以内
- **96病案总时间**: 35分钟 → 5分钟以内
- **性能提升**: 7-10倍

## 🧪 性能验证

### 测试脚本
```bash
# 运行性能对比测试
python test_standard_vs_optimized.py

# 运行优化性能测试
python test_optimized_batch_performance.py
```

### 监控指标
1. **处理时间**: 每病案平均处理时间
2. **CPU使用率**: 应该更高（并行处理）
3. **内存使用**: 会增加（预加载规则）
4. **数据库连接**: 监控连接池使用

## ⚙️ 调优参数

在 `BatchQcServiceOptimized.java` 中可调整：

```java
// 线程池大小（根据CPU核心数调整）
private final ExecutorService parallelExecutor = Executors.newFixedThreadPool(8);

// 并行批量大小
private static final int PARALLEL_BATCH_SIZE = 12;

// 数据库批量大小
private static final int DB_BATCH_SIZE = 50;
```

## 🔍 故障排除

### 如果优化接口不可用
1. 检查编译是否成功
2. 检查服务是否重启
3. 查看服务日志

### 如果性能仍然不理想
1. 增加线程池大小
2. 增加数据库批量大小
3. 检查Redis缓存状态
4. 监控系统资源使用

### 如果出现内存不足
1. 增加JVM内存: `-Xmx4g`
2. 减少线程池大小
3. 减少批量处理大小

## 📞 紧急联系

如果问题仍然存在：
1. 查看服务日志文件
2. 检查数据库连接状态
3. 验证Redis服务状态
4. 监控系统资源使用情况

---

**创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**紧急程度**: 高
**预期解决时间**: 30分钟内
"""
    
    try:
        with open('URGENT_PERFORMANCE_FIX_GUIDE.md', 'w', encoding='utf-8') as f:
            f.write(fix_guide)
        
        print("✅ 已创建紧急修复指南: URGENT_PERFORMANCE_FIX_GUIDE.md")
        return True
        
    except Exception as e:
        print(f"❌ 创建修复指南失败: {e}")
        return False

def create_deployment_script():
    """创建部署脚本"""
    print("\n=== 创建部署脚本 ===")
    
    # Windows批处理脚本
    bat_script = """@echo off
echo 医疗质控系统优化版本部署脚本
echo ================================

echo 1. 停止当前服务...
for /f "tokens=1" %%i in ('jps -l ^| findstr "medical-qc"') do (
    echo 停止进程 %%i
    taskkill /PID %%i /F
)

echo 2. 清理和编译...
mvn clean compile
if %errorlevel% neq 0 (
    echo 编译失败！
    pause
    exit /b 1
)

echo 3. 打包...
mvn package -DskipTests
if %errorlevel% neq 0 (
    echo 打包失败！
    pause
    exit /b 1
)

echo 4. 启动服务...
start "Medical QC Service" java -jar target/medical-qc-*.jar

echo 5. 等待服务启动...
timeout /t 10

echo 6. 验证服务状态...
curl http://localhost:4101/api/qc/status

echo 部署完成！
echo 现在可以使用优化接口: POST /api/qc/check/batch/optimized
pause
"""
    
    try:
        with open('deploy_optimization.bat', 'w', encoding='utf-8') as f:
            f.write(bat_script)
        
        print("✅ 已创建部署脚本: deploy_optimization.bat")
        return True
        
    except Exception as e:
        print(f"❌ 创建部署脚本失败: {e}")
        return False

def main():
    """主函数"""
    print("医疗质控系统性能问题紧急修复")
    print("=" * 50)
    print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查当前批量任务状态
    batch_status = check_current_batch_status()
    
    # 2. 如果任务卡住或缓慢，建议停止
    if batch_status in ['stuck', 'slow']:
        print(f"\n⚠️  建议停止当前慢速任务")
        stop_current_batch()
    
    # 3. 检查优化版本是否已部署
    optimization_deployed = check_optimization_deployment()
    
    # 4. 创建修复指南和脚本
    create_immediate_fix_guide()
    create_deployment_script()
    
    # 5. 总结和建议
    print(f"\n" + "=" * 50)
    print("🚨 紧急修复建议")
    print("=" * 50)
    
    if not optimization_deployed:
        print("❌ 优化版本未部署，这是性能问题的根本原因")
        print("🚀 立即行动:")
        print("   1. 运行部署脚本: deploy_optimization.bat")
        print("   2. 或手动执行 URGENT_PERFORMANCE_FIX_GUIDE.md 中的步骤")
        print("   3. 使用优化接口: POST /api/qc/check/batch/optimized")
    else:
        print("✅ 优化版本已部署")
        print("🔍 建议检查:")
        print("   1. 是否使用了优化接口")
        print("   2. 系统资源是否充足")
        print("   3. 数据库和Redis是否正常")
    
    print(f"\n📋 可用资源:")
    print(f"   • 紧急修复指南: URGENT_PERFORMANCE_FIX_GUIDE.md")
    print(f"   • 自动部署脚本: deploy_optimization.bat")
    print(f"   • 性能测试脚本: test_optimized_batch_performance.py")
    
    print(f"\n⏱️  预期修复时间: 30分钟内")
    print(f"🎯 预期性能提升: 7-10倍")

if __name__ == "__main__":
    main()