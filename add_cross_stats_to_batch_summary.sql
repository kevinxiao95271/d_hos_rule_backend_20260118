-- 为kiro_qc_batch_summary表添加Cross规则统计字段

ALTER TABLE kiro_qc_batch_summary 
ADD COLUMN cross_defect_count INT DEFAULT 0 COMMENT 'Cross规则违规总数',
ADD COLUMN cross_total_deduct DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Cross规则总扣分',
ADD COLUMN avg_cross_defect DECIMAL(10,2) DEFAULT 0.00 COMMENT '平均Cross规则违规数';

-- 验证表结构
DESCRIBE kiro_qc_batch_summary;