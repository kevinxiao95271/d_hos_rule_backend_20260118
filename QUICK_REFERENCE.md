# 医疗病案质控系统 - 快速参考

## 🌐 访问地址

### Swagger在线文档
```
http://localhost:4101/swagger-ui/index.html
```
**说明**: 在浏览器中打开，可以在线测试所有API

### API基础地址
```
http://localhost:4101/api/qc
```

---

## 📋 19个核心API接口

### 质控管理 (7个)

#### 1️⃣ 获取所有规则
```bash
GET /api/qc/rules
```
**示例**:
```bash
curl http://localhost:4101/api/qc/rules
```

#### 2️⃣ 单个病案质控
```bash
POST /api/qc/check/single?a48=19079841&a49=1
```
**参数说明**:
- a48: 病案号
- a49: 住院次数

**示例**:
```bash
curl -X POST "http://localhost:4101/api/qc/check/single?a48=19079841&a49=1"
```

#### 3️⃣ 批量质控
```bash
POST /api/qc/check/batch
Content-Type: application/json
Body: {"periodType":"month","year":2020,"month":1}
```
**示例**:
```bash
curl -X POST "http://localhost:4101/api/qc/check/batch" \
  -H "Content-Type: application/json" \
  -d '{"periodType":"month","year":2020,"month":1}'
```

#### 4️⃣ 获取质控结果
```bash
GET /api/qc/result/{recordId}
```

#### 5️⃣ 获取统计数据
```bash
POST /api/qc/stats
```

#### 6️⃣ 获取字段列表
```bash
GET /api/qc/fields
```

#### 7️⃣ 测试规则
```bash
POST /api/qc/test-rule
```

### 规则管理 (6个)

#### 8️⃣ 搜索规则
```bash
GET /api/qc/rules/search?status=active&fieldCode=A18x01&keyword=新生儿
```
**参数说明**:
- status: 规则状态 (draft/active)
- fieldCode: 字段代码
- keyword: 关键词

**示例**:
```bash
curl "http://localhost:4101/api/qc/rules/search?keyword=新生儿"
```

#### 9️⃣ 创建规则
```bash
POST /api/qc/rules
Content-Type: application/json
```

#### 🔟 更新规则
```bash
PUT /api/qc/rules/{id}
Content-Type: application/json
```

#### 1️⃣1️⃣ 删除规则
```bash
DELETE /api/qc/rules/{id}
```

#### 1️⃣2️⃣ 更新规则状态
```bash
PUT /api/qc/rules/{id}/status?status=active
```

#### 1️⃣3️⃣ 测试规则
```bash
POST /api/qc/rules/{id}/test
Content-Type: application/json
Body: {"periodType":"month","year":2020,"month":1,"limit":10}
```

### 字典管理 (6个)

#### 1️⃣4️⃣ 查询字典数据
```bash
POST /api/dict/query
Content-Type: application/json
Body: {"dictTypeCode":"RC001","keyword":""}
```
**示例**:
```bash
curl -X POST "http://localhost:4101/api/dict/query" \
  -H "Content-Type: application/json" \
  -d '{"dictTypeCode":"RC001"}'
```

#### 1️⃣5️⃣ 获取所有字典类型
```bash
GET /api/dict/types
```
**示例**:
```bash
curl http://localhost:4101/api/dict/types
```

#### 1️⃣6️⃣ 获取字典类型名称映射
```bash
GET /api/dict/type-names
```

#### 1️⃣7️⃣ 按类型获取字典
```bash
GET /api/dict/type/{dictTypeCode}
```
**示例**:
```bash
curl http://localhost:4101/api/dict/type/RC001
```

#### 1️⃣8️⃣ 搜索字段所在表
```bash
GET /api/dict/field/search?fieldCode=A48
```
**示例**:
```bash
curl "http://localhost:4101/api/dict/field/search?fieldCode=A48"
```

#### 1️⃣9️⃣ 验证字段值
```bash
POST /api/dict/validate
Content-Type: application/json
Body: {"dictTypeCode":"RC001","value":"1"}
```
**示例**:
```bash
curl -X POST "http://localhost:4101/api/dict/validate" \
  -H "Content-Type: application/json" \
  -d '{"dictTypeCode":"RC001","value":"1"}'
```

---

## 🚀 快速测试

### Python测试
```bash
# 质控API测试
python test_api_auto.py

# 字典API测试
python test_dict_api.py

# 规则管理测试
python test_rule_management.py
```

### Curl测试
```bash
test_curl.bat
```

---

## 📊 测试数据

### 可用的测试病案
- **A48=19079841, A49=1** (2020/1/2) - 得分88分，3个缺陷
- **A48=20004836, A49=1** (2020/1/27) - 得分92分，2个缺陷

### 可用的时间范围
- **2020年**: 6095条病案
- **2023年**: 99条病案
- **2020年1月**: 部分病案

---

## 💡 常用场景

### 场景1: 检查单个病案
```python
import requests

response = requests.post(
    "http://localhost:4101/api/qc/check/single",
    params={"a48": "19079841", "a49": "1"}
)
result = response.json()
print(f"得分: {result['data']['finalScore']}")
```

### 场景2: 批量质控2020年1月
```python
import requests

response = requests.post(
    "http://localhost:4101/api/qc/check/batch",
    json={"periodType": "month", "year": 2020, "month": 1}
)
result = response.json()
print(f"平均得分: {result['data']['avgScore']}")
```

### 场景3: 查看质控结果
```python
import requests

response = requests.get(
    "http://localhost:4101/api/qc/result/case",
    params={"a48": "19079841", "a49": "1"}
)
result = response.json()
for field, defects in result['data']['defectsByField'].items():
    print(f"{field}: {len(defects)}个缺陷")
```

---

## 🔧 服务管理

### 启动服务
```bash
java -jar target/qc-system-1.0.0.jar
```

### 检查服务状态
```bash
curl http://localhost:4101/api/qc/rules
```

### 查看日志
服务启动后，日志会输出到控制台

---

## 📖 详细文档

- **完整API文档**: API_EXAMPLES.md
- **字典API文档**: DICT_API_DOCUMENTATION.md
- **字典快速开始**: DICT_QUICK_START.md
- **规则管理API**: RULE_MANAGEMENT_API.md
- **部署指南**: DEPLOYMENT_GUIDE.md
- **测试报告**: TEST_REPORT.md
- **项目说明**: README.md
- **文档索引**: INDEX.md

---

## ⚡ 一分钟快速开始

```bash
# 1. 启动服务
java -jar target/qc-system-1.0.0.jar

# 2. 打开浏览器访问Swagger
http://localhost:4101/swagger-ui/index.html

# 3. 或使用curl测试
curl http://localhost:4101/api/qc/rules

# 4. 或运行Python测试
python test_api_auto.py
```

---

**服务端口**: 4101  
**Swagger地址**: http://localhost:4101/swagger-ui/index.html  
**最后更新**: 2026-01-16
