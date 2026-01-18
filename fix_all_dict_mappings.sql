-- ========================================
-- 修复规则表字典类型配置 - 完整合并版
-- ========================================
USE d_hosq_traegj_20260115;

-- 显示修复前的统计
SELECT '修复前统计:' as stage;
SELECT dict_types, COUNT(*) as count FROM kiro_qc_rule WHERE dict_types IS NOT NULL GROUP BY dict_types ORDER BY count DESC LIMIT 10;

-- 1. 性别 -> RC001
UPDATE kiro_qc_rule SET dict_types = 'RC001' WHERE field_name LIKE '%性别%' AND dict_types != 'RC001';

-- 2. 婚姻状况 -> RC002
UPDATE kiro_qc_rule SET dict_types = 'RC002' WHERE field_name LIKE '%婚姻%' AND dict_types != 'RC002';

-- 3. 职业 -> RC003
UPDATE kiro_qc_rule SET dict_types = 'RC003' WHERE field_name LIKE '%职业%' AND dict_types != 'RC003';

-- 4. 病案质量 -> RC011
UPDATE kiro_qc_rule SET dict_types = 'RC011' WHERE field_name LIKE '%病案质量%' AND dict_types != 'RC011';

-- 5. 麻醉方式 -> RC013
UPDATE kiro_qc_rule SET dict_types = 'RC013' WHERE field_name LIKE '%麻醉方式%' AND dict_types != 'RC013';

-- 6. 切口愈合等级 -> RC014
UPDATE kiro_qc_rule SET dict_types = 'RC014' WHERE field_name LIKE '%切口愈合%' AND dict_types != 'RC014';

-- 7. 尸检 -> RC016
UPDATE kiro_qc_rule SET dict_types = 'RC016' WHERE field_name LIKE '%尸检%' AND dict_types != 'RC016';

-- 8. 离院方式 -> RC019
UPDATE kiro_qc_rule SET dict_types = 'RC019' WHERE field_name LIKE '%离院方式%' AND dict_types != 'RC019';

-- 9. 科别 -> RC023
UPDATE kiro_qc_rule SET dict_types = 'RC023' WHERE field_name LIKE '%科别%' AND dict_types != 'RC023';

-- 10. 入院途径 -> RC026
UPDATE kiro_qc_rule SET dict_types = 'RC026' WHERE field_name LIKE '%入院途径%' AND dict_types != 'RC026';

-- 11. 入院病情 -> RC027
UPDATE kiro_qc_rule SET dict_types = 'RC027' WHERE field_name LIKE '%入院病情%' AND dict_types != 'RC027';

-- 12. 再住院计划 -> RC028
UPDATE kiro_qc_rule SET dict_types = 'RC028' WHERE field_name LIKE '%再住院%' AND dict_types != 'RC028';

-- 13. 手术级别 -> RC029
UPDATE kiro_qc_rule SET dict_types = 'RC029' WHERE field_name LIKE '%手术级别%' AND dict_types != 'RC029';

-- 14. ABO血型 -> RC030
UPDATE kiro_qc_rule SET dict_types = 'RC030' WHERE (field_name LIKE '%ABO%' OR (field_name LIKE '%血型%' AND field_name NOT LIKE '%Rh%')) AND dict_types != 'RC030';

-- 15. Rh血型 -> RC031
UPDATE kiro_qc_rule SET dict_types = 'RC031' WHERE field_name LIKE '%Rh%' AND dict_types != 'RC031';

-- 16. 医疗付费方式 -> RC032
UPDATE kiro_qc_rule SET dict_types = 'RC032' WHERE field_name LIKE '%付费%' AND dict_types != 'RC032';

-- 17. 联系人关系 -> RC033
UPDATE kiro_qc_rule SET dict_types = 'RC033' WHERE field_name LIKE '%联系人关系%' AND dict_types != 'RC033';

-- 18. 民族 -> RC035
UPDATE kiro_qc_rule SET dict_types = 'RC035' WHERE field_name LIKE '%民族%' AND dict_types != 'RC035';

-- 19. 省市 -> RC036
UPDATE kiro_qc_rule SET dict_types = 'RC036' WHERE (field_name LIKE '%省%' OR field_name LIKE '%直辖市%') AND dict_types != 'RC036';

-- 20. 药物过敏 -> RC037
UPDATE kiro_qc_rule SET dict_types = 'RC037' WHERE field_name LIKE '%药物过敏%' AND dict_types != 'RC037';

-- 21. 患者证件类别 -> RC038
UPDATE kiro_qc_rule SET dict_types = 'RC038' WHERE field_name LIKE '%证件%' AND dict_types != 'RC038';

-- 22. 判断代码 -> RC039
UPDATE kiro_qc_rule SET dict_types = 'RC039' WHERE field_name LIKE '%有无%' AND dict_types != 'RC039';

-- 显示修复后的统计
SELECT '修复后统计:' as stage;
SELECT dict_types, COUNT(*) as count FROM kiro_qc_rule WHERE dict_types IS NOT NULL GROUP BY dict_types ORDER BY count DESC LIMIT 10;
