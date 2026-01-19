CREATE TABLE IF NOT EXISTS `kiro_qc_rule` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `rule_code` varchar(64) NOT NULL COMMENT '规则编码',
  `field_name` varchar(200) DEFAULT NULL COMMENT '字段名称',
  `field_code` varchar(64) DEFAULT NULL COMMENT '字段编码',
  `table_name` varchar(64) DEFAULT NULL COMMENT '表名',
  `rule_type` varchar(32) DEFAULT NULL COMMENT '规则类型',
  `deduct_score` decimal(10,2) DEFAULT '0.00' COMMENT '扣分',
  `description` text COMMENT '规则描述',
  `urule_content` text COMMENT 'URule规则内容',
  `canonical_expr` text COMMENT '规范化表达式',
  `status` varchar(16) DEFAULT 'draft' COMMENT '状态: draft草稿, active正式',
  `source_tables` varchar(500) DEFAULT NULL COMMENT '源数据表，多个用逗号分隔',
  `dict_types` varchar(500) DEFAULT NULL COMMENT '值域数据集，多个用逗号分隔',
  `involved_tables` varchar(500) DEFAULT NULL COMMENT '涉及的表',
  `involved_fields` varchar(1000) DEFAULT NULL COMMENT '涉及的字段',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_rule_code` (`rule_code`),
  KEY `idx_field_code` (`field_code`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='质控规则表';

-- 交叉质控规则表（专门存放cross_check类规则）
CREATE TABLE IF NOT EXISTS `kiro_qc_rule_cross` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `rule_code` varchar(64) NOT NULL COMMENT '规则编码',
  `field_name` varchar(200) DEFAULT NULL COMMENT '字段名称',
  `field_code` varchar(64) DEFAULT NULL COMMENT '主字段编码',
  `table_name` varchar(64) DEFAULT NULL COMMENT '主表名',
  `rule_type` varchar(32) DEFAULT NULL COMMENT '规则类型',
  `deduct_score` decimal(10,2) DEFAULT '0.00' COMMENT '扣分',
  `description` text COMMENT '规则描述',
  `urule_content` text COMMENT 'URule规则内容',
  `canonical_expr` text COMMENT '规范化表达式',
  `status` varchar(16) DEFAULT 'draft' COMMENT '状态: draft草稿, active正式',
  `source_tables` varchar(500) DEFAULT NULL COMMENT '源数据表，多个用逗号分隔',
  `dict_types` varchar(500) DEFAULT NULL COMMENT '值域数据集，多个用逗号分隔',
  `involved_tables` varchar(500) DEFAULT NULL COMMENT '涉及的表',
  `involved_fields` varchar(1000) DEFAULT NULL COMMENT '涉及的字段',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_cross_rule_code` (`rule_code`),
  KEY `idx_cross_field_code` (`field_code`),
  KEY `idx_cross_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交叉质控规则表';

-- 字段映射表
CREATE TABLE IF NOT EXISTS `kiro_field_mapping` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `field_code` varchar(64) NOT NULL COMMENT '字段编码',
  `field_name` varchar(200) DEFAULT NULL COMMENT '字段名称',
  `table_name` varchar(64) NOT NULL COMMENT '表名',
  `column_name` varchar(64) NOT NULL COMMENT '列名',
  `data_type` varchar(32) DEFAULT NULL COMMENT '数据类型',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_field_table` (`field_code`, `table_name`),
  KEY `idx_field_code` (`field_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='字段映射表';

-- 质控缺陷明细表
CREATE TABLE IF NOT EXISTS `kiro_qc_defect_detail` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `mr_key` varchar(128) NOT NULL COMMENT '病案唯一键 A48_A49',
  `a48` varchar(100) NOT NULL,
  `a49` varchar(100) NOT NULL,
  `rule_id` bigint NOT NULL COMMENT '规则ID',
  `rule_code` varchar(64) NOT NULL COMMENT '规则编码',
  `field_code` varchar(64) DEFAULT NULL COMMENT '字段编码',
  `field_name` varchar(200) DEFAULT NULL COMMENT '字段名称',
  `actual_value` text COMMENT '实际值',
  `expected_value` text COMMENT '预期值',
  `rule_description` text COMMENT '规则说明',
  `deduct_score` decimal(10,2) DEFAULT '0.00' COMMENT '扣分',
  `check_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '检查时间',
  PRIMARY KEY (`id`),
  KEY `idx_mr_key` (`mr_key`),
  KEY `idx_a48_a49` (`a48`, `a49`),
  KEY `idx_rule_id` (`rule_id`),
  KEY `idx_field_code` (`field_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='质控缺陷明细表';

-- 病案质控结果表
CREATE TABLE IF NOT EXISTS `kiro_qc_case_result` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `mr_key` varchar(128) NOT NULL COMMENT '病案唯一键',
  `a48` varchar(100) NOT NULL,
  `a49` varchar(100) NOT NULL,
  `b15` varchar(40) DEFAULT NULL COMMENT '时间字段',
  `check_year` int DEFAULT NULL COMMENT '年份',
  `check_quarter` int DEFAULT NULL COMMENT '季度',
  `check_month` int DEFAULT NULL COMMENT '月份',
  `defect_count` int DEFAULT 0 COMMENT '缺陷数',
  `total_deduct` decimal(10,2) DEFAULT '0.00' COMMENT '总扣分',
  `final_score` decimal(6,2) DEFAULT '100.00' COMMENT '最终得分',
  `check_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '检查时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_mr_key` (`mr_key`),
  KEY `idx_a48_a49` (`a48`, `a49`),
  KEY `idx_year_quarter_month` (`check_year`, `check_quarter`, `check_month`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='病案质控结果表';

-- 批量质控汇总表
CREATE TABLE IF NOT EXISTS `kiro_qc_batch_summary` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `batch_key` varchar(64) NOT NULL COMMENT '批次键',
  `period_type` varchar(16) NOT NULL COMMENT '周期类型: year/quarter/month',
  `check_year` int NOT NULL COMMENT '年份',
  `check_quarter` int DEFAULT NULL COMMENT '季度',
  `check_month` int DEFAULT NULL COMMENT '月份',
  `case_count` int DEFAULT 0 COMMENT '病案数量',
  `total_defect_count` int DEFAULT 0 COMMENT '总缺陷数',
  `avg_defect` decimal(12,4) DEFAULT '0.0000' COMMENT '平均缺陷',
  `avg_score` decimal(6,2) DEFAULT '100.00' COMMENT '平均得分',
  `status` varchar(16) DEFAULT 'pending' COMMENT '状态: pending/processing/completed',
  `progress` int DEFAULT 0 COMMENT '进度百分比',
  `start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_batch_key` (`batch_key`),
  KEY `idx_period` (`period_type`, `check_year`, `check_quarter`, `check_month`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='批量质控汇总表';

-- 质控运行上下文表
CREATE TABLE IF NOT EXISTS `kiro_qc_run_context` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `context_key` varchar(64) NOT NULL COMMENT '上下文键',
  `start_date` varchar(40) DEFAULT NULL COMMENT '开始日期',
  `end_date` varchar(40) DEFAULT NULL COMMENT '结束日期',
  `last_used` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_context_key` (`context_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='质控运行上下文表';
