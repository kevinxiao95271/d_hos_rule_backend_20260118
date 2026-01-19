-- 创建跨字段约束规则表
CREATE TABLE IF NOT EXISTS kiro_qc_rule_cross (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    rule_code VARCHAR(64) NOT NULL UNIQUE COMMENT '规则编码',
    rule_name VARCHAR(200) NOT NULL COMMENT '规则名称',
    description TEXT NOT NULL COMMENT '规则描述',
    
    -- 规则类型
    cross_type VARCHAR(32) NOT NULL COMMENT '跨字段类型: field_pair, logic_check, age_gender, date_consistency',
    
    -- 主字段信息
    primary_field VARCHAR(64) NOT NULL COMMENT '主字段代码',
    primary_field_name VARCHAR(200) COMMENT '主字段名称',
    
    -- 关联字段信息 (JSON格式存储多个字段)
    related_fields JSON COMMENT '关联字段列表 [{"field":"C07x01C","name":"出院其他诊断名称1"}]',
    
    -- 约束条件 (JSON格式存储复杂条件)
    constraint_conditions JSON COMMENT '约束条件 {"type":"both_or_neither","logic":"AND"}',
    
    -- 逻辑表达式 (用于复杂逻辑判断)
    logic_expression TEXT COMMENT '逻辑表达式，如年龄性别限制等',
    
    -- 错误信息
    error_message TEXT COMMENT '违规时的错误信息',
    expected_value TEXT COMMENT '期望值描述',
    
    -- 规则配置
    deduct_score DECIMAL(10,2) DEFAULT 0.20 COMMENT '扣分',
    severity VARCHAR(16) DEFAULT 'warning' COMMENT '严重程度: error, warning, info',
    
    -- 适用范围
    source_tables VARCHAR(500) COMMENT '数据来源表',
    applicable_conditions TEXT COMMENT '适用条件',
    
    -- 状态管理
    status VARCHAR(16) DEFAULT 'active' COMMENT '状态: draft, active, inactive',
    priority INT DEFAULT 100 COMMENT '优先级',
    
    -- 审计字段
    created_by VARCHAR(64) COMMENT '创建人',
    updated_by VARCHAR(64) COMMENT '更新人',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引
    INDEX idx_rule_code (rule_code),
    INDEX idx_primary_field (primary_field),
    INDEX idx_cross_type (cross_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='跨字段约束规则表';

-- 插入示例跨字段规则
INSERT INTO kiro_qc_rule_cross (
    rule_code, description, cross_type, 
    primary_field, primary_field_name, related_fields, constraint_conditions,
    error_message, expected_value, deduct_score, source_tables
) VALUES 
-- 诊断编码与名称配对规则
('CROSS_C06x01C_C07x01C', '出院其他诊断编码1为空，但出院其他诊断名称1不为空，两者必须同时有值或同时为空',
 'field_pair', 'C06x01C', '出院其他诊断编码1',
 '[{"field":"C07x01C","name":"出院其他诊断名称1"}]',
 '{"type":"both_or_neither","logic":"AND"}',
 '诊断编码与名称必须同时填写或同时为空', '编码和名称同时有值或同时为空', 0.20, 'd_mr'),

('CROSS_C06x02C_C07x02C', '出院其他诊断编码2为空，但出院其他诊断名称2不为空，两者必须同时有值或同时为空',
 'field_pair', 'C06x02C', '出院其他诊断编码2',
 '[{"field":"C07x02C","name":"出院其他诊断名称2"}]',
 '{"type":"both_or_neither","logic":"AND"}',
 '诊断编码与名称必须同时填写或同时为空', '编码和名称同时有值或同时为空', 0.20, 'd_mr'),

-- 手术编码与名称配对规则
('CROSS_C14x01C_C15x01C', '主要手术操作编码为空，但主要手术操作名称不为空，两者必须同时有值或同时为空',
 'field_pair', 'C14x01C', '主要手术操作编码',
 '[{"field":"C15x01C","name":"主要手术操作名称"}]',
 '{"type":"both_or_neither","logic":"AND"}',
 '手术编码与名称必须同时填写或同时为空', '编码和名称同时有值或同时为空', 0.20, 'd_mr'),

-- 性别与诊断逻辑检查
('CROSS_C03C_GENDER_MALE', '出院主要诊断编码不符合逻辑判断，男性不允许编码妇科相关疾病',
 'age_gender', 'C03C', '出院主要诊断编码',
 '[{"field":"A12C","name":"性别"}]',
 '{"type":"gender_diagnosis","gender":"1","forbidden_codes":["A34","B37.3","C51-C58","C79.6","D06","D07.0-D07.3","D24-D28","D39","E28","E89.4","F52.5","F53","I86.3","L29.2","L70.5","M80.0-M80.1","M83.0","N70-N98","N99.2-N99.3","O00-O99","P54.6","Q50-Q52","R87","S31.4","S37.4-S37.6","T19.2-T19.3","T83.3","Z01.4","Z12.4","Z30.1","Z30.3","Z30.5","Z31.1-Z31.2","Z32-Z37","Z39","Z87.5","Z97.5"]}',
 '男性患者不应编码妇科相关疾病', '符合性别的诊断编码', 0.20, 'd_mr'),

('CROSS_C03C_GENDER_FEMALE', '出院主要诊断编码不符合逻辑判断，女性不允许编码男科相关疾病',
 'age_gender', 'C03C', '出院主要诊断编码',
 '[{"field":"A12C","name":"性别"}]',
 '{"type":"gender_diagnosis","gender":"2","forbidden_codes":["B26.0","C60-C63","D07.4-D07.6","D17.6","D29","D29.1","D40","E29","E89.5","F52.4","I86.1","K40.907","L29.1","N40-N51","Q53-Q55","R86","S31.2-S31.3","Z12.5"]}',
 '女性患者不应编码男科相关疾病', '符合性别的诊断编码', 0.20, 'd_mr'),

-- 年龄与诊断逻辑检查
('CROSS_C03C_AGE_CHILD', '出院主要诊断编码不符合逻辑判断，12岁以下儿童一般不应编码成人疾病',
 'age_gender', 'C03C', '出院主要诊断编码',
 '[{"field":"A13","name":"年龄"}]',
 '{"type":"age_diagnosis","age_limit":12,"comparison":"<","forbidden_codes":["C50-C63","D24-D29"]}',
 '12岁以下儿童不应编码成人相关疾病', '符合年龄的诊断编码', 0.20, 'd_mr'),

-- 手术与日期配对规则
('CROSS_C35x01C_C37x01', '其他手术1操作日期为空，但其他手术编码1不为空或其他手术操作名称1不为空',
 'field_pair', 'C35x01C', '其他手术操作编码1',
 '[{"field":"C37x01","name":"其他手术1操作日期"},{"field":"C36x01C","name":"其他手术操作名称1"}]',
 '{"type":"date_required","logic":"OR"}',
 '有手术编码或名称时必须填写手术日期', '手术编码、名称、日期保持一致', 0.20, 'd_mr');

-- 创建跨字段规则执行日志表
CREATE TABLE IF NOT EXISTS kiro_qc_cross_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    rule_id BIGINT NOT NULL COMMENT '规则ID',
    mr_key VARCHAR(128) NOT NULL COMMENT '病案键',
    execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '执行时间',
    result VARCHAR(16) NOT NULL COMMENT '结果: pass, fail, error',
    error_details TEXT COMMENT '错误详情',
    field_values JSON COMMENT '相关字段值',
    
    INDEX idx_rule_id (rule_id),
    INDEX idx_mr_key (mr_key),
    INDEX idx_execution_time (execution_time),
    FOREIGN KEY (rule_id) REFERENCES kiro_qc_rule_cross(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='跨字段规则执行日志表';