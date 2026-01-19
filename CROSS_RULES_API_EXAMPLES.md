# Cross规则API示例

## API调用示例

### 单个病案质控API

**请求:**
```http
POST /api/qc/check/single?a48=445583&a49=1
Content-Type: application/json
```

**响应:**
```json
{
  "code": 200,
  "message": "质控完成",
  "data": {
    "mrKey": "445583_1",
    "a48": "445583",
    "a49": "1",
    "b15": "2020/1/14 13:00",
    "defectCount": 9,
    "totalDeduct": 24.0,
    "finalScore": 76.0,
    
    "crossDefects": [
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
    ],
    
    "allDefects": [
      {
        "fieldCode": "D26",
        "fieldName": "输血记录",
        "ruleCode": "RULE_CROSS_D26_TRANSFUSION_FEE1",
        "ruleDescription": "存在输血记录，未发生血液费用",
        "actualValue": "有输血记录但无血费",
        "expectedValue": "输血记录与血液费用应保持一致",
        "deductScore": 0.0
      },
      {
        "fieldCode": "C21x01C",
        "fieldName": "主要手术操作切口愈合等级",
        "ruleCode": "C21x01C_value_check",
        "ruleDescription": "主要手术操作切口愈合等级编码取值不符合国家标准值域定义",
        "actualValue": "1",
        "expectedValue": "字典operation_dict_v3中的有效值",
        "deductScore": 2.0
      }
      // ... 其他普通违规
    ],
    
    "defectsByField": {
      "C21x01C": [
        {
          "fieldCode": "C21x01C",
          "fieldName": "主要手术操作切口愈合等级",
          "ruleCode": "C21x01C_value_check",
          "ruleDescription": "主要手术操作切口愈合等级编码取值不符合国家标准值域定义",
          "actualValue": "1",
          "expectedValue": "字典operation_dict_v3中的有效值",
          "deductScore": 2.0
        }
      ],
      "C14x01C": [
        {
          "fieldCode": "C14x01C",
          "fieldName": "主要手术操作编码 字符",
          "ruleCode": "RULE_C14x01C_RC013",
          "ruleDescription": "主要手术操作编码 字符 必须在RC027字典范围内",
          "actualValue": "81.51",
          "expectedValue": "字典RC027中的有效值: 1, 2, 3, 4",
          "deductScore": 1.0
        }
      ]
      // 注意：Cross规则不会出现在defectsByField中
    }
  }
}
```

## 前端处理示例

### React组件示例

```jsx
import React from 'react';

// Cross规则违规组件
const CrossDefectCard = ({ crossDefect }) => {
  const {
    ruleCode,
    ruleDescription,
    crossType,
    involvedFields,
    fieldValues,
    logicDescription,
    deductScore,
    severity
  } = crossDefect;

  const getSeverityColor = (severity) => {
    const colors = {
      high: '#f44336',
      medium: '#ff9800',
      low: '#4caf50'
    };
    return colors[severity] || colors.medium;
  };

  const getTypeIcon = (crossType) => {
    const icons = {
      field_pair: '🔗',
      age_gender: '👤',
      transfusion_logic: '🩸',
      conditional_required: '⚠️',
      age_diagnosis: '📅',
      logic_check: '🔍'
    };
    return icons[crossType] || '📋';
  };

  return (
    <div 
      className="cross-defect-card"
      style={{ 
        border: `2px solid ${getSeverityColor(severity)}`,
        borderRadius: '8px',
        padding: '15px',
        margin: '10px 0',
        backgroundColor: '#f9f9f9'
      }}
    >
      <div className="cross-defect-header" style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
        <span style={{ marginRight: '8px', fontSize: '18px' }}>
          {getTypeIcon(crossType)}
        </span>
        <span style={{ fontWeight: 'bold', marginRight: '10px' }}>
          {ruleCode}
        </span>
        <span 
          style={{
            background: getSeverityColor(severity),
            color: 'white',
            padding: '2px 8px',
            borderRadius: '12px',
            fontSize: '12px',
            textTransform: 'uppercase'
          }}
        >
          {severity}
        </span>
      </div>

      <div className="cross-defect-content">
        <p style={{ fontWeight: 'bold', color: '#333', marginBottom: '5px' }}>
          {logicDescription}
        </p>
        <p style={{ color: '#666', marginBottom: '10px' }}>
          {ruleDescription}
        </p>

        <div style={{ marginBottom: '10px' }}>
          <strong>涉及字段：</strong>
          {involvedFields.map((field, index) => (
            <span 
              key={index}
              style={{
                background: '#2196f3',
                color: 'white',
                padding: '2px 6px',
                borderRadius: '4px',
                margin: '2px',
                fontSize: '12px'
              }}
            >
              {field}
            </span>
          ))}
        </div>

        {fieldValues && (
          <div style={{ marginBottom: '10px', padding: '8px', background: 'white', borderRadius: '4px' }}>
            <strong>字段值：</strong>
            {Object.entries(fieldValues).map(([field, value]) => (
              <div key={field} style={{ margin: '4px 0' }}>
                <span style={{ fontWeight: 'bold', color: '#666' }}>{field}:</span>
                <span style={{ marginLeft: '5px' }}>{value}</span>
              </div>
            ))}
          </div>
        )}

        <div style={{ textAlign: 'right', fontWeight: 'bold', color: '#f44336' }}>
          扣分: {deductScore}
        </div>
      </div>
    </div>
  );
};

// 质控结果展示组件
const QcResultDisplay = ({ qcResult }) => {
  const { crossDefects, defectsByField, allDefects } = qcResult;

  return (
    <div className="qc-result-display">
      {/* Cross规则违规专区 */}
      {crossDefects && crossDefects.length > 0 && (
        <div className="cross-defects-section">
          <h3 style={{ color: '#f44336', borderBottom: '2px solid #f44336', paddingBottom: '5px' }}>
            🔗 跨字段规则违规 ({crossDefects.length}个)
          </h3>
          {crossDefects.map((crossDefect, index) => (
            <CrossDefectCard key={index} crossDefect={crossDefect} />
          ))}
        </div>
      )}

      {/* 普通违规按字段分组展示 */}
      {Object.keys(defectsByField).length > 0 && (
        <div className="normal-defects-section">
          <h3 style={{ color: '#666', borderBottom: '2px solid #666', paddingBottom: '5px' }}>
            📋 字段违规 ({Object.keys(defectsByField).length}个字段)
          </h3>
          {Object.entries(defectsByField).map(([fieldCode, defects]) => (
            <div key={fieldCode} className="field-defects">
              <h4>{fieldCode} ({defects.length}个违规)</h4>
              {defects.map((defect, index) => (
                <div key={index} className="normal-defect-card" style={{ 
                  border: '1px solid #ddd', 
                  padding: '10px', 
                  margin: '5px 0',
                  borderRadius: '4px'
                }}>
                  <div><strong>规则:</strong> {defect.ruleCode}</div>
                  <div><strong>描述:</strong> {defect.ruleDescription}</div>
                  <div><strong>实际值:</strong> {defect.actualValue}</div>
                  <div><strong>期望值:</strong> {defect.expectedValue}</div>
                  <div style={{ textAlign: 'right', color: '#f44336' }}>
                    <strong>扣分: {defect.deductScore}</strong>
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default QcResultDisplay;
```

### Vue组件示例

```vue
<template>
  <div class="qc-result-display">
    <!-- Cross规则违规专区 -->
    <div v-if="crossDefects && crossDefects.length > 0" class="cross-defects-section">
      <h3 class="section-title cross-title">
        🔗 跨字段规则违规 ({{ crossDefects.length }}个)
      </h3>
      <div 
        v-for="(crossDefect, index) in crossDefects" 
        :key="index"
        class="cross-defect-card"
        :class="getSeverityClass(crossDefect.severity)"
      >
        <div class="cross-defect-header">
          <span class="type-icon">{{ getTypeIcon(crossDefect.crossType) }}</span>
          <span class="rule-code">{{ crossDefect.ruleCode }}</span>
          <span class="severity-badge" :style="{ background: getSeverityColor(crossDefect.severity) }">
            {{ crossDefect.severity }}
          </span>
        </div>

        <div class="cross-defect-content">
          <p class="logic-description">{{ crossDefect.logicDescription }}</p>
          <p class="rule-description">{{ crossDefect.ruleDescription }}</p>

          <div class="involved-fields">
            <strong>涉及字段：</strong>
            <span 
              v-for="field in crossDefect.involvedFields" 
              :key="field"
              class="field-tag"
            >
              {{ field }}
            </span>
          </div>

          <div v-if="crossDefect.fieldValues" class="field-values">
            <strong>字段值：</strong>
            <div 
              v-for="(value, field) in crossDefect.fieldValues" 
              :key="field"
              class="field-value"
            >
              <span class="field-name">{{ field }}:</span>
              <span class="field-val">{{ value }}</span>
            </div>
          </div>

          <div class="deduct-score">扣分: {{ crossDefect.deductScore }}</div>
        </div>
      </div>
    </div>

    <!-- 普通违规按字段分组展示 -->
    <div v-if="Object.keys(defectsByField).length > 0" class="normal-defects-section">
      <h3 class="section-title normal-title">
        📋 字段违规 ({{ Object.keys(defectsByField).length }}个字段)
      </h3>
      <div 
        v-for="(defects, fieldCode) in defectsByField" 
        :key="fieldCode"
        class="field-defects"
      >
        <h4>{{ fieldCode }} ({{ defects.length }}个违规)</h4>
        <div 
          v-for="(defect, index) in defects" 
          :key="index"
          class="normal-defect-card"
        >
          <div><strong>规则:</strong> {{ defect.ruleCode }}</div>
          <div><strong>描述:</strong> {{ defect.ruleDescription }}</div>
          <div><strong>实际值:</strong> {{ defect.actualValue }}</div>
          <div><strong>期望值:</strong> {{ defect.expectedValue }}</div>
          <div class="deduct-score">扣分: {{ defect.deductScore }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QcResultDisplay',
  props: {
    qcResult: {
      type: Object,
      required: true
    }
  },
  computed: {
    crossDefects() {
      return this.qcResult.crossDefects || [];
    },
    defectsByField() {
      return this.qcResult.defectsByField || {};
    }
  },
  methods: {
    getSeverityClass(severity) {
      return `severity-${severity}`;
    },
    getSeverityColor(severity) {
      const colors = {
        high: '#f44336',
        medium: '#ff9800',
        low: '#4caf50'
      };
      return colors[severity] || colors.medium;
    },
    getTypeIcon(crossType) {
      const icons = {
        field_pair: '🔗',
        age_gender: '👤',
        transfusion_logic: '🩸',
        conditional_required: '⚠️',
        age_diagnosis: '📅',
        logic_check: '🔍'
      };
      return icons[crossType] || '📋';
    }
  }
};
</script>

<style scoped>
.qc-result-display {
  padding: 20px;
}

.section-title {
  padding-bottom: 5px;
  margin-bottom: 15px;
}

.cross-title {
  color: #f44336;
  border-bottom: 2px solid #f44336;
}

.normal-title {
  color: #666;
  border-bottom: 2px solid #666;
}

.cross-defect-card {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  margin: 10px 0;
  padding: 15px;
  background: #f9f9f9;
}

.cross-defect-card.severity-high {
  border-color: #f44336;
  background: #ffebee;
}

.cross-defect-card.severity-medium {
  border-color: #ff9800;
  background: #fff3e0;
}

.cross-defect-card.severity-low {
  border-color: #4caf50;
  background: #e8f5e8;
}

.cross-defect-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.type-icon {
  margin-right: 8px;
  font-size: 18px;
}

.rule-code {
  font-weight: bold;
  color: #333;
  margin-right: 10px;
}

.severity-badge {
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  text-transform: uppercase;
}

.logic-description {
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.rule-description {
  color: #666;
  margin-bottom: 10px;
}

.field-tag {
  background: #2196f3;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  margin: 2px;
  font-size: 12px;
}

.field-values {
  margin: 10px 0;
  padding: 8px;
  background: white;
  border-radius: 4px;
}

.field-value {
  margin: 4px 0;
}

.field-name {
  font-weight: bold;
  color: #666;
}

.field-val {
  color: #333;
  margin-left: 5px;
}

.deduct-score {
  text-align: right;
  font-weight: bold;
  color: #f44336;
}

.normal-defect-card {
  border: 1px solid #ddd;
  padding: 10px;
  margin: 5px 0;
  border-radius: 4px;
  background: white;
}
</style>
```

## JavaScript工具函数

```javascript
// Cross规则处理工具类
class CrossRuleUtils {
  
  // 检查是否为Cross规则
  static isCrossRule(ruleCode) {
    return ruleCode && ruleCode.startsWith('RULE_CROSS_');
  }
  
  // 从allDefects中分离Cross规则和普通规则
  static separateDefects(allDefects) {
    const crossDefects = [];
    const normalDefects = [];
    
    allDefects.forEach(defect => {
      if (this.isCrossRule(defect.ruleCode)) {
        crossDefects.push(defect);
      } else {
        normalDefects.push(defect);
      }
    });
    
    return { crossDefects, normalDefects };
  }
  
  // 获取Cross规则类型的中文描述
  static getCrossTypeDescription(crossType) {
    const descriptions = {
      'field_pair': '字段配对检查',
      'age_gender': '年龄性别逻辑',
      'transfusion_logic': '输血逻辑检查',
      'conditional_required': '条件必填检查',
      'age_diagnosis': '年龄诊断匹配',
      'logic_check': '逻辑一致性检查'
    };
    return descriptions[crossType] || '跨字段检查';
  }
  
  // 获取严重程度的中文描述
  static getSeverityDescription(severity) {
    const descriptions = {
      'high': '高',
      'medium': '中',
      'low': '低'
    };
    return descriptions[severity] || '中';
  }
  
  // 统计Cross规则违规
  static getCrossDefectStats(crossDefects) {
    const stats = {
      total: crossDefects.length,
      byType: {},
      bySeverity: {},
      totalDeduct: 0
    };
    
    crossDefects.forEach(defect => {
      // 按类型统计
      const type = defect.crossType;
      stats.byType[type] = (stats.byType[type] || 0) + 1;
      
      // 按严重程度统计
      const severity = defect.severity;
      stats.bySeverity[severity] = (stats.bySeverity[severity] || 0) + 1;
      
      // 总扣分
      stats.totalDeduct += defect.deductScore || 0;
    });
    
    return stats;
  }
}

// 使用示例
const qcResult = {
  crossDefects: [...],
  allDefects: [...],
  defectsByField: {...}
};

// 获取Cross规则统计
const crossStats = CrossRuleUtils.getCrossDefectStats(qcResult.crossDefects);
console.log('Cross规则统计:', crossStats);

// 分离违规类型
const { crossDefects, normalDefects } = CrossRuleUtils.separateDefects(qcResult.allDefects);
console.log('Cross规则违规:', crossDefects.length);
console.log('普通违规:', normalDefects.length);
```

这些示例提供了完整的前端集成方案，包括React和Vue组件，以及实用的工具函数。前端开发者可以根据实际需求选择合适的实现方式。