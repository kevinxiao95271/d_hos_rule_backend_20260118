# 医疗质控系统性能优化部署指南

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
curl -X POST http://localhost:4101/api/qc/check/batch/optimized \
  -H "Content-Type: application/json" \
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
