# Cross规则前端开发指引

## ⚠️ 重要更新：大量Cross规则

**最新发现：系统中实际有接近600条Cross规则！**

- **专门Cross规则表**: 12条
- **普通规则表中的Cross规则**: 583条 (需要迁移)
- **总计**: 595条Cross规则

这意味着在某些病案中可能会有**大量的Cross规则违规**，前端需要特别考虑性能和用户体验。

## 概述

本文档说明医疗质控系统中Cross规则（跨字段规则）相关的API字段变动和前端开发指引。Cross规则用于检查多个字段之间的逻辑关系，如字段配对、年龄性别匹配、输血逻辑等。

**注意：由于Cross规则数量庞大，单个病案可能触发多个Cross规则违规，前端需要考虑大量数据的展示和性能优化。**

## API变更说明

### 1. 新增字段

质控结果API (`POST /api/qc/check/single`) 响应中新增了专门用于Cross规则展示的字段：

```json
{
  "code": 200,
  "message": "质控完成",
  "data": {
    "mrKey": "445583_1",
    "a48": "445583",
    "a49": "1",
    "defectCount": 9,
    "totalDeduct": 24.0,
    "finalScore": 76.0,
    
    // 原有字段（保持不变）
    "allDefects": [...],           // 所有违规（包括Cross规则）
    "defectsByField": {...},       // 按字段分组的普通违规
    
    // 新增字段
    "crossDefects": [...]          // Cross规则违规专用字段
  }
}
```

### 2. crossDefects字段结构

```typescript
interface CrossDefectDTO {
  ruleCode: string;              // 规则代码，格式：RULE_CROSS_*
  ruleDescription: string;       // 规则描述
  crossType: string;            // Cross规则类型
  involvedFields: string[];     // 涉及的字段列表
  fieldValues: Record<string, string>; // 字段值映射
  logicDescription: string;     // 逻辑描述
  deductScore: number;          // 扣分
  severity: string;             // 严重程度：low/medium/high
}
```

### 3. Cross规则类型说明

| crossType | 说明 | 示例 |
|-----------|------|------|
| `field_pair` | 字段配对检查 | 诊断编码与名称必须同时有值或同时为空 |
| `age_gender` | 年龄性别逻辑 | 男性患者不应有妇科诊断 |
| `transfusion_logic` | 输血逻辑检查 | 有输血记录但无血液费用 |
| `conditional_required` | 条件必填 | 手术时麻醉方式必填 |
| `age_diagnosis` | 年龄诊断匹配 | 儿童不应有成人疾病诊断 |
| `logic_check` | 其他逻辑检查 | 通用跨字段逻辑验证 |

## 向后兼容性

### ✅ 完全兼容
- `allDefects`: 仍包含所有违规（包括Cross规则）
- `defectsByField`: 仍按字段分组普通违规
- 原有API结构完全保持不变
- 现有前端代码无需修改即可正常工作

### 🆕 增强功能
- `crossDefects`: 提供Cross规则的专门展示支持
- 更丰富的Cross规则信息
- 更好的用户体验

## 前端开发建议

### ⚠️ 大量Cross规则的性能考虑

由于系统中有接近600条Cross规则，单个病案可能触发大量Cross规则违规，前端需要特别注意：

#### 性能优化
```javascript
// 分页展示Cross规则违规
function displayCrossDefectsPaginated(crossDefects, pageSize = 20) {
  const totalPages = Math.ceil(crossDefects.length / pageSize);
  let currentPage = 1;
  
  function renderPage(page) {
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const pageDefects = crossDefects.slice(start, end);
    
    renderCrossDefects(pageDefects);
    renderPagination(page, totalPages);
  }
  
  renderPage(currentPage);
}

// 虚拟滚动处理大量违规
function setupVirtualScrolling(crossDefects) {
  const container = document.getElementById('cross-defects-container');
  const itemHeight = 120; // 每个违规项的高度
  const visibleCount = Math.ceil(container.clientHeight / itemHeight);
  
  let scrollTop = 0;
  
  container.addEventListener('scroll', () => {
    scrollTop = container.scrollTop;
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(startIndex + visibleCount, crossDefects.length);
    
    renderVisibleItems(crossDefects.slice(startIndex, endIndex), startIndex);
  });
}
```

#### 分组展示
```javascript
// 按类型分组展示Cross规则
function groupCrossDefectsByType(crossDefects) {
  const grouped = crossDefects.reduce((groups, defect) => {
    const type = defect.crossType;
    if (!groups[type]) {
      groups[type] = [];
    }
    groups[type].push(defect);
    return groups;
  }, {});
  
  return grouped;
}

// 可折叠的分组展示
function renderGroupedCrossDefects(groupedDefects) {
  Object.entries(groupedDefects).forEach(([type, defects]) => {
    const groupElement = createCollapsibleGroup(type, defects.length);
    
    // 默认只展示前5个，其余折叠
    const visibleDefects = defects.slice(0, 5);
    const hiddenDefects = defects.slice(5);
    
    visibleDefects.forEach(defect => {
      groupElement.appendChild(renderCrossDefect(defect));
    });
    
    if (hiddenDefects.length > 0) {
      const expandButton = createExpandButton(hiddenDefects.length);
      expandButton.onclick = () => showHiddenDefects(hiddenDefects, groupElement);
      groupElement.appendChild(expandButton);
    }
  });
}
```

### 1. 基础展示方案

```javascript
// 处理质控结果
function handleQcResult(response) {
  const data = response.data;
  
  // 普通违规展示（原有逻辑保持不变）
  displayNormalDefects(data.defectsByField);
  
  // Cross规则违规展示（新增）
  if (data.crossDefects && data.crossDefects.length > 0) {
    displayCrossDefects(data.crossDefects);
  }
}

// 展示普通违规（按字段分组）
function displayNormalDefects(defectsByField) {
  Object.keys(defectsByField).forEach(fieldCode => {
    const defects = defectsByField[fieldCode];
    // 原有展示逻辑
    renderFieldDefects(fieldCode, defects);
  });
}

// 展示Cross规则违规
function displayCrossDefects(crossDefects) {
  crossDefects.forEach(crossDefect => {
    renderCrossDefect(crossDefect);
  });
}
```

### 2. Cross规则专门展示

```javascript
function renderCrossDefect(crossDefect) {
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
  
  // 根据严重程度设置样式
  const severityClass = getSeverityClass(severity);
  
  // 根据类型设置图标
  const typeIcon = getCrossTypeIcon(crossType);
  
  return `
    <div class="cross-defect ${severityClass}">
      <div class="cross-defect-header">
        <span class="type-icon">${typeIcon}</span>
        <span class="rule-code">${ruleCode}</span>
        <span class="severity-badge">${severity}</span>
      </div>
      
      <div class="cross-defect-content">
        <p class="logic-description">${logicDescription}</p>
        <p class="rule-description">${ruleDescription}</p>
        
        <div class="involved-fields">
          <h4>涉及字段：</h4>
          ${involvedFields.map(field => `<span class="field-tag">${field}</span>`).join('')}
        </div>
        
        ${fieldValues ? renderFieldValues(fieldValues) : ''}
        
        <div class="deduct-score">扣分: ${deductScore}</div>
      </div>
    </div>
  `;
}

// 渲染字段值
function renderFieldValues(fieldValues) {
  return `
    <div class="field-values">
      <h4>字段值：</h4>
      ${Object.entries(fieldValues).map(([field, value]) => 
        `<div class="field-value">
          <span class="field-name">${field}:</span>
          <span class="field-val">${value}</span>
        </div>`
      ).join('')}
    </div>
  `;
}
```

### 3. 样式建议

```css
/* Cross规则违规容器 */
.cross-defect {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  margin: 10px 0;
  padding: 15px;
  background: #f9f9f9;
}

/* 严重程度样式 */
.cross-defect.high {
  border-color: #f44336;
  background: #ffebee;
}

.cross-defect.medium {
  border-color: #ff9800;
  background: #fff3e0;
}

.cross-defect.low {
  border-color: #4caf50;
  background: #e8f5e8;
}

/* 头部样式 */
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
  background: #666;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  text-transform: uppercase;
}

/* 字段标签 */
.field-tag {
  background: #2196f3;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  margin: 2px;
  font-size: 12px;
}

/* 字段值展示 */
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
```

### 4. 工具函数

```javascript
// 获取严重程度样式类
function getSeverityClass(severity) {
  const classMap = {
    'high': 'high',
    'medium': 'medium', 
    'low': 'low'
  };
  return classMap[severity] || 'medium';
}

// 获取Cross规则类型图标
function getCrossTypeIcon(crossType) {
  const iconMap = {
    'field_pair': '🔗',
    'age_gender': '👤',
    'transfusion_logic': '🩸',
    'conditional_required': '⚠️',
    'age_diagnosis': '📅',
    'logic_check': '🔍'
  };
  return iconMap[crossType] || '📋';
}

// 检查是否为Cross规则
function isCrossRule(ruleCode) {
  return ruleCode && ruleCode.startsWith('RULE_CROSS_');
}
```

## 实际示例

### API响应示例

```json
{
  "code": 200,
  "message": "质控完成",
  "data": {
    "mrKey": "445583_1",
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
      // 包含所有违规，包括上面的Cross规则
      {
        "fieldCode": "D26",
        "ruleCode": "RULE_CROSS_D26_TRANSFUSION_FEE1",
        "ruleDescription": "存在输血记录，未发生血液费用",
        "deductScore": 0.0
      }
      // ... 其他普通违规
    ],
    
    "defectsByField": {
      // 只包含普通违规，Cross规则不在这里
      "C21x01C": [
        {
          "fieldCode": "C21x01C",
          "ruleCode": "C21x01C_value_check",
          "ruleDescription": "主要手术操作切口愈合等级编码取值不符合国家标准值域定义"
        }
      ]
    }
  }
}
```

## 开发步骤

### ⚠️ 大量Cross规则的分阶段实现

考虑到系统中有接近600条Cross规则，建议分阶段实现：

### 1. 立即可用（无需修改）
现有前端代码可以继续使用 `allDefects` 和 `defectsByField`，功能完全正常。

### 2. 基础适配（处理大量违规）
```javascript
// 检查Cross规则数量，决定展示策略
function handleCrossDefects(crossDefects) {
  if (crossDefects.length === 0) {
    return; // 无Cross规则违规
  }
  
  if (crossDefects.length <= 10) {
    // 少量违规，直接展示
    displayAllCrossDefects(crossDefects);
  } else if (crossDefects.length <= 50) {
    // 中等数量，分组展示
    displayGroupedCrossDefects(crossDefects);
  } else {
    // 大量违规，分页或虚拟滚动
    displayPaginatedCrossDefects(crossDefects);
  }
}
```

### 3. 性能优化（推荐）
- 实现虚拟滚动或分页
- 按规则类型分组折叠展示
- 添加搜索和过滤功能
- 使用懒加载渲染详细信息

### 4. 完整实现
- 实现Cross规则的专门UI组件
- 根据 `crossType` 和 `severity` 设置不同样式
- 展示 `involvedFields` 和 `fieldValues`
- 提供更好的用户体验

## 注意事项

1. **向后兼容**: 现有代码无需修改即可正常工作
2. **渐进增强**: 可以逐步添加Cross规则的专门展示
3. **规则命名**: 所有Cross规则都以 `RULE_CROSS_` 开头
4. **数据完整性**: `allDefects` 仍包含所有违规，确保数据不丢失
5. **⚠️ 性能考虑**: Cross规则数量庞大（接近600条），可能影响性能
6. **⚠️ 大量违规**: 单个病案可能触发多个Cross规则，需要优化展示
7. **⚠️ 内存使用**: 大量Cross规则违规可能占用较多内存

## 性能优化建议

### 前端性能优化
```javascript
// 1. 延迟渲染
function lazyRenderCrossDefects(crossDefects) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        renderCrossDefect(entry.target.dataset.defect);
        observer.unobserve(entry.target);
      }
    });
  });
  
  crossDefects.forEach((defect, index) => {
    const placeholder = createPlaceholder(defect, index);
    observer.observe(placeholder);
  });
}

// 2. 防抖搜索
function setupCrossDefectSearch(crossDefects) {
  const searchInput = document.getElementById('cross-defect-search');
  let searchTimeout;
  
  searchInput.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      const filtered = filterCrossDefects(crossDefects, e.target.value);
      renderFilteredCrossDefects(filtered);
    }, 300);
  });
}

// 3. 批量DOM操作
function batchRenderCrossDefects(crossDefects) {
  const fragment = document.createDocumentFragment();
  
  crossDefects.forEach(defect => {
    const element = createCrossDefectElement(defect);
    fragment.appendChild(element);
  });
  
  document.getElementById('cross-defects-container').appendChild(fragment);
}
```

## 测试建议

使用以下病案进行测试：
- `445583-1`: 有输血逻辑Cross规则违规
- `19065857-1`: 有输血逻辑Cross规则违规
- `19072516-1`: 有输血逻辑Cross规则违规

这些病案会触发 `RULE_CROSS_D26_TRANSFUSION_FEE1` 规则，可以用来测试Cross规则的展示效果。

## 总结

Cross规则功能为医疗质控系统提供了更强大的跨字段逻辑检查能力。通过新增的 `crossDefects` 字段，前端可以为Cross规则提供更好的展示体验，同时完全保持向后兼容性。建议前端团队优先实现基础的Cross规则展示，然后逐步完善用户界面。