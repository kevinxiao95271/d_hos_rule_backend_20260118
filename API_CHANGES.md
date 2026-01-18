# API变更说明

## 版本：2.0.1
## 日期：2026-01-16

---

## ⚠️ 重要变更：批量质控改为异步执行

### 变更原因
大批量数据处理时间较长，同步方式会导致HTTP请求超时。

### 影响接口
- `POST /api/qc/check/batch` - 批量质控接口

---

## 变更详情

### 之前（同步）
```
POST /api/qc/check/batch
↓
等待处理完成（可能超时）
↓
返回完整结果
```

**问题**:
- 大批量数据会超时
- 前端长时间等待
- 用户体验差

---

### 现在（异步）
```
POST /api/qc/check/batch
↓
立即返回（<1秒）
↓
后台异步处理
↓
前端轮询查询进度
GET /api/qc/batch/status/{batchKey}
```

**优势**:
- ✅ 不会超时
- ✅ 立即响应
- ✅ 实时进度
- ✅ 更好的用户体验

---

## 前端调整要点

### 1. 启动任务
```javascript
// 调用启动接口
const response = await fetch('/api/qc/check/batch', {
  method: 'POST',
  body: JSON.stringify({ periodType: 'month', year: 2023, month: 1 })
});

const { data } = await response.json();
const batchKey = data.batchKey;  // ⭐ 保存批次键
```

### 2. 轮询进度
```javascript
// 每2秒查询一次进度
const timer = setInterval(async () => {
  const response = await fetch(`/api/qc/batch/status/${batchKey}`);
  const { data: status } = await response.json();
  
  // 更新UI
  updateProgress(status.progress);
  updateStats(status);
  
  // 检查是否完成
  if (status.status === 'completed') {
    clearInterval(timer);
    showSuccess();
  }
}, 2000);
```

### 3. 关键字段
| 字段 | 说明 | 示例 |
|------|------|------|
| `batchKey` | 批次键，用于查询进度 | "2023_M1" |
| `status` | 任务状态 | "processing" / "completed" / "failed" |
| `progress` | 进度百分比 | 0-100 |
| `caseCount` | 已完成病案数 | 50 |
| `elapsedSeconds` | 已执行时间（秒）| 45 |

---

## 完整示例

### React示例
```jsx
const [batchKey, setBatchKey] = useState(null);
const [status, setStatus] = useState(null);

// 启动任务
const start = async () => {
  const res = await fetch('/api/qc/check/batch', {
    method: 'POST',
    body: JSON.stringify({ periodType: 'month', year: 2023, month: 1 })
  });
  const { data } = await res.json();
  setBatchKey(data.batchKey);
};

// 轮询进度
useEffect(() => {
  if (!batchKey) return;
  
  const timer = setInterval(async () => {
    const res = await fetch(`/api/qc/batch/status/${batchKey}`);
    const { data } = await res.json();
    setStatus(data);
    
    if (data.status === 'completed') {
      clearInterval(timer);
    }
  }, 2000);
  
  return () => clearInterval(timer);
}, [batchKey]);
```

---

## 其他接口（无变化）

以下接口保持不变：
- ✅ `POST /api/qc/check/single` - 单个病案质控
- ✅ `GET /api/qc/rules` - 获取规则列表
- ✅ `POST /api/qc/rules/test` - 规则试运行
- ✅ `GET /api/qc/result/case` - 获取病案结果
- ✅ 所有字典查询接口
- ✅ 所有规则管理接口

---

## 迁移检查清单

### 前端开发
- [ ] 修改批量质控启动逻辑
- [ ] 实现进度轮询机制
- [ ] 更新UI显示进度
- [ ] 处理完成/失败状态
- [ ] 添加超时处理
- [ ] 测试小批量数据（<100条）
- [ ] 测试大批量数据（>1000条）

### 测试
- [ ] 测试任务启动
- [ ] 测试进度查询
- [ ] 测试任务完成
- [ ] 测试网络异常
- [ ] 测试页面刷新
- [ ] 测试并发任务

---

## 技术支持

### 文档
- `FRONTEND_INTEGRATION_GUIDE.md` - 详细对接指南
- `BATCH_PROGRESS_API.md` - API完整文档
- `PERFORMANCE_OPTIMIZATION.md` - 性能优化说明

### 测试脚本
- `test_batch_progress.py` - Python测试示例
- `test_optimized_performance.py` - 性能测试

### 联系方式
如有问题，请查看相关文档或联系后端开发团队。

---

**变更版本**: 2.0.1  
**发布日期**: 2026-01-16  
**影响范围**: 批量质控功能  
**兼容性**: 向后不兼容（需要前端调整）
