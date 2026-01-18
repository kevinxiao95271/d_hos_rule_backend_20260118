-- 自动生成的字典验证规则
-- 生成时间: 1
-- 总计: 50条规则

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_A01_RC035', 'A01', '民族', 'value_check', '民族必须在RC035字典范围内',
    -1.0, 'active', 'RC035', 'd_mr', 'A01 IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC035\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_A02_RC002', 'A02', '婚姻状况', 'value_check', '婚姻状况必须在RC002字典范围内',
    -1.0, 'active', 'RC002', 'd_mr', 'A02 IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC002\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_A16_RC016', 'A16', '死亡患者尸检', 'value_check', '死亡患者尸检必须在RC016字典范围内',
    -1.0, 'active', 'RC016', 'd_mr', 'A16 IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC016\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_A17_RC019', 'A17', '离院方式', 'value_check', '离院方式必须在RC019字典范围内',
    -1.0, 'active', 'RC019', 'd_mr', 'A17 IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC019\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_A20_RC030', 'A20', 'ABO血型', 'value_check', 'ABO血型必须在RC030字典范围内',
    -1.0, 'active', 'RC030', 'd_mr', 'A20 IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC030\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_A22_RC011', 'A22', '病案质量', 'value_check', '病案质量必须在RC011字典范围内',
    -1.0, 'active', 'RC011', 'd_mr', 'A22 IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC011\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_A26_RC026', 'A26', '入院途径', 'value_check', '入院途径必须在RC026字典范围内',
    -1.0, 'active', 'RC026', 'd_mr', 'A26 IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC026\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_A27_RC027', 'A27', '入院病情', 'value_check', '入院病情必须在RC027字典范围内',
    -1.0, 'active', 'RC027', 'd_mr', 'A27 IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC027\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_A32_RC032', 'A32', '医疗付费方式', 'value_check', '医疗付费方式必须在RC032字典范围内',
    -1.0, 'active', 'RC032', 'd_mr', 'A32 IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC032\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C22x01C_RC013', 'C22x01C', '主要手术操作麻醉方式', 'value_check', '主要手术操作麻醉方式必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr', 'C22x01C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x01C_RC013', 'C43x01C', '其他手术操作麻醉方式1', 'value_check', '其他手术操作麻醉方式1必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x01C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x02C_RC013', 'C43x02C', '其他手术操作麻醉方式2', 'value_check', '其他手术操作麻醉方式2必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x02C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x03C_RC013', 'C43x03C', '其他手术操作麻醉方式3', 'value_check', '其他手术操作麻醉方式3必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x03C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x04C_RC013', 'C43x04C', '其他手术操作麻醉方式4', 'value_check', '其他手术操作麻醉方式4必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x04C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x05C_RC013', 'C43x05C', '其他手术操作麻醉方式5', 'value_check', '其他手术操作麻醉方式5必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x05C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x06C_RC013', 'C43x06C', '其他手术操作麻醉方式6', 'value_check', '其他手术操作麻醉方式6必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x06C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x07C_RC013', 'C43x07C', '其他手术操作麻醉方式7', 'value_check', '其他手术操作麻醉方式7必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x07C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x08C_RC013', 'C43x08C', '其他手术操作麻醉方式8', 'value_check', '其他手术操作麻醉方式8必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x08C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x09C_RC013', 'C43x09C', '其他手术操作麻醉方式9', 'value_check', '其他手术操作麻醉方式9必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x09C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x10C_RC013', 'C43x10C', '其他手术操作麻醉方式10', 'value_check', '其他手术操作麻醉方式10必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x10C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x11C_RC013', 'C43x11C', '其他手术操作麻醉方式11', 'value_check', '其他手术操作麻醉方式11必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x11C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x12C_RC013', 'C43x12C', '其他手术操作麻醉方式12', 'value_check', '其他手术操作麻醉方式12必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x12C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x13C_RC013', 'C43x13C', '其他手术操作麻醉方式13', 'value_check', '其他手术操作麻醉方式13必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x13C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x14C_RC013', 'C43x14C', '其他手术操作麻醉方式14', 'value_check', '其他手术操作麻醉方式14必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x14C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x15C_RC013', 'C43x15C', '其他手术操作麻醉方式15', 'value_check', '其他手术操作麻醉方式15必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x15C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x16C_RC013', 'C43x16C', '其他手术操作麻醉方式16', 'value_check', '其他手术操作麻醉方式16必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x16C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x17C_RC013', 'C43x17C', '其他手术操作麻醉方式17', 'value_check', '其他手术操作麻醉方式17必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x17C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x18C_RC013', 'C43x18C', '其他手术操作麻醉方式18', 'value_check', '其他手术操作麻醉方式18必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x18C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x19C_RC013', 'C43x19C', '其他手术操作麻醉方式19', 'value_check', '其他手术操作麻醉方式19必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x19C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x20C_RC013', 'C43x20C', '其他手术操作麻醉方式20', 'value_check', '其他手术操作麻醉方式20必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_1_20', 'C43x20C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x21C_RC013', 'C43x21C', '其他手术操作麻醉方式21', 'value_check', '其他手术操作麻醉方式21必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x21C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x22C_RC013', 'C43x22C', '其他手术操作麻醉方式22', 'value_check', '其他手术操作麻醉方式22必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x22C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x23C_RC013', 'C43x23C', '其他手术操作麻醉方式23', 'value_check', '其他手术操作麻醉方式23必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x23C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x24C_RC013', 'C43x24C', '其他手术操作麻醉方式24', 'value_check', '其他手术操作麻醉方式24必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x24C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x25C_RC013', 'C43x25C', '其他手术操作麻醉方式25', 'value_check', '其他手术操作麻醉方式25必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x25C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x26C_RC013', 'C43x26C', '其他手术操作麻醉方式26', 'value_check', '其他手术操作麻醉方式26必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x26C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x27C_RC013', 'C43x27C', '其他手术操作麻醉方式27', 'value_check', '其他手术操作麻醉方式27必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x27C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x28C_RC013', 'C43x28C', '其他手术操作麻醉方式28', 'value_check', '其他手术操作麻醉方式28必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x28C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x29C_RC013', 'C43x29C', '其他手术操作麻醉方式29', 'value_check', '其他手术操作麻醉方式29必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x29C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x30C_RC013', 'C43x30C', '其他手术操作麻醉方式30', 'value_check', '其他手术操作麻醉方式30必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x30C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x31C_RC013', 'C43x31C', '其他手术操作麻醉方式31', 'value_check', '其他手术操作麻醉方式31必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x31C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x32C_RC013', 'C43x32C', '其他手术操作麻醉方式32', 'value_check', '其他手术操作麻醉方式32必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x32C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x33C_RC013', 'C43x33C', '其他手术操作麻醉方式33', 'value_check', '其他手术操作麻醉方式33必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x33C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x34C_RC013', 'C43x34C', '其他手术操作麻醉方式34', 'value_check', '其他手术操作麻醉方式34必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x34C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x35C_RC013', 'C43x35C', '其他手术操作麻醉方式35', 'value_check', '其他手术操作麻醉方式35必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x35C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x36C_RC013', 'C43x36C', '其他手术操作麻醉方式36', 'value_check', '其他手术操作麻醉方式36必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x36C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x37C_RC013', 'C43x37C', '其他手术操作麻醉方式37', 'value_check', '其他手术操作麻醉方式37必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x37C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x38C_RC013', 'C43x38C', '其他手术操作麻醉方式38', 'value_check', '其他手术操作麻醉方式38必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x38C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x39C_RC013', 'C43x39C', '其他手术操作麻醉方式39', 'value_check', '其他手术操作麻醉方式39必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x39C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    'RULE_C43x40C_RC013', 'C43x40C', '其他手术操作麻醉方式40', 'value_check', '其他手术操作麻醉方式40必须在RC013字典范围内',
    -1.0, 'active', 'RC013', 'd_mr_other_21_40', 'C43x40C IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \'RC013\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);

