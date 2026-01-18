# 医疗质控系统综合性能优化方案

## 📊 性能现状分析

### 当前性能指标
- **单病案处理时间**: 27-29秒
- **2023年病案数量**: ~96个
- **串行处理预估时间**: 45分钟
- **目标处理时间**: 5分钟以内
- **性能差距**: 9倍

### 关键性能瓶颈

#### 1. 规则引擎效率问题
- **1699条活跃规则**: 每个病案遍历所有规则
- **重复字段查找**: 每次字段访问尝试3次(原始/大写/小写)
- **低效的规则匹配**: 没有索引,线性遍历

#### 2. 数据访问效率低
- **频繁数据库查询**: 缺少数据预加载和缓存
- **重复查询**: 相同数据被多次查询
- **单条查询**: 没有批量查询优化

#### 3. 并行处理未启用
- **8线程池闲置**: 代码中使用串行处理方法
- **资源未充分利用**: CPU利用率低

#### 4. 规则逻辑可优化
- **循环查找**: 诊断代码查找循环40次
- **字符串操作**: 大量trim()、toString()等操作
- **正则表达式**: 每次都重新编译

## 🎯 优化策略

### 策略一: 规则引擎优化(预期提升5-8倍)

#### 1.1 规则预处理和索引
```java
// 创建规则索引,避免线性遍历
public class OptimizedRuleEngine {
    // 按字段代码分组规则
    private Map<String, List<KiroQcRule>> rulesByField;

    // 按规则类型分组
    private Map<String, List<KiroQcRule>> rulesByType;

    // 预编译正则表达式
    private Map<Long, Pattern> compiledPatterns;

    public void initialize(List<KiroQcRule> rules) {
        // 构建索引
        rulesByField = rules.stream()
            .collect(Collectors.groupingBy(KiroQcRule::getFieldCode));

        rulesByType = rules.stream()
            .collect(Collectors.groupingBy(KiroQcRule::getRuleType));

        // 预编译正则
        compiledPatterns = precompilePatterns(rules);
    }
}
```

#### 1.2 字段访问优化
```java
// 优化字段查找,避免重复尝试
private Map<String, Object> normalizeFieldKeys(Map<String, Object> record) {
    Map<String, Object> normalized = new HashMap<>();
    for (Map.Entry<String, Object> entry : record.entrySet()) {
        String key = entry.getKey().toUpperCase();
        normalized.put(key, entry.getValue());
    }
    return normalized;
}
```

#### 1.3 规则优先级和短路
```java
// 按重要性排序规则,支持快速失败
List<KiroQcRule> sortedRules = rules.stream()
    .sorted(Comparator.comparing(KiroQcRule::getDeductScore).reversed())
    .collect(Collectors.toList());
```

### 策略二: 数据访问优化(预期提升3-5倍)

#### 2.1 数据预加载
```java
public class CaseDataPreloader {
    public Map<String, Map<String, Object>> preloadAllCaseData(
            Integer year, Integer quarter, Integer month) {

        // 一次性加载所有病案数据(已实现)
        Map<String, Map<String, Object>> records =
            recordMapper.findRecords(year, quarter, month, null, null);

        // 规范化字段名
        Map<String, Map<String, Object>> normalized = new HashMap<>();
        for (Map.Entry<String, Map<String, Object>> entry : records.entrySet()) {
            normalized.put(entry.getKey(), normalizeFieldKeys(entry.getValue()));
        }

        return normalized;
    }
}
```

#### 2.2 批量写入优化
```java
// 使用MyBatis批量插入
@Mapper
public interface QcResultMapper {
    // 批量插入病案结果
    @Insert("<script>" +
            "INSERT INTO kiro_qc_case_result " +
            "(mr_key, a48, a49, b15, check_year, defect_count, total_deduct, final_score) " +
            "VALUES " +
            "<foreach collection='list' item='item' separator=','>" +
            "(#{item.mrKey}, #{item.a48}, #{item.a49}, #{item.b15}, " +
            "#{item.checkYear}, #{item.defectCount}, #{item.totalDeduct}, #{item.finalScore})" +
            "</foreach>" +
            "</script>")
    void batchInsertCaseResults(List<KiroQcCaseResult> results);

    // 批量插入缺陷明细
    @Insert("<script>" +
            "INSERT INTO kiro_qc_defect_detail " +
            "(mr_key, a48, a49, rule_id, rule_code, field_code, actual_value, deduct_score) " +
            "VALUES " +
            "<foreach collection='list' item='item' separator=','>" +
            "(#{item.mrKey}, #{item.a48}, #{item.a49}, #{item.ruleId}, " +
            "#{item.ruleCode}, #{item.fieldCode}, #{item.actualValue}, #{item.deductScore})" +
            "</foreach>" +
            "</script>")
    void batchInsertDefectDetails(List<KiroQcDefectDetail> details);
}
```

### 策略三: 并行处理优化(预期提升6-8倍)

#### 3.1 启用并行处理
```java
// 修改BatchQcServiceOptimized.java
public void executeBatchCheckAsyncOptimized(QcRequest request, String batchKey) {
    // ...前置代码...

    // 使用并行处理而非串行
    processBatchRecordsParallel(records, rules, request, summary, batchKey);

    // ...后续代码...
}
```

#### 3.2 优化线程池配置
```java
// 根据CPU核心数优化线程池
private final ExecutorService parallelExecutor =
    Executors.newFixedThreadPool(
        Runtime.getRuntime().availableProcessors()
    );
```

#### 3.3 优化批次大小
```java
// 根据数据量动态调整批次大小
private int calculateOptimalBatchSize(int totalRecords, int threadCount) {
    int minBatchSize = 5;
    int maxBatchSize = 20;
    int optimalSize = (totalRecords + threadCount - 1) / threadCount;
    return Math.max(minBatchSize, Math.min(maxBatchSize, optimalSize));
}
```

### 策略四: 算法优化(预期提升2-3倍)

#### 4.1 诊断代码查找优化
```java
// 预处理诊断代码,避免每次循环40次
private Set<String> extractDiagnosisCodes(Map<String, Object> record) {
    Set<String> codes = new HashSet<>();
    for (int i = 1; i <= 40; i++) {
        String key = String.format("C06X%02dC", i);
        Object value = record.get(key);
        if (value != null && !value.toString().trim().isEmpty()) {
            codes.add(value.toString());
        }
    }
    return codes;
}

// 一次性检查
private boolean hasDiagnosisCode(Set<String> diagCodes, List<String> requiredCodes) {
    for (String code : requiredCodes) {
        for (String diagCode : diagCodes) {
            if (diagCode.contains(code)) {
                return true;
            }
        }
    }
    return false;
}
```

#### 4.2 正则表达式优化
```java
// 预编译正则表达式
private static final Pattern RANGE_PATTERN = Pattern.compile("(\\d+).*-(\\d+)");
private static final Pattern DIAG_CODE_PATTERN = Pattern.compile("Z\\d+\\.\\d+");

// 缓存编译结果
private Map<String, Pattern> patternCache = new ConcurrentHashMap<>();
```

## 📋 实施计划

### 阶段一: 快速优化(预期1-2小时,提升3-5倍)

#### 任务1: 启用并行处理
**文件**: `BatchQcServiceOptimized.java`
**修改**:
1. 将`processBatchRecordsSerial`改为`processBatchRecordsParallel`
2. 优化线程池大小
3. 调整批次大小

**预期效果**: 8倍性能提升

#### 任务2: 字段访问优化
**文件**: `RuleEngineService.java`
**修改**:
1. 添加字段键规范化方法
2. 缓存字段查找结果
3. 避免重复的大小写转换

**预期效果**: 1.5-2倍性能提升

#### 任务3: 批量数据库写入
**文件**: `QcResultMapper.java`, `BatchQcServiceOptimized.java`
**修改**:
1. 实现批量插入方法
2. 增大批次大小到100-200
3. 使用事务批处理

**预期效果**: 2-3倍性能提升

### 阶段二: 深度优化(预期3-4小时,额外提升2-3倍)

#### 任务4: 规则引擎重构
**文件**: 新建`OptimizedRuleEngineService.java`
**功能**:
1. 实现规则索引
2. 预编译正则表达式
3. 规则分组和优先级

**预期效果**: 2-3倍性能提升

#### 任务5: 数据预处理
**文件**: `BatchQcServiceOptimized.java`
**功能**:
1. 一次性提取诊断代码
2. 缓存常用字段
3. 预处理空值检查

**预期效果**: 1.5-2倍性能提升

### 阶段三: 系统优化(预期1-2天,额外提升1.5-2倍)

#### 任务6: 数据库优化
1. 添加更多索引
2. 优化SQL查询
3. 启用查询缓存

#### 任务7: JVM优化
1. 调整堆内存大小
2. 优化GC策略
3. 启用性能监控

## 📊 预期优化效果

### 综合性能提升
- **阶段一**: 3-5倍提升 → 单病案 6-10秒, 96病案 10-16分钟
- **阶段二**: 额外2-3倍 → 单病案 2-5秒, 96病案 3-8分钟
- **阶段三**: 额外1.5-2倍 → 单病案 1-3秒, 96病案 2-5分钟

### 最终目标达成
- ✅ **96病案5分钟内完成**: 可以达成
- ✅ **单病案3秒内完成**: 可以达成
- ✅ **保持规则完整性**: 1699条规则全部保留

## 🔧 立即可实施的优化

### 最小改动,最大收益

#### 优化1: 启用并行处理(预计提升8倍)
```java
// BatchQcServiceOptimized.java 第83行
// 修改前:
processBatchRecordsSerial(records, rules, request, summary, batchKey);

// 修改后:
processBatchRecordsParallel(records, rules, request, summary, batchKey);
```

#### 优化2: 增加线程数(预计提升1.5倍)
```java
// BatchQcServiceOptimized.java 第37行
// 修改前:
private final ExecutorService parallelExecutor = Executors.newFixedThreadPool(8);

// 修改后:
private final ExecutorService parallelExecutor =
    Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());
```

#### 优化3: 增大数据库批次(预计提升2倍)
```java
// BatchQcServiceOptimized.java 第41行
// 修改前:
private static final int DB_BATCH_SIZE = 50;

// 修改后:
private static final int DB_BATCH_SIZE = 200;
```

### 立即执行这3个优化
这3个优化只需要修改3行代码,预期可以获得 **8 × 1.5 × 2 = 24倍性能提升**!

如果优化成功:
- **单病案时间**: 29秒 ÷ 24 = 1.2秒
- **96病案时间**: 29秒 × 96 ÷ 24 = 116秒 = **不到2分钟**!

## ⚠️ 风险评估

### 低风险
- 启用并行处理: 代码已存在,只是未启用
- 增加批次大小: 不影响逻辑正确性
- 字段访问优化: 逻辑等价转换

### 中风险
- 规则引擎重构: 需要充分测试
- 数据预处理: 可能增加内存使用

### 建议
1. 先实施低风险优化,验证效果
2. 在测试环境验证中风险优化
3. 保留回滚方案
4. 增量部署,逐步优化

## 📞 下一步行动

### 建议优先级
1. **立即**: 修改3行代码,启用并行+增大批次
2. **今天**: 实施字段访问优化
3. **本周**: 实施规则引擎优化
4. **下周**: 实施数据预处理优化

### 需要确认
1. 是否立即实施"3行代码优化"?
2. 服务器CPU核心数是多少?
3. 是否有测试环境可以验证?
4. 是否需要保持规则100%完整?

---

**文档创建时间**: 2026-01-17
**预期优化收益**: 20-30倍性能提升
**实施难度**: 低到中等
**风险等级**: 低
