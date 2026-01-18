# 规则列表页面展示指南

## 数据字段说明

### 规则完整性字段

每条规则包含以下关键字段用于展示：

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `id` | Long | 规则ID | 7 |
| `ruleCode` | String | 规则编码 | RULE_A02_RC002 |
| `fieldCode` | String | 字段编码 | A02 |
| `fieldName` | String | 字段名称 | 婚姻状况 |
| `ruleType` | String | 规则类型 | value_check |
| `status` | String | 规则状态 | active/draft |
| `deductScore` | BigDecimal | 扣分 | 1.0 |
| `description` | String | 规则描述 | 婚姻状况必须在RC002字典范围内 |
| **`sourceTables`** | String | **源数据表** | d_mr |
| **`dictTypes`** | String | **值域数据集** | RC002 |
| `canonicalExpr` | String | 规范表达式 | A02 IN RC002 |

## API端点

### 规则搜索API

```
GET /api/qc/rules/search
```

**请求参数**:
- `status` (可选): 规则状态 (draft/active)
- `fieldCode` (可选): 字段编码
- `keyword` (可选): 关键词搜索

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 7,
      "ruleCode": "RULE_A02_RC002",
      "fieldCode": "A02",
      "fieldName": "婚姻状况",
      "ruleType": "value_check",
      "status": "active",
      "deductScore": 1.0,
      "description": "婚姻状况必须在RC002字典范围内",
      "sourceTables": "d_mr",
      "dictTypes": "RC002",
      "canonicalExpr": "A02 IN RC002"
    },
    {
      "id": 12,
      "ruleCode": "RULE_C06x01C_RC013",
      "fieldCode": "C06x01C",
      "fieldName": "出院其他诊断编码1 字符",
      "ruleType": "value_check",
      "status": "draft",
      "deductScore": 1.0,
      "description": "出院其他诊断编码1 字符必须在RC013字典范围内",
      "sourceTables": "d_mr",
      "dictTypes": "RC013",
      "canonicalExpr": "C06x01C IN RC013"
    }
  ]
}
```

## 前端展示建议

### 1. 规则列表表格

建议的表格列：

| 列名 | 字段 | 宽度 | 说明 |
|------|------|------|------|
| 规则ID | id | 80px | 唯一标识 |
| 状态 | status | 80px | 徽章显示 |
| 字段编码 | fieldCode | 100px | - |
| 字段名称 | fieldName | 150px | - |
| 规则类型 | ruleType | 120px | - |
| **源数据表** | **sourceTables** | **150px** | **重点展示** |
| **值域数据集** | **dictTypes** | **120px** | **重点展示** |
| 扣分 | deductScore | 80px | - |
| 操作 | - | 150px | 编辑/删除/测试 |

### 2. 状态徽章

```jsx
// 根据status字段显示不同颜色的徽章
{status === 'active' ? (
  <Badge color="green">已完善</Badge>
) : (
  <Badge color="orange">未完善</Badge>
)}
```

### 3. 完整性指示器

根据字段完整性显示不同的图标：

```jsx
// 完整性判断
const isComplete = sourceTables && dictTypes;
const isPartial = !sourceTables && dictTypes;

{isComplete ? (
  <Tooltip title="规则完整：包含源数据表和值域数据集">
    <CheckCircleOutlined style={{ color: 'green' }} />
  </Tooltip>
) : isPartial ? (
  <Tooltip title="部分完整：仅包含值域数据集">
    <WarningOutlined style={{ color: 'orange' }} />
  </Tooltip>
) : (
  <Tooltip title="信息不完整">
    <CloseCircleOutlined style={{ color: 'red' }} />
  </Tooltip>
)}
```

### 4. 源数据表展示

```jsx
// 多个表用逗号分隔，可以用标签展示
{sourceTables ? (
  sourceTables.split(',').map(table => (
    <Tag key={table} color="blue">{table.trim()}</Tag>
  ))
) : (
  <span style={{ color: '#999' }}>未设置</span>
)}
```

### 5. 值域数据集展示

```jsx
// 多个字典用逗号分隔，可以用标签展示
{dictTypes ? (
  dictTypes.split(',').map(dict => (
    <Tag key={dict} color="purple">{dict.trim()}</Tag>
  ))
) : (
  <span style={{ color: '#999' }}>未设置</span>
)}
```

### 6. 详情弹窗

点击规则行时，显示详细信息：

```jsx
<Modal title="规则详情" visible={visible}>
  <Descriptions column={2}>
    <Descriptions.Item label="规则ID">{rule.id}</Descriptions.Item>
    <Descriptions.Item label="规则编码">{rule.ruleCode}</Descriptions.Item>
    <Descriptions.Item label="字段编码">{rule.fieldCode}</Descriptions.Item>
    <Descriptions.Item label="字段名称">{rule.fieldName}</Descriptions.Item>
    <Descriptions.Item label="规则类型">{rule.ruleType}</Descriptions.Item>
    <Descriptions.Item label="状态">
      <Badge status={rule.status === 'active' ? 'success' : 'warning'} 
             text={rule.status === 'active' ? '已完善' : '未完善'} />
    </Descriptions.Item>
    <Descriptions.Item label="扣分">{rule.deductScore}</Descriptions.Item>
    <Descriptions.Item label="源数据表" span={2}>
      {rule.sourceTables || '未设置'}
    </Descriptions.Item>
    <Descriptions.Item label="值域数据集" span={2}>
      {rule.dictTypes || '未设置'}
    </Descriptions.Item>
    <Descriptions.Item label="规则描述" span={2}>
      {rule.description}
    </Descriptions.Item>
    <Descriptions.Item label="规范表达式" span={2}>
      <code>{rule.canonicalExpr}</code>
    </Descriptions.Item>
  </Descriptions>
</Modal>
```

## 数据统计

### 当前规则统计（2026-01-16）

| 状态 | 总数 | 有源数据表 | 有值域数据集 | 完整度 |
|------|------|-----------|-------------|--------|
| **Active** | 52 | 46 (88.5%) | 45 (86.5%) | 86.5% |
| **Draft** | 167 | 167 (100%) | 167 (100%) | 100% |
| **总计** | 219 | 213 (97.3%) | 212 (96.8%) | 96.8% |

### 按值域数据集分类

| 字典类型 | 规则数量 | 说明 |
|---------|---------|------|
| RC013 | 208 | 麻醉方式 |
| RC002 | 1 | 婚姻状况 |
| RC019 | 1 | 离院方式 |
| RC030 | 1 | ABO血型 |
| RC011 | 1 | 病案质量 |

## 筛选和搜索

### 1. 按状态筛选

```jsx
<Select 
  placeholder="选择状态" 
  onChange={handleStatusChange}
  allowClear
>
  <Option value="active">已完善</Option>
  <Option value="draft">未完善</Option>
</Select>
```

### 2. 按完整性筛选

```jsx
<Select 
  placeholder="选择完整性" 
  onChange={handleCompletenessChange}
  allowClear
>
  <Option value="complete">完整（有源表+字典）</Option>
  <Option value="partial">部分（仅有字典）</Option>
  <Option value="incomplete">不完整</Option>
</Select>
```

### 3. 按字典类型筛选

```jsx
<Select 
  placeholder="选择字典类型" 
  onChange={handleDictTypeChange}
  allowClear
>
  <Option value="RC001">RC001 - 性别</Option>
  <Option value="RC002">RC002 - 婚姻状况</Option>
  <Option value="RC013">RC013 - 麻醉方式</Option>
  <Option value="RC019">RC019 - 离院方式</Option>
  {/* 更多字典类型... */}
</Select>
```

## 批量操作

### 1. 批量激活

将选中的draft规则批量改为active状态：

```jsx
<Button 
  type="primary" 
  onClick={handleBatchActivate}
  disabled={selectedRows.length === 0}
>
  批量激活 ({selectedRows.length})
</Button>
```

### 2. 批量补充信息

对于缺少源数据表或值域数据集的规则，提供批量补充功能：

```jsx
<Button 
  onClick={handleBatchComplete}
  disabled={incompleteRows.length === 0}
>
  批量补充信息 ({incompleteRows.length})
</Button>
```

## 导出功能

### 导出规则列表

```jsx
<Button icon={<DownloadOutlined />} onClick={handleExport}>
  导出规则列表
</Button>
```

导出的Excel应包含所有字段，特别是：
- 源数据表（sourceTables）
- 值域数据集（dictTypes）

## 规则编辑

### 编辑表单

编辑规则时，确保可以修改：

```jsx
<Form>
  <Form.Item label="字段编码" name="fieldCode">
    <Input />
  </Form.Item>
  <Form.Item label="字段名称" name="fieldName">
    <Input />
  </Form.Item>
  <Form.Item label="源数据表" name="sourceTables">
    <Select mode="tags" placeholder="选择或输入源数据表">
      <Option value="d_mr">d_mr</Option>
      <Option value="d_mr_other_1_20">d_mr_other_1_20</Option>
      <Option value="d_mr_other_21_40">d_mr_other_21_40</Option>
      <Option value="d_mr_other_f">d_mr_other_f</Option>
    </Select>
  </Form.Item>
  <Form.Item label="值域数据集" name="dictTypes">
    <Select mode="tags" placeholder="选择或输入字典类型">
      <Option value="RC001">RC001 - 性别</Option>
      <Option value="RC002">RC002 - 婚姻状况</Option>
      <Option value="RC013">RC013 - 麻醉方式</Option>
      {/* 更多字典类型... */}
    </Select>
  </Form.Item>
  <Form.Item label="规则描述" name="description">
    <TextArea rows={3} />
  </Form.Item>
  <Form.Item label="状态" name="status">
    <Radio.Group>
      <Radio value="draft">未完善</Radio>
      <Radio value="active">已完善</Radio>
    </Radio.Group>
  </Form.Item>
</Form>
```

## 提示信息

### 1. 未完善规则提示

对于status为draft的规则，显示提示：

```jsx
{status === 'draft' && (
  <Alert 
    message="此规则尚未完善" 
    description="请补充完整的源数据表和值域数据集信息后激活"
    type="warning" 
    showIcon 
  />
)}
```

### 2. 缺少字段提示

对于缺少sourceTables或dictTypes的规则：

```jsx
{!sourceTables && (
  <Tag color="red">缺少源数据表</Tag>
)}
{!dictTypes && (
  <Tag color="red">缺少值域数据集</Tag>
)}
```

## 测试验证

### 验证脚本

使用 `check_rule_fields.py` 验证数据完整性：

```bash
python check_rule_fields.py
```

### 验证API返回

使用 `test_rule_display.py` 测试API是否正确返回字段：

```bash
python test_rule_display.py
```

## 总结

1. ✅ 数据库中已包含 `source_tables` 和 `dict_types` 字段
2. ✅ API返回的RuleDTO已包含这两个字段
3. ✅ Active规则86.5%有完整信息
4. ✅ Draft规则100%有完整信息
5. ✅ 前端可以根据这些字段展示规则完整性
6. ✅ 支持按完整性筛选和批量操作

---

**文档创建时间**: 2026-01-16  
**数据统计时间**: 2026-01-16 14:06  
**规则总数**: 219条（52 active + 167 draft）
