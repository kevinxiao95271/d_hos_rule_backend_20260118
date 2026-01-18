# Dictionary API Quick Start Guide

## 🚀 Quick Access

**Swagger UI**: http://localhost:4101/swagger-ui/index.html  
**Base URL**: http://localhost:4101/api/dict

---

## 📋 Common Operations

### 1. Search for a Field
```bash
curl "http://localhost:4101/api/dict/field/search?fieldCode=A48"
```

### 2. Get Gender Codes
```bash
curl -X POST "http://localhost:4101/api/dict/query" \
  -H "Content-Type: application/json" \
  -d '{"dictTypeCode":"RC001"}'
```

### 3. Search Disease Codes
```bash
curl -X POST "http://localhost:4101/api/dict/query" \
  -H "Content-Type: application/json" \
  -d '{"dictTypeCode":"RCJBBM","keyword":"肺炎","limit":10}'
```

### 4. Validate a Value
```bash
curl -X POST "http://localhost:4101/api/dict/validate" \
  -H "Content-Type: application/json" \
  -d '{"dictTypeCode":"RC001","value":"1"}'
```

### 5. List All Dictionary Types
```bash
curl "http://localhost:4101/api/dict/types"
```

---

## 🐍 Python Examples

```python
import requests

BASE_URL = "http://localhost:4101/api/dict"

# Search for field
response = requests.get(f"{BASE_URL}/field/search", params={"fieldCode": "A48"})
print(response.json())

# Query dictionary
response = requests.post(f"{BASE_URL}/query", json={"dictTypeCode": "RC001"})
print(response.json())

# Validate value
response = requests.post(f"{BASE_URL}/validate", json={"dictTypeCode": "RC001", "value": "1"})
print(f"Valid: {response.json()['data']}")
```

---

## 📚 Dictionary Type Codes

### Most Common
- **RC001** - 性别 (Gender)
- **RC002** - 婚姻状况 (Marital Status)
- **RC019** - 离院方式 (Discharge Method)
- **RC030** - ABO血型 (Blood Type)
- **RCJBBM** - 疾病编码 (Disease Codes)
- **operation_dict_v3** - 手术编码 (Surgery Codes)

### Full List
See `DICT_API_DOCUMENTATION.md` for complete reference.

---

## 🧪 Test Script

Run the complete test suite:
```bash
python test_dict_api.py
```

---

## 📖 Full Documentation

- **DICT_API_DOCUMENTATION.md** - Complete API reference
- **API_EXAMPLES.md** - More examples
- **TASK3_COMPLETION_SUMMARY.md** - Implementation details
