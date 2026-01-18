# 质控规则空值处理逻辑

## 核心业务规则

**如果规则没有明确说明该字段不能为空，则该病案的某字段没有值就不参与该质控规则的计算。**

## 详细说明

### 1. 空值判断标准

字段被认为是"空值"的情况：
- 字段值为 `NULL`
- 字段值为空字符串 `""`
- 字段值为纯空格字符串（trim后为空）
- 字段值为字符串 `"null"`（不区分大小写）

### 2. 规则处理逻辑

#### 情况A：规则明确要求字段不能为空

**触发条件**：规则描述（description字段）中包含以下关键词之一：
- "必填"
- "不能为空"
- "必须填写"
- "不得为空"
- "必须有值"

**处理方式**：
- 如果字段为空 → **报告质控缺陷**
- 如果字段有值 → 继续进行值域/范围检查

**示例规则**：
```
规则描述：性别字段必填，且必须在RC001字典范围内
字段值为空 → 报告缺陷："性别不能为空"
字段值为"1" → 检查是否在RC001字典中
```

#### 情况B：规则没有明确要求字段不能为空

**触发条件**：规则描述中不包含上述关键词

**处理方式**：
- 如果字段为空 → **跳过该规则检查**（不报告缺陷）
- 如果字段有值 → 继续进行值域/范围检查

**示例规则**：
```
规则描述：婚姻状况必须在RC002字典范围内
字段值为空 → 跳过检查（不报告缺陷）
字段值为"10" → 检查是否在RC002字典中
```

### 3. 适用的规则类型

此逻辑适用于所有规则类型：

#### value_check（值域检查）
```java
// 字段为空且规则未要求必填 → 跳过
// 字段为空且规则要求必填 → 报告缺陷
// 字段有值 → 检查是否在字典范围内
```

#### range_check（范围检查）
```java
// 字段为空且规则未要求必填 → 跳过
// 字段为空且规则要求必填 → 报告缺陷
// 字段有值 → 检查是否在指定范围内
```

#### cross_check_null（交叉检查）
```java
// 根据条件字段判断目标字段是否必填
// 如果必填但为空 → 报告缺陷
// 如果非必填且为空 → 跳过
```

## 实现代码

### RuleEngineService.java

```java
/**
 * 判断规则是否明确要求字段不能为空
 */
private boolean isRequiredField(String description) {
    if (description == null) return false;
    
    return description.contains("必填") 
        || description.contains("不能为空")
        || description.contains("必须填写")
        || description.contains("不得为空")
        || description.contains("必须有值");
}

private RuleViolation checkValueRule(Map<String, Object> record, KiroQcRule rule) {
    Object value = getFieldValue(record, rule.getFieldCode());
    boolean requiresNonNull = isRequiredField(rule.getDescription());
    
    if (isNullOrEmpty(value)) {
        if (requiresNonNull) {
            // 报告违规
            return createViolation(rule, "空", "不能为空");
        } else {
            // 跳过检查
            return null;
        }
    }
    
    // 字段有值，继续检查...
}
```

## 规则配置示例

### 必填字段规则
```sql
INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type,
    description, deduct_score, status
) VALUES (
    'RULE_A01_REQUIRED', 'A01', '性别', 'value_check',
    '性别必填，且必须在RC001字典范围内',  -- 包含"必填"关键词
    2, 'active'
);
```

### 非必填字段规则
```sql
INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type,
    description, deduct_score, status
) VALUES (
    'RULE_A02_VALUE', 'A02', '婚姻状况', 'value_check',
    '婚姻状况必须在RC002字典范围内',  -- 不包含"必填"关键词
    1, 'active'
);
```

## 测试场景

### 场景1：必填字段为空
```
规则：性别必填，且必须在RC001字典范围内
病案数据：A01 = NULL
结果：报告缺陷 "性别不能为空"，扣2分
```

### 场景2：非必填字段为空
```
规则：婚姻状况必须在RC002字典范围内
病案数据：A02 = NULL
结果：跳过检查，不报告缺陷，不扣分
```

### 场景3：非必填字段有值但不在字典范围
```
规则：婚姻状况必须在RC002字典范围内
病案数据：A02 = "99"（不在RC002字典中）
结果：报告缺陷 "婚姻状况不在字典范围内"，扣1分
```

### 场景4：必填字段有值且在字典范围
```
规则：性别必填，且必须在RC001字典范围内
病案数据：A01 = "1"（在RC001字典中）
结果：通过检查，不报告缺陷
```

## 业务价值

1. **减少误报**：非必填字段为空时不报告缺陷，避免不必要的扣分
2. **灵活性**：通过规则描述控制字段是否必填，无需修改代码
3. **符合实际**：医疗记录中很多字段是可选的，只有在填写时才需要验证格式
4. **提高效率**：跳过空值字段的检查，减少不必要的计算

## 注意事项

1. 规则描述必须准确：如果字段确实必填，描述中必须包含"必填"等关键词
2. 字典验证：即使字段非必填，一旦有值就必须符合字典规范
3. 范围验证：即使字段非必填，一旦有值就必须在合理范围内
4. 交叉验证：某些字段是否必填可能依赖于其他字段的值

## 更新日期

2026-01-16
