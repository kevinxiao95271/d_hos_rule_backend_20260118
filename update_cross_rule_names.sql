-- 更新Cross规则命名，统一使用RULE_CROSS_前缀
-- 这样与普通规则的RULE_前缀保持一致

-- 1. 更新kiro_qc_rule表中的Cross规则（如果有的话）
UPDATE kiro_qc_rule 
SET rule_code = CONCAT('RULE_', rule_code)
WHERE rule_code LIKE 'CROSS_%' 
  AND rule_code NOT LIKE 'RULE_CROSS_%';

-- 2. 更新kiro_qc_rule_cross表中的Cross规则
UPDATE kiro_qc_rule_cross 
SET rule_code = CONCAT('RULE_', rule_code)
WHERE rule_code LIKE 'CROSS_%' 
  AND rule_code NOT LIKE 'RULE_CROSS_%';

-- 3. 更新已存在的具体规则
UPDATE kiro_qc_rule_cross 
SET rule_code = 'RULE_CROSS_D26_TRANSFUSION_FEE1'
WHERE rule_code = 'CROSS_D26_TRANSFUSION_FEE1';

UPDATE kiro_qc_rule_cross 
SET rule_code = 'RULE_CROSS_C06x01C_C07x01C'
WHERE rule_code = 'CROSS_C06x01C_C07x01C';

UPDATE kiro_qc_rule_cross 
SET rule_code = 'RULE_CROSS_C14x01C_C15x01C'
WHERE rule_code = 'CROSS_C14x01C_C15x01C';

UPDATE kiro_qc_rule_cross 
SET rule_code = 'RULE_CROSS_C03C_GENDER_MALE'
WHERE rule_code = 'CROSS_C03C_GENDER_MALE';

-- 4. 更新质控结果表中的历史记录（如果需要的话）
-- 注意：这可能会影响大量历史数据，请谨慎执行
-- UPDATE kiro_qc_case_result 
-- SET defects_json = REPLACE(defects_json, '"ruleCode":"CROSS_', '"ruleCode":"RULE_CROSS_')
-- WHERE defects_json LIKE '%"ruleCode":"CROSS_%';

-- 查看更新结果
SELECT rule_code, description, cross_type, status 
FROM kiro_qc_rule_cross 
WHERE rule_code LIKE 'RULE_CROSS_%'
ORDER BY rule_code;