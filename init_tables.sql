-- 质控缺陷明细表
CREATE TABLE IF NOT EXISTS `kiro_qc_defect_detail` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `mr_key` varchar(64) NOT NULL COMMENT '病案唯一键 A48_A49',
  `a48` varchar(64) NOT NULL,
  `a49` varchar(64) NOT NULL,
  `rule_id` bigint NOT NULL COMMENT '规则ID',
  `rule_code` varchar(64) NOT NULL COMMENT '规则编码',
  `rule_name` varchar(200) DEFAULT NULL COMMENT '规则名称',
  `field_code` varchar(64) DEFAULT NULL COMMENT '字段编码',
  `field_name` varchar(200) DEFAULT NULL COMMENT '字段名称',
  `actual_value` text COMMENT '实际值',
  `expected_value` text COMMENT '预期值',
  `rule_description` text COMMENT '规则说明',
  `deduct_score` decimal(10,2) DEFAULT '0.00' COMMENT '扣分',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_mr_key` (`mr_key`),
  KEY `idx_a48_a49` (`a48`, `a49`),
  KEY `idx_rule_id` (`rule_id`),
  KEY `idx_field_code` (`field_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='质控缺陷明细表';
