# 前端对接指南 - 异步批量质控

## 接口变化说明

### ⚠️ 重要变化

批量质控接口已改为**异步执行**，前端需要调整为**轮询查询进度**的方式。

---

## 接口对比

### 之前（同步方式）❌
```javascript
// 旧方式：一次请求等待完成（会超时）
const response = await fetch('/api/qc/check/batch', {
  method: 'POST',
  body: JSON.stringify({ periodType: 'month', year: 2023, month: 1 })
});
const result = await response.json();
// 直接获取完整结果（但大批量会超时）
```

### 现在（异步方式）✅
```javascript
// 新方式：启动任务 + 轮询进度
// 1. 启动任务（立即返回）
const startResponse = await fetch('/api/qc/check/batch', {
  method: 'POST',
  body: JSON.stringify({ periodType: 'month', year: 2023, month: 1 })
});
const { data } = await startResponse.json();
const batchKey = data.batchKey;  // 获取批次键

// 2. 轮询查询进度
const timer = setInterval(async () => {
  const statusResponse = await fetch(`/api/qc/batch/status/${batchKey}`);
  const { data: status } = await statusResponse.json();
  
  updateUI(status);  // 更新UI
  
  if (status.status === 'completed') {
    clearInterval(timer);
    showSuccess(status);
  }
}, 2000);  // 每2秒查询一次
```

---

## 完整前端实现

### 1. React + Ant Design 实现

```jsx
import React, { useState, useEffect } from 'react';
import { Button, Progress, Card, Statistic, Row, Col, message } from 'antd';

function BatchQcPage() {
  const [loading, setLoading] = useState(false);
  const [batchKey, setBatchKey] = useState(null);
  const [status, setStatus] = useState(null);

  // 启动批量质控
  const startBatchQc = async (params) => {
    try {
      setLoading(true);
      
      const response = await fetch('/api/qc/check/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      
      const { code, data, message: msg } = await response.json();
      
      if (code === 200) {
        setBatchKey(data.batchKey);
        setStatus(data);
        message.success('批量质控任务已启动');
      } else {
        message.error(msg || '启动失败');
        setLoading(false);
      }
    } catch (error) {
      message.error('启动失败: ' + error.message);
      setLoading(false);
    }
  };

  // 轮询查询进度
  useEffect(() => {
    if (!batchKey || !loading) return;

    const timer = setInterval(async () => {
      try {
        const response = await fetch(`/api/qc/batch/status/${batchKey}`);
        const { code, data } = await response.json();
        
        if (code === 200) {
          setStatus(data);
          
          // 检查是否完成
          if (data.status === 'completed') {
            setLoading(false);
            clearInterval(timer);
            message.success('批量质控完成！');
          } else if (data.status === 'failed') {
            setLoading(false);
            clearInterval(timer);
            message.error('批量质控失败');
          }
        }
      } catch (error) {
        console.error('查询进度失败:', error);
      }
    }, 2000);  // 每2秒查询一次

    return () => clearInterval(timer);
  }, [batchKey, loading]);

  // 格式化时间
  const formatTime = (seconds) => {
    if (!seconds) return '0秒';
    if (seconds < 60) return `${seconds}秒`;
    if (seconds < 3600) return `${Math.floor(seconds/60)}分${seconds%60}秒`;
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}小时${minutes}分`;
  };

  return (
    <div>
      <Card title="批量质控">
        <Button 
          type="primary" 
          loading={loading}
          onClick={() => startBatchQc({
            periodType: 'month',
            year: 2023,
            month: 1
          })}
        >
          启动批量质控
        </Button>

        {status && (
          <div style={{ marginTop: 20 }}>
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
          </div>
        )}
      </Card>
    </div>
  );
}

export default BatchQcPage;
```

---

### 2. Vue 3 + Element Plus 实现

```vue
<template>
  <el-card title="批量质控">
    <el-button 
      type="primary" 
      :loading="loading"
      @click="startBatchQc"
    >
      启动批量质控
    </el-button>

    <div v-if="status" style="margin-top: 20px">
      <el-progress 
        :percentage="status.progress" 
        :status="status.status === 'completed' ? 'success' : undefined"
      />
      
      <el-row :gutter="16" style="margin-top: 20px">
        <el-col :span="6">
          <el-statistic title="已完成" :value="status.caseCount" suffix="条" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="总缺陷数" :value="status.totalDefectCount" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="平均得分" :value="status.avgScore" :precision="2" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="已执行时间" :value="formatTime(status.elapsedSeconds)" />
        </el-col>
      </el-row>
    </div>
  </el-card>
</template>

<script setup>
import { ref, watch } from 'vue';
import { ElMessage } from 'element-plus';

const loading = ref(false);
const batchKey = ref(null);
const status = ref(null);
let timer = null;

// 启动批量质控
const startBatchQc = async () => {
  try {
    loading.value = true;
    
    const response = await fetch('/api/qc/check/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        periodType: 'month',
        year: 2023,
        month: 1
      })
    });
    
    const { code, data, message: msg } = await response.json();
    
    if (code === 200) {
      batchKey.value = data.batchKey;
      status.value = data;
      ElMessage.success('批量质控任务已启动');
    } else {
      ElMessage.error(msg || '启动失败');
      loading.value = false;
    }
  } catch (error) {
    ElMessage.error('启动失败: ' + error.message);
    loading.value = false;
  }
};

// 查询进度
const fetchStatus = async () => {
  try {
    const response = await fetch(`/api/qc/batch/status/${batchKey.value}`);
    const { code, data } = await response.json();
    
    if (code === 200) {
      status.value = data;
      
      if (data.status === 'completed') {
        loading.value = false;
        clearInterval(timer);
        ElMessage.success('批量质控完成！');
      } else if (data.status === 'failed') {
        loading.value = false;
        clearInterval(timer);
        ElMessage.error('批量质控失败');
      }
    }
  } catch (error) {
    console.error('查询进度失败:', error);
  }
};

// 监听batchKey变化，启动轮询
watch([batchKey, loading], ([key, isLoading]) => {
  if (key && isLoading) {
    timer = setInterval(fetchStatus, 2000);
  } else if (timer) {
    clearInterval(timer);
  }
});

// 格式化时间
const formatTime = (seconds) => {
  if (!seconds) return '0秒';
  if (seconds < 60) return `${seconds}秒`;
  if (seconds < 3600) return `${Math.floor(seconds/60)}分${seconds%60}秒`;
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${hours}小时${minutes}分`;
};
</script>
```

---

### 3. 原生JavaScript实现

```javascript
class BatchQcManager {
  constructor(baseUrl = '/api/qc') {
    this.baseUrl = baseUrl;
    this.batchKey = null;
    this.timer = null;
  }

  // 启动批量质控
  async start(params) {
    try {
      const response = await fetch(`${this.baseUrl}/check/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      
      const { code, data, message } = await response.json();
      
      if (code === 200) {
        this.batchKey = data.batchKey;
        this.startPolling();
        return { success: true, data };
      } else {
        return { success: false, message };
      }
    } catch (error) {
      return { success: false, message: error.message };
    }
  }

  // 开始轮询
  startPolling(interval = 2000) {
    if (this.timer) clearInterval(this.timer);
    
    this.timer = setInterval(async () => {
      const status = await this.getStatus();
      
      if (status) {
        this.onProgress(status);
        
        if (status.status === 'completed') {
          this.stopPolling();
          this.onComplete(status);
        } else if (status.status === 'failed') {
          this.stopPolling();
          this.onError(status);
        }
      }
    }, interval);
  }

  // 停止轮询
  stopPolling() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  // 查询状态
  async getStatus() {
    if (!this.batchKey) return null;
    
    try {
      const response = await fetch(`${this.baseUrl}/batch/status/${this.batchKey}`);
      const { code, data } = await response.json();
      return code === 200 ? data : null;
    } catch (error) {
      console.error('查询进度失败:', error);
      return null;
    }
  }

  // 回调函数（需要重写）
  onProgress(status) {
    console.log('进度更新:', status);
  }

  onComplete(status) {
    console.log('任务完成:', status);
  }

  onError(status) {
    console.error('任务失败:', status);
  }
}

// 使用示例
const qcManager = new BatchQcManager();

// 重写回调函数
qcManager.onProgress = (status) => {
  document.getElementById('progress').innerText = `${status.progress}%`;
  document.getElementById('completed').innerText = status.caseCount;
  document.getElementById('elapsed').innerText = formatTime(status.elapsedSeconds);
};

qcManager.onComplete = (status) => {
  alert('批量质控完成！');
  console.log('最终结果:', status);
};

// 启动任务
document.getElementById('startBtn').onclick = async () => {
  const result = await qcManager.start({
    periodType: 'month',
    year: 2023,
    month: 1
  });
  
  if (result.success) {
    console.log('任务已启动:', result.data);
  } else {
    alert('启动失败: ' + result.message);
  }
};
```

---

## API详细说明

### 1. 启动批量质控（已改为异步）

**接口**: `POST /api/qc/check/batch`

**请求参数**:
```json
{
  "periodType": "month",  // year/quarter/month
  "year": 2023,
  "quarter": 1,           // 可选
  "month": 1              // 可选
}
```

**响应（立即返回）**:
```json
{
  "code": 200,
  "message": "批量质控完成",
  "data": {
    "batchKey": "2023_M1",        // ⭐ 重要：用于后续查询进度
    "periodType": "month",
    "year": 2023,
    "month": 1,
    "caseCount": 94,              // 病案总数
    "totalDefectCount": 0,
    "avgDefect": 0.0,
    "avgScore": 100.0,
    "status": "processing",       // 状态：processing
    "progress": 0,                // 进度：0%
    "startTime": "2026-01-16T16:31:54",
    "endTime": null,
    "elapsedSeconds": 0
  }
}
```

**⚠️ 重要变化**:
- 接口**立即返回**（<1秒），不再等待任务完成
- 返回 `batchKey`，用于后续查询进度
- `status` 为 `processing`，表示正在处理

---

### 2. 查询批量任务进度（新增）

**接口**: `GET /api/qc/batch/status/{batchKey}`

**路径参数**:
- `batchKey`: 从启动接口返回的批次键

**响应（进行中）**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "batchKey": "2023_M1",
    "periodType": "month",
    "year": 2023,
    "month": 1,
    "caseCount": 50,              // 已完成50条
    "totalDefectCount": 150,
    "avgDefect": 3.0,
    "avgScore": 88.5,
    "status": "processing",       // 正在处理
    "progress": 53,               // 进度53%
    "startTime": "2026-01-16T16:31:54",
    "endTime": null,
    "elapsedSeconds": 45          // 已执行45秒
  }
}
```

**响应（已完成）**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "batchKey": "2023_M1",
    "caseCount": 94,              // 全部完成
    "totalDefectCount": 276,
    "avgDefect": 2.94,
    "avgScore": 88.26,
    "status": "completed",        // ⭐ 已完成
    "progress": 100,              // 100%
    "startTime": "2026-01-16T16:31:54",
    "endTime": "2026-01-16T16:32:39",
    "elapsedSeconds": 45          // 总耗时45秒
  }
}
```

---

## 前端调整清单

### ✅ 必须调整
1. **启动任务后不再等待完成**
   - 获取 `batchKey`
   - 立即显示"任务已启动"

2. **实现轮询机制**
   - 使用 `setInterval` 定时查询进度
   - 建议间隔：2-5秒

3. **更新UI显示**
   - 显示进度条（`progress`）
   - 显示已完成数（`caseCount`）
   - 显示已执行时间（`elapsedSeconds`）

4. **处理完成状态**
   - 检查 `status === 'completed'`
   - 停止轮询
   - 显示完成提示

### 📋 建议调整
1. **添加超时处理**
   - 设置最大轮询时间（如10分钟）
   - 超时后提示用户

2. **错误处理**
   - 检查 `status === 'failed'`
   - 网络错误重试机制

3. **用户体验优化**
   - 显示预计剩余时间
   - 允许用户取消任务
   - 任务完成后播放提示音

---

## 轮询间隔建议

| 病案数量 | 建议间隔 | 预计完成时间 |
|---------|---------|-------------|
| <100条 | 2秒 | <10秒 |
| 100-1000条 | 3秒 | <2分钟 |
| 1000-10000条 | 5秒 | <10分钟 |
| >10000条 | 5-10秒 | >10分钟 |

---

## 常见问题

### Q1: 为什么要改成异步？
**A**: 大批量数据（如6000+条）处理时间较长，同步方式会导致HTTP请求超时。异步方式可以立即返回，避免超时问题。

### Q2: 如何知道任务完成？
**A**: 轮询查询 `status` 字段，当 `status === 'completed'` 时表示完成。

### Q3: 轮询会不会影响性能？
**A**: 不会。查询进度接口非常轻量，只是读取数据库中的一条记录。建议间隔2-5秒。

### Q4: 如果用户刷新页面怎么办？
**A**: 可以将 `batchKey` 保存到 `localStorage`，页面加载时检查是否有未完成的任务。

### Q5: 多个用户同时启动任务会冲突吗？
**A**: 不会。每个时间范围有独立的 `batchKey`（如 `2023_M1`），不同时间范围互不影响。

---

## 测试建议

### 1. 小批量测试
```javascript
// 测试94条数据（2023年1月）
await qcManager.start({
  periodType: 'month',
  year: 2023,
  month: 1
});
// 预计10秒内完成
```

### 2. 大批量测试
```javascript
// 测试6095条数据（2020年1月）
await qcManager.start({
  periodType: 'month',
  year: 2020,
  month: 1
});
// 预计8-10分钟完成
```

---

## 相关文档

- `BATCH_PROGRESS_API.md` - 完整API文档
- `PERFORMANCE_OPTIMIZATION.md` - 性能优化说明
- `test_batch_progress.py` - Python测试示例

---

**文档版本**: 1.0  
**更新时间**: 2026-01-16  
**适用版本**: 2.0.1+
