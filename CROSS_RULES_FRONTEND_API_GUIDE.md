# Cross规则前端开发指引 - API变动说明

## 📋 概述

本文档专门针对Cross规则功能对API的影响变动，为前端开发团队提供详细的集成指引。

**重要提示**: 所有变动都是**向后兼容**的，现有前端代码无需修改即可正常工作。

---

## 🔄 API变动总览

### 影响的API接口
1. **单病案质控API**: `POST /api/qc/check/single`
2. **批量质控API**: `POST /api/qc/check/batch`
3. **批量状态查询API**: `GET /api/qc/batch/status/{batchKey}`

### 变动类型
- ✅ **新增字段**: 添加了Cross规则统计字段
- ✅ **保持兼容**: 所有原有字段完全不变
- ✅ **数据增强**: 提供更丰富的Cross规则信息

---

## 📊 单病案质控API变动

### API端点
```
POST /api/qc/check/single?a48={病案号}&a49={住院次数}
```

### 响应结构变动

#### 🆕 新增字段
```json
{
  "code": 200,
  "message": "质控完成",
  "data": {
    // === 原有字段（完全不变） ===
    "mrKey": "445583_1",
    "defectCount": 9,
    "totalDeduct": 24.0,
    "finalScore": 76.0,
    "allDefects": [...],
    "defectsByField": {...},
    "crossDefects": [...],
    
    // === 🆕 新增：Cross规则统计字段 ===
    "crossDefectCount": 1,        // Cross规则违规总数
    "crossTotalDeduct": 0.0       // Cross规则总扣分
  }
}
```

#### 字段说明
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| `crossDefectCount` | `number` | Cross规则违规总数 | `1` |
| `crossTotalDeduct` | `number` | Cross规则总扣分 | `0.0` |

#### 数据关系
- `crossDefectCount` = `crossDefects.length`（保证数据一致性）
- `crossTotalDeduct` = Cross规则违规的扣分总和
- `defectCount` = 普通规则违规数 + Cross规则违规数
- `totalDeduct` = 普通规则扣分 + Cross规则扣分

---

## 📈 批量质控API变动

### API端点
```
POST /api/qc/check/batch
Content-Type: application/json

{
  "periodType": "month",
  "year": 2023,
  "month": 1
}
```

### 响应结构变动

#### 🆕 新增字段
```json
{
  "code": 200,
  "message": "批量质控完成",
  "data": {
    // === 原有字段（完全不变） ===
    "batchKey": "2023_M1",
    "caseCount": 94,
    "totalDefectCount": 156,
    "avgDefect": 1.66,
    "avgScore": 92.5,
    "status": "completed",
    "progress": 100,
    
    // === 🆕 新增：Cross规则统计字段 ===
    "crossDefectCount": 12,       // Cross规则违规总数
    "crossTotalDeduct": 15.5,     // Cross规则总扣分
    "avgCrossDefect": 0.13        // 平均Cross规则违规数
  }
}
```

#### 字段说明
| 字段名 | 类型 | 说明 | 计算方式 |
|--------|------|------|----------|
| `crossDefectCount` | `number` | 批量中Cross规则违规总数 | 所有病案Cross违规数之和 |
| `crossTotalDeduct` | `number` | 批量中Cross规则总扣分 | 所有病案Cross扣分之和 |
| `avgCrossDefect` | `number` | 平均Cross规则违规数 | `crossDefectCount / caseCount` |

---

## 💻 前端集成方案

### 方案1: 零改动（推荐用于快速上线）

现有代码完全不需要修改，继续使用原有字段：

```javascript
// 现有代码继续正常工作
const { defectCount, totalDeduct, finalScore, allDefects } = response.data;
console.log(`总违规: ${defectCount}, 总扣分: ${totalDeduct}`);
```

### 方案2: 基础增强（推荐用于渐进升级）

在现有基础上添加Cross规则统计展示：

```javascript
// 单病案质控结果处理
function handleQcResult(data) {
  // 原有逻辑保持不变
  displayBasicStats(data.defectCount, data.totalDeduct, data.finalScore);
  displayDefects(data.allDefects);
  
  // 🆕 新增：Cross规则统计展示
  if (data.crossDefectCount > 0) {
    displayCrossStats(data.crossDefectCount, data.crossTotalDeduct);
    displayCrossDefects(data.crossDefects);
  }
}

// Cross规则统计展示函数
function displayCrossStats(count, deduct) {
  const crossStatsHtml = `
    <div class="cross-stats">
      <h4>🎯 Cross规则统计</h4>
      <p>违规数量: <span class="cross-count">${count}</span></p>
      <p>扣分总计: <span class="cross-deduct">${deduct}</span></p>
    </div>
  `;
  document.getElementById('cross-stats').innerHTML = crossStatsHtml;
}
```

### 方案3: 完整集成（推荐用于新功能开发）

完整利用Cross规则统计信息：

```javascript
// 完整的质控结果处理
function handleQcResult(data) {
  // 基础统计
  const stats = {
    total: {
      defects: data.defectCount,
      deduct: data.totalDeduct,
      score: data.finalScore
    },
    normal: {
      defects: data.defectCount - data.crossDefectCount,
      deduct: data.totalDeduct - data.crossTotalDeduct
    },
    cross: {
      defects: data.crossDefectCount,
      deduct: data.crossTotalDeduct
    }
  };
  
  // 计算占比
  const crossRatio = stats.total.defects > 0 
    ? (stats.cross.defects / stats.total.defects * 100).toFixed(1)
    : 0;
  
  // 渲染统计图表
  renderStatsChart(stats, crossRatio);
  
  // 分类展示违规
  renderDefectsByCategory({
    normal: data.allDefects.filter(d => !d.ruleCode.startsWith('RULE_CROSS_')),
    cross: data.crossDefects
  });
}

// 批量质控结果处理
function handleBatchResult(data) {
  const batchStats = {
    cases: data.caseCount,
    totalDefects: data.totalDefectCount,
    crossDefects: data.crossDefectCount,
    avgDefects: data.avgDefect,
    avgCrossDefects: data.avgCrossDefect,
    crossRatio: data.totalDefectCount > 0 
      ? (data.crossDefectCount / data.totalDefectCount * 100).toFixed(1)
      : 0
  };
  
  renderBatchDashboard(batchStats);
}
```

---

## 🎨 UI设计建议

### Cross规则统计卡片
```html
<div class="cross-rules-stats-card">
  <div class="stats-header">
    <h3>🎯 Cross规则统计</h3>
    <span class="stats-badge">跨字段检查</span>
  </div>
  
  <div class="stats-content">
    <div class="stat-item">
      <span class="stat-label">违规数量</span>
      <span class="stat-value cross-count">{{crossDefectCount}}</span>
    </div>
    
    <div class="stat-item">
      <span class="stat-label">扣分总计</span>
      <span class="stat-value cross-deduct">{{crossTotalDeduct}}</span>
    </div>
    
    <div class="stat-item">
      <span class="stat-label">占比</span>
      <span class="stat-value cross-ratio">{{crossRatio}}%</span>
    </div>
  </div>
</div>
```

### CSS样式建议
```css
.cross-rules-stats-card {
  border: 1px solid #e1f5fe;
  border-radius: 8px;
  background: linear-gradient(135deg, #f3e5f5 0%, #e8f5e8 100%);
  padding: 16px;
  margin: 16px 0;
}

.cross-count {
  color: #ff6b35;
  font-weight: bold;
}

.cross-deduct {
  color: #d32f2f;
  font-weight: bold;
}

.cross-ratio {
  color: #1976d2;
  font-weight: bold;
}

.stats-badge {
  background: #4caf50;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}
```

---

## 📱 响应式处理

### 移动端适配
```javascript
// 移动端简化显示
function renderMobileStats(data) {
  if (window.innerWidth < 768) {
    // 移动端只显示关键统计
    return `
      <div class="mobile-stats">
        <span>总违规: ${data.defectCount}</span>
        <span>Cross: ${data.crossDefectCount}</span>
        <span>得分: ${data.finalScore}</span>
      </div>
    `;
  }
  
  // 桌面端显示完整统计
  return renderFullStats(data);
}
```

---

## 🔍 数据验证

### 前端数据一致性检查
```javascript
// 验证Cross规则统计数据一致性
function validateCrossStats(data) {
  const errors = [];
  
  // 检查Cross违规数量一致性
  if (data.crossDefectCount !== data.crossDefects.length) {
    errors.push(`Cross违规数量不一致: count=${data.crossDefectCount}, details=${data.crossDefects.length}`);
  }
  
  // 检查总违规数量逻辑
  const normalDefects = data.allDefects.filter(d => !d.ruleCode.startsWith('RULE_CROSS_')).length;
  if (data.defectCount !== normalDefects + data.crossDefectCount) {
    errors.push('总违规数量计算错误');
  }
  
  if (errors.length > 0) {
    console.warn('Cross规则数据验证失败:', errors);
  }
  
  return errors.length === 0;
}
```

---

## 📊 图表集成

### Chart.js示例
```javascript
// Cross规则占比饼图
function renderCrossRatioPieChart(data) {
  const ctx = document.getElementById('crossRatioChart').getContext('2d');
  
  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['普通规则违规', 'Cross规则违规'],
      datasets: [{
        data: [
          data.defectCount - data.crossDefectCount,
          data.crossDefectCount
        ],
        backgroundColor: ['#36a2eb', '#ff6b35'],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Cross规则违规占比'
        },
        legend: {
          position: 'bottom'
        }
      }
    }
  });
}

// 批量质控趋势图
function renderBatchTrendChart(batchData) {
  const ctx = document.getElementById('batchTrendChart').getContext('2d');
  
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: batchData.map(d => d.batchKey),
      datasets: [
        {
          label: '总违规数',
          data: batchData.map(d => d.totalDefectCount),
          borderColor: '#36a2eb',
          fill: false
        },
        {
          label: 'Cross规则违规数',
          data: batchData.map(d => d.crossDefectCount),
          borderColor: '#ff6b35',
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}
```

---

## 🚨 错误处理

### API错误处理
```javascript
// 处理Cross规则统计字段缺失
function handleApiResponse(response) {
  try {
    const data = response.data;
    
    // 设置默认值，防止字段缺失
    const safeData = {
      ...data,
      crossDefectCount: data.crossDefectCount ?? 0,
      crossTotalDeduct: data.crossTotalDeduct ?? 0,
      crossDefects: data.crossDefects ?? []
    };
    
    // 批量质控额外字段
    if (data.avgCrossDefect !== undefined) {
      safeData.avgCrossDefect = data.avgCrossDefect ?? 0;
    }
    
    return safeData;
    
  } catch (error) {
    console.error('Cross规则数据处理错误:', error);
    return getDefaultCrossData();
  }
}

function getDefaultCrossData() {
  return {
    crossDefectCount: 0,
    crossTotalDeduct: 0,
    crossDefects: [],
    avgCrossDefect: 0
  };
}
```

---

## 🧪 测试建议

### 单元测试
```javascript
// Jest测试示例
describe('Cross规则统计处理', () => {
  test('应该正确处理Cross规则统计数据', () => {
    const mockData = {
      defectCount: 9,
      crossDefectCount: 1,
      crossTotalDeduct: 0.0,
      crossDefects: [
        {
          ruleCode: 'RULE_CROSS_D26_TRANSFUSION_FEE1',
          ruleDescription: '存在输血记录，未发生血液费用'
        }
      ]
    };
    
    const result = handleQcResult(mockData);
    
    expect(result.crossStats.count).toBe(1);
    expect(result.crossStats.deduct).toBe(0.0);
    expect(result.crossStats.ratio).toBe('11.1'); // 1/9 * 100
  });
  
  test('应该处理Cross规则字段缺失的情况', () => {
    const mockData = {
      defectCount: 5,
      // 缺失Cross规则字段
    };
    
    const result = handleApiResponse({ data: mockData });
    
    expect(result.crossDefectCount).toBe(0);
    expect(result.crossTotalDeduct).toBe(0);
    expect(result.crossDefects).toEqual([]);
  });
});
```

---

## 📋 迁移检查清单

### 开发阶段
- [ ] 确认API响应结构变动
- [ ] 更新TypeScript接口定义
- [ ] 实现Cross规则统计展示组件
- [ ] 添加数据验证逻辑
- [ ] 编写单元测试

### 测试阶段
- [ ] 验证向后兼容性
- [ ] 测试Cross规则统计数据准确性
- [ ] 测试错误处理逻辑
- [ ] 验证移动端适配
- [ ] 性能测试

### 上线阶段
- [ ] 灰度发布验证
- [ ] 监控API响应时间
- [ ] 收集用户反馈
- [ ] 优化UI交互体验

---

## 🔗 相关资源

### API文档
- [Cross规则API完整示例](./CROSS_RULES_API_EXAMPLES.md)
- [Cross规则快速参考](./CROSS_RULES_QUICK_REFERENCE.md)

### 测试数据
- 测试病案: `445583_1`, `19065857_1`, `19072516_1`
- 这些病案包含Cross规则违规，适合前端测试

### 技术支持
- 后端API: `http://localhost:4101`
- Swagger文档: `http://localhost:4101/swagger-ui/index.html`

---

## 📞 联系方式

如有疑问，请联系：
- **后端团队**: 负责API接口问题
- **产品团队**: 负责业务逻辑确认
- **测试团队**: 负责测试用例支持

---

**更新日期**: 2026年1月19日  
**API版本**: 1.0.0  
**兼容性**: 完全向后兼容  
**状态**: ✅ 生产就绪