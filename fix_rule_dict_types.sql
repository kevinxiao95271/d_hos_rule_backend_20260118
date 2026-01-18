-- 修复规则表中的字典类型配置错误
-- 根据字段含义匹配正确的字典类型

USE d_hosq_traegj_20260115;

-- 1. 修复入院病情相关字段 (应该使用RC027)
UPDATE kiro_qc_rule
SET dict_types = 'RC027'
WHERE field_code LIKE '%入院病情%'
   OR field_name LIKE '%入院病情%'
   OR field_code IN ('C08x07C', 'C09x07C', 'C10x07C', 'C11x07C', 'C12x07C', 'C13x07C', 'C14x07C');

-- 2. 修复切口愈合等级相关字段 (应该使用RC014)
UPDATE kiro_qc_rule
SET dict_types = 'RC014'
WHERE field_code LIKE '%切口愈合%'
   OR field_name LIKE '%切口愈合%'
   OR field_code IN ('C21x01C', 'C22x01C', 'C23x01C', 'C24x01C', 'C25x01C', 'C26x01C');

-- 3. 修复麻醉方式相关字段 (应该使用RC013)
UPDATE kiro_qc_rule
SET dict_types = 'RC013'
WHERE field_code LIKE '%麻醉%'
   OR field_name LIKE '%麻醉%'
   OR field_code IN ('C21x02C', 'C22x02C', 'C23x02C', 'C24x02C', 'C25x02C', 'C26x02C');

-- 4. 修复性别相关字段 (应该使用RC001)
UPDATE kiro_qc_rule
SET dict_types = 'RC001'
WHERE field_code LIKE '%性别%'
   OR field_name LIKE '%性别%'
   OR field_code = 'A02';

-- 5. 修复婚姻状况相关字段 (应该使用RC002)
UPDATE kiro_qc_rule
SET dict_types = 'RC002'
WHERE field_code LIKE '%婚姻%'
   OR field_name LIKE '%婚姻%'
   OR field_code = 'A05';
