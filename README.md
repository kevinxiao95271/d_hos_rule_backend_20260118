# 医疗病案质控系统

基于Spring Boot 2.7 + MyBatis的医疗病案质控规则引擎系统

## 🌐 在线文档

**Swagger API文档**: http://localhost:4101/swagger-ui/index.html

**快速参考**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**API使用范例**: [API_EXAMPLES.md](API_EXAMPLES.md)

## 功能特性

- ✅ 规则引擎：支持多种规则类型（必填检查、范围检查、交叉验证）
- ✅ 规则管理：规则增删改查、状态管理（草稿/正式）、规则测试
- ✅ 字典管理：28种字典类型查询、字段搜索、值域验证
- ✅ 单个病案质控：实时检查单个病案数据
- ✅ 批量质控：支持按年/季度/月批量检查
- ✅ 缺陷管理：详细记录每个缺陷，按字段分组展示
- ✅ 统计分析：自动计算平均缺陷、平均得分
- ✅ API文档：集成Swagger 3.0，19个API接口

## 技术栈

- Spring Boot 2.7.18
- MyBatis
- MySQL 8.0
- Swagger 3.0
- Lombok
- FastJSON

## 快速开始

### 1. 环境要求

- JDK 1.8+
- Maven 3.6+
- MySQL 8.0+

### 2. 数据库初始化

```bash
# 创建表结构
python create_tables.py

# 初始化规则数据
python init_rules.py
```

### 3. 配置数据库

编辑 `src/main/resources/application.yml`:

```yaml
spring:
  datasource:
    url: jdbc:mysql://your-host:port/database?useUnicode=true&characterEncoding=utf8
    username: your-username
    password: your-password
```

### 4. 编译运行

```bash
# 编译
mvn clean package -DskipTests

# 运行
java -jar target/qc-system-1.0.0.jar
```

服务将启动在 http://localhost:4101

### 5. 访问API文档

浏览器打开: http://localhost:4101/swagger-ui/index.html

## API接口

系统提供19个API接口，分为三大类：

### 质控管理 (7个接口)

#### 获取所有规则
```
GET /api/qc/rules
```

#### 单个病案质控
```
POST /api/qc/check/single?a48=19079841&a49=1
```

#### 批量质控
```
POST /api/qc/check/batch
Content-Type: application/json

{
  "periodType": "month",
  "year": 2020,
  "month": 1
}
```

支持的periodType:
- `year`: 按年
- `quarter`: 按季度
- `month`: 按月

#### 获取质控结果
```
GET /api/qc/result/{recordId}
```

#### 获取统计数据
```
POST /api/qc/stats
Content-Type: application/json

{
  "periodType": "year",
  "year": 2020
}
```

#### 获取字段列表
```
GET /api/qc/fields
```

#### 测试规则
```
POST /api/qc/test-rule
Content-Type: application/json

{
  "ruleExpression": "A18x01 >= 100 && A18x01 <= 9999",
  "testData": {"A18x01": "3500"}
}
```

### 规则管理 (6个接口)

#### 搜索规则
```
GET /api/qc/rules/search?status=active&fieldCode=A18x01&keyword=新生儿
```

参数：
- `status`: 规则状态 (draft/active)
- `fieldCode`: 字段代码
- `keyword`: 关键词搜索

#### 创建规则
```
POST /api/qc/rules
Content-Type: application/json

{
  "fieldCode": "A18x01",
  "fieldName": "新生儿出生体重",
  "ruleType": "range_check",
  "ruleExpression": "A18x01 >= 100 && A18x01 <= 9999",
  "errorMessage": "新生儿出生体重范围：100克-9999克",
  "score": -4,
  "status": "draft",
  "sourceTables": "d_mr",
  "dictTypes": ""
}
```

#### 更新规则
```
PUT /api/qc/rules/{id}
Content-Type: application/json

{
  "fieldName": "新生儿出生体重(克)",
  "ruleExpression": "A18x01 >= 100 && A18x01 <= 9999",
  "errorMessage": "新生儿出生体重范围：100克-9999克，需为整数且精确到10g",
  "score": -4,
  "sourceTables": "d_mr",
  "dictTypes": ""
}
```

#### 删除规则
```
DELETE /api/qc/rules/{id}
```

#### 更新规则状态
```
PUT /api/qc/rules/{id}/status?status=active
```

状态值：
- `draft`: 草稿（不参与质控）
- `active`: 正式（参与质控）

#### 测试规则
```
POST /api/qc/rules/{id}/test
Content-Type: application/json

{
  "periodType": "month",
  "year": 2020,
  "month": 1,
  "limit": 10
}
```

### 字典管理 (6个接口)

#### 查询字典数据
```
POST /api/dict/query
Content-Type: application/json

{
  "dictTypeCode": "RC001",
  "keyword": "",
  "limit": 100
}
```

或查询多个字典类型：
```json
{
  "dictTypeCodes": ["RC001", "RC002"],
  "keyword": "男"
}
```

#### 获取所有字典类型
```
GET /api/dict/types
```

返回28种字典类型代码列表

#### 获取字典类型名称映射
```
GET /api/dict/type-names
```

返回字典类型代码到中文名称的映射

#### 按类型获取字典
```
GET /api/dict/type/RC001
```

获取指定类型的所有字典条目

#### 搜索字段所在表
```
GET /api/dict/field/search?fieldCode=A48
```

或使用fieldName参数：
```
GET /api/dict/field/search?fieldName=A18x01
```

搜索字段在哪些表中存在（d_mr, d_mr_other_1_20, d_mr_other_21_40, d_mr_other_f）

#### 验证字段值
```
POST /api/dict/validate
Content-Type: application/json

{
  "dictTypeCode": "RC001",
  "value": "1"
}
```

验证值是否在指定字典中存在

## 测试

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

## 文档导航

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - 快速参考指南
- **[API_EXAMPLES.md](API_EXAMPLES.md)** - API使用范例（包含字典API）
- **[DICT_API_DOCUMENTATION.md](DICT_API_DOCUMENTATION.md)** - 字典API完整文档
- **[DICT_QUICK_START.md](DICT_QUICK_START.md)** - 字典API快速开始
- **[RULE_MANAGEMENT_API.md](RULE_MANAGEMENT_API.md)** - 规则管理API文档
- **[TEST_REPORT.md](TEST_REPORT.md)** - 测试报告
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - 部署指南
- **[INDEX.md](INDEX.md)** - 完整文档索引

## 项目结构

```
.
├── src/main/java/com/medical/qc/
│   ├── QcApplication.java          # 启动类
│   ├── common/
│   │   └── Result.java             # 统一返回结果
│   ├── config/
│   │   └── SwaggerConfig.java      # Swagger配置
│   ├── controller/
│   │   ├── QcController.java       # 质控控制器
│   │   └── DictController.java     # 字典控制器
│   ├── dto/                        # 数据传输对象
│   │   ├── RuleDTO.java            # 规则DTO
│   │   ├── RuleUpdateRequest.java  # 规则更新请求
│   │   ├── RuleTestRequest.java    # 规则测试请求
│   │   ├── DictQueryRequest.java   # 字典查询请求
│   │   ├── DictDTO.java            # 字典DTO
│   │   └── FieldSearchResult.java  # 字段搜索结果
│   ├── entity/                     # 实体类
│   │   └── KiroQcRule.java         # 规则实体
│   ├── mapper/                     # MyBatis Mapper
│   │   ├── QcRuleMapper.java       # 规则Mapper
│   │   ├── QcResultMapper.java     # 结果Mapper
│   │   ├── DictMapper.java         # 字典Mapper
│   │   └── FieldSearchMapper.java  # 字段搜索Mapper
│   └── service/                    # 业务逻辑
│       ├── QcService.java          # 质控服务
│       ├── RuleEngineService.java  # 规则引擎
│       └── DictService.java        # 字典服务
├── src/main/resources/
│   └── application.yml             # 配置文件
├── init_kiro_tables.sql            # 表结构SQL
├── init_rules.py                   # 规则初始化脚本
├── test_api_auto.py                # 质控API测试脚本
├── test_dict_api.py                # 字典API测试脚本
├── test_rule_management.py         # 规则管理测试脚本
├── TEST_REPORT.md                  # 测试报告
├── DICT_API_DOCUMENTATION.md       # 字典API文档
├── RULE_MANAGEMENT_API.md          # 规则管理API文档
└── README.md                       # 本文件
```

## 数据库表

系统使用6个kiro_前缀的表：

### kiro_qc_rule
规则表，存储所有质控规则

**新增字段**：
- `source_tables`: 源数据表（逗号分隔，如"d_mr,d_mr_other_1_20"）
- `dict_types`: 字典类型（逗号分隔，如"RC001,RCJBBM"）

### kiro_qc_case_result
病案质控结果表，存储每个病案的质控结果

### kiro_qc_defect_detail
缺陷明细表，存储每个缺陷的详细信息

### kiro_qc_batch_summary
批量质控汇总表，存储批量质控的统计信息

### kiro_field_mapping
字段映射表，存储字段与表的映射关系

### kiro_qc_run_context
运行上下文表，存储质控运行的上下文信息

## 字典类型

系统支持28种字典类型：

### 标准RC代码（22种）
- RC001: 性别值域代码表
- RC002: 婚姻状况代码表
- RC003: 职业代码表
- RC011: 病案质量代码表
- RC013: 麻醉方式代码表
- RC014: 切口愈合等级代码表
- RC016: 死亡患者尸检代码表
- RC019: 离院方式代码表
- RC023: 科别代码表
- RC026: 入院途径代码表
- RC027: 入院病情代码表
- RC028: 出院31天内再住院计划代码表
- RC029: 手术级别代码表
- RC030: ABO血型代码表
- RC031: Rh血型代码表
- RC032: 医疗付费方式代码表
- RC033: 联系人关系代码表
- RC035: 民族表
- RC036: 省、自治区、直辖市表
- RC037: 有无药物过敏表
- RC038: 患者证件类别代码表
- RC039: 判断代码表

### 医疗编码（6种）
- RCJBBM: 疾病编码（ICD-10）
- level4_operation_code_v2: 四级手术编码
- operation_dict_v3: 手术编码
- microfracture_oper_code_v2: 微创手术
- day_operation_code_2022: 日间手术
- operation_code_with_type: 手术类型

## 规则类型

### value_check
必填项检查，验证特定条件下字段是否必填

示例：产妇诊断编码中含有Z37.5时，必须填写新生儿出生体重

### cross_check_null
交叉验证必填，多个字段之间的关联验证

示例：产妇诊断编码中含有Z37.0/Z37.2/Z37.3时，必须填写新生儿出生体重

### range_check
范围检查，验证字段值是否在指定范围内

示例：新生儿出生体重范围100-9999克，需为整数且精确到10g

## 质控流程

1. **规则配置**：在kiro_qc_rule表中配置质控规则
2. **执行质控**：调用质控接口，系统自动应用所有active状态的规则
3. **记录缺陷**：将不符合规则的数据记录到kiro_qc_defect_detail表
4. **计算得分**：基础分100分，每个缺陷扣除相应分数
5. **保存结果**：将质控结果保存到kiro_qc_case_result表
6. **统计汇总**：批量质控时自动计算平均缺陷、平均得分等统计指标

## 扣分规则

- 每个规则都有deduct_score字段，表示违反该规则的扣分
- 一份病案满分100分
- 最终得分 = 100 - 总扣分（最低0分）
- 平均缺陷 = 总缺陷数 / 病案总数

## 测试结果

详见 [TEST_REPORT.md](TEST_REPORT.md)

### 测试案例

- ✅ 2020年1月批量质控：1条病案，平均得分92.0
- ✅ 2023年全年批量质控：1条病案，平均得分88.0
- ✅ 单个病案质控：成功识别3个缺陷，得分88.0

## 开发说明

### 添加新规则

1. 在kiro_qc_rule表中插入新规则
2. 如需自定义规则逻辑，在RuleEngineService中添加相应方法
3. 规则状态设置为active后自动生效

### 扩展规则类型

在RuleEngineService.applyRule方法中添加新的规则类型处理逻辑

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或联系开发团队
