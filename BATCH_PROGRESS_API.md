# 批量质控进度查询API文档

## 概述

批量质控任务支持实时进度查询，可以在任务执行过程中获取：
- 已完成病案数
- 进度百分比
- 已执行时间
- 实时统计数据（缺陷数、平均得分等）

## API接口

### 1. 启动批量质控任务

**接口**: `POST /api/qc/check/batch`

**请求参数**:
```json
{
  "periodType": "month",  // 时间类型: year/quarter/month
  "year": 2023,           // 年份（必填）
  "quarter": 1,           // 季度（可选，periodType=quarter时必填）
  "month": 1              // 月份（可选，periodType=month时必填）
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "批量质控完成",
  "data": {
    "batchKey": "2023_M1",           // 批次键，用于后续查询进度
    "periodType": "month",
    "year": 2023,
    "month": 1,
    "caseCount": 94,                 // 病案总数
    "totalDefectCount": 0,           // 初始缺陷数
    "avgDefect": 0.0,
    "avgScore": 100.0,
    "status": "processing",          // 状态: processing/completed/failed
    "progress": 0,                   // 进度: 0-100
    "startTime": "2026-01-16T16:00:00",
    "endTime": null,
    "elapsedSeconds": 0              // 已执行时间（秒）
  }
}
```

**批次键格式**:
- 按年: `"2023"`
- 按季度: `"2023_Q1"`
- 按月: `"2023_M1"`

---

### 2. 查询批量任务进度 ⭐ 新增

**接口**: `GET /api/qc/batch/status/{batchKey}`

**路径参数**:
- `batchKey`: 批次键，从启动接口返回的batchKey字段获取

**请求示例**:
```bash
GET /api/qc/batch/status/2023_M1
```

**响应示例（进行中）**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "batchKey": "2023_M1",
    "periodType": "month",
    "year": 2023,
    "month": 1,
    "caseCount": 50,                 // 已完成病案数
    "totalDefectCount": 150,         // 已发现缺陷总数
    "avgDefect": 3.0,                // 平均缺陷数
    "avgScore": 88.5,                // 平均得分
    "status": "processing",          // 状态: processing
    "progress": 53,                  // 进度: 53%
    "startTime": "2026-01-16T16:00:00",
    "endTime": null,                 // 未完成时为null
    "elapsedSeconds": 45             // 已执行45秒
  }
}
```

**响应示例（已完成）**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "batchKey": "2023_M1",
    "periodType": "month",
    "year": 2023,
    "month": 1,
    "caseCount": 94,                 // 总病案数
    "totalDefectCount": 276,         // 总缺陷数
    "avgDefect": 2.94,               // 平均缺陷数
    "avgScore": 88.26,               // 平均得分
    "status": "completed",           // 状态: completed
    "progress": 100,                 // 进度: 100%
    "startTime": "2026-01-16T16:00:00",
    "endTime": "2026-01-16T16:01:30",
    "elapsedSeconds": 90             // 总耗时90秒
  }
}
```

**响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| batchKey | String | 批次键 |
| periodType | String | 时间类型: year/quarter/month |
| year | Integer | 年份 |
| quarter | Integer | 季度（可选） |
| month | Integer | 月份（可选） |
| caseCount | Integer | 已完成病案数 |
| totalDefectCount | Integer | 已发现缺陷总数 |
| avgDefect | BigDecimal | 平均缺陷数 |
| avgScore | BigDecimal | 平均得分 |
| status | String | 任务状态 |
| progress | Integer | 进度百分比（0-100） |
| startTime | Date | 开始时间 |
| endTime | Date | 结束时间（未完成时为null） |
| elapsedSeconds | Long | 已执行时间（秒） |

**任务状态说明**:
- `processing`: 正在处理中
- `completed`: 已完成
- `failed`: 失败

---

## 使用场景

### 场景1: 前端轮询显示进度

```javascript
// 1. 启动批量任务
const startResponse = await fetch('/api/qc/check/batch', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    periodType: 'month',
    year: 2023,
    month: 1
  })
});

const { data } = await startResponse.json();
const batchKey = data.batchKey;

// 2. 轮询查询进度
const pollInterval = setInterval(async () => {
  const statusResponse = await fetch(`/api/qc/batch/status/${batchKey}`);
  const { data: status } = await statusResponse.json();
  
  // 更新UI
  updateProgressBar(status.progress);
  updateStats({
    completed: status.caseCount,
    total: status.caseCount, // 从初始响应获取
    defects: status.totalDefectCount,
    avgScore: status.avgScore,
    elapsed: formatTime(status.elapsedSeconds)
  });
  
  // 检查是否完成
  if (status.status === 'completed') {
    clearInterval(pollInterval);
    showCompletedMessage(status);
  } else if (status.status === 'failed') {
    clearInterval(pollInterval);
    showErrorMessage();
  }
}, 2000); // 每2秒查询一次
```

### 场景2: React组件示例

```jsx
import React, { useState, useEffect } from 'react';
import { Progress, Card, Statistic, Row, Col } from 'antd';

function BatchQcProgress({ batchKey }) {
  const [status, setStatus] = useState(null);
  
  useEffect(() => {
    const fetchStatus = async () => {
      const response = await fetch(`/api/qc/batch/status/${batchKey}`);
      const { data } = await response.json();
      setStatus(data);
      
      // 如果未完成，继续轮询
      if (data.status === 'processing') {
        setTimeout(fetchStatus, 2000);
      }
    };
    
    fetchStatus();
  }, [batchKey]);
  
  if (!status) return <div>加载中...</div>;
  
  return (
    <Card title="批量质控进度">
      <Progress 
        percent={status.progress} 
        status={status.status === 'completed' ? 'success' : 'active'}
      />
      
      <Row gutter={16} style={{ marginTop: 20 }}>
        <Col span={6}>
          <Statistic 
            title="已完成" 
            value={status.caseCount} 
            suffix="条"
          />
        </Col>
        <Col span={6}>
          <Statistic 
            title="总缺陷数" 
            value={status.totalDefectCount}
          />
        </Col>
        <Col span={6}>
          <Statistic 
            title="平均得分" 
            value={status.avgScore} 
            precision={2}
          />
        </Col>
        <Col span={6}>
          <Statistic 
            title="已执行时间" 
            value={formatTime(status.elapsedSeconds)}
          />
        </Col>
      </Row>
      
      {status.status === 'completed' && (
        <div style={{ marginTop: 20, color: 'green' }}>
          ✓ 任务已完成！
        </div>
      )}
    </Card>
  );
}

function formatTime(seconds) {
  if (seconds < 60) return `${seconds}秒`;
  if (seconds < 3600) return `${Math.floor(seconds/60)}分${seconds%60}秒`;
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${hours}小时${minutes}分`;
}
```

### 场景3: Vue组件示例

```vue
<template>
  <div class="batch-qc-progress">
    <a-card title="批量质控进度">
      <a-progress 
        :percent="status.progress" 
        :status="progressStatus"
      />
      
      <a-row :gutter="16" style="margin-top: 20px">
        <a-col :span="6">
          <a-statistic title="已完成" :value="status.caseCount" suffix="条" />
        </a-col>
        <a-col :span="6">
          <a-statistic title="总缺陷数" :value="status.totalDefectCount" />
        </a-col>
        <a-col :span="6">
          <a-statistic title="平均得分" :value="status.avgScore" :precision="2" />
        </a-col>
        <a-col :span="6">
          <a-statistic title="已执行时间" :value="elapsedTime" />
        </a-col>
      </a-row>
      
      <div v-if="status.status === 'completed'" style="margin-top: 20px; color: green">
        ✓ 任务已完成！
      </div>
    </a-card>
  </div>
</template>

<script>
export default {
  props: {
    batchKey: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      status: {
        progress: 0,
        caseCount: 0,
        totalDefectCount: 0,
        avgScore: 100,
        status: 'processing',
        elapsedSeconds: 0
      },
      timer: null
    };
  },
  computed: {
    progressStatus() {
      return this.status.status === 'completed' ? 'success' : 'active';
    },
    elapsedTime() {
      const seconds = this.status.elapsedSeconds;
      if (seconds < 60) return `${seconds}秒`;
      if (seconds < 3600) return `${Math.floor(seconds/60)}分${seconds%60}秒`;
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      return `${hours}小时${minutes}分`;
    }
  },
  mounted() {
    this.fetchStatus();
  },
  beforeUnmount() {
    if (this.timer) {
      clearTimeout(this.timer);
    }
  },
  methods: {
    async fetchStatus() {
      try {
        const response = await fetch(`/api/qc/batch/status/${this.batchKey}`);
        const { data } = await response.json();
        this.status = data;
        
        // 如果未完成，继续轮询
        if (data.status === 'processing') {
          this.timer = setTimeout(() => this.fetchStatus(), 2000);
        }
      } catch (error) {
        console.error('获取进度失败:', error);
      }
    }
  }
};
</script>
```

---

## 性能建议

### 轮询间隔
- 小批量（<100条）: 建议2秒
- 中批量（100-1000条）: 建议3-5秒
- 大批量（>1000条）: 建议5-10秒

### 超时处理
```javascript
const MAX_WAIT_TIME = 30 * 60 * 1000; // 30分钟
const startTime = Date.now();

const pollInterval = setInterval(async () => {
  // 检查超时
  if (Date.now() - startTime > MAX_WAIT_TIME) {
    clearInterval(pollInterval);
    showTimeoutMessage();
    return;
  }
  
  // 查询进度...
}, 2000);
```

### 错误处理
```javascript
const fetchStatus = async () => {
  try {
    const response = await fetch(`/api/qc/batch/status/${batchKey}`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const { code, data, message } = await response.json();
    
    if (code !== 200) {
      throw new Error(message || '查询失败');
    }
    
    return data;
  } catch (error) {
    console.error('查询进度失败:', error);
    // 显示错误提示
    showErrorNotification(error.message);
    return null;
  }
};
```

---

## 测试脚本

### Python测试脚本

```bash
python test_batch_progress.py
```

该脚本会：
1. 启动一个批量任务
2. 每2秒查询一次进度
3. 显示实时进度信息
4. 任务完成后显示最终统计

### cURL测试

```bash
# 1. 启动批量任务
curl -X POST http://localhost:4101/api/qc/check/batch \
  -H "Content-Type: application/json" \
  -d '{"periodType":"month","year":2023,"month":1}'

# 2. 查询进度（使用返回的batchKey）
curl http://localhost:4101/api/qc/batch/status/2023_M1
```

---

## 注意事项

1. **批次键唯一性**: 相同时间范围的批量任务会使用相同的batchKey，新任务会覆盖旧任务的数据

2. **并发限制**: 当前实现是同步处理，建议避免同时启动多个大批量任务

3. **数据持久化**: 任务进度数据保存在 `kiro_qc_batch_summary` 表中，可以查询历史任务

4. **时间计算**: `elapsedSeconds` 字段：
   - 任务进行中：当前时间 - 开始时间
   - 任务已完成：结束时间 - 开始时间

5. **进度更新频率**: 系统每处理10条病案或完成时更新一次进度，不是实时更新

---

## 相关文档

- `API_EXAMPLES.md` - 完整API示例
- `test_batch_progress.py` - 进度查询测试脚本
- `FINAL_SUMMARY.md` - 系统总体说明

---

**更新时间**: 2026-01-16  
**版本**: 1.0.0  
**状态**: ✅ 已实现并测试
