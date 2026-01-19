# Cross规则与普通规则字段结构对比指南

## 📋 概述

Cross规则和普通规则在API返回的JSON结构中有显著不同，因为它们检查的逻辑本质不同：
- **普通规则**: 检查单个字段的值是否符合要求
- **Cross规则**: 检查多个字段之间的逻辑关系是否一致

---

## 🔍 JSON字段结构对比

### 普通规则违规结构 (`allDefects` 数组中)

```json
{
  "fieldCode": "A18x01",                    // 具体的违规字段代码
  "fieldName": "新生儿出生体重(克)",          // 具体的违规字段名称
  "ruleCode": "A18x01_range_check",         // 规则代码
  "ruleDescription": "新生儿出生体重范围检查", // 规则描述
  "actualValue": "0",                       // 实际值（问题所在）
  "expectedValue": "100.0-9999.0",          // 期望值范围
  "deductScore": 4.0                        // 扣分
}
```

### Cross规则违规结构 (`crossDefects` 数组中)

```json
{
  "ruleCode": "RULE_CROSS_D26_TRANSFUSION_FEE1",     // Cross规则代码
  "ruleDescription": "存在输血记录，未发生血液费用",    // Cross规则描述
  "crossType": "transfusion_logic",                  // Cross规则类型
  "involvedFields": ["输血记录", "血液费用"],          // 涉及的多个字段
  "fieldValues": {                                   // 各字段的实际值
    "输血记录": "存在",
    "血液费用": "无"
  },
  "logicDescription": "输血记录与血液费用逻辑不一致",   // 逻辑关系描述
  "deductScore": 0.0,                               // 扣分
  "severity": "medium"                              // 严重程度
}
```

---

## 📊 关键差异对比表

| 特征 | 普通规则违规 | Cross规则违规 |
|------|-------------|---------------|
| **问题性质** | 单个字段值不符合要求 | 多个字段间逻辑关系不一致 |
| **字段标识** | `fieldCode` + `fieldName` | `involvedFields` 数组 |
| **值信息** | `actualValue` + `expectedValue` | `fieldValues` 对象 |
| **逻辑描述** | 通过 `ruleDescription` | 专门的 `logicDescription` |
| **类型标识** | 通过 `ruleCode` 推断 | 明确的 `crossType` |
| **严重程度** | 无专门字段 | 专门的 `severity` 字段 |
| **存储位置** | `allDefects` 和 `defectsByField` | `crossDefects` 专门数组 |

---

## 🎯 不同Cross规则类型的字段结构示例

### 1. 输血逻辑检查 (`transfusion_logic`)

```json
{
  "ruleCode": "RULE_CROSS_D26_TRANSFUSION_FEE1",
  "ruleDescription": "存在输血记录，未发生血液费用",
  "crossType": "transfusion_logic",
  "involvedFields": ["输血记录", "血液费用"],
  "fieldValues": {
    "输血记录": "存在",
    "血液费用": "无"
  },
  "logicDescription": "输血记录与血液费用逻辑不一致",
  "deductScore": 0.0,
  "severity": "medium"
}
```

### 2. 字段配对检查 (`field_pair`)

```json
{
  "ruleCode": "RULE_CROSS_FIELD_PAIR_C06C07",
  "ruleDescription": "诊断编码与诊断名称不匹配",
  "crossType": "field_pair",
  "involvedFields": ["C06x01C", "C07x01C"],
  "fieldValues": {
    "C06x01C": "I10.x00",
    "C07x01C": ""
  },
  "logicDescription": "诊断编码已填写但诊断名称为空",
  "deductScore": 2.0,
  "severity": "high"
}
```

### 3. 年龄诊断匹配 (`age_diagnosis`)

```json
{
  "ruleCode": "RULE_CROSS_AGE_DIAGNOSIS_001",
  "ruleDescription": "年龄与诊断不匹配",
  "crossType": "age_diagnosis",
  "involvedFields": ["A02", "C06x01C"],
  "fieldValues": {
    "A02": "5",
    "C06x01C": "I25.100"
  },
  "logicDescription": "5岁患者不应有冠心病诊断",
  "deductScore": 3.0,
  "severity": "high"
}
```

### 4. 条件必填检查 (`conditional_required`)

```json
{
  "ruleCode": "RULE_CROSS_CONDITIONAL_REQUIRED_001",
  "ruleDescription": "手术时麻醉方式必填",
  "crossType": "conditional_required",
  "involvedFields": ["C14x01C", "C23x01C"],
  "fieldValues": {
    "C14x01C": "64.00x002",
    "C23x01C": ""
  },
  "logicDescription": "存在手术记录时麻醉方式不能为空",
  "deductScore": 1.5,
  "severity": "medium"
}
```

### 5. 年龄性别逻辑 (`age_gender`)

```json
{
  "ruleCode": "RULE_CROSS_AGE_GENDER_001",
  "ruleDescription": "年龄性别逻辑不符",
  "crossType": "age_gender",
  "involvedFields": ["A02", "A03", "C06x01C"],
  "fieldValues": {
    "A02": "30",
    "A03": "1",
    "C06x01C": "N80.100"
  },
  "logicDescription": "男性患者不应有妇科疾病诊断",
  "deductScore": 4.0,
  "severity": "high"
}
```

### 6. 日期一致性检查 (`date_consistency`)

```json
{
  "ruleCode": "RULE_CROSS_DATE_CONSISTENCY_001",
  "ruleDescription": "入院出院日期逻辑错误",
  "crossType": "date_consistency",
  "involvedFields": ["B11", "B15"],
  "fieldValues": {
    "B11": "2023-05-15",
    "B15": "2023-05-10"
  },
  "logicDescription": "出院日期不能早于入院日期",
  "deductScore": 2.5,
  "severity": "high"
}
```

---

## 💻 前端处理差异化代码示例

### JavaScript处理示例

```javascript
// 处理违规数据的通用函数
function processDefects(qcResult) {
  const { allDefects, crossDefects } = qcResult;
  
  // 处理普通规则违规
  const normalDefects = allDefects.filter(defect => 
    !defect.ruleCode.startsWith('RULE_CROSS_')
  );
  
  console.log('=== 普通规则违规 ===');
  normalDefects.forEach(defect => {
    console.log(`字段: ${defect.fieldName} (${defect.fieldCode})`);
    console.log(`问题: ${defect.actualValue} 不符合要求 ${defect.expectedValue}`);
    console.log(`扣分: ${defect.deductScore}`);
    console.log('---');
  });
  
  // 处理Cross规则违规
  console.log('=== Cross规则违规 ===');
  crossDefects.forEach(defect => {
    console.log(`规则类型: ${defect.crossType}`);
    console.log(`涉及字段: ${defect.involvedFields.join(', ')}`);
    console.log(`逻辑问题: ${defect.logicDescription}`);
    console.log(`字段值:`);
    Object.entries(defect.fieldValues).forEach(([field, value]) => {
      console.log(`  - ${field}: ${value}`);
    });
    console.log(`严重程度: ${defect.severity}`);
    console.log(`扣分: ${defect.deductScore}`);
    console.log('---');
  });
}
```

### React组件处理示例

```tsx
// 普通规则违规组件
const NormalDefectItem: React.FC<{defect: NormalDefect}> = ({ defect }) => (
  <div className="normal-defect">
    <div className="defect-header">
      <span className="field-name">{defect.fieldName}</span>
      <span className="field-code">({defect.fieldCode})</span>
    </div>
    <div className="defect-content">
      <div className="value-comparison">
        <span className="actual">实际: {defect.actualValue}</span>
        <span className="expected">期望: {defect.expectedValue}</span>
      </div>
      <div className="rule-info">
        <span className="rule-desc">{defect.ruleDescription}</span>
        <span className="deduct-score">-{defect.deductScore}分</span>
      </div>
    </div>
  </div>
);

// Cross规则违规组件
const CrossDefectItem: React.FC<{defect: CrossDefect}> = ({ defect }) => (
  <div className="cross-defect">
    <div className="defect-header">
      <span className="cross-type">{defect.crossType}</span>
      <span className={`severity severity-${defect.severity}`}>
        {defect.severity}
      </span>
    </div>
    <div className="defect-content">
      <div className="logic-description">{defect.logicDescription}</div>
      <div className="involved-fields">
        <strong>涉及字段:</strong>
        <div className="field-values">
          {Object.entries(defect.fieldValues).map(([field, value]) => (
            <div key={field} className="field-value-pair">
              <span className="field">{field}:</span>
              <span className="value">{value}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="rule-info">
        <span className="rule-desc">{defect.ruleDescription}</span>
        <span className="deduct-score">-{defect.deductScore}分</span>
      </div>
    </div>
  </div>
);
```

---

## 🎨 UI展示差异化建议

### 普通规则违规展示
```css
.normal-defect {
  border-left: 4px solid #ff6b35;
  background: #fff5f5;
  padding: 12px;
  margin: 8px 0;
}

.normal-defect .field-name {
  font-weight: bold;
  color: #d32f2f;
}

.normal-defect .value-comparison {
  display: flex;
  gap: 16px;
  margin: 8px 0;
}

.normal-defect .actual {
  color: #d32f2f;
  background: #ffebee;
  padding: 2px 6px;
  border-radius: 3px;
}

.normal-defect .expected {
  color: #4caf50;
  background: #e8f5e8;
  padding: 2px 6px;
  border-radius: 3px;
}
```

### Cross规则违规展示
```css
.cross-defect {
  border-left: 4px solid #1976d2;
  background: linear-gradient(135deg, #f3e5f5 0%, #e8f5e8 100%);
  padding: 12px;
  margin: 8px 0;
  border-radius: 6px;
}

.cross-defect .cross-type {
  background: #1976d2;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.cross-defect .severity-high {
  background: #f44336;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.cross-defect .severity-medium {
  background: #ff9800;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.cross-defect .severity-low {
  background: #4caf50;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.cross-defect .field-values {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
  margin: 8px 0;
}

.cross-defect .field-value-pair {
  background: rgba(255,255,255,0.7);
  padding: 6px 10px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.cross-defect .field {
  font-weight: bold;
  color: #1976d2;
}

.cross-defect .value {
  color: #333;
  margin-left: 8px;
}
```

---

## 📱 移动端适配差异

### 普通规则违规 - 移动端简化
```javascript
function renderNormalDefectMobile(defect) {
  return `
    <div class="mobile-normal-defect">
      <div class="mobile-field">${defect.fieldName}</div>
      <div class="mobile-problem">
        ${defect.actualValue} → ${defect.expectedValue}
      </div>
      <div class="mobile-score">-${defect.deductScore}分</div>
    </div>
  `;
}
```

### Cross规则违规 - 移动端简化
```javascript
function renderCrossDefectMobile(defect) {
  const fieldSummary = Object.entries(defect.fieldValues)
    .map(([field, value]) => `${field}:${value}`)
    .join(', ');
    
  return `
    <div class="mobile-cross-defect">
      <div class="mobile-cross-type">${defect.crossType}</div>
      <div class="mobile-logic">${defect.logicDescription}</div>
      <div class="mobile-fields">${fieldSummary}</div>
      <div class="mobile-score">-${defect.deductScore}分</div>
    </div>
  `;
}
```

---

## 🔧 数据处理工具函数

### 字段提取工具
```javascript
// 从普通规则违规中提取字段信息
function extractNormalDefectFields(defects) {
  return defects.map(defect => ({
    fieldCode: defect.fieldCode,
    fieldName: defect.fieldName,
    hasIssue: true,
    issueType: 'value',
    actualValue: defect.actualValue,
    expectedValue: defect.expectedValue
  }));
}

// 从Cross规则违规中提取字段信息
function extractCrossDefectFields(defects) {
  const fieldMap = new Map();
  
  defects.forEach(defect => {
    defect.involvedFields.forEach(fieldName => {
      const fieldValue = defect.fieldValues[fieldName];
      const key = fieldName;
      
      if (!fieldMap.has(key)) {
        fieldMap.set(key, {
          fieldName: fieldName,
          hasIssue: true,
          issueType: 'logic',
          crossRules: [],
          values: []
        });
      }
      
      const fieldInfo = fieldMap.get(key);
      fieldInfo.crossRules.push({
        ruleCode: defect.ruleCode,
        crossType: defect.crossType,
        logicDescription: defect.logicDescription
      });
      fieldInfo.values.push(fieldValue);
    });
  });
  
  return Array.from(fieldMap.values());
}
```

### 统计分析工具
```javascript
// 分析违规字段分布
function analyzeDefectDistribution(qcResult) {
  const normalFields = extractNormalDefectFields(
    qcResult.allDefects.filter(d => !d.ruleCode.startsWith('RULE_CROSS_'))
  );
  
  const crossFields = extractCrossDefectFields(qcResult.crossDefects);
  
  return {
    normalFieldCount: normalFields.length,
    crossFieldCount: crossFields.length,
    totalAffectedFields: new Set([
      ...normalFields.map(f => f.fieldCode),
      ...crossFields.map(f => f.fieldName)
    ]).size,
    fieldTypes: {
      valueIssues: normalFields.length,
      logicIssues: crossFields.length
    }
  };
}
```

---

## 📋 总结

### 关键区别
1. **普通规则**: 关注单个字段的值是否正确
2. **Cross规则**: 关注多个字段之间的逻辑关系是否合理

### 前端处理要点
1. **数据结构**: 两种违规有完全不同的JSON结构
2. **展示方式**: Cross规则需要展示多字段关系，普通规则展示单字段问题
3. **用户理解**: Cross规则需要更多的逻辑说明，普通规则更直观
4. **交互设计**: Cross规则可能需要更复杂的展开/收起交互

### 开发建议
1. 为两种违规类型创建不同的组件
2. 使用不同的视觉样式区分两种违规
3. 在移动端提供简化的展示方式
4. 提供工具函数处理复杂的字段关系

这样的设计能让用户清楚地理解不同类型违规的本质差异，提供更好的用户体验。