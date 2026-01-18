-- ========================================
-- 修复规则表字典类型配置 - 第3部分(手术和疾病编码)
-- ========================================
USE d_hosq_traegj_20260115;

-- 21. 患者证件类别 -> RC038
UPDATE kiro_qc_rule SET dict_types = 'RC038'
WHERE field_name LIKE '%证件%' AND dict_types != 'RC038';

-- 22. 判断代码 -> RC039
UPDATE kiro_qc_rule SET dict_types = 'RC039'
WHERE field_name LIKE '%有无%' AND dict_types != 'RC039';

-- ========================================
-- 手术相关字典
-- ========================================

-- 23. 四级手术编码 -> level4_operation_code_v2
UPDATE kiro_qc_rule SET dict_types = 'level4_operation_code_v2'
WHERE field_name LIKE '%四级手术%' AND dict_types != 'level4_operation_code_v2';

-- 24. 手术编码 -> operation_dict_v3
UPDATE kiro_qc_rule SET dict_types = 'operation_dict_v3'
WHERE field_name LIKE '%手术%'
  AND field_name NOT LIKE '%四级%'
  AND field_name NOT LIKE '%微创%'
  AND field_name NOT LIKE '%日间%'
  AND field_name NOT LIKE '%级别%'
  AND field_name NOT LIKE '%类型%'
  AND dict_types != 'operation_dict_v3';

-- 25. 疾病编码 -> RCJBBM
UPDATE kiro_qc_rule SET dict_types = 'RCJBBM'
WHERE field_name LIKE '%诊断%' AND dict_types != 'RCJBBM';

-- 26. 微创手术 -> microfracture_oper_code_v2
UPDATE kiro_qc_rule SET dict_types = 'microfracture_oper_code_v2'
WHERE field_name LIKE '%微创%' AND dict_types != 'microfracture_oper_code_v2';

-- 27. 日间手术 -> day_operation_code_2022
UPDATE kiro_qc_rule SET dict_types = 'day_operation_code_2022'
WHERE field_name LIKE '%日间手术%' AND dict_types != 'day_operation_code_2022';

-- 28. 手术类型 -> operation_code_with_type
UPDATE kiro_qc_rule SET dict_types = 'operation_code_with_type'
WHERE field_name LIKE '%手术类型%' AND dict_types != 'operation_code_with_type';

-- ========================================
-- 验证修复结果
-- ========================================
SELECT
    '修复完成 - 字典类型分布统计:' as message;

SELECT
    dict_types,
    COUNT(*) as rule_count
FROM kiro_qc_rule
WHERE dict_types IS NOT NULL
GROUP BY dict_types
ORDER BY rule_count DESC;
