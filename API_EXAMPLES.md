# 医疗病案质控系统 - API使用范例

## Swagger文档地址

**在线文档**: http://localhost:4101/swagger-ui/index.html

**说明**: 
- 服务启动后，直接在浏览器中打开上述地址
- 可以在线测试所有API接口
- 支持参数填写和实时调用

---

## API基础信息

- **Base URL**: http://localhost:4101
- **API前缀**: /api/qc
- **Content-Type**: application/json
- **响应格式**: JSON

---

## API接口列表

### 1. 获取所有规则列表

**接口**: `GET /api/qc/rules`

**请求示例 (curl)**:
```bash
curl -X GET "http://localhost:4101/api/qc/rules"
```

**请求示例 (Python)**:
```python
import requests

response = requests.get("http://localhost:4101/api/qc/rules")
print(response.json())
```

**请求示例 (JavaScript)**:
```javascript
fetch('http://localhost:4101/api/qc/rules')
  .then(response => response.json())
  .then(data => console.log(data));
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

### 2. 搜索规则

**接口**: `GET /api/qc/rules/search`

**参数**:
- `fieldCode` (可选): 字段编码
- `keyword` (可选): 关键词

**请求示例 (curl)**:
```bash
# 按关键词搜索
curl -X GET "http://localhost:4101/api/qc/rules/search?keyword=新生儿"

# 按字段编码搜索
curl -X GET "http://localhost:4101/api/qc/rules/search?fieldCode=A18x01"

# 组合搜索
curl -X GET "http://localhost:4101/api/qc/rules/search?fieldCode=A18x01&keyword=体重"
```

**请求示例 (Python)**:
```python
import requests

# 按关键词搜索
params = {"keyword": "新生儿"}
response = requests.get("http://localhost:4101/api/qc/rules/search", params=params)
print(response.json())
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
      "ruleType": "value_check",
      "deductScore": -4.0,
      "description": "error16：产妇诊断编码中含有Z37.5，Z37.6编码时，必须填写新生儿出生体重3",
      "status": "active"
    }
  ]
}
```

---

### 3. 单个病案质控

**接口**: `POST /api/qc/check/single`

**参数**:
- `a48` (必填): 病案号
- `a49` (必填): 住院次数

**请求示例 (curl)**:
```bash
curl -X POST "http://localhost:4101/api/qc/check/single?a48=19079841&a49=1"
```

**请求示例 (Python)**:
```python
import requests

params = {
    "a48": "19079841",  # 病案号
    "a49": "1"          # 住院次数（第1次住院）
}
response = requests.post("http://localhost:4101/api/qc/check/single", params=params)
result = response.json()
print(f"最终得分: {result['data']['finalScore']}")
print(f"缺陷数: {result['data']['defectCount']}")
```

**请求示例 (JavaScript)**:
```javascript
fetch('http://localhost:4101/api/qc/check/single?a48=19079841&a49=1', {
  method: 'POST'
})
  .then(response => response.json())
  .then(data => {
    console.log('最终得分:', data.data.finalScore);
    console.log('缺陷数:', data.data.defectCount);
  });
```

**响应示例**:
```json
{
  "code": 200,
  "message": "质控完成",
  "data": {
    "mrKey": "19079841_1",
    "a48": "19079841",
    "a49": "1",
    "b15": "2020/1/2 9:00",
    "defectCount": 3,
    "totalDeduct": 12.0,
    "finalScore": 88.0,
    "defectsByField": {
      "A18x01": [
        {
          "fieldCode": "A18x01",
          "fieldName": "新生儿出生体重(克)",
          "ruleCode": "A18x01_range_check",
          "ruleDescription": "新生儿出生体重范围：100克-9999克，需为整数且精确到10g",
          "actualValue": "0",
          "expectedValue": "100.0-9999.0",
          "deductScore": -4.0
        }
      ]
    },
    "allDefects": [...]
  }
}
```

---

### 4. 批量质控

**接口**: `POST /api/qc/check/batch`

**请求体**:
```json
{
  "periodType": "month",  // year/quarter/month
  "year": 2020,
  "quarter": 1,           // 可选，periodType为quarter时必填
  "month": 1              // 可选，periodType为month时必填
}
```

**请求示例 (curl)**:
```bash
# 按月质控
curl -X POST "http://localhost:4101/api/qc/check/batch" \
  -H "Content-Type: application/json" \
  -d '{"periodType":"month","year":2020,"month":1}'

# 按季度质控
curl -X POST "http://localhost:4101/api/qc/check/batch" \
  -H "Content-Type: application/json" \
  -d '{"periodType":"quarter","year":2020,"quarter":1}'

# 按年质控
curl -X POST "http://localhost:4101/api/qc/check/batch" \
  -H "Content-Type: application/json" \
  -d '{"periodType":"year","year":2020}'
```

**请求示例 (Python)**:
```python
import requests

# 2020年1月批量质控
data = {
    "periodType": "month",
    "year": 2020,
    "month": 1
}
response = requests.post(
    "http://localhost:4101/api/qc/check/batch",
    json=data
)
result = response.json()
print(f"病案数量: {result['data']['caseCount']}")
print(f"平均得分: {result['data']['avgScore']}")
```

**请求示例 (JavaScript)**:
```javascript
// 2020年1月批量质控
fetch('http://localhost:4101/api/qc/check/batch', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    periodType: 'month',
    year: 2020,
    month: 1
  })
})
  .then(response => response.json())
  .then(data => {
    console.log('病案数量:', data.data.caseCount);
    console.log('平均得分:', data.data.avgScore);
  });
```

**响应示例**:
```json
{
  "code": 200,
  "message": "批量质控完成",
  "data": {
    "periodType": "month",
    "year": 2020,
    "quarter": null,
    "month": 1,
    "caseCount": 1,
    "totalDefectCount": 2,
    "avgDefect": 2.0,
    "avgScore": 92.0,
    "status": "completed",
    "progress": 100
  }
}
```

---

### 5. 获取单个病案质控结果

**接口**: `GET /api/qc/result/case`

**参数**:
- `a48` (必填): 病案号
- `a49` (必填): 住院次数

**请求示例 (curl)**:
```bash
curl -X GET "http://localhost:4101/api/qc/result/case?a48=19079841&a49=1"
```

**请求示例 (Python)**:
```python
import requests

params = {
    "a48": "19079841",  # 病案号
    "a49": "1"          # 住院次数
}
response = requests.get("http://localhost:4101/api/qc/result/case", params=params)
result = response.json()

# 打印缺陷明细
if result['code'] == 200:
    data = result['data']
    print(f"病案: {data['mrKey']}")
    print(f"得分: {data['finalScore']}")
    print(f"缺陷数: {data['defectCount']}")
    
    # 按字段分组的缺陷
    for field, defects in data['defectsByField'].items():
        print(f"\n字段 {field}:")
        for defect in defects:
            print(f"  - {defect['ruleDescription']}")
            print(f"    实际值: {defect['actualValue']}")
            print(f"    预期值: {defect['expectedValue']}")
```

**响应示例**: 同"单个病案质控"接口

---

### 6. 获取批量质控汇总

**接口**: `POST /api/qc/result/batch/summary`

**请求体**:
```json
{
  "periodType": "month",
  "year": 2020,
  "month": 1
}
```

**请求示例 (curl)**:
```bash
curl -X POST "http://localhost:4101/api/qc/result/batch/summary" \
  -H "Content-Type: application/json" \
  -d '{"periodType":"month","year":2020,"month":1}'
```

**请求示例 (Python)**:
```python
import requests

data = {
    "periodType": "month",
    "year": 2020,
    "month": 1
}
response = requests.post(
    "http://localhost:4101/api/qc/result/batch/summary",
    json=data
)
print(response.json())
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "periodType": "month",
    "year": 2020,
    "quarter": null,
    "month": 1,
    "caseCount": 1,
    "totalDefectCount": 2,
    "avgDefect": 2.0,
    "avgScore": 92.0,
    "status": "completed",
    "progress": 100
  }
}
```

---

### 7. 获取批量质控明细列表

**接口**: `POST /api/qc/result/batch/cases`

**请求体**:
```json
{
  "periodType": "month",
  "year": 2020,
  "month": 1
}
```

**请求示例 (curl)**:
```bash
curl -X POST "http://localhost:4101/api/qc/result/batch/cases" \
  -H "Content-Type: application/json" \
  -d '{"periodType":"month","year":2020,"month":1}'
```

**请求示例 (Python)**:
```python
import requests

data = {
    "periodType": "month",
    "year": 2020,
    "month": 1
}
response = requests.post(
    "http://localhost:4101/api/qc/result/batch/cases",
    json=data
)
result = response.json()

# 打印每个病案的结果
if result['code'] == 200:
    for case in result['data']:
        print(f"\n病案: {case['mrKey']}")
        print(f"  得分: {case['finalScore']}")
        print(f"  缺陷数: {case['defectCount']}")
        print(f"  按字段分组的缺陷:")
        for field, defects in case['defectsByField'].items():
            print(f"    {field}: {len(defects)}个缺陷")
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "mrKey": "20004836_1",
      "a48": "20004836",
      "a49": "1",
      "b15": "2020/1/27 10:00",
      "defectCount": 2,
      "totalDeduct": 8.0,
      "finalScore": 92.0,
      "defectsByField": {...},
      "allDefects": [...]
    }
  ]
}
```

---

## 完整测试脚本

### Python完整示例

```python
import requests
import json

BASE_URL = "http://localhost:4101/api/qc"

# 1. 获取所有规则
print("1. 获取所有规则")
response = requests.get(f"{BASE_URL}/rules")
print(f"规则数量: {len(response.json()['data'])}\n")

# 2. 搜索规则
print("2. 搜索规则")
response = requests.get(f"{BASE_URL}/rules/search", params={"keyword": "新生儿"})
print(f"搜索结果: {len(response.json()['data'])}条\n")

# 3. 单个病案质控
print("3. 单个病案质控")
response = requests.post(f"{BASE_URL}/check/single", params={"a48": "19079841", "a49": "1"})
result = response.json()['data']
print(f"病案: {result['mrKey']}")
print(f"得分: {result['finalScore']}")
print(f"缺陷数: {result['defectCount']}\n")

# 4. 批量质控
print("4. 批量质控 - 2020年1月")
data = {"periodType": "month", "year": 2020, "month": 1}
response = requests.post(f"{BASE_URL}/check/batch", json=data)
result = response.json()['data']
print(f"病案数量: {result['caseCount']}")
print(f"平均得分: {result['avgScore']}\n")

# 5. 获取批量汇总
print("5. 获取批量汇总")
response = requests.post(f"{BASE_URL}/result/batch/summary", json=data)
result = response.json()['data']
print(f"总缺陷数: {result['totalDefectCount']}")
print(f"平均缺陷: {result['avgDefect']}\n")

print("测试完成！")
```

---

## 错误处理

### 错误响应格式

```json
{
  "code": 500,
  "message": "错误信息",
  "data": null
}
```

### 常见错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 500 | 服务器内部错误 |
| 404 | 资源不存在 |

### 错误处理示例 (Python)

```python
import requests

try:
    response = requests.post(
        "http://localhost:4101/api/qc/check/single",
        params={"a48": "19079841", "a49": "1"}
    )
    result = response.json()
    
    if result['code'] == 200:
        print("质控成功:", result['data'])
    else:
        print("质控失败:", result['message'])
        
except requests.exceptions.ConnectionError:
    print("无法连接到服务器，请确保服务已启动")
except Exception as e:
    print(f"发生错误: {e}")
```

---

## 使用Postman测试

### 导入步骤

1. 打开Postman
2. 点击 Import
3. 选择 Link
4. 输入: http://localhost:4101/v3/api-docs
5. 点击 Continue 和 Import

### 测试步骤

1. 选择要测试的接口
2. 填写参数或请求体
3. 点击 Send
4. 查看响应结果

---

## 快速测试命令

```bash
# 测试服务是否启动
curl http://localhost:4101/api/qc/rules

# 测试单个病案质控
curl -X POST "http://localhost:4101/api/qc/check/single?a48=19079841&a49=1"

# 测试批量质控
curl -X POST "http://localhost:4101/api/qc/check/batch" \
  -H "Content-Type: application/json" \
  -d '{"periodType":"year","year":2020}'
```

---

**Swagger文档地址**: http://localhost:4101/swagger-ui/index.html

**服务端口**: 4101

**最后更新**: 2026-01-16


---

## 字典管理API (Dictionary Management)

### 1. 查询字典数据

**接口**: `POST /api/dict/query`

**请求示例 (curl)**:
```bash
# 查询性别代码
curl -X POST "http://localhost:4101/api/dict/query" \
  -H "Content-Type: application/json" \
  -d '{"dictTypeCode":"RC001","keyword":""}'

# 查询疾病编码（包含"肺炎"关键词）
curl -X POST "http://localhost:4101/api/dict/query" \
  -H "Content-Type: application/json" \
  -d '{"dictTypeCode":"RCJBBM","keyword":"肺炎","limit":10}'
```

**请求示例 (Python)**:
```python
import requests

# 查询性别代码
response = requests.post(
    "http://localhost:4101/api/dict/query",
    json={"dictTypeCode": "RC001", "keyword": ""}
)
print(response.json())

# 查询疾病编码
response = requests.post(
    "http://localhost:4101/api/dict/query",
    json={"dictTypeCode": "RCJBBM", "keyword": "肺炎", "limit": 10}
)
print(response.json())
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "dictId": 1661265059478806529,
      "dictCode": "0",
      "dictName": "0 - 未知的性别",
      "dictTypeCode": "RC001",
      "dictTypeName": "性别值域代码表"
    },
    {
      "dictId": 1661265061357854721,
      "dictCode": "1",
      "dictName": "1 - 男",
      "dictTypeCode": "RC001",
      "dictTypeName": "性别值域代码表"
    }
  ]
}
```

---

### 2. 获取所有字典类型

**接口**: `GET /api/dict/types`

**请求示例 (curl)**:
```bash
curl -X GET "http://localhost:4101/api/dict/types"
```

**请求示例 (Python)**:
```python
import requests

response = requests.get("http://localhost:4101/api/dict/types")
print(response.json())
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    "RC001",
    "RC002",
    "RC003",
    "RCJBBM",
    "level4_operation_code_v2",
    "operation_dict_v3"
  ]
}
```

---

### 3. 获取字典类型名称映射

**接口**: `GET /api/dict/type-names`

**请求示例 (curl)**:
```bash
curl -X GET "http://localhost:4101/api/dict/type-names"
```

**请求示例 (Python)**:
```python
import requests

response = requests.get("http://localhost:4101/api/dict/type-names")
print(response.json())
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "RC001": "性别值域代码表",
    "RC002": "婚姻状况代码表",
    "RCJBBM": "疾病编码",
    "level4_operation_code_v2": "四级手术编码"
  }
}
```

---

### 4. 按类型获取字典

**接口**: `GET /api/dict/type/{dictTypeCode}`

**请求示例 (curl)**:
```bash
curl -X GET "http://localhost:4101/api/dict/type/RC001"
```

**请求示例 (Python)**:
```python
import requests

response = requests.get("http://localhost:4101/api/dict/type/RC001")
print(response.json())
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "dictId": 1661265059478806529,
      "dictCode": "0",
      "dictName": "0 - 未知的性别",
      "dictTypeCode": "RC001",
      "dictTypeName": "性别值域代码表"
    }
  ]
}
```

---

### 5. 搜索字段所在表

**接口**: `GET /api/dict/field/search`

**请求示例 (curl)**:
```bash
# 搜索A48字段
curl -X GET "http://localhost:4101/api/dict/field/search?fieldCode=A48"

# 搜索A18x01字段
curl -X GET "http://localhost:4101/api/dict/field/search?fieldName=A18x01"
```

**请求示例 (Python)**:
```python
import requests

# 搜索A48字段
response = requests.get(
    "http://localhost:4101/api/dict/field/search",
    params={"fieldCode": "A48"}
)
print(response.json())

# 搜索A18x01字段
response = requests.get(
    "http://localhost:4101/api/dict/field/search",
    params={"fieldName": "A18x01"}
)
print(response.json())
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "fieldName": "A48",
    "foundInTables": [
      {
        "tableName": "d_mr",
        "columnName": "A48",
        "dataType": "varchar",
        "isNullable": false
      },
      {
        "tableName": "d_mr_other_1_20",
        "columnName": "A48",
        "dataType": "varchar",
        "isNullable": false
      },
      {
        "tableName": "d_mr_other_21_40",
        "columnName": "A48",
        "dataType": "varchar",
        "isNullable": false
      },
      {
        "tableName": "d_mr_other_f",
        "columnName": "A48",
        "dataType": "varchar",
        "isNullable": false
      }
    ]
  }
}
```

---

### 6. 验证字段值

**接口**: `POST /api/dict/validate`

**请求示例 (curl)**:
```bash
# 验证性别代码"1"是否有效
curl -X POST "http://localhost:4101/api/dict/validate" \
  -H "Content-Type: application/json" \
  -d '{"dictTypeCode":"RC001","value":"1"}'

# 验证性别代码"5"是否有效（无效值）
curl -X POST "http://localhost:4101/api/dict/validate" \
  -H "Content-Type: application/json" \
  -d '{"dictTypeCode":"RC001","value":"5"}'
```

**请求示例 (Python)**:
```python
import requests

# 验证有效值
response = requests.post(
    "http://localhost:4101/api/dict/validate",
    json={"dictTypeCode": "RC001", "value": "1"}
)
print(f"Is valid: {response.json()['data']}")  # True

# 验证无效值
response = requests.post(
    "http://localhost:4101/api/dict/validate",
    json={"dictTypeCode": "RC001", "value": "5"}
)
print(f"Is valid: {response.json()['data']}")  # False
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": true
}
```

---

## 字典类型代码参考

### 标准RC代码
- **RC001**: 性别值域代码表
- **RC002**: 婚姻状况代码表
- **RC003**: 职业代码表
- **RC011**: 病案质量代码表
- **RC013**: 麻醉方式代码表
- **RC014**: 切口愈合等级代码表
- **RC016**: 死亡患者尸检代码表
- **RC019**: 离院方式代码表
- **RC023**: 科别代码表
- **RC026**: 入院途径代码表
- **RC027**: 入院病情代码表
- **RC028**: 出院31天内再住院计划代码表
- **RC029**: 手术级别代码表
- **RC030**: ABO血型代码表
- **RC031**: Rh血型代码表
- **RC032**: 医疗付费方式代码表
- **RC033**: 联系人关系代码表
- **RC035**: 民族表
- **RC036**: 省、自治区、直辖市表
- **RC037**: 有无药物过敏表
- **RC038**: 患者证件类别代码表
- **RC039**: 判断代码表

### 医疗编码
- **RCJBBM**: 疾病编码 (ICD-10)
- **level4_operation_code_v2**: 四级手术编码
- **operation_dict_v3**: 手术编码
- **microfracture_oper_code_v2**: 微创手术
- **day_operation_code_2022**: 日间手术
- **operation_code_with_type**: 手术类型

---

## 完整测试脚本

查看 `test_dict_api.py` 文件获取完整的字典API测试脚本。

运行测试:
```bash
python test_dict_api.py
```
