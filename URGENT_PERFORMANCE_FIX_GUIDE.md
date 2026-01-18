# 医疗质控系统性能问题立即修复指南

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
curl -X POST http://localhost:4101/api/qc/check/batch/optimized \
  -H "Content-Type: application/json" \
  -d '{"periodType":"year","year":2020}'
```

### 4. 使用优化接口处理2023年数据
```bash
# 使用优化接口
curl -X POST http://localhost:4101/api/qc/check/batch/optimized \
  -H "Content-Type: application/json" \
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
