-- 添加源数据表和值域数据集字段
ALTER TABLE kiro_qc_rule 
ADD COLUMN `source_tables` varchar(500) DEFAULT NULL COMMENT '源数据表，多个用逗号分隔' AFTER `status`,
ADD COLUMN `dict_types` varchar(500) DEFAULT NULL COMMENT '值域数据集，多个用逗号分隔' AFTER `source_tables`;
