# Dictionary and Field Search API Documentation

## Overview
The Dictionary API provides functionality to query dictionary data from the `sys_dict` table and search for fields across medical record tables. This is essential for rule validation and field mapping.

## Base URL
```
http://localhost:4101/api/dict
```

## Endpoints

### 1. Query Dictionary Data
Query dictionary entries by type code and optional keyword.

**Endpoint:** `POST /api/dict/query`

**Request Body:**
```json
{
  "dictTypeCode": "RC001",     // Single dictionary type code
  "keyword": "",                // Optional: search keyword
  "limit": 100                  // Optional: limit results
}
```

Or with multiple dictionary types:
```json
{
  "dictTypeCodes": ["RC001", "RC002"],  // Multiple dictionary type codes
  "keyword": "男",                       // Optional: search keyword
  "limit": 50                            // Optional: limit results
}
```

**Response:**
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

**Example - Query Gender Codes:**
```bash
curl -X POST http://localhost:4101/api/dict/query \
  -H "Content-Type: application/json" \
  -d '{"dictTypeCode":"RC001","keyword":""}'
```

**Example - Query Disease Codes with Keyword:**
```bash
curl -X POST http://localhost:4101/api/dict/query \
  -H "Content-Type: application/json" \
  -d '{"dictTypeCode":"RCJBBM","keyword":"肺炎"}'
```

---

### 2. Get All Dictionary Types
Retrieve a list of all available dictionary type codes.

**Endpoint:** `GET /api/dict/types`

**Response:**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    "RC001",
    "RC002",
    "RC003",
    "RC011",
    "RC013",
    "RCJBBM",
    "level4_operation_code_v2",
    "operation_dict_v3",
    "day_operation_code_2022",
    "microfracture_oper_code_v2",
    "operation_code_with_type"
  ]
}
```

**Example:**
```bash
curl http://localhost:4101/api/dict/types
```

---

### 3. Get Dictionary Type Names
Retrieve a mapping of dictionary type codes to their Chinese names.

**Endpoint:** `GET /api/dict/type-names`

**Response:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "RC001": "性别值域代码表",
    "RC002": "婚姻状况代码表",
    "RC003": "职业代码表",
    "RCJBBM": "疾病编码",
    "level4_operation_code_v2": "四级手术编码",
    "operation_dict_v3": "手术编码"
  }
}
```

**Example:**
```bash
curl http://localhost:4101/api/dict/type-names
```

---

### 4. Get Dictionary by Type
Retrieve all dictionary entries for a specific type code.

**Endpoint:** `GET /api/dict/type/{dictTypeCode}`

**Path Parameters:**
- `dictTypeCode` - The dictionary type code (e.g., "RC001", "RCJBBM")

**Response:**
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

**Example:**
```bash
curl http://localhost:4101/api/dict/type/RC001
```

---

### 5. Search Field in Tables
Search for a field name across all medical record tables (d_mr, d_mr_other_1_20, d_mr_other_21_40, d_mr_other_f).

**Endpoint:** `GET /api/dict/field/search`

**Query Parameters:**
- `fieldName` or `fieldCode` - The field name to search for (e.g., "A48", "A18x01")

**Response:**
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

**Example:**
```bash
curl "http://localhost:4101/api/dict/field/search?fieldCode=A48"
```

---

### 6. Validate Field Value
Validate if a value exists in a specific dictionary type.

**Endpoint:** `POST /api/dict/validate`

**Request Body:**
```json
{
  "dictTypeCode": "RC001",
  "value": "1"
}
```

**Response:**
```json
{
  "code": 200,
  "message": "success",
  "data": true
}
```

**Example:**
```bash
curl -X POST http://localhost:4101/api/dict/validate \
  -H "Content-Type: application/json" \
  -d '{"dictTypeCode":"RC001","value":"1"}'
```

---

## Dictionary Type Codes Reference

### Standard RC Codes
| Code | Name | Description |
|------|------|-------------|
| RC001 | 性别值域代码表 | Gender codes |
| RC002 | 婚姻状况代码表 | Marital status codes |
| RC003 | 职业代码表 | Occupation codes |
| RC011 | 病案质量代码表 | Medical record quality codes |
| RC013 | 麻醉方式代码表 | Anesthesia method codes |
| RC014 | 切口愈合等级代码表 | Incision healing level codes |
| RC016 | 死亡患者尸检代码表 | Deceased patient autopsy codes |
| RC019 | 离院方式代码表 | Discharge method codes |
| RC023 | 科别代码表 | Department codes |
| RC026 | 入院途径代码表 | Admission route codes |
| RC027 | 入院病情代码表 | Admission condition codes |
| RC028 | 出院31天内再住院计划代码表 | 31-day readmission plan codes |
| RC029 | 手术级别代码表 | Surgery level codes |
| RC030 | ABO血型代码表 | ABO blood type codes |
| RC031 | Rh血型代码表 | Rh blood type codes |
| RC032 | 医疗付费方式代码表 | Medical payment method codes |
| RC033 | 联系人关系代码表 | Contact relationship codes |
| RC035 | 民族表 | Ethnicity codes |
| RC036 | 省、自治区、直辖市表 | Province codes |
| RC037 | 有无药物过敏表 | Drug allergy codes |
| RC038 | 患者证件类别代码表 | Patient ID type codes |
| RC039 | 判断代码表 | Judgment codes |

### Medical Codes
| Code | Name | Description |
|------|------|-------------|
| RCJBBM | 疾病编码 | Disease codes (ICD-10) |
| level4_operation_code_v2 | 四级手术编码 | Level 4 surgery codes |
| operation_dict_v3 | 手术编码 | Surgery codes |
| microfracture_oper_code_v2 | 微创手术 | Minimally invasive surgery codes |
| day_operation_code_2022 | 日间手术 | Day surgery codes |
| operation_code_with_type | 手术类型 | Surgery type codes |

---

## Use Cases

### 1. Rule Creation - Field Validation
When creating a quality control rule, use the field search endpoint to verify that the field exists in the source tables:

```python
# Search for field A18x01
response = requests.get("http://localhost:4101/api/dict/field/search?fieldCode=A18x01")
if response.json()["data"]["foundInTables"]:
    print("Field found in:", [t["tableName"] for t in response.json()["data"]["foundInTables"]])
```

### 2. Rule Creation - Value Domain Validation
When creating a rule that checks against a dictionary, query the dictionary to show available values:

```python
# Get all gender codes
response = requests.post("http://localhost:4101/api/dict/query", 
                        json={"dictTypeCode": "RC001"})
gender_codes = response.json()["data"]
print("Valid gender codes:", [g["dictCode"] for g in gender_codes])
```

### 3. Rule Execution - Value Validation
During rule execution, validate field values against dictionaries:

```python
# Validate if "1" is a valid gender code
response = requests.post("http://localhost:4101/api/dict/validate",
                        json={"dictTypeCode": "RC001", "value": "1"})
is_valid = response.json()["data"]
print("Is valid:", is_valid)
```

---

## Integration with Quality Control Rules

The dictionary API is integrated with the quality control rule system:

1. **source_tables** field in `kiro_qc_rule` - Stores which tables the rule applies to
2. **dict_types** field in `kiro_qc_rule` - Stores which dictionary types are used for validation

Example rule with dictionary validation:
```json
{
  "fieldCode": "A01",
  "fieldName": "性别",
  "ruleType": "value_check",
  "ruleExpression": "A01 in ['0','1','2','9']",
  "errorMessage": "性别代码必须在RC001字典范围内",
  "score": -2,
  "status": "active",
  "sourceTables": "d_mr",
  "dictTypes": "RC001"
}
```

---

## Error Handling

All endpoints return a standard response format:

**Success Response:**
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

**Error Response:**
```json
{
  "code": 500,
  "message": "Error description",
  "data": null
}
```

Common error scenarios:
- Missing required parameters: Returns 400 Bad Request
- Database connection issues: Returns 500 Internal Server Error
- Invalid dictionary type code: Returns empty data array
- Field not found: Returns empty foundInTables array
