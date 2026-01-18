-- 自动生成的质控规则（修正版）
-- 生成时间: 2026-01-16 13:36:38
-- 高置信度规则: 214 条

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_A01_RC001', 'A01', '性别', 'value_check', 'A01 IN RC001',
    '性别必须在RC001字典范围内', 1, 'draft', 'd_mr', 'RC001',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_A02_RC002', 'A02', '婚姻状况', 'value_check', 'A02 IN RC002',
    '婚姻状况必须在RC002字典范围内', 1, 'draft', 'd_mr', 'RC002',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_A16_RANGE', 'A16', '住院天数', 'range_check', 'A16 >= 0 AND A16 <= 365',
    '住院天数应在0-365范围内', 2, 'draft', 'd_mr', '',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_A17_RC019', 'A17', '离院方式', 'value_check', 'A17 IN RC019',
    '离院方式必须在RC019字典范围内', 1, 'draft', 'd_mr', 'RC019',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_A20_RC030', 'A20', 'ABO血型', 'value_check', 'A20 IN RC030',
    'ABO血型必须在RC030字典范围内', 1, 'draft', 'd_mr', 'RC030',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_A22_RC011', 'A22', '病案质量', 'value_check', 'A22 IN RC011',
    '病案质量必须在RC011字典范围内', 1, 'draft', 'd_mr', 'RC011',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x01C_RC013', 'C06x01C', '出院其他诊断编码1 字符 ', 'value_check', 'C06x01C IN RC013',
    '出院其他诊断编码1 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x02C_RC013', 'C06x02C', '出院其他诊断编码2 字符 ', 'value_check', 'C06x02C IN RC013',
    '出院其他诊断编码2 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x03C_RC013', 'C06x03C', '出院其他诊断编码3 字符 ', 'value_check', 'C06x03C IN RC013',
    '出院其他诊断编码3 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x04C_RC013', 'C06x04C', '出院其他诊断编码4 字符 ', 'value_check', 'C06x04C IN RC013',
    '出院其他诊断编码4 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x05C_RC013', 'C06x05C', '出院其他诊断编码5 字符 ', 'value_check', 'C06x05C IN RC013',
    '出院其他诊断编码5 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x06C_RC013', 'C06x06C', '出院其他诊断编码6 字符 ', 'value_check', 'C06x06C IN RC013',
    '出院其他诊断编码6 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x07C_RC013', 'C06x07C', '出院其他诊断编码7 字符 ', 'value_check', 'C06x07C IN RC013',
    '出院其他诊断编码7 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x08C_RC013', 'C06x08C', '出院其他诊断编码8 字符 ', 'value_check', 'C06x08C IN RC013',
    '出院其他诊断编码8 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x09C_RC013', 'C06x09C', '出院其他诊断编码9 字符 ', 'value_check', 'C06x09C IN RC013',
    '出院其他诊断编码9 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x10C_RC013', 'C06x10C', '出院其他诊断编码10 字符 ', 'value_check', 'C06x10C IN RC013',
    '出院其他诊断编码10 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x11C_RC013', 'C06x11C', '出院其他诊断编码11 字符 ', 'value_check', 'C06x11C IN RC013',
    '出院其他诊断编码11 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x12C_RC013', 'C06x12C', '出院其他诊断编码12 字符 ', 'value_check', 'C06x12C IN RC013',
    '出院其他诊断编码12 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x13C_RC013', 'C06x13C', '出院其他诊断编码13 字符 ', 'value_check', 'C06x13C IN RC013',
    '出院其他诊断编码13 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x14C_RC013', 'C06x14C', '出院其他诊断编码14 字符 ', 'value_check', 'C06x14C IN RC013',
    '出院其他诊断编码14 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x15C_RC013', 'C06x15C', '出院其他诊断编码15 字符 ', 'value_check', 'C06x15C IN RC013',
    '出院其他诊断编码15 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x16C_RC013', 'C06x16C', '出院其他诊断编码16 字符 ', 'value_check', 'C06x16C IN RC013',
    '出院其他诊断编码16 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x17C_RC013', 'C06x17C', '出院其他诊断编码17 字符 ', 'value_check', 'C06x17C IN RC013',
    '出院其他诊断编码17 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x18C_RC013', 'C06x18C', '出院其他诊断编码18 字符 ', 'value_check', 'C06x18C IN RC013',
    '出院其他诊断编码18 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x19C_RC013', 'C06x19C', '出院其他诊断编码19 字符 ', 'value_check', 'C06x19C IN RC013',
    '出院其他诊断编码19 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x20C_RC013', 'C06x20C', '出院其他诊断编码20 字符 ', 'value_check', 'C06x20C IN RC013',
    '出院其他诊断编码20 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x21C_RC013', 'C06x21C', '出院其他诊断编码21 字符 ', 'value_check', 'C06x21C IN RC013',
    '出院其他诊断编码21 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x22C_RC013', 'C06x22C', '出院其他诊断编码22 字符 ', 'value_check', 'C06x22C IN RC013',
    '出院其他诊断编码22 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x23C_RC013', 'C06x23C', '出院其他诊断编码23 字符 ', 'value_check', 'C06x23C IN RC013',
    '出院其他诊断编码23 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x24C_RC013', 'C06x24C', '出院其他诊断编码24 字符 ', 'value_check', 'C06x24C IN RC013',
    '出院其他诊断编码24 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x25C_RC013', 'C06x25C', '出院其他诊断编码25 字符 ', 'value_check', 'C06x25C IN RC013',
    '出院其他诊断编码25 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x26C_RC013', 'C06x26C', '出院其他诊断编码26 字符 ', 'value_check', 'C06x26C IN RC013',
    '出院其他诊断编码26 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x27C_RC013', 'C06x27C', '出院其他诊断编码27  字符 ', 'value_check', 'C06x27C IN RC013',
    '出院其他诊断编码27  字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x28C_RC013', 'C06x28C', '出院其他诊断编码28 字符 ', 'value_check', 'C06x28C IN RC013',
    '出院其他诊断编码28 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x29C_RC013', 'C06x29C', '出院其他诊断编码29 字符 ', 'value_check', 'C06x29C IN RC013',
    '出院其他诊断编码29 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x30C_RC013', 'C06x30C', '出院其他诊断编码30 字符 ', 'value_check', 'C06x30C IN RC013',
    '出院其他诊断编码30 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x31C_RC013', 'C06x31C', '出院其他诊断编码31 字符 ', 'value_check', 'C06x31C IN RC013',
    '出院其他诊断编码31 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x32C_RC013', 'C06x32C', '出院其他诊断编码32 字符 ', 'value_check', 'C06x32C IN RC013',
    '出院其他诊断编码32 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x33C_RC013', 'C06x33C', '出院其他诊断编码33 字符 ', 'value_check', 'C06x33C IN RC013',
    '出院其他诊断编码33 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x34C_RC013', 'C06x34C', '出院其他诊断编码34 字符 ', 'value_check', 'C06x34C IN RC013',
    '出院其他诊断编码34 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x35C_RC013', 'C06x35C', '出院其他诊断编码35 字符 ', 'value_check', 'C06x35C IN RC013',
    '出院其他诊断编码35 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x36C_RC013', 'C06x36C', '出院其他诊断编码36 字符 ', 'value_check', 'C06x36C IN RC013',
    '出院其他诊断编码36 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x37C_RC013', 'C06x37C', '出院其他诊断编码37 字符 ', 'value_check', 'C06x37C IN RC013',
    '出院其他诊断编码37 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x38C_RC013', 'C06x38C', '出院其他诊断编码38 字符 ', 'value_check', 'C06x38C IN RC013',
    '出院其他诊断编码38 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x39C_RC013', 'C06x39C', '出院其他诊断编码39 字符 ', 'value_check', 'C06x39C IN RC013',
    '出院其他诊断编码39 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C06x40C_RC013', 'C06x40C', '出院其他诊断编码40 字符 ', 'value_check', 'C06x40C IN RC013',
    '出院其他诊断编码40 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x01C_RC013', 'C08x01C', '出院其他诊断入院病情1 字符 ', 'value_check', 'C08x01C IN RC013',
    '出院其他诊断入院病情1 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x02C_RC013', 'C08x02C', '出院其他诊断入院病情2 字符 ', 'value_check', 'C08x02C IN RC013',
    '出院其他诊断入院病情2 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x03C_RC013', 'C08x03C', '出院其他诊断入院病情3 字符 ', 'value_check', 'C08x03C IN RC013',
    '出院其他诊断入院病情3 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x04C_RC013', 'C08x04C', '出院其他诊断入院病情4 字符 ', 'value_check', 'C08x04C IN RC013',
    '出院其他诊断入院病情4 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x05C_RC013', 'C08x05C', '出院其他诊断入院病情5 字符 ', 'value_check', 'C08x05C IN RC013',
    '出院其他诊断入院病情5 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x06C_RC013', 'C08x06C', '出院其他诊断入院病情6 字符 ', 'value_check', 'C08x06C IN RC013',
    '出院其他诊断入院病情6 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x07C_RC013', 'C08x07C', '出院其他诊断入院病情7 字符 ', 'value_check', 'C08x07C IN RC013',
    '出院其他诊断入院病情7 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x08C_RC013', 'C08x08C', '出院其他诊断入院病情8 字符 ', 'value_check', 'C08x08C IN RC013',
    '出院其他诊断入院病情8 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x09C_RC013', 'C08x09C', '出院其他诊断入院病情9 字符 ', 'value_check', 'C08x09C IN RC013',
    '出院其他诊断入院病情9 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x10C_RC013', 'C08x10C', '出院其他诊断入院病情10 字符 ', 'value_check', 'C08x10C IN RC013',
    '出院其他诊断入院病情10 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x11C_RC013', 'C08x11C', '出院其他诊断入院病情11 字符 ', 'value_check', 'C08x11C IN RC013',
    '出院其他诊断入院病情11 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x12C_RC013', 'C08x12C', '出院其他诊断入院病情12 字符 ', 'value_check', 'C08x12C IN RC013',
    '出院其他诊断入院病情12 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x13C_RC013', 'C08x13C', '出院其他诊断入院病情13 字符 ', 'value_check', 'C08x13C IN RC013',
    '出院其他诊断入院病情13 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x14C_RC013', 'C08x14C', '出院其他诊断入院病情14 字符 ', 'value_check', 'C08x14C IN RC013',
    '出院其他诊断入院病情14 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x15C_RC013', 'C08x15C', '出院其他诊断入院病情15 字符 ', 'value_check', 'C08x15C IN RC013',
    '出院其他诊断入院病情15 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x16C_RC013', 'C08x16C', '出院其他诊断入院病情16 字符 ', 'value_check', 'C08x16C IN RC013',
    '出院其他诊断入院病情16 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x17C_RC013', 'C08x17C', '出院其他诊断入院病情17 字符 ', 'value_check', 'C08x17C IN RC013',
    '出院其他诊断入院病情17 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x18C_RC013', 'C08x18C', '出院其他诊断入院病情18 字符 ', 'value_check', 'C08x18C IN RC013',
    '出院其他诊断入院病情18 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x19C_RC013', 'C08x19C', '出院其他诊断入院病情19 字符 ', 'value_check', 'C08x19C IN RC013',
    '出院其他诊断入院病情19 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x20C_RC013', 'C08x20C', '出院其他诊断入院病情20 字符 ', 'value_check', 'C08x20C IN RC013',
    '出院其他诊断入院病情20 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x21C_RC013', 'C08x21C', '出院其他诊断入院病情21 字符 ', 'value_check', 'C08x21C IN RC013',
    '出院其他诊断入院病情21 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x22C_RC013', 'C08x22C', '出院其他诊断入院病情22 字符 ', 'value_check', 'C08x22C IN RC013',
    '出院其他诊断入院病情22 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x23C_RC013', 'C08x23C', '出院其他诊断入院病情23 字符 ', 'value_check', 'C08x23C IN RC013',
    '出院其他诊断入院病情23 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x24C_RC013', 'C08x24C', '出院其他诊断入院病情24 字符 ', 'value_check', 'C08x24C IN RC013',
    '出院其他诊断入院病情24 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x25C_RC013', 'C08x25C', '出院其他诊断入院病情25 字符 ', 'value_check', 'C08x25C IN RC013',
    '出院其他诊断入院病情25 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x26C_RC013', 'C08x26C', '出院其他诊断入院病情26 字符 ', 'value_check', 'C08x26C IN RC013',
    '出院其他诊断入院病情26 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x27C_RC013', 'C08x27C', '出院其他诊断入院病情27 字符 ', 'value_check', 'C08x27C IN RC013',
    '出院其他诊断入院病情27 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x28C_RC013', 'C08x28C', '出院其他诊断入院病情28 字符 ', 'value_check', 'C08x28C IN RC013',
    '出院其他诊断入院病情28 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x29C_RC013', 'C08x29C', '出院其他诊断入院病情29 字符 ', 'value_check', 'C08x29C IN RC013',
    '出院其他诊断入院病情29 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x30C_RC013', 'C08x30C', '出院其他诊断入院病情30 字符 ', 'value_check', 'C08x30C IN RC013',
    '出院其他诊断入院病情30 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x31C_RC013', 'C08x31C', '出院其他诊断入院病情31 字符 ', 'value_check', 'C08x31C IN RC013',
    '出院其他诊断入院病情31 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x32C_RC013', 'C08x32C', '出院其他诊断入院病情32 字符 ', 'value_check', 'C08x32C IN RC013',
    '出院其他诊断入院病情32 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x33C_RC013', 'C08x33C', '出院其他诊断入院病情33 字符 ', 'value_check', 'C08x33C IN RC013',
    '出院其他诊断入院病情33 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x34C_RC013', 'C08x34C', '出院其他诊断入院病情34 字符 ', 'value_check', 'C08x34C IN RC013',
    '出院其他诊断入院病情34 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x35C_RC013', 'C08x35C', '出院其他诊断入院病情35 字符 ', 'value_check', 'C08x35C IN RC013',
    '出院其他诊断入院病情35 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x36C_RC013', 'C08x36C', '出院其他诊断入院病情36 字符 ', 'value_check', 'C08x36C IN RC013',
    '出院其他诊断入院病情36 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x37C_RC013', 'C08x37C', '出院其他诊断入院病情37 字符 ', 'value_check', 'C08x37C IN RC013',
    '出院其他诊断入院病情37 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x38C_RC013', 'C08x38C', '出院其他诊断入院病情38 字符 ', 'value_check', 'C08x38C IN RC013',
    '出院其他诊断入院病情38 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x39C_RC013', 'C08x39C', '出院其他诊断入院病情39 字符 ', 'value_check', 'C08x39C IN RC013',
    '出院其他诊断入院病情39 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C08x40C_RC013', 'C08x40C', '出院其他诊断入院病情40 字符 ', 'value_check', 'C08x40C IN RC013',
    '出院其他诊断入院病情40 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C14x01C_RC013', 'C14x01C', '主要手术操作编码 字符 ', 'value_check', 'C14x01C IN RC013',
    '主要手术操作编码 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C21x01C_RC013', 'C21x01C', '主要手术操作切口愈合等级 字符 ', 'value_check', 'C21x01C IN RC013',
    '主要手术操作切口愈合等级 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C22x01C_RC013', 'C22x01C', '主要手术操作麻醉方式 字符 ', 'value_check', 'C22x01C IN RC013',
    '主要手术操作麻醉方式 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x01C_RC013', 'C35x01C', '其他手术操作编码1 字符 ', 'value_check', 'C35x01C IN RC013',
    '其他手术操作编码1 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x02C_RC013', 'C35x02C', '其他手术操作编码2 字符 ', 'value_check', 'C35x02C IN RC013',
    '其他手术操作编码2 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x03C_RC013', 'C35x03C', '其他手术操作编码3 字符 ', 'value_check', 'C35x03C IN RC013',
    '其他手术操作编码3 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x04C_RC013', 'C35x04C', '其他手术操作编码4 字符 ', 'value_check', 'C35x04C IN RC013',
    '其他手术操作编码4 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x05C_RC013', 'C35x05C', '其他手术操作编码5 字符 ', 'value_check', 'C35x05C IN RC013',
    '其他手术操作编码5 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x06C_RC013', 'C35x06C', '其他手术操作编码6 字符 ', 'value_check', 'C35x06C IN RC013',
    '其他手术操作编码6 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x07C_RC013', 'C35x07C', '其他手术操作编码7 字符 ', 'value_check', 'C35x07C IN RC013',
    '其他手术操作编码7 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x08C_RC013', 'C35x08C', '其他手术操作编码8 字符 ', 'value_check', 'C35x08C IN RC013',
    '其他手术操作编码8 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x09C_RC013', 'C35x09C', '其他手术操作编码9 字符 ', 'value_check', 'C35x09C IN RC013',
    '其他手术操作编码9 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x10C_RC013', 'C35x10C', '其他手术操作编码10 字符 ', 'value_check', 'C35x10C IN RC013',
    '其他手术操作编码10 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x11C_RC013', 'C35x11C', '其他手术操作编码11 字符 ', 'value_check', 'C35x11C IN RC013',
    '其他手术操作编码11 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x12C_RC013', 'C35x12C', '其他手术操作编码12 字符 ', 'value_check', 'C35x12C IN RC013',
    '其他手术操作编码12 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x13C_RC013', 'C35x13C', '其他手术操作编码13 字符 ', 'value_check', 'C35x13C IN RC013',
    '其他手术操作编码13 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x14C_RC013', 'C35x14C', '其他手术操作编码14 字符 ', 'value_check', 'C35x14C IN RC013',
    '其他手术操作编码14 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x15C_RC013', 'C35x15C', '其他手术操作编码15 字符 ', 'value_check', 'C35x15C IN RC013',
    '其他手术操作编码15 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x16C_RC013', 'C35x16C', '其他手术操作编码16 字符 ', 'value_check', 'C35x16C IN RC013',
    '其他手术操作编码16 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x17C_RC013', 'C35x17C', '其他手术操作编码17 字符 ', 'value_check', 'C35x17C IN RC013',
    '其他手术操作编码17 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x18C_RC013', 'C35x18C', '其他手术操作编码18 字符 ', 'value_check', 'C35x18C IN RC013',
    '其他手术操作编码18 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x19C_RC013', 'C35x19C', '其他手术操作编码19 字符 ', 'value_check', 'C35x19C IN RC013',
    '其他手术操作编码19 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x20C_RC013', 'C35x20C', '其他手术操作编码20 字符 ', 'value_check', 'C35x20C IN RC013',
    '其他手术操作编码20 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x21C_RC013', 'C35x21C', '其他手术操作编码21 字符 ', 'value_check', 'C35x21C IN RC013',
    '其他手术操作编码21 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x22C_RC013', 'C35x22C', '其他手术操作编码22 字符 ', 'value_check', 'C35x22C IN RC013',
    '其他手术操作编码22 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x23C_RC013', 'C35x23C', '其他手术操作编码23 字符 ', 'value_check', 'C35x23C IN RC013',
    '其他手术操作编码23 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x24C_RC013', 'C35x24C', '其他手术操作编码24 字符 ', 'value_check', 'C35x24C IN RC013',
    '其他手术操作编码24 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x25C_RC013', 'C35x25C', '其他手术操作编码25 字符 ', 'value_check', 'C35x25C IN RC013',
    '其他手术操作编码25 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x26C_RC013', 'C35x26C', '其他手术操作编码26 字符 ', 'value_check', 'C35x26C IN RC013',
    '其他手术操作编码26 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x27C_RC013', 'C35x27C', '其他手术操作编码27 字符 ', 'value_check', 'C35x27C IN RC013',
    '其他手术操作编码27 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x28C_RC013', 'C35x28C', '其他手术操作编码28 字符 ', 'value_check', 'C35x28C IN RC013',
    '其他手术操作编码28 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x29C_RC013', 'C35x29C', '其他手术操作编码29 字符 ', 'value_check', 'C35x29C IN RC013',
    '其他手术操作编码29 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x30C_RC013', 'C35x30C', '其他手术操作编码30 字符 ', 'value_check', 'C35x30C IN RC013',
    '其他手术操作编码30 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x31C_RC013', 'C35x31C', '其他手术操作编码31 字符 ', 'value_check', 'C35x31C IN RC013',
    '其他手术操作编码31 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x32C_RC013', 'C35x32C', '其他手术操作编码32 字符 ', 'value_check', 'C35x32C IN RC013',
    '其他手术操作编码32 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x33C_RC013', 'C35x33C', '其他手术操作编码33 字符 ', 'value_check', 'C35x33C IN RC013',
    '其他手术操作编码33 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x34C_RC013', 'C35x34C', '其他手术操作编码34 字符 ', 'value_check', 'C35x34C IN RC013',
    '其他手术操作编码34 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x35C_RC013', 'C35x35C', '其他手术操作编码35 字符 ', 'value_check', 'C35x35C IN RC013',
    '其他手术操作编码35 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x36C_RC013', 'C35x36C', '其他手术操作编码36 字符 ', 'value_check', 'C35x36C IN RC013',
    '其他手术操作编码36 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x37C_RC013', 'C35x37C', '其他手术操作编码37 字符 ', 'value_check', 'C35x37C IN RC013',
    '其他手术操作编码37 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x38C_RC013', 'C35x38C', '其他手术操作编码38 字符 ', 'value_check', 'C35x38C IN RC013',
    '其他手术操作编码38 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x39C_RC013', 'C35x39C', '其他手术操作编码39 字符 ', 'value_check', 'C35x39C IN RC013',
    '其他手术操作编码39 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C35x40C_RC013', 'C35x40C', '其他手术操作编码40 字符 ', 'value_check', 'C35x40C IN RC013',
    '其他手术操作编码40 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x01C_RC013', 'C42x01C', '其他手术操作切口愈合等级1 字符 ', 'value_check', 'C42x01C IN RC013',
    '其他手术操作切口愈合等级1 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x02C_RC013', 'C42x02C', '其他手术操作切口愈合等级2 字符 ', 'value_check', 'C42x02C IN RC013',
    '其他手术操作切口愈合等级2 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x03C_RC013', 'C42x03C', '其他手术操作切口愈合等级3 字符 ', 'value_check', 'C42x03C IN RC013',
    '其他手术操作切口愈合等级3 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x04C_RC013', 'C42x04C', '其他手术操作切口愈合等级4 字符 ', 'value_check', 'C42x04C IN RC013',
    '其他手术操作切口愈合等级4 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x05C_RC013', 'C42x05C', '其他手术操作切口愈合等级5 字符 ', 'value_check', 'C42x05C IN RC013',
    '其他手术操作切口愈合等级5 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x06C_RC013', 'C42x06C', '其他手术操作切口愈合等级6 字符 ', 'value_check', 'C42x06C IN RC013',
    '其他手术操作切口愈合等级6 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x07C_RC013', 'C42x07C', '其他手术操作切口愈合等级7 字符 ', 'value_check', 'C42x07C IN RC013',
    '其他手术操作切口愈合等级7 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x08C_RC013', 'C42x08C', '其他手术操作切口愈合等级8 字符 ', 'value_check', 'C42x08C IN RC013',
    '其他手术操作切口愈合等级8 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x09C_RC013', 'C42x09C', '其他手术操作切口愈合等级9 字符 ', 'value_check', 'C42x09C IN RC013',
    '其他手术操作切口愈合等级9 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x10C_RC013', 'C42x10C', '其他手术操作切口愈合等级10 字符 ', 'value_check', 'C42x10C IN RC013',
    '其他手术操作切口愈合等级10 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x11C_RC013', 'C42x11C', '其他手术操作切口愈合等级11 字符 ', 'value_check', 'C42x11C IN RC013',
    '其他手术操作切口愈合等级11 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x12C_RC013', 'C42x12C', '其他手术操作切口愈合等级12 字符 ', 'value_check', 'C42x12C IN RC013',
    '其他手术操作切口愈合等级12 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x13C_RC013', 'C42x13C', '其他手术操作切口愈合等级13 字符 ', 'value_check', 'C42x13C IN RC013',
    '其他手术操作切口愈合等级13 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x14C_RC013', 'C42x14C', '其他手术操作切口愈合等级14 字符 ', 'value_check', 'C42x14C IN RC013',
    '其他手术操作切口愈合等级14 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x15C_RC013', 'C42x15C', '其他手术操作切口愈合等级15 字符 ', 'value_check', 'C42x15C IN RC013',
    '其他手术操作切口愈合等级15 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x16C_RC013', 'C42x16C', '其他手术操作切口愈合等级16 字符 ', 'value_check', 'C42x16C IN RC013',
    '其他手术操作切口愈合等级16 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x17C_RC013', 'C42x17C', '其他手术操作切口愈合等级17 字符 ', 'value_check', 'C42x17C IN RC013',
    '其他手术操作切口愈合等级17 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x18C_RC013', 'C42x18C', '其他手术操作切口愈合等级18 字符 ', 'value_check', 'C42x18C IN RC013',
    '其他手术操作切口愈合等级18 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x19C_RC013', 'C42x19C', '其他手术操作切口愈合等级19 字符 ', 'value_check', 'C42x19C IN RC013',
    '其他手术操作切口愈合等级19 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x20C_RC013', 'C42x20C', '其他手术操作切口愈合等级20 字符 ', 'value_check', 'C42x20C IN RC013',
    '其他手术操作切口愈合等级20 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x21C_RC013', 'C42x21C', '其他手术操作切口愈合等级21 字符 ', 'value_check', 'C42x21C IN RC013',
    '其他手术操作切口愈合等级21 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x22C_RC013', 'C42x22C', '其他手术操作切口愈合等级22 字符 ', 'value_check', 'C42x22C IN RC013',
    '其他手术操作切口愈合等级22 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x23C_RC013', 'C42x23C', '其他手术操作切口愈合等级23 字符 ', 'value_check', 'C42x23C IN RC013',
    '其他手术操作切口愈合等级23 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x24C_RC013', 'C42x24C', '其他手术操作切口愈合等级24 字符 ', 'value_check', 'C42x24C IN RC013',
    '其他手术操作切口愈合等级24 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x25C_RC013', 'C42x25C', '其他手术操作切口愈合等级25 字符 ', 'value_check', 'C42x25C IN RC013',
    '其他手术操作切口愈合等级25 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x26C_RC013', 'C42x26C', '其他手术操作切口愈合等级26 字符 ', 'value_check', 'C42x26C IN RC013',
    '其他手术操作切口愈合等级26 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x27C_RC013', 'C42x27C', '其他手术操作切口愈合等级27 字符 ', 'value_check', 'C42x27C IN RC013',
    '其他手术操作切口愈合等级27 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x28C_RC013', 'C42x28C', '其他手术操作切口愈合等级28 字符 ', 'value_check', 'C42x28C IN RC013',
    '其他手术操作切口愈合等级28 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x29C_RC013', 'C42x29C', '其他手术操作切口愈合等级29 字符 ', 'value_check', 'C42x29C IN RC013',
    '其他手术操作切口愈合等级29 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x30C_RC013', 'C42x30C', '其他手术操作切口愈合等级30 字符 ', 'value_check', 'C42x30C IN RC013',
    '其他手术操作切口愈合等级30 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x31C_RC013', 'C42x31C', '其他手术操作切口愈合等级31 字符 ', 'value_check', 'C42x31C IN RC013',
    '其他手术操作切口愈合等级31 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x32C_RC013', 'C42x32C', '其他手术操作切口愈合等级32 字符 ', 'value_check', 'C42x32C IN RC013',
    '其他手术操作切口愈合等级32 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x33C_RC013', 'C42x33C', '其他手术操作切口愈合等级33 字符 ', 'value_check', 'C42x33C IN RC013',
    '其他手术操作切口愈合等级33 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x34C_RC013', 'C42x34C', '其他手术操作切口愈合等级34 字符 ', 'value_check', 'C42x34C IN RC013',
    '其他手术操作切口愈合等级34 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x35C_RC013', 'C42x35C', '其他手术操作切口愈合等级35 字符 ', 'value_check', 'C42x35C IN RC013',
    '其他手术操作切口愈合等级35 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x36C_RC013', 'C42x36C', '其他手术操作切口愈合等级36 字符 ', 'value_check', 'C42x36C IN RC013',
    '其他手术操作切口愈合等级36 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x37C_RC013', 'C42x37C', '其他手术操作切口愈合等级37 字符 ', 'value_check', 'C42x37C IN RC013',
    '其他手术操作切口愈合等级37 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x38C_RC013', 'C42x38C', '其他手术操作切口愈合等级38 字符 ', 'value_check', 'C42x38C IN RC013',
    '其他手术操作切口愈合等级38 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x39C_RC013', 'C42x39C', '其他手术操作切口愈合等级39 字符 ', 'value_check', 'C42x39C IN RC013',
    '其他手术操作切口愈合等级39 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C42x40C_RC013', 'C42x40C', '其他手术操作切口愈合等级40 字符 ', 'value_check', 'C42x40C IN RC013',
    '其他手术操作切口愈合等级40 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x01C_RC013', 'C43x01C', '其他手术操作麻醉方式1 字符 ', 'value_check', 'C43x01C IN RC013',
    '其他手术操作麻醉方式1 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x02C_RC013', 'C43x02C', '其他手术操作麻醉方式2 字符 ', 'value_check', 'C43x02C IN RC013',
    '其他手术操作麻醉方式2 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x03C_RC013', 'C43x03C', '其他手术操作麻醉方式3 字符 ', 'value_check', 'C43x03C IN RC013',
    '其他手术操作麻醉方式3 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x04C_RC013', 'C43x04C', '其他手术操作麻醉方式4 字符 ', 'value_check', 'C43x04C IN RC013',
    '其他手术操作麻醉方式4 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x05C_RC013', 'C43x05C', '其他手术操作麻醉方式5 字符 ', 'value_check', 'C43x05C IN RC013',
    '其他手术操作麻醉方式5 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x06C_RC013', 'C43x06C', '其他手术操作麻醉方式6 字符 ', 'value_check', 'C43x06C IN RC013',
    '其他手术操作麻醉方式6 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x07C_RC013', 'C43x07C', '其他手术操作麻醉方式7 字符 ', 'value_check', 'C43x07C IN RC013',
    '其他手术操作麻醉方式7 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x08C_RC013', 'C43x08C', '其他手术操作麻醉方式8 字符 ', 'value_check', 'C43x08C IN RC013',
    '其他手术操作麻醉方式8 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x09C_RC013', 'C43x09C', '其他手术操作麻醉方式9 字符 ', 'value_check', 'C43x09C IN RC013',
    '其他手术操作麻醉方式9 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x10C_RC013', 'C43x10C', '其他手术操作麻醉方式10 字符 ', 'value_check', 'C43x10C IN RC013',
    '其他手术操作麻醉方式10 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x11C_RC013', 'C43x11C', '其他手术操作麻醉方式11 字符 ', 'value_check', 'C43x11C IN RC013',
    '其他手术操作麻醉方式11 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x12C_RC013', 'C43x12C', '其他手术操作麻醉方式12 字符 ', 'value_check', 'C43x12C IN RC013',
    '其他手术操作麻醉方式12 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x13C_RC013', 'C43x13C', '其他手术操作麻醉方式13 字符 ', 'value_check', 'C43x13C IN RC013',
    '其他手术操作麻醉方式13 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x14C_RC013', 'C43x14C', '其他手术操作麻醉方式14 字符 ', 'value_check', 'C43x14C IN RC013',
    '其他手术操作麻醉方式14 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x15C_RC013', 'C43x15C', '其他手术操作麻醉方式15 字符 ', 'value_check', 'C43x15C IN RC013',
    '其他手术操作麻醉方式15 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x16C_RC013', 'C43x16C', '其他手术操作麻醉方式16 字符 ', 'value_check', 'C43x16C IN RC013',
    '其他手术操作麻醉方式16 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x17C_RC013', 'C43x17C', '其他手术操作麻醉方式17 字符 ', 'value_check', 'C43x17C IN RC013',
    '其他手术操作麻醉方式17 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x18C_RC013', 'C43x18C', '其他手术操作麻醉方式18 字符 ', 'value_check', 'C43x18C IN RC013',
    '其他手术操作麻醉方式18 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x19C_RC013', 'C43x19C', '其他手术操作麻醉方式19 字符 ', 'value_check', 'C43x19C IN RC013',
    '其他手术操作麻醉方式19 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x20C_RC013', 'C43x20C', '其他手术操作麻醉方式20 字符 ', 'value_check', 'C43x20C IN RC013',
    '其他手术操作麻醉方式20 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_1_20', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x21C_RC013', 'C43x21C', '其他手术操作麻醉方式21 字符 ', 'value_check', 'C43x21C IN RC013',
    '其他手术操作麻醉方式21 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x22C_RC013', 'C43x22C', '其他手术操作麻醉方式22 字符 ', 'value_check', 'C43x22C IN RC013',
    '其他手术操作麻醉方式22 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x23C_RC013', 'C43x23C', '其他手术操作麻醉方式23 字符 ', 'value_check', 'C43x23C IN RC013',
    '其他手术操作麻醉方式23 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x24C_RC013', 'C43x24C', '其他手术操作麻醉方式24 字符 ', 'value_check', 'C43x24C IN RC013',
    '其他手术操作麻醉方式24 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x25C_RC013', 'C43x25C', '其他手术操作麻醉方式25 字符 ', 'value_check', 'C43x25C IN RC013',
    '其他手术操作麻醉方式25 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x26C_RC013', 'C43x26C', '其他手术操作麻醉方式26 字符 ', 'value_check', 'C43x26C IN RC013',
    '其他手术操作麻醉方式26 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x27C_RC013', 'C43x27C', '其他手术操作麻醉方式27 字符 ', 'value_check', 'C43x27C IN RC013',
    '其他手术操作麻醉方式27 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x28C_RC013', 'C43x28C', '其他手术操作麻醉方式28 字符 ', 'value_check', 'C43x28C IN RC013',
    '其他手术操作麻醉方式28 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x29C_RC013', 'C43x29C', '其他手术操作麻醉方式29 字符 ', 'value_check', 'C43x29C IN RC013',
    '其他手术操作麻醉方式29 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x30C_RC013', 'C43x30C', '其他手术操作麻醉方式30 字符 ', 'value_check', 'C43x30C IN RC013',
    '其他手术操作麻醉方式30 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x31C_RC013', 'C43x31C', '其他手术操作麻醉方式31 字符 ', 'value_check', 'C43x31C IN RC013',
    '其他手术操作麻醉方式31 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x32C_RC013', 'C43x32C', '其他手术操作麻醉方式32 字符 ', 'value_check', 'C43x32C IN RC013',
    '其他手术操作麻醉方式32 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x33C_RC013', 'C43x33C', '其他手术操作麻醉方式33 字符 ', 'value_check', 'C43x33C IN RC013',
    '其他手术操作麻醉方式33 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x34C_RC013', 'C43x34C', '其他手术操作麻醉方式34 字符 ', 'value_check', 'C43x34C IN RC013',
    '其他手术操作麻醉方式34 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x35C_RC013', 'C43x35C', '其他手术操作麻醉方式35 字符 ', 'value_check', 'C43x35C IN RC013',
    '其他手术操作麻醉方式35 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x36C_RC013', 'C43x36C', '其他手术操作麻醉方式36 字符 ', 'value_check', 'C43x36C IN RC013',
    '其他手术操作麻醉方式36 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x37C_RC013', 'C43x37C', '其他手术操作麻醉方式37 字符 ', 'value_check', 'C43x37C IN RC013',
    '其他手术操作麻醉方式37 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x38C_RC013', 'C43x38C', '其他手术操作麻醉方式38 字符 ', 'value_check', 'C43x38C IN RC013',
    '其他手术操作麻醉方式38 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x39C_RC013', 'C43x39C', '其他手术操作麻醉方式39 字符 ', 'value_check', 'C43x39C IN RC013',
    '其他手术操作麻醉方式39 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C43x40C_RC013', 'C43x40C', '其他手术操作麻醉方式40 字符 ', 'value_check', 'C43x40C IN RC013',
    '其他手术操作麻醉方式40 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr_other_21_40', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C48x01C_RC013', 'C48x01C', '重症监护室名称1 字符 ', 'value_check', 'C48x01C IN RC013',
    '重症监护室名称1 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C48x02C_RC013', 'C48x02C', '重症监护室名称2 字符 ', 'value_check', 'C48x02C IN RC013',
    '重症监护室名称2 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C48x03C_RC013', 'C48x03C', '重症监护室名称3 字符 ', 'value_check', 'C48x03C IN RC013',
    '重症监护室名称3 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C48x04C_RC013', 'C48x04C', '重症监护室名称4 字符 ', 'value_check', 'C48x04C IN RC013',
    '重症监护室名称4 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, canonical_expr,
    description, deduct_score, status, source_tables, dict_types,
    created_at, updated_at
) VALUES (
    'RULE_C48x05C_RC013', 'C48x05C', '重症监护室名称5 字符 ', 'value_check', 'C48x05C IN RC013',
    '重症监护室名称5 字符 必须在RC013字典范围内', 1, 'draft', 'd_mr', 'RC013',
    NOW(), NOW()
);

