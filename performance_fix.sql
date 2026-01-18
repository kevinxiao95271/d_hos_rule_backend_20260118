-- 医疗质控系统性能优化SQL脚本

-- 1. 添加关键索引
CREATE INDEX IF NOT EXISTS idx_d_mr_a48_a49 ON d_mr(A48, A49);
CREATE INDEX IF NOT EXISTS idx_d_mr_b15 ON d_mr(B15);
CREATE INDEX IF NOT EXISTS idx_qc_dict_type ON kiro_qc_dict(dict_type_code);

-- 2. 检查表统计信息
SELECT 'kiro_qc_rule' as table_name, COUNT(*) as count FROM kiro_qc_rule
UNION ALL
SELECT 'kiro_qc_dict' as table_name, COUNT(*) as count FROM kiro_qc_dict
UNION ALL
SELECT 'd_mr' as table_name, COUNT(*) as count FROM d_mr
UNION ALL
SELECT 'd_mr_2023' as table_name, COUNT(*) as count FROM d_mr WHERE B15 LIKE '2023/%';

-- 3. 分析规则分布
SELECT 
    CASE 
        WHEN rule_description LIKE '%字典%' THEN '字典验证规则'
        WHEN rule_description LIKE '%范围%' THEN '范围检查规则'
        WHEN rule_description LIKE '%逻辑%' THEN '逻辑检查规则'
        ELSE '其他规则'
    END as rule_category,
    COUNT(*) as count
FROM kiro_qc_rule 
GROUP BY rule_category;
