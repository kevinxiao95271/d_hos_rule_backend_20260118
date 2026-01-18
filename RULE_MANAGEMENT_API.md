# 规则管理API文档

## 概述

规则管理功能支持规则的查询、更新、状态管理和试运行。规则有两种状态：
- **draft**: 未完善（草稿状态）
- **active**: 已完善（正式状态，参与质控）

## API接口列表

### 1. 获取所有规则

**接口**: `GET /api/qc/rules`

**说明**: 获取所有规则，包括draft和active状态

**请求示例**:
```bash
curl http://localhost:4101/api/qc/rules
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "ruleCode": "A18x03_value_check",
      "fieldName": "新生儿出生体重(克)3",
      "fieldCode": "A18x03",
      "tableName": "d_mr",
      "ruleType": "value_check",
      "deductScore": -4.0,
      "description": "error16：产妇诊断编码中含有Z37.5，Z37.6编码时，必须填写新生儿出生体重3",
      "status": "active"
    }
  ]
}
```

---

### 2. 按状态获取规则

**接口**: `GET /api/qc/rules/status/{status}`

**参数**:
- `status` (路径参数): draft 或 active

**说明**: 
- `draft`: 获取未完善的规则
- `active`: 获取已完善的规则（参与质控）

**请求示例**:
```bash
# 获取已完善规则
curl http://localhost:4101/api/qc/rules/status/active

# 获取未完善规则
curl http://localhost:4101/api/qc/rules/status/draft
```

**Python示例**:
```python
import requests

# 获取已完善规则
response = requests.get("http://localhost:4101/api/qc/rules/status/active")
active_rules = response.json()['data']
print(f"已完善规则数: {len(active_rules)}")

# 获取未完善规则
response = requests.get("http://localhost:4101/api/qc/rules/status/draft")
draft_rules = response.json()['data']
print(f"未完善规则数: {len(draft_rules)}")
```

---

### 3. 获取规则详情

**接口**: `GET /api/qc/rules/{id}`

**参数**:
- `id` (路径参数): 规则ID

**请求示例**:
```bash
curl http://localhost:4101/api/qc/rules/1
```

**Python示例**:
```python
import requests

response = requests.get("http://localhost:4101/api/qc/rules/1")
rule = response.json()['data']
print(f"规则编码: {rule['ruleCode']}")
print(f"状态: {rule['status']}")
print(f"描述: {rule['description']}")
```

---

### 4. 搜索规则（支持状态筛选）

**接口**: `GET /api/qc/rules/search`

**参数**:
- `status` (可选): draft 或 active
- `fieldCode` (可选): 字段编码
- `keyword` (可选): 关键词

**请求示例**:
```bash
# 搜索已完善规则中包含"新生儿"的规则
curl "http://localhost:4101/api/qc/rules/search?status=active&keyword=新生儿"

# 搜索未完善规则
curl "http://localhost:4101/api/qc/rules/search?status=draft"

# 搜索特定字段的规则
curl "http://localhost:4101/api/qc/rules/search?fieldCode=A18x01"

# 组合搜索
curl "http://localhost:4101/api/qc/rules/search?status=active&fieldCode=A18x01&keyword=体重"
```

**Python示例**:
```python
import requests

# 搜索已完善规则
params = {
    "status": "active",
    "keyword": "新生儿"
}
response = requests.get("http://localhost:4101/api/qc/rules/search", params=params)
rules = response.json()['data']
print(f"搜索结果: {len(rules)}条")
```

---

### 5. 更新规则

**接口**: `PUT /api/qc/rules`

**请求体**:
```json
{
  "id": 1,
  "ruleCode": "A18x03_value_check",
  "fieldName": "新生儿出生体重(克)3",
  "fieldCode": "A18x03",
  "tableName": "d_mr",
  "ruleType": "value_check",
  "deductScore": -4.0,
  "description": "更新后的描述",
  "status": "active",
  "involvedTables": "d_mr",
  "involvedFields": "A18x03,C06x01C"
}
```

**请求示例**:
```bash
curl -X PUT "http://localhost:4101/api/qc/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "fieldName": "新生儿出生体重(克)3",
    "fieldCode": "A18x03",
    "tableName": "d_mr",
    "ruleType": "value_check",
    "deductScore": -4.0,
    "description": "更新后的描述",
    "status": "active"
  }'
```

**Python示例**:
```python
import requests

data = {
    "id": 1,
    "fieldName": "新生儿出生体重(克)3",
    "fieldCode": "A18x03",
    "tableName": "d_mr",
    "ruleType": "value_check",
    "deductScore": -4.0,
    "description": "更新后的描述",
    "status": "active"
}
response = requests.put("http://localhost:4101/api/qc/rules", json=data)
print(response.json())
```

---

### 6. 更新规则状态

**接口**: `PUT /api/qc/rules/{id}/status`

**参数**:
- `id` (路径参数): 规则ID
- `status` (查询参数): draft 或 active

**说明**: 
- 将规则从draft改为active：规则完善后，测试通过，可以参与质控
- 将规则从active改为draft：规则需要修改，暂时不参与质控

**请求示例**:
```bash
# 将规则1设置为已完善状态
curl -X PUT "http://localhost:4101/api/qc/rules/1/status?status=active"

# 将规则1设置为未完善状态
curl -X PUT "http://localhost:4101/api/qc/rules/1/status?status=draft"
```

**Python示例**:
```python
import requests

# 将规则设置为已完善
response = requests.put(
    "http://localhost:4101/api/qc/rules/1/status",
    params={"status": "active"}
)
print(response.json()['message'])

# 将规则设置为未完善
response = requests.put(
    "http://localhost:4101/api/qc/rules/1/status",
    params={"status": "draft"}
)
print(response.json()['message'])
```

---

### 7. 规则试运行

**接口**: `POST /api/qc/rules/test`

**说明**: 在不影响正式质控的情况下，测试规则的执行效果

**请求体**:
```json
{
  "ruleId": 3,
  "a48": "19079841",
  "a49": "1",
  "limit": 10
}
```

**参数说明**:
- `ruleId` (必填): 要测试的规则ID
- `a48` (可选): 测试单个病案时使用
- `a49` (可选): 测试单个病案时使用
- `year` (可选): 测试批量数据时使用
- `month` (可选): 测试批量数据时使用
- `limit` (可选): 返回的违规明细数量限制，默认10

**场景1: 测试单个病案**
```bash
curl -X POST "http://localhost:4101/api/qc/rules/test" \
  -H "Content-Type: application/json" \
  -d '{
    "ruleId": 3,
    "a48": "19079841",
    "a49": "1",
    "limit": 5
  }'
```

**场景2: 测试批量数据**
```bash
curl -X POST "http://localhost:4101/api/qc/rules/test" \
  -H "Content-Type: application/json" \
  -d '{
    "ruleId": 3,
    "year": 2020,
    "month": 1,
    "limit": 10
  }'
```

**Python示例**:
```python
import requests

# 测试单个病案
test_request = {
    "ruleId": 3,
    "a48": "19079841",
    "a49": "1",
    "limit": 5
}
response = requests.post("http://localhost:4101/api/qc/rules/test", json=test_request)
result = response.json()['data']

print(f"规则编码: {result['ruleCode']}")
print(f"测试记录数: {result['totalRecords']}")
print(f"违规数量: {result['violationCount']}")
print(f"违规率: {result['violationRate']:.2f}%")

print("\n违规明细:")
for v in result['violations']:
    print(f"  病案: {v['mrKey']}")
    print(f"  字段: {v['fieldCode']}")
    print(f"  实际值: {v['actualValue']}")
    print(f"  预期值: {v['expectedValue']}")
    print(f"  原因: {v['reason']}")
    print()
```

**响应示例**:
```json
{
  "code": 200,
  "message": "试运行完成",
  "data": {
    "ruleId": 3,
    "ruleCode": "A18x01_range_check",
    "description": "新生儿出生体重范围：100克-9999克，需为整数且精确到10g",
    "totalRecords": 1,
    "violationCount": 1,
    "violationRate": 100.0,
    "violations": [
      {
        "mrKey": "19079841_1",
        "a48": "19079841",
        "a49": "1",
        "fieldCode": "A18x01",
        "actualValue": "0",
        "expectedValue": "100.0-9999.0",
        "reason": "新生儿出生体重范围：100克-9999克，需为整数且精确到10g"
      }
    ]
  }
}
```

---

## 规则管理工作流程

### 1. 创建新规则（草稿状态）
```sql
INSERT INTO kiro_qc_rule 
(rule_code, field_name, field_code, table_name, rule_type, deduct_score, description, status)
VALUES 
('NEW_RULE_001', '字段名称', 'FIELD_CODE', 'd_mr', 'range_check', -4, '规则描述', 'draft');
```

### 2. 查看未完善规则
```bash
curl http://localhost:4101/api/qc/rules/status/draft
```

### 3. 试运行规则
```bash
curl -X POST "http://localhost:4101/api/qc/rules/test" \
  -H "Content-Type: application/json" \
  -d '{
    "ruleId": 7,
    "year": 2020,
    "month": 1,
    "limit": 10
  }'
```

### 4. 根据试运行结果修改规则
```bash
curl -X PUT "http://localhost:4101/api/qc/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 7,
    "description": "修改后的描述",
    ...
  }'
```

### 5. 再次试运行验证
重复步骤3

### 6. 确认无误后，将规则设置为已完善
```bash
curl -X PUT "http://localhost:4101/api/qc/rules/7/status?status=active"
```

### 7. 规则开始参与正式质控
只有status为active的规则才会在质控时被应用

---

## 注意事项

1. **规则状态**:
   - draft: 不参与质控，可以随意修改和测试
   - active: 参与质控，修改需谨慎

2. **试运行**:
   - 试运行不会保存结果到数据库
   - 可以安全地测试规则效果
   - 建议在将规则设置为active前进行充分测试

3. **规则修改**:
   - 修改active状态的规则会影响后续质控
   - 建议先改为draft，修改并测试后再改回active

4. **违规率**:
   - 违规率 = 违规数量 / 测试记录数 × 100%
   - 可以用来评估规则的严格程度

---

## 完整测试脚本

```python
import requests

BASE_URL = "http://localhost:4101/api/qc"

# 1. 获取所有未完善规则
response = requests.get(f"{BASE_URL}/rules/status/draft")
draft_rules = response.json()['data']
print(f"未完善规则: {len(draft_rules)}条")

# 2. 对每个未完善规则进行试运行
for rule in draft_rules:
    print(f"\n测试规则: {rule['ruleCode']}")
    
    test_request = {
        "ruleId": rule['id'],
        "year": 2020,
        "month": 1,
        "limit": 5
    }
    
    response = requests.post(f"{BASE_URL}/rules/test", json=test_request)
    result = response.json()['data']
    
    print(f"  测试记录数: {result['totalRecords']}")
    print(f"  违规数量: {result['violationCount']}")
    print(f"  违规率: {result['violationRate']:.2f}%")
    
    # 3. 如果测试通过，将规则设置为已完善
    if result['violationRate'] > 0:  # 根据实际情况调整条件
        response = requests.put(
            f"{BASE_URL}/rules/{rule['id']}/status",
            params={"status": "active"}
        )
        print(f"  ✓ 规则已设置为已完善")
```

---

**最后更新**: 2026-01-16
