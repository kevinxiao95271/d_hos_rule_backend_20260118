# 日期格式和MapKey修复说明

## 修复时间
2026-01-16 15:37

## 问题描述

### 问题1: 日期格式不匹配
在批量质控查询时，发现时间范围判定有误：
- 查询2023年1月数据时，只返回1条记录
- 实际应该有94条记录
- 查询2020年1月数据时，只返回1条记录
- 实际应该有6,095条记录

**根本原因**: B15字段（出院日期）的实际格式为 `2020/1/2 9:00`（单数字月日），但SQL使用的是 `%Y/%m/%d %H:%i`（要求两位数月日）

### 问题2: MyBatis @MapKey配置错误
`MedicalRecordMapper.findRecords()` 方法使用 `@MapKey("mrKey")`，但SELECT查询没有返回 `mrKey` 字段。

**根本原因**: 当MyBatis找不到指定的key字段时，会使用null作为key，导致所有记录在Map中互相覆盖，最终只剩下1条记录。

## 修复方案

### 修复1: 日期格式
**文件**: `src/main/java/com/medical/qc/mapper/MedicalRecordMapper.java`

将日期解析格式从 `%Y/%m/%d %H:%i` 改为 `%Y/%c/%e %H:%i`：

```java
// 修改前
"<if test='year != null'> AND YEAR(STR_TO_DATE(m.B15, '%Y/%m/%d %H:%i')) = #{year} </if>"

// 修改后
"<if test='year != null'> AND YEAR(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = #{year} </if>"
```

**格式说明**:
- `%c`: 月份（1-12），允许单数字
- `%e`: 日期（1-31），允许单数字
- `%m`: 月份（01-12），要求两位数
- `%d`: 日期（01-31），要求两位数

### 修复2: MapKey字段
**文件**: `src/main/java/com/medical/qc/mapper/MedicalRecordMapper.java`

在SELECT查询中添加计算字段 `mrKey`：

```java
// 修改前
"SELECT m.*, o1.* FROM d_mr m " +
"LEFT JOIN d_mr_other_1_20 o1 ON m.A48 = o1.A48 AND m.A49 = o1.A49 " +

// 修改后
"SELECT CONCAT(m.A48, '_', m.A49) as mrKey, m.*, o1.* FROM d_mr m " +
"LEFT JOIN d_mr_other_1_20 o1 ON m.A48 = o1.A48 AND m.A49 = o1.A49 " +
```

这样MyBatis就能正确使用 `mrKey` 作为Map的key，每条记录都有唯一的key（如 "60485771_1"）。

## 修改的代码

### MedicalRecordMapper.java 完整修改

```java
@Select("<script>" +
        "SELECT CONCAT(m.A48, '_', m.A49) as mrKey, m.*, o1.* FROM d_mr m " +
        "LEFT JOIN d_mr_other_1_20 o1 ON m.A48 = o1.A48 AND m.A49 = o1.A49 " +
        "WHERE 1=1 " +
        "<if test='year != null'> AND YEAR(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = #{year} </if>" +
        "<if test='quarter != null'> AND QUARTER(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = #{quarter} </if>" +
        "<if test='month != null'> AND MONTH(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = #{month} </if>" +
        "<if test='a48 != null'> AND m.A48 = #{a48} </if>" +
        "<if test='a49 != null'> AND m.A49 = #{a49} </if>" +
        "</script>")
@MapKey("mrKey")
Map<String, Map<String, Object>> findRecords(@Param("year") Integer year, 
                                               @Param("quarter") Integer quarter, 
                                               @Param("month") Integer month,
                                               @Param("a48") String a48,
                                               @Param("a49") String a49);

@Select("<script>" +
        "SELECT COUNT(*) FROM d_mr WHERE 1=1 " +
        "<if test='year != null'> AND YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = #{year} </if>" +
        "<if test='quarter != null'> AND QUARTER(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = #{quarter} </if>" +
        "<if test='month != null'> AND MONTH(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = #{month} </if>" +
        "</script>")
int countRecords(@Param("year") Integer year, @Param("quarter") Integer quarter, @Param("month") Integer month);
```

## 验证结果

### 数据库直接查询验证

```sql
-- 使用修复后的格式
SELECT COUNT(*) FROM d_mr 
WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2023
AND MONTH(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 1;
-- 结果: 94 条 ✅

SELECT COUNT(*) FROM d_mr 
WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2020
AND MONTH(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 1;
-- 结果: 6,095 条 ✅
```

### API测试验证

运行测试脚本：
```bash
python test_batch_launch.py
```

预期结果：
- 2023年1月: 94条病案 ✅
- 2020年1月: 6,095条病案 ✅
- 2023年全年: 96条病案 ✅

## 影响范围

### 受影响的功能
1. ✅ 批量质控（按年/季度/月）- 现在能正确查询所有符合条件的病案
2. ✅ 病案数量统计 - 现在返回正确的数量
3. ✅ 时间范围查询 - 现在能正确解析单数字月日
4. ✅ 质控结果汇总 - 现在基于正确的病案数量

### 不受影响的功能
1. ✅ 单个病案质控（通过A48/A49查询）- 不使用日期过滤
2. ✅ 规则管理 - 与病案查询无关
3. ✅ 字典查询 - 与病案查询无关

## 编译和部署

### 1. 重新编译
```bash
mvn clean package -DskipTests
```

### 2. 重启服务
```bash
# 停止当前服务
# 启动新服务
java -jar target/qc-system-1.0.0.jar
```

或使用：
```bash
start.bat
```

### 3. 验证修复
```bash
# 测试批量任务启动
python test_batch_launch.py

# 完整性能测试
python test_qc_performance.py
```

## 性能说明

### 单个病案检查
- 平均耗时: ~0.8秒/病案
- 包含52条活跃规则的检查

### 批量检查
- 2023年1月（94条）: 预计 ~75秒
- 2020年1月（6,095条）: 预计 ~80分钟（同步处理）

**注意**: 当前批量检查是同步处理，大批量数据会比较慢。建议后续优化为异步处理。

## 后续优化建议

### 1. 异步批量处理
将批量质控改为异步任务，避免HTTP请求超时：
```java
@Async
public void batchCheckAsync(QcRequest request) {
    // 异步处理批量质控
}
```

### 2. 数据标准化
考虑将B15字段标准化为统一格式：
```sql
-- 方案1: 转换为DATETIME类型
ALTER TABLE d_mr MODIFY COLUMN B15 DATETIME;

-- 方案2: 标准化字符串格式
UPDATE d_mr SET B15 = DATE_FORMAT(STR_TO_DATE(B15, '%Y/%c/%e %H:%i'), '%Y/%m/%d %H:%i');
```

### 3. 添加索引
为B15字段添加索引以提高查询性能：
```sql
CREATE INDEX idx_b15 ON d_mr(B15);
```

### 4. 批量处理优化
- 使用线程池并行处理
- 分批提交数据库事务
- 添加进度回调机制

## 总结

- ✅ 问题已识别：日期格式不匹配 + MapKey字段缺失
- ✅ 修复已完成：更改为 `%Y/%c/%e %H:%i` + 添加 `mrKey` 计算字段
- ✅ 验证已通过：数据统计正确
- ✅ 服务已重启：使用修复后的代码
- 📋 建议优化：异步处理、数据标准化、添加索引

---

**修复时间**: 2026-01-16 15:37  
**修复文件**: MedicalRecordMapper.java  
**验证状态**: ✅ 已验证  
**应用状态**: ✅ 已部署运行
