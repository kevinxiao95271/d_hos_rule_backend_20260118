# 医疗病案质控系统 - 文件结构

## 项目文件清单

### 📁 根目录

```
testk001/
├── pom.xml                          # Maven项目配置文件
├── README.md                        # 项目说明文档
├── TEST_REPORT.md                   # 测试报告
├── SELF_TEST_RESULTS.md             # 自测结果文档
├── PROJECT_SUMMARY.md               # 项目总结
├── DEPLOYMENT_GUIDE.md              # 部署和使用指南
├── FILE_STRUCTURE.md                # 本文件
├── start.bat                        # Windows启动脚本
├── test_curl.bat                    # Curl测试脚本
├── init_kiro_tables.sql             # 数据库表结构SQL
├── init_tables.sql                  # 初始表结构SQL (已废弃)
├── init_rules.py                    # 规则初始化脚本
├── create_tables.py                 # 创建表脚本
├── test_db_connection.py            # 数据库连接测试
├── check_dict.py                    # 字典表检查脚本
├── check_other_tables.py            # 附属表检查脚本
├── test_api.py                      # API测试脚本(交互式)
└── test_api_auto.py                 # API自动化测试脚本
```

### 📁 源代码目录

```
src/main/java/com/medical/qc/
├── QcApplication.java               # Spring Boot启动类
│
├── common/
│   └── Result.java                  # 统一返回结果封装
│
├── config/
│   └── SwaggerConfig.java           # Swagger配置类
│
├── controller/
│   ├── QcController.java            # 质控REST API控制器
│   └── DictController.java          # 字典REST API控制器
│
├── dto/                             # 数据传输对象
│   ├── BatchSummaryDTO.java         # 批量汇总DTO
│   ├── QcRequest.java               # 质控请求DTO
│   ├── QcResultDTO.java             # 质控结果DTO
│   ├── RuleDTO.java                 # 规则DTO
│   ├── RuleUpdateRequest.java       # 规则更新请求DTO
│   ├── RuleTestRequest.java         # 规则测试请求DTO
│   ├── DictQueryRequest.java        # 字典查询请求DTO
│   ├── DictDTO.java                 # 字典DTO
│   └── FieldSearchResult.java       # 字段搜索结果DTO
│
├── entity/                          # 实体类
│   ├── KiroQcBatchSummary.java      # 批量汇总实体
│   ├── KiroQcCaseResult.java        # 病案结果实体
│   ├── KiroQcDefectDetail.java      # 缺陷明细实体
│   ├── KiroQcRule.java              # 规则实体
│   ├── MedicalRecord.java           # 病案实体
│   ├── QcCaseResult.java            # 病案结果实体(已废弃)
│   ├── QcDefectDetail.java          # 缺陷明细实体(已废弃)
│   └── QcRule.java                  # 规则实体(已废弃)
│
├── mapper/                          # MyBatis Mapper接口
│   ├── MedicalRecordMapper.java     # 病案数据Mapper
│   ├── QcResultMapper.java          # 质控结果Mapper
│   ├── QcRuleMapper.java            # 规则Mapper
│   ├── DictMapper.java              # 字典Mapper
│   └── FieldSearchMapper.java       # 字段搜索Mapper
│
└── service/                         # 业务逻辑层
    ├── QcService.java               # 质控服务
    ├── RuleEngineService.java       # 规则引擎服务
    └── DictService.java             # 字典服务
```

### 📁 资源文件目录

```
src/main/resources/
└── application.yml                  # Spring Boot配置文件
```

### 📁 编译输出目录

```
target/
├── classes/                         # 编译后的class文件
├── generated-sources/               # 生成的源代码
├── maven-archiver/                  # Maven归档信息
├── maven-status/                    # Maven状态信息
└── qc-system-1.0.0.jar             # 可执行JAR包
```

---

## 文件说明

### 核心代码文件

#### 1. QcApplication.java
- **作用**: Spring Boot应用启动类
- **关键注解**: @SpringBootApplication, @MapperScan
- **功能**: 启动Spring容器，扫描Mapper接口

#### 2. QcController.java
- **作用**: 质控REST API控制器
- **端点数量**: 7个
- **功能**: 
  - 规则管理接口
  - 质控执行接口
  - 结果查询接口

#### 2.1 DictController.java
- **作用**: 字典REST API控制器
- **端点数量**: 6个
- **功能**:
  - 字典查询接口
  - 字段搜索接口
  - 值域验证接口

#### 3. QcService.java
- **作用**: 质控业务逻辑服务
- **主要方法**:
  - getAllRules(): 获取所有规则
  - searchRules(): 搜索规则
  - checkSingleCase(): 单个病案质控
  - batchCheck(): 批量质控
  - getCaseResult(): 获取病案结果
  - getBatchSummary(): 获取批量汇总

#### 4. RuleEngineService.java
- **作用**: 规则引擎核心逻辑
- **支持规则类型**:
  - value_check: 必填项检查
  - cross_check_null: 交叉验证
  - range_check: 范围检查
- **主要方法**:
  - checkRecord(): 检查单个病案
  - applyRule(): 应用单个规则
  - checkValueRule(): 必填检查
  - checkRangeRule(): 范围检查

#### 5. DictService.java
- **作用**: 字典服务
- **主要方法**:
  - queryDicts(): 查询字典数据
  - getAllDictTypes(): 获取所有字典类型
  - searchFieldInTables(): 搜索字段所在表
  - validateFieldValue(): 验证字段值

### 配置文件

#### 1. pom.xml
- **作用**: Maven项目配置
- **关键依赖**:
  - spring-boot-starter-web: Web框架
  - mybatis-spring-boot-starter: MyBatis集成
  - mysql-connector-java: MySQL驱动
  - springfox-boot-starter: Swagger文档
  - lombok: 简化代码

#### 2. application.yml
- **作用**: Spring Boot应用配置
- **配置项**:
  - server.port: 服务端口(4101)
  - spring.datasource: 数据库连接
  - mybatis: MyBatis配置
  - logging: 日志配置

### 数据库脚本

#### 1. init_kiro_tables.sql
- **作用**: 创建质控系统所需的所有表
- **表列表**:
  - kiro_qc_rule: 规则表
  - kiro_field_mapping: 字段映射表
  - kiro_qc_defect_detail: 缺陷明细表
  - kiro_qc_case_result: 病案结果表
  - kiro_qc_batch_summary: 批量汇总表
  - kiro_qc_run_context: 运行上下文表

#### 2. init_rules.py
- **作用**: 初始化6条质控规则
- **规则列表**:
  - A18x03_value_check
  - A18x01_cross_check_null
  - A18x01_range_check
  - A18x02_value_check
  - A18x02_range_check
  - A18x03_range_check

### 测试脚本

#### 1. test_api_auto.py
- **作用**: 自动化API测试
- **测试用例**: 8个
- **功能**: 
  - 规则查询测试
  - 单个病案质控测试
  - 批量质控测试
  - 结果查询测试

#### 2. test_curl.bat
- **作用**: 使用curl测试API
- **适用场景**: 无Python环境

#### 3. test_db_connection.py
- **作用**: 测试数据库连接
- **功能**:
  - 查看表结构
  - 查看数据分布
  - 验证关联关系

### 文档文件

#### 1. README.md
- **内容**: 项目介绍、快速开始、API文档
- **目标读者**: 开发者、使用者

#### 2. TEST_REPORT.md
- **内容**: 完整的测试报告
- **包含**: 测试用例、测试结果、数据分析

#### 3. SELF_TEST_RESULTS.md
- **内容**: 实际API调用结果
- **包含**: 请求示例、响应示例、案例分析

#### 4. PROJECT_SUMMARY.md
- **内容**: 项目总结
- **包含**: 完成情况、技术亮点、测试验证

#### 5. DEPLOYMENT_GUIDE.md
- **内容**: 部署和使用指南
- **包含**: 环境要求、部署步骤、常见问题

---

## 文件统计

### 代码文件统计

| 类型 | 数量 | 说明 |
|------|------|------|
| Java源文件 | 31个 | 包含实体、服务、控制器、Mapper等 |
| Python脚本 | 8个 | 数据库初始化和测试脚本 |
| SQL脚本 | 2个 | 表结构定义 |
| Markdown文档 | 15个 | 项目文档 |
| 配置文件 | 2个 | pom.xml, application.yml |
| 文档文件 | 6个 | Markdown格式 |
| 批处理脚本 | 2个 | Windows启动和测试脚本 |

### 代码行数统计 (估算)

| 文件类型 | 行数 | 占比 |
|----------|------|------|
| Java代码 | ~3000行 | 60% |
| Python脚本 | ~800行 | 16% |
| SQL脚本 | ~200行 | 4% |
| 配置文件 | ~100行 | 2% |
| 文档 | ~900行 | 18% |
| **总计** | **~5000行** | **100%** |

---

## 依赖关系

### 模块依赖

```
QcApplication
    ↓
QcController
    ↓
QcService
    ├→ QcRuleMapper
    ├→ MedicalRecordMapper
    ├→ QcResultMapper
    └→ RuleEngineService
```

### 数据流向

```
用户请求
    ↓
QcController (接收请求)
    ↓
QcService (业务处理)
    ↓
RuleEngineService (规则执行)
    ↓
Mapper (数据访问)
    ↓
MySQL数据库
```

---

## 关键文件路径

### 启动相关
- 启动类: `src/main/java/com/medical/qc/QcApplication.java`
- 配置文件: `src/main/resources/application.yml`
- 启动脚本: `start.bat`

### API相关
- 控制器: `src/main/java/com/medical/qc/controller/QcController.java`
- Swagger配置: `src/main/java/com/medical/qc/config/SwaggerConfig.java`

### 业务逻辑
- 质控服务: `src/main/java/com/medical/qc/service/QcService.java`
- 规则引擎: `src/main/java/com/medical/qc/service/RuleEngineService.java`

### 数据访问
- 规则Mapper: `src/main/java/com/medical/qc/mapper/QcRuleMapper.java`
- 病案Mapper: `src/main/java/com/medical/qc/mapper/MedicalRecordMapper.java`
- 结果Mapper: `src/main/java/com/medical/qc/mapper/QcResultMapper.java`

### 测试相关
- 自动化测试: `test_api_auto.py`
- 数据库测试: `test_db_connection.py`
- Curl测试: `test_curl.bat`

### 文档相关
- 项目说明: `README.md`
- 测试报告: `TEST_REPORT.md`
- 部署指南: `DEPLOYMENT_GUIDE.md`

---

## 文件大小估算

| 文件/目录 | 大小 | 说明 |
|-----------|------|------|
| src/ | ~500KB | 源代码 |
| target/ | ~50MB | 编译输出和依赖 |
| *.py | ~50KB | Python脚本 |
| *.md | ~200KB | 文档文件 |
| pom.xml | ~3KB | Maven配置 |
| **总计** | **~51MB** | 包含所有依赖 |

---

## 版本信息

- **项目版本**: 1.0.0
- **Spring Boot版本**: 2.7.18
- **Java版本**: 1.8
- **Maven版本**: 3.9.11
- **MySQL版本**: 8.0

---

**最后更新**: 2026-01-16
**文档版本**: 1.0.0
