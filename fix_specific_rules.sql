-- ========================================
-- 精确修复规则表字典类型配置错误
-- 基于规则代码精确匹配
-- ========================================
USE d_hosq_traegj_20260115;

-- 修复入院病情字段 (C08x07C到C14x07C) -> RC027
UPDATE kiro_qc_rule
SET dict_types = 'RC027'
WHERE rule_code LIKE 'RULE_C08x07C_%'
   OR rule_code LIKE 'RULE_C09x07C_%'
   OR rule_code LIKE 'RULE_C10x07C_%'
   OR rule_code LIKE 'RULE_C11x07C_%'
   OR rule_code LIKE 'RULE_C12x07C_%'
   OR rule_code LIKE 'RULE_C13x07C_%'
   OR rule_code LIKE 'RULE_C14x07C_%';

-- 修复切口愈合等级字段 (C21x01C到C26x01C) -> RC014
UPDATE kiro_qc_rule
SET dict_types = 'RC014'
WHERE rule_code LIKE 'RULE_C21x01C_%'
   OR rule_code LIKE 'RULE_C22x01C_%'
   OR rule_code LIKE 'RULE_C23x01C_%'
   OR rule_code LIKE 'RULE_C24x01C_%'
   OR rule_code LIKE 'RULE_C25x01C_%'
   OR rule_code LIKE 'RULE_C26x01C_%';

-- 验证修复结果
SELECT '修复后的规则示例:' as message;
SELECT rule_code, field_code, field_name, dict_types
FROM kiro_qc_rule
WHERE rule_code IN ('RULE_C08x07C_RC013', 'RULE_C21x01C_RC013')
   OR rule_code LIKE 'RULE_C08x07C_%'
   OR rule_code LIKE 'RULE_C21x01C_%'
LIMIT 10;
