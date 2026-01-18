-- ========================================
-- 修复规则表字典类型配置 - 第2部分
-- ========================================
USE d_hosq_traegj_20260115;

-- 11. 入院病情 -> RC027
UPDATE kiro_qc_rule SET dict_types = 'RC027'
WHERE field_name LIKE '%入院病情%' AND dict_types != 'RC027';

-- 12. 再住院计划 -> RC028
UPDATE kiro_qc_rule SET dict_types = 'RC028'
WHERE field_name LIKE '%再住院%' AND dict_types != 'RC028';

-- 13. 手术级别 -> RC029
UPDATE kiro_qc_rule SET dict_types = 'RC029'
WHERE field_name LIKE '%手术级别%' AND dict_types != 'RC029';

-- 14. ABO血型 -> RC030
UPDATE kiro_qc_rule SET dict_types = 'RC030'
WHERE field_name LIKE '%ABO%' OR field_name LIKE '%血型%' AND field_name NOT LIKE '%Rh%' AND dict_types != 'RC030';

-- 15. Rh血型 -> RC031
UPDATE kiro_qc_rule SET dict_types = 'RC031'
WHERE field_name LIKE '%Rh%' AND dict_types != 'RC031';

-- 16. 医疗付费方式 -> RC032
UPDATE kiro_qc_rule SET dict_types = 'RC032'
WHERE field_name LIKE '%付费%' AND dict_types != 'RC032';

-- 17. 联系人关系 -> RC033
UPDATE kiro_qc_rule SET dict_types = 'RC033'
WHERE field_name LIKE '%联系人关系%' AND dict_types != 'RC033';

-- 18. 民族 -> RC035
UPDATE kiro_qc_rule SET dict_types = 'RC035'
WHERE field_name LIKE '%民族%' AND dict_types != 'RC035';

-- 19. 省市 -> RC036
UPDATE kiro_qc_rule SET dict_types = 'RC036'
WHERE (field_name LIKE '%省%' OR field_name LIKE '%直辖市%') AND dict_types != 'RC036';

-- 20. 药物过敏 -> RC037
UPDATE kiro_qc_rule SET dict_types = 'RC037'
WHERE field_name LIKE '%药物过敏%' AND dict_types != 'RC037';
