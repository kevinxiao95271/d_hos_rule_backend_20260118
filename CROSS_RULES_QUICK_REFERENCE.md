# Cross规则快速参考

## ⚠️ 重要：大量Cross规则

**系统中实际有接近600条Cross规则！**
- 专门Cross规则表: 12条
- 普通规则表中的Cross规则: 583条
- **单个病案可能触发大量Cross规则违规**

## 🚀 核心变更

### 新增API字段
```json
{
  "data": {
    // 原有字段（保持不变）
    "allDefects": [...],           // 所有违规
    "defectsByField": {...},       // 按字段分组的普通违规
    
    // 新增字段
    "crossDefects": [...]          // Cross规则专用字段 ⭐
  }
}
```

### CrossDefect数据结构
```typescript
interface CrossDefectDTO {
  ruleCode: string;              // RULE_CROSS_* 格式
  ruleDescription: string;       // 规则描述
  crossType: string;            // 规则类型
  involvedFields: string[];     // 涉及字段
  fieldValues: object;          // 字段值映射
  logicDescription: string;     // 逻辑描述
  deductScore: number;          // 扣分
  severity: string;             // 严重程度: low/medium/high
}
```

## 🎯 Cross规则类型

| 类型 | 说明 | 图标 |
|------|------|------|
| `field_pair` | 字段配对检查 | 🔗 |
| `age_gender` | 年龄性别逻辑 | 👤 |
| `transfusion_logic` | 输血逻辑检查 | 🩸 |
| `conditional_required` | 条件必填 | ⚠️ |
| `age_diagnosis` | 年龄诊断匹配 | 📅 |
| `logic_check` | 其他逻辑检查 | 🔍 |

## 💡 前端实现要点

### 1. 向后兼容 ✅
```javascript
// 现有代码无需修改，继续正常工作
function displayDefects(data) {
  // 使用 allDefects 或 defectsByField
  renderDefects(data.allDefects);
}
```

### 2. 增强展示 🆕
```javascript
// 检查并展示Cross规则
if (data.crossDefects && data.crossDefects.length > 0) {
  renderCrossDefects(data.crossDefects);
}
```

### 3. 样式建议
```css
.cross-defect.high { border-color: #f44336; }    /* 高严重程度 */
.cross-defect.medium { border-color: #ff9800; }  /* 中严重程度 */
.cross-defect.low { border-color: #4caf50; }     /* 低严重程度 */
```

## 🔧 实用工具函数

```javascript
// 检查是否为Cross规则
const isCrossRule = (ruleCode) => ruleCode?.startsWith('RULE_CROSS_');

// 获取类型图标
const getTypeIcon = (crossType) => {
  const icons = {
    'field_pair': '🔗', 'age_gender': '👤', 'transfusion_logic': '🩸',
    'conditional_required': '⚠️', 'age_diagnosis': '📅', 'logic_check': '🔍'
  };
  return icons[crossType] || '📋';
};

// 获取严重程度颜色
const getSeverityColor = (severity) => {
  const colors = { 'high': '#f44336', 'medium': '#ff9800', 'low': '#4caf50' };
  return colors[severity] || colors.medium;
};
```

## 📋 测试病案

| 病案号 | Cross规则 | 类型 |
|--------|-----------|------|
| `445583-1` | RULE_CROSS_D26_TRANSFUSION_FEE1 | 输血逻辑 |
| `19065857-1` | RULE_CROSS_D26_TRANSFUSION_FEE1 | 输血逻辑 |
| `19072516-1` | RULE_CROSS_D26_TRANSFUSION_FEE1 | 输血逻辑 |

## ⚡ 快速集成步骤

1. **立即可用**: 无需修改现有代码
2. **检查数量**: 判断 `crossDefects.length` 决定展示策略
3. **性能优化**: 大量违规时使用分页或虚拟滚动
4. **分组展示**: 按 `crossType` 分组折叠显示
5. **搜索过滤**: 提供搜索和过滤功能

## 📊 大量违规处理

```javascript
// 根据数量选择展示策略
function handleCrossDefects(crossDefects) {
  if (crossDefects.length <= 10) {
    displayAll(crossDefects);           // 直接展示
  } else if (crossDefects.length <= 50) {
    displayGrouped(crossDefects);       // 分组展示
  } else {
    displayPaginated(crossDefects);     // 分页展示
  }
}

// 分页展示
const pageSize = 20;
const totalPages = Math.ceil(crossDefects.length / pageSize);
```

## 🎨 UI建议

- **分区展示**: Cross规则单独一个区域
- **视觉突出**: 使用边框颜色区分严重程度
- **图标标识**: 根据类型显示对应图标
- **字段关联**: 清晰展示涉及的多个字段
- **逻辑说明**: 显示具体的逻辑描述

## 📞 技术支持

如有疑问，请参考：
- `CROSS_RULES_FRONTEND_GUIDE.md` - 详细开发指引
- `CROSS_RULES_API_EXAMPLES.md` - 完整代码示例