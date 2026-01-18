package com.medical.qc.util;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;
import lombok.extern.slf4j.Slf4j;

import javax.annotation.PostConstruct;

/**
 * 规则表字典类型修复工具
 */
@Component
@Slf4j
public class RuleDictTypeFixer {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    /**
     * 修复规则表中的字典类型配置错误
     * 在应用启动时自动执行
     */
    @PostConstruct
    public void fixRuleDictTypes() {
        log.info("开始修复规则表字典类型配置...");

        try {
            // 1. 修复所有入院病情字段 -> RC027
            // C08x01C-C08x16C, C09x01C-C09x16C, C10x01C-C10x16C, etc.
            // 需要同时更新 dict_types, description, canonical_expr 三个字段
            int count1 = jdbcTemplate.update(
                "UPDATE kiro_qc_rule SET " +
                "  dict_types = 'RC027', " +
                "  description = REPLACE(description, 'RC013', 'RC027'), " +
                "  canonical_expr = REPLACE(canonical_expr, 'RC013', 'RC027') " +
                "WHERE (rule_code LIKE 'RULE_C08x__C_%' " +
                "   OR rule_code LIKE 'RULE_C09x__C_%' " +
                "   OR rule_code LIKE 'RULE_C10x__C_%' " +
                "   OR rule_code LIKE 'RULE_C11x__C_%' " +
                "   OR rule_code LIKE 'RULE_C12x__C_%' " +
                "   OR rule_code LIKE 'RULE_C13x__C_%' " +
                "   OR rule_code LIKE 'RULE_C14x__C_%') " +
                "AND (dict_types != 'RC027' OR description LIKE '%RC013%')"
            );
            log.info("修复入院病情字段: {} 条规则", count1);

            // 2. 修复切口愈合等级字段 -> RC014
            // 同时更新 dict_types, description, canonical_expr 三个字段
            int count2 = jdbcTemplate.update(
                "UPDATE kiro_qc_rule SET " +
                "  dict_types = 'RC014', " +
                "  description = REPLACE(description, 'RC013', 'RC014'), " +
                "  canonical_expr = REPLACE(canonical_expr, 'RC013', 'RC014') " +
                "WHERE (rule_code LIKE 'RULE_C21x01C_%' " +
                "   OR rule_code LIKE 'RULE_C22x01C_%' " +
                "   OR rule_code LIKE 'RULE_C23x01C_%' " +
                "   OR rule_code LIKE 'RULE_C24x01C_%' " +
                "   OR rule_code LIKE 'RULE_C25x01C_%' " +
                "   OR rule_code LIKE 'RULE_C26x01C_%') " +
                "AND (dict_types != 'RC014' OR description LIKE '%RC013%')"
            );
            log.info("修复切口愈合等级字段: {} 条规则", count2);

            log.info("规则表字典类型修复完成! 共修复 {} 条规则", count1 + count2);

        } catch (Exception e) {
            log.error("修复规则表字典类型失败", e);
        }
    }
}
