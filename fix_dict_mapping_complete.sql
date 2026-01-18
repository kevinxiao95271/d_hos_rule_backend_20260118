-- ========================================
-- 修复规则表字典类型配置 - 完整版
-- 基于正确的字典映射关系
-- ========================================
USE d_hosq_traegj_20260115;

-- ========================================
-- 基础字典类型修复
-- ========================================

-- 1. 性别 -> RC001
UPDATE kiro_qc_rule SET dict_types = 'RC001'
WHERE field_name LIKE '%性别%' AND dict_types != 'RC001';

-- 2. 婚姻状况 -> RC002
UPDATE kiro_qc_rule SET dict_types = 'RC002'
WHERE field_name LIKE '%婚姻%' AND dict_types != 'RC002';

-- 3. 职业 -> RC003
UPDATE kiro_qc_rule SET dict_types = 'RC003'
WHERE field_name LIKE '%职业%' AND dict_types != 'RC003';

-- 4. 病案质量 -> RC011
UPDATE kiro_qc_rule SET dict_types = 'RC011'
WHERE field_name LIKE '%病案质量%' AND dict_types != 'RC011';

-- 5. 麻醉方式 -> RC013
UPDATE kiro_qc_rule SET dict_types = 'RC013'
WHERE field_name LIKE '%麻醉方式%' AND dict_types != 'RC013';

-- 6. 切口愈合等级 -> RC014
UPDATE kiro_qc_rule SET dict_types = 'RC014'
WHERE field_name LIKE '%切口愈合%' AND dict_types != 'RC014';

-- 7. 尸检 -> RC016
UPDATE kiro_qc_rule SET dict_types = 'RC016'
WHERE field_name LIKE '%尸检%' AND dict_types != 'RC016';

-- 8. 离院方式 -> RC019
UPDATE kiro_qc_rule SET dict_types = 'RC019'
WHERE field_name LIKE '%离院方式%' AND dict_types != 'RC019';

-- 9. 科别 -> RC023
UPDATE kiro_qc_rule SET dict_types = 'RC023'
WHERE field_name LIKE '%科别%' AND dict_types != 'RC023';

-- 10. 入院途径 -> RC026
UPDATE kiro_qc_rule SET dict_types = 'RC026'
WHERE field_name LIKE '%入院途径%' AND dict_types != 'RC026';
