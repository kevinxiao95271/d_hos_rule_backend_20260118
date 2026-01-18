# 更新日志

## 版本 1.1.0 (2026-01-16)

### 🎉 新增功能

#### 1. 规则管理功能
- ✅ 规则状态管理（draft/active）
- ✅ 按状态查询规则
- ✅ 规则详情查询
- ✅ 规则搜索（支持状态筛选）
- ✅ 规则更新
- ✅ 规则状态切换
- ✅ 规则试运行

#### 2. 规则状态说明
- **draft（未完善）**: 草稿状态，不参与质控，可以随意修改和测试
- **active（已完善）**: 正式状态，参与质控，修改需谨慎

#### 3. 规则试运行功能
- 支持单个病案测试
- 支持批量数据测试
- 返回违规统计和明细
- 不影响正式质控结果

### 📋 新增API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/qc/rules/status/{status} | GET | 按状态获取规则 |
| /api/qc/rules/{id} | GET | 获取规则详情 |
| /api/qc/rules/search | GET | 搜索规则（支持状态筛选） |
| /api/qc/rules | PUT | 更新规则 |
| /api/qc/rules/{id}/status | PUT | 更新规则状态 |
| /api/qc/rules/test | POST | 规则试运行 |

### 🔧 改进

1. **字段说明优化**
   - A49字段明确为"住院次数"
   - 更新所有相关文档和注释

2. **搜索功能增强**
   - 搜索接口支持按状态筛选
   - 支持status、fieldCode、keyword组合查询

3. **规则DTO扩展**
   - 添加uruleContent字段
   - 添加canonicalExpr字段

### 📖 新增文档

- **RULE_MANAGEMENT_API.md** - 规则管理API完整文档
- **FIELD_DESCRIPTION.md** - 字段说明文档
- **test_rule_management.py** - 规则管理功能测试脚本

### 🎯 使用场景

#### 场景1: 创建并测试新规则
```bash
# 1. 创建规则（status=draft）
INSERT INTO kiro_qc_rule ...

# 2. 试运行测试
curl -X POST "/api/qc/rules/test" -d '{"ruleId":7,"year":2020}'

# 3. 确认无误后设置为active
curl -X PUT "/api/qc/rules/7/status?status=active"
```

#### 场景2: 修改现有规则
```bash
# 1. 将规则改为draft
curl -X PUT "/api/qc/rules/1/status?status=draft"

# 2. 修改规则
curl -X PUT "/api/qc/rules" -d '{...}'

# 3. 试运行测试
curl -X POST "/api/qc/rules/test" -d '{"ruleId":1}'

# 4. 恢复为active
curl -X PUT "/api/qc/rules/1/status?status=active"
```

#### 场景3: 查看规则完善情况
```bash
# 查看未完善规则
curl "/api/qc/rules/status/draft"

# 查看已完善规则
curl "/api/qc/rules/status/active"
```

### ✅ 测试验证

所有新功能已通过测试：
- ✅ 按状态获取规则
- ✅ 规则详情查询
- ✅ 规则搜索（带状态筛选）
- ✅ 规则状态更新
- ✅ 规则试运行（单个病案）
- ✅ 规则试运行（批量数据）

### 📊 统计

- **新增接口**: 6个
- **新增DTO**: 3个
- **新增文档**: 3个
- **新增测试脚本**: 1个
- **总接口数**: 13个（原7个 + 新增6个）

---

## 版本 1.0.0 (2026-01-16)

### 🎉 初始版本

#### 核心功能
- ✅ 规则引擎（3种规则类型）
- ✅ 单个病案质控
- ✅ 批量质控（年/季度/月）
- ✅ 缺陷管理
- ✅ 统计分析
- ✅ REST API（7个接口）
- ✅ Swagger文档

#### 数据库
- ✅ 6张kiro_前缀表
- ✅ 6条预置规则

#### 文档
- ✅ README.md
- ✅ API_EXAMPLES.md
- ✅ TEST_REPORT.md
- ✅ DEPLOYMENT_GUIDE.md
- ✅ 等共9个文档

---

**最后更新**: 2026-01-16
