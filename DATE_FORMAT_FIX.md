# 日期格式修复说明

## 问题描述

在批量质控查询时，发现时间范围判定有误：
- 查询2020年数据时，只返回1条记录
- 实际应该有6,095条记录

## 问题原因

### B15字段格式

B15字段（出院日期）的实际格式为：
```
2020/1/2 9:00
2020/1/8 15:00
2023/1/1 9:49
```

注意：**月份和日期是单数字**（如 `1/2` 而不是 `01/02`）

### 原始SQL格式

原始代码使用的日期解析格式：
```sql
STR_TO_DATE(B15, '%Y/%m/%d %H:%i')
```

这个格式要求：
- `%m`: 两位数的月份（01-12）
- `%d`: 两位数的日期（01-31）

但实际数据是单数字，导致解析失败。

## 修复方案

### 修改日期解析格式

将格式改为：
```sql
STR_TO_DATE(B15, '%Y/%c/%e %H:%i')
```

新格式说明：
- `%c`: 月份（1-12），允许单数字
- `%e`: 日期（1-31），允许单数字

### 修改的文件

**文件**: `src/main/java/com/medical/qc/mapper/MedicalRecordMapper.java`

#### 修改1: findRecords方法

```java
// 修改前
"<if test='year != null'> AND YEAR(STR_TO_DATE(m.B15, '%Y/%m/%d %H:%i')) = #{year} </if>" +
"<if test='quarter != null'> AND QUARTER(STR_TO_DATE(m.B15, '%Y/%m/%d %H:%i')) = #{quarter} </if>" +
"<if test='month != null'> AND MONTH(STR_TO_DATE(m.B15, '%Y/%m/%d %H:%i')) = #{month} </if>" +

// 修改后
"<if test='year != null'> AND YEAR(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = #{year} </if>" +
"<if test='quarter != null'> AND QUARTER(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = #{quarter} </if>" +
"<if test='month != null'> AND MONTH(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = #{month} </if>" +
```

#### 修改2: countRecords方法

```java
// 修改前
"<if test='year != null'> AND YEAR(STR_TO_DATE(B15, '%Y/%m/%d %H:%i')) = #{year} </if>" +
"<if test='quarter != null'> AND QUARTER(STR_TO_DATE(B15, '%Y/%m/%d %H:%i')) = #{quarter} </if>" +
"<if test='month != null'> AND MONTH(STR_TO_DATE(B15, '%Y/%m/%d %H:%i')) = #{month} </if>" +

// 修改后
"<if test='year != null'> AND YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = #{year} </if>" +
"<if test='quarter != null'> AND QUARTER(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = #{quarter} </if>" +
"<if test='month != null'> AND MONTH(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = #{month} </if>" +
```

## 验证结果

### 修复前

```sql
-- 使用 '%Y/%m/%d %H:%i' 格式
SELECT COUNT(*) FROM d_mr 
WHERE YEAR(STR_TO_DATE(B15, '%Y/%m/%d %H:%i')) = 2020;
-- 结果: 1 条（错误）
```

### 修复后

```sql
-- 使用 '%Y/%c/%e %H:%i' 格式
SELECT COUNT(*) FROM d_mr 
WHERE YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = 2020;
-- 结果: 6,095 条（正确）
```

### 详细统计

| 年份 | 月份 | 修复前 | 修复后 | 说明 |
|------|------|--------|--------|------|
| 2020 | 1月 | 1 | 6,095 | ✅ 修复成功 |
| 2023 | 1月 | 1 | 94 | ✅ 修复成功 |
| 2023 | 8月 | 0 | 1 | ✅ 修复成功 |
| 2023 | 11月 | 0 | 1 | ✅ 修复成功 |

## 应用修复

### 1. 重新编译

```bash
mvn clean package
```

### 2. 重启服务

```bash
# 停止当前服务
# 启动新服务
java -jar target/qc-0.0.1-SNAPSHOT.jar
```

或使用：
```bash
start.bat
```

### 3. 验证修复

运行测试脚本：
```bash
python test_date_format_fix.py
```

预期输出：
```
2020年总数: 6,095 条
2020年按月分布:
   1月: 6,095 条

2023年总数: 96 条
2023年按月分布:
   1月: 94 条
   8月: 1 条
  11月: 1 条
```

## 测试脚本

### test_date_format_fix.py

验证日期格式修复是否生效：
```bash
python test_date_format_fix.py
```

### check_b15_format.py

检查B15字段的实际格式：
```bash
python check_b15_format.py
```

### check_time_range.py

全面检查时间范围查询：
```bash
python check_time_range.py
```

## MySQL日期格式说明

### 常用格式符

| 格式符 | 说明 | 示例 |
|--------|------|------|
| `%Y` | 四位年份 | 2020 |
| `%m` | 两位月份（01-12） | 01, 12 |
| `%c` | 月份（1-12） | 1, 12 |
| `%d` | 两位日期（01-31） | 01, 31 |
| `%e` | 日期（1-31） | 1, 31 |
| `%H` | 小时（00-23） | 09, 15 |
| `%i` | 分钟（00-59） | 00, 49 |

### 选择建议

- 如果数据格式固定为两位数：使用 `%m` 和 `%d`
- 如果数据格式可能是单数字：使用 `%c` 和 `%e`
- **本项目应使用**: `%Y/%c/%e %H:%i`

## 影响范围

### 受影响的功能

1. ✅ 批量质控（按年/季度/月）
2. ✅ 病案数量统计
3. ✅ 时间范围查询
4. ✅ 质控结果汇总

### 不受影响的功能

1. ✅ 单个病案质控（通过A48/A49查询）
2. ✅ 规则管理
3. ✅ 字典查询

## 后续建议

### 1. 数据标准化

考虑将B15字段标准化为统一格式：
```sql
-- 方案1: 转换为DATE类型
ALTER TABLE d_mr MODIFY COLUMN B15 DATETIME;

-- 方案2: 标准化字符串格式
UPDATE d_mr SET B15 = DATE_FORMAT(STR_TO_DATE(B15, '%Y/%c/%e %H:%i'), '%Y/%m/%d %H:%i');
```

### 2. 添加索引

为B15字段添加索引以提高查询性能：
```sql
CREATE INDEX idx_b15 ON d_mr(B15);
```

### 3. 数据验证

定期检查B15字段的数据质量：
```sql
-- 检查无效日期
SELECT COUNT(*) FROM d_mr 
WHERE B15 IS NOT NULL 
AND STR_TO_DATE(B15, '%Y/%c/%e %H:%i') IS NULL;
```

## 总结

- ✅ 问题已识别：日期格式不匹配
- ✅ 修复已完成：更改为 `%Y/%c/%e %H:%i`
- ✅ 验证已通过：数据统计正确
- ⚠️ 需要重启：重新编译并重启服务
- 📋 建议优化：数据标准化和添加索引

---

**修复时间**: 2026-01-16  
**修复文件**: MedicalRecordMapper.java  
**验证状态**: ✅ 已验证  
**应用状态**: ⚠️ 需要重启服务
