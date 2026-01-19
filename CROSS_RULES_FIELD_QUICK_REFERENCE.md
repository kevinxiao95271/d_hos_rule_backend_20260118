# Cross规则字段快速参考卡片

## 🔍 核心区别一览

| 特征 | 普通规则违规 | Cross规则违规 |
|------|-------------|---------------|
| **问题本质** | 单个字段值错误 | 多字段逻辑关系错误 |
| **数据位置** | `allDefects` 数组 | `crossDefects` 数组 |
| **字段标识** | `fieldCode` + `fieldName` | `involvedFields[]` |
| **值信息** | `actualValue` + `expectedValue` | `fieldValues{}` |
| **规则标识** | 普通规则代码 | `RULE_CROSS_` 开头 |

---

## 📋 JSON字段对比

### 普通规则违规
```json
{
  "fieldCode": "A18x01",           // ✅ 单个字段代码
  "fieldName": "新生儿出生体重",    // ✅ 单个字段名称
  "actualValue": "0",              // ✅ 实际值
  "expectedValue": "100.0-9999.0", // ✅ 期望值
  "ruleCode": "A18x01_range_check",
  "ruleDescription": "体重范围检查",
  "deductScore": 4.0
}
```

### Cross规则违规
```json
{
  "ruleCode": "RULE_CROSS_D26_TRANSFUSION_FEE1",
  "ruleDescription": "存在输血记录，未发生血液费用",
  "crossType": "transfusion_logic",        // ✅ Cross规则类型
  "involvedFields": ["输血记录", "血液费用"], // ✅ 多个字段
  "fieldValues": {                         // ✅ 字段值对象
    "输血记录": "存在",
    "血液费用": "无"
  },
  "logicDescription": "逻辑不一致",         // ✅ 逻辑描述
  "severity": "medium",                    // ✅ 严重程度
  "deductScore": 0.0
}
```

---

## 🎯 Cross规则类型速查

| 类型 | 说明 | 涉及字段示例 |
|------|------|-------------|
| `transfusion_logic` | 输血逻辑 | 输血记录 + 血液费用 |
| `field_pair` | 字段配对 | 诊断编码 + 诊断名称 |
| `age_diagnosis` | 年龄诊断 | 年龄 + 诊断 |
| `conditional_required` | 条件必填 | 手术 + 麻醉方式 |
| `age_gender` | 年龄性别 | 年龄 + 性别 + 诊断 |
| `date_consistency` | 日期一致性 | 入院日期 + 出院日期 |

---

## 💻 前端处理要点

### 数据提取
```javascript
// 普通规则违规
const normalDefects = allDefects.filter(d => 
  !d.ruleCode.startsWith('RULE_CROSS_')
);

// Cross规则违规
const crossDefects = data.crossDefects; // 直接使用
```

### 显示差异
```javascript
// 普通规则：显示字段值问题
`${defect.fieldName}: ${defect.actualValue} → ${defect.expectedValue}`

// Cross规则：显示逻辑关系问题
`${defect.logicDescription}`
Object.entries(defect.fieldValues).map(([field, value]) => 
  `${field}: ${value}`
).join(', ')
```

### UI区分
- **普通规则**: 红色边框，突出单个字段
- **Cross规则**: 蓝色边框，展示多字段关系

---

## 📊 统计计算

### 单病案统计
```javascript
const crossCount = data.crossDefectCount;           // Cross违规数
const normalCount = data.defectCount - crossCount;  // 普通违规数
const crossRatio = (crossCount / data.defectCount) * 100; // Cross占比
```

### 批量统计
```javascript
const batchCrossCount = data.crossDefectCount;      // 批量Cross违规总数
const batchNormalCount = data.totalDefectCount - batchCrossCount;
const avgCrossDefect = data.avgCrossDefect;         // 平均Cross违规数
```

---

## 🎨 样式建议

### 普通规则违规
```css
.normal-defect {
  border-left: 4px solid #ff6b35;
  background: #fff5f5;
}
.field-problem {
  color: #d32f2f;
  font-weight: bold;
}
```

### Cross规则违规
```css
.cross-defect {
  border-left: 4px solid #1976d2;
  background: linear-gradient(135deg, #f3e5f5 0%, #e8f5e8 100%);
}
.logic-problem {
  color: #1976d2;
  font-style: italic;
}
.severity-high { background: #f44336; }
.severity-medium { background: #ff9800; }
.severity-low { background: #4caf50; }
```

---

## 🔧 实用工具函数

```javascript
// 判断是否为Cross规则
const isCrossRule = (ruleCode) => ruleCode.startsWith('RULE_CROSS_');

// 获取Cross规则涉及的所有字段
const getCrossRuleFields = (crossDefects) => {
  return [...new Set(crossDefects.flatMap(d => d.involvedFields))];
};

// 计算字段影响统计
const getFieldImpactStats = (qcResult) => {
  const normalFields = new Set(
    qcResult.allDefects
      .filter(d => !isCrossRule(d.ruleCode))
      .map(d => d.fieldCode)
  );
  
  const crossFields = new Set(getCrossRuleFields(qcResult.crossDefects));
  
  return {
    normalFieldCount: normalFields.size,
    crossFieldCount: crossFields.size,
    totalUniqueFields: new Set([...normalFields, ...crossFields]).size
  };
};
```

---

## ⚡ 关键记忆点

1. **Cross规则 ≠ 单字段问题**，而是多字段逻辑关系问题
2. **`involvedFields`** 是数组，**`fieldValues`** 是对象
3. **`logicDescription`** 比 `ruleDescription` 更具体
4. **`severity`** 字段只有Cross规则才有
5. **`crossDefects`** 数组独立于 `allDefects`
6. 批量质控只返回统计数据，不返回具体违规详情

---

**💡 提示**: Cross规则的核心是"关系检查"而非"值检查"，前端展示时要突出这种逻辑关系！