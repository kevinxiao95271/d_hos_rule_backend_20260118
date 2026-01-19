# Cross规则前端集成使用示例

## 📋 快速开始

### 1. 基础JavaScript使用

```javascript
// 调用单病案质控API
async function checkSingleCase(a48, a49) {
  try {
    const response = await fetch(`/api/qc/check/single?a48=${a48}&a49=${a49}`);
    const result = await response.json();
    
    if (result.code === 200) {
      const data = result.data;
      
      // 显示基础统计
      console.log('=== 基础统计 ===');
      console.log(`病案: ${data.mrKey}`);
      console.log(`总违规: ${data.defectCount}`);
      console.log(`总扣分: ${data.totalDeduct}`);
      console.log(`最终得分: ${data.finalScore}`);
      
      // 🆕 显示Cross规则统计
      console.log('=== Cross规则统计 ===');
      console.log(`Cross违规数: ${data.crossDefectCount}`);
      console.log(`Cross扣分: ${data.crossTotalDeduct}`);
      
      if (data.crossDefectCount > 0) {
        const ratio = (data.crossDefectCount / data.defectCount * 100).toFixed(1);
        console.log(`Cross占比: ${ratio}%`);
        
        console.log('=== Cross违规详情 ===');
        data.crossDefects.forEach((defect, index) => {
          console.log(`${index + 1}. ${defect.ruleCode}`);
          console.log(`   描述: ${defect.ruleDescription}`);
          console.log(`   类型: ${defect.crossType}`);
          console.log(`   严重程度: ${defect.severity}`);
        });
      }
    }
  } catch (error) {
    console.error('API调用失败:', error);
  }
}

// 使用示例
checkSingleCase('445583', '1');
```

### 2. 批量质控使用

```javascript
// 调用批量质控API
async function checkBatch(year, month) {
  try {
    const response = await fetch('/api/qc/check/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        periodType: 'month',
        year: year,
        month: month
      })
    });
    
    const result = await response.json();
    
    if (result.code === 200) {
      const data = result.data;
      
      console.log('=== 批量质控结果 ===');
      console.log(`批次: ${data.batchKey}`);
      console.log(`病案数: ${data.caseCount}`);
      console.log(`总违规: ${data.totalDefectCount}`);
      console.log(`平均得分: ${data.avgScore}`);
      
      // 🆕 Cross规则统计
      console.log('=== Cross规则统计 ===');
      console.log(`Cross违规总数: ${data.crossDefectCount}`);
      console.log(`Cross总扣分: ${data.crossTotalDeduct}`);
      console.log(`平均Cross违规: ${data.avgCrossDefect}`);
      
      if (data.totalDefectCount > 0) {
        const crossRatio = (data.crossDefectCount / data.totalDefectCount * 100).toFixed(1);
        console.log(`Cross占比: ${crossRatio}%`);
      }
    }
  } catch (error) {
    console.error('批量质控失败:', error);
  }
}

// 使用示例
checkBatch(2023, 1);
```

## 🎨 HTML + CSS 展示示例

### 单病案Cross规则统计卡片

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        .cross-stats-card {
            border: 1px solid #e1f5fe;
            border-radius: 8px;
            background: linear-gradient(135deg, #f3e5f5 0%, #e8f5e8 100%);
            padding: 16px;
            margin: 16px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stats-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
        
        .stats-title {
            margin: 0;
            color: #1976d2;
            font-size: 18px;
        }
        
        .stats-badge {
            background: #4caf50;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 16px;
        }
        
        .stat-item {
            text-align: center;
            padding: 12px;
            background: rgba(255,255,255,0.7);
            border-radius: 6px;
        }
        
        .stat-label {
            display: block;
            font-size: 12px;
            color: #666;
            margin-bottom: 4px;
        }
        
        .stat-value {
            display: block;
            font-size: 20px;
            font-weight: bold;
        }
        
        .cross-count { color: #ff6b35; }
        .cross-deduct { color: #d32f2f; }
        .cross-ratio { color: #1976d2; }
    </style>
</head>
<body>
    <div class="cross-stats-card">
        <div class="stats-header">
            <h3 class="stats-title">🎯 Cross规则统计</h3>
            <span class="stats-badge">跨字段检查</span>
        </div>
        
        <div class="stats-grid">
            <div class="stat-item">
                <span class="stat-label">违规数量</span>
                <span class="stat-value cross-count" id="crossCount">1</span>
            </div>
            
            <div class="stat-item">
                <span class="stat-label">扣分总计</span>
                <span class="stat-value cross-deduct" id="crossDeduct">0.0</span>
            </div>
            
            <div class="stat-item">
                <span class="stat-label">占比</span>
                <span class="stat-value cross-ratio" id="crossRatio">11.1%</span>
            </div>
        </div>
    </div>

    <script>
        // 更新Cross规则统计显示
        function updateCrossStats(data) {
            document.getElementById('crossCount').textContent = data.crossDefectCount;
            document.getElementById('crossDeduct').textContent = data.crossTotalDeduct.toFixed(1);
            
            const ratio = data.defectCount > 0 
                ? (data.crossDefectCount / data.defectCount * 100).toFixed(1)
                : 0;
            document.getElementById('crossRatio').textContent = ratio + '%';
        }
    </script>
</body>
</html>
```

## ⚛️ React组件使用示例

### 基础使用

```tsx
import React, { useState, useEffect } from 'react';
import { CrossRuleStatsCard, BatchCrossRuleStats } from './CrossRuleStatsComponent';
import { SingleQcResult, BatchQcResult } from './cross-rules-api-types';

const QcResultPage: React.FC = () => {
  const [qcResult, setQcResult] = useState<SingleQcResult | null>(null);
  const [batchResult, setBatchResult] = useState<BatchQcResult | null>(null);
  
  // 加载单病案质控结果
  const loadQcResult = async (a48: string, a49: string) => {
    try {
      const response = await fetch(`/api/qc/check/single?a48=${a48}&a49=${a49}`);
      const result = await response.json();
      
      if (result.code === 200) {
        setQcResult(result.data);
      }
    } catch (error) {
      console.error('加载质控结果失败:', error);
    }
  };
  
  // 加载批量质控结果
  const loadBatchResult = async () => {
    try {
      const response = await fetch('/api/qc/check/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ periodType: 'month', year: 2023, month: 1 })
      });
      
      const result = await response.json();
      
      if (result.code === 200) {
        setBatchResult(result.data);
      }
    } catch (error) {
      console.error('加载批量结果失败:', error);
    }
  };
  
  useEffect(() => {
    loadQcResult('445583', '1');
    loadBatchResult();
  }, []);
  
  return (
    <div>
      <h1>质控结果页面</h1>
      
      {/* 单病案Cross规则统计 */}
      {qcResult && (
        <CrossRuleStatsCard 
          data={qcResult} 
          showDetails={true} 
        />
      )}
      
      {/* 批量Cross规则统计 */}
      {batchResult && (
        <BatchCrossRuleStats 
          data={batchResult} 
        />
      )}
    </div>
  );
};

export default QcResultPage;
```

### 使用自定义Hook

```tsx
import React from 'react';
import { useCrossRuleStats } from './CrossRuleStatsComponent';
import { SingleQcResult } from './cross-rules-api-types';

interface QcSummaryProps {
  data: SingleQcResult;
}

const QcSummary: React.FC<QcSummaryProps> = ({ data }) => {
  const { crossStats, isValid, hasViolations } = useCrossRuleStats(data);
  
  return (
    <div className="qc-summary">
      <h3>质控摘要</h3>
      
      <div className="summary-stats">
        <div>总违规: {data.defectCount}</div>
        <div>总扣分: {data.totalDeduct}</div>
        <div>最终得分: {data.finalScore}</div>
      </div>
      
      {hasViolations && (
        <div className="cross-summary">
          <h4>Cross规则违规</h4>
          <div>数量: {crossStats.count}</div>
          <div>扣分: {crossStats.totalDeduct}</div>
          <div>占比: {crossStats.ratio}%</div>
        </div>
      )}
      
      {!isValid && (
        <div className="warning">
          ⚠️ 数据一致性检查失败
        </div>
      )}
    </div>
  );
};
```

## 📊 图表集成示例

### Chart.js饼图

```javascript
// Cross规则占比饼图
function renderCrossRatioPieChart(canvasId, data) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  const normalDefects = data.defectCount - data.crossDefectCount;
  
  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['普通规则违规', 'Cross规则违规'],
      datasets: [{
        data: [normalDefects, data.crossDefectCount],
        backgroundColor: ['#36a2eb', '#ff6b35'],
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Cross规则违规占比分析'
        },
        legend: {
          position: 'bottom'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.label;
              const value = context.parsed;
              const total = data.defectCount;
              const percentage = ((value / total) * 100).toFixed(1);
              return `${label}: ${value} (${percentage}%)`;
            }
          }
        }
      }
    }
  });
}

// 使用示例
// renderCrossRatioPieChart('crossRatioChart', qcResultData);
```

### ECharts柱状图

```javascript
// Cross规则统计柱状图
function renderCrossStatsBarChart(containerId, data) {
  const chart = echarts.init(document.getElementById(containerId));
  
  const option = {
    title: {
      text: 'Cross规则统计对比',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['普通规则', 'Cross规则'],
      bottom: 0
    },
    xAxis: {
      type: 'category',
      data: ['违规数量', '扣分总计']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '普通规则',
        type: 'bar',
        data: [
          data.defectCount - data.crossDefectCount,
          data.totalDeduct - data.crossTotalDeduct
        ],
        itemStyle: {
          color: '#36a2eb'
        }
      },
      {
        name: 'Cross规则',
        type: 'bar',
        data: [
          data.crossDefectCount,
          data.crossTotalDeduct
        ],
        itemStyle: {
          color: '#ff6b35'
        }
      }
    ]
  };
  
  chart.setOption(option);
}

// 使用示例
// renderCrossStatsBarChart('crossStatsChart', qcResultData);
```

## 🔧 工具函数示例

### 数据处理工具

```javascript
// Cross规则数据处理工具类
class CrossRuleUtils {
  // 计算Cross规则统计
  static calculateStats(data) {
    const ratio = data.defectCount > 0 
      ? (data.crossDefectCount / data.defectCount) * 100 
      : 0;
      
    return {
      count: data.crossDefectCount,
      totalDeduct: data.crossTotalDeduct,
      ratio: Math.round(ratio * 10) / 10
    };
  }
  
  // 验证数据一致性
  static validateData(data) {
    const errors = [];
    
    if (data.crossDefectCount !== data.crossDefects.length) {
      errors.push('Cross违规数量不一致');
    }
    
    const normalDefects = data.allDefects.filter(d => 
      !d.ruleCode.startsWith('RULE_CROSS_')
    ).length;
    
    if (data.defectCount !== normalDefects + data.crossDefectCount) {
      errors.push('总违规数量计算错误');
    }
    
    return {
      isValid: errors.length === 0,
      errors: errors
    };
  }
  
  // 格式化Cross规则类型
  static formatCrossType(crossType) {
    const typeMap = {
      'field_pair': '字段配对检查',
      'age_gender': '年龄性别逻辑',
      'conditional_required': '条件必填检查',
      'age_diagnosis': '年龄诊断匹配',
      'transfusion_logic': '输血逻辑检查',
      'date_consistency': '日期一致性检查',
      'logic_check': '逻辑检查'
    };
    
    return typeMap[crossType] || crossType;
  }
  
  // 获取严重程度颜色
  static getSeverityColor(severity) {
    const colorMap = {
      'low': '#4caf50',
      'medium': '#ff9800',
      'high': '#f44336'
    };
    
    return colorMap[severity] || '#999';
  }
}

// 使用示例
const stats = CrossRuleUtils.calculateStats(qcResultData);
const validation = CrossRuleUtils.validateData(qcResultData);
console.log('Cross规则统计:', stats);
console.log('数据验证:', validation);
```

## 📱 移动端适配示例

```css
/* 移动端响应式样式 */
@media (max-width: 768px) {
  .cross-stats-card {
    margin: 8px;
    padding: 12px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .stat-item {
    padding: 8px;
  }
  
  .stat-value {
    font-size: 16px;
  }
  
  .stats-title {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .stats-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .stats-badge {
    align-self: flex-end;
  }
}
```

```javascript
// 移动端简化显示逻辑
function renderMobileCrossStats(data) {
  const isMobile = window.innerWidth < 768;
  
  if (isMobile) {
    // 移动端简化显示
    return `
      <div class="mobile-cross-stats">
        <span class="mobile-stat">
          Cross: ${data.crossDefectCount}个
        </span>
        <span class="mobile-stat">
          扣分: ${data.crossTotalDeduct}
        </span>
      </div>
    `;
  } else {
    // 桌面端完整显示
    return renderFullCrossStats(data);
  }
}
```

---

这些示例涵盖了从基础JavaScript到React组件的各种使用场景，帮助前端团队快速集成Cross规则统计功能。所有代码都考虑了向后兼容性和错误处理，确保在各种情况下都能正常工作。