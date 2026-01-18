-- ========================================
-- 修复规则表字典类型配置错误 - 第1部分
-- ========================================
USE d_hosq_traegj_20260115;

-- 先查看当前错误配置的统计
SELECT
    dict_types,
    COUNT(*) as rule_count,
    GROUP_CONCAT(DISTINCT field_name SEPARATOR '; ') as sample_fields
FROM kiro_qc_rule
WHERE dict_types IS NOT NULL
GROUP BY dict_types
ORDER BY rule_count DESC;

-- ========================================
-- 1. 修复入院病情字段 -> RC027
-- ========================================
UPDATE kiro_qc_rule
SET dict_types = 'RC027'
WHERE (
    field_name LIKE '%入院病情%'
    OR field_code IN ('C08x07C', 'C09x07C', 'C10x07C', 'C11x07C', 'C12x07C', 'C13x07C', 'C14x07C')
)
AND dict_types != 'RC027';

-- ========================================
-- 2. 修复切口愈合等级字段 -> RC014
-- ========================================
UPDATE kiro_qc_rule
SET dict_types = 'RC014'
WHERE (
    field_name LIKE '%切口愈合%'
    OR field_code IN ('C21x01C', 'C22x01C', 'C23x01C', 'C24x01C', 'C25x01C', 'C26x01C')
)
AND dict_types != 'RC014';

-- ========================================
-- 3. 修复麻醉方式字段 -> RC013
-- ========================================
UPDATE kiro_qc_rule
SET dict_types = 'RC013'
WHERE (
    field_name LIKE '%麻醉方式%'
    OR field_code IN ('C21x02C', 'C22x02C', 'C23x02C', 'C24x02C', 'C25x02C', 'C26x02C')
)
AND dict_types != 'RC013';
