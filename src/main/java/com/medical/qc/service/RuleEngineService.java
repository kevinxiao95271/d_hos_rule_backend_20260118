package com.medical.qc.service;

import com.medical.qc.entity.KiroQcRule;
import com.medical.qc.entity.KiroQcRuleCross;
import com.medical.qc.mapper.DictMapper;
import com.medical.qc.mapper.CrossRuleMapper;
import lombok.extern.slf4j.Slf4j;
import com.medical.qc.service.DictCacheServiceEnhanced;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.type.TypeReference;
import java.math.BigDecimal;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Slf4j
@Service
public class RuleEngineService {

    @Autowired
    private DictMemoryCacheService dictMemoryCache;
    
    @Autowired
    private CrossRuleMapper crossRuleMapper;
    
    private ObjectMapper objectMapper = new ObjectMapper();

    // 规则索引: 按字段代码分组规则
    private Map<String, List<KiroQcRule>> ruleIndex = new HashMap<>();
    
    // Cross规则缓存
    private List<KiroQcRuleCross> crossRules = new ArrayList<>();
    private long crossRulesLastLoaded = 0;
    private static final long CROSS_RULES_CACHE_TTL = 5 * 60 * 1000; // 5分钟缓存

    public static class RuleViolation {
        public String fieldCode;
        public String fieldName;
        public String actualValue;
        public String expectedValue;
        public String ruleDescription;
        public BigDecimal deductScore;
        public Long ruleId;
        public String ruleCode;
    }

    /**
     * 优化的规则检查 - 使用字段索引,只检查相关规则
     */
    public List<RuleViolation> checkRecord(Map<String, Object> record, List<KiroQcRule> rules) {
        List<RuleViolation> violations = new ArrayList<>();

        // 预处理: 规范化字段名为大写,避免重复查找
        Map<String, Object> normalizedRecord = normalizeFieldKeys(record);

        // 建立规则索引(如果还没有)
        if (ruleIndex.isEmpty() && !rules.isEmpty()) {
            buildRuleIndex(rules);
        }

        // 只检查病案中存在字段的相关规则
        Set<String> checkedRules = new HashSet<>(); // 避免重复检查

        for (String fieldCode : normalizedRecord.keySet()) {
            List<KiroQcRule> relevantRules = ruleIndex.get(fieldCode);
            if (relevantRules != null) {
                for (KiroQcRule rule : relevantRules) {
                    // 避免重复检查同一规则
                    String ruleKey = rule.getId().toString();
                    if (checkedRules.contains(ruleKey)) {
                        continue;
                    }
                    checkedRules.add(ruleKey);

                    try {
                        RuleViolation violation = applyRule(normalizedRecord, rule);
                        if (violation != null) {
                            violations.add(violation);
                        }
                    } catch (Exception e) {
                        log.error("规则执行失败: {} - {}", rule.getRuleCode(), e.getMessage());
                    }
                }
            }
        }

        // 检查跨字段规则
        List<RuleViolation> crossViolations = checkCrossRules(normalizedRecord);
        violations.addAll(crossViolations);

        return violations;
    }

    /**
     * 建立规则索引
     */
    private void buildRuleIndex(List<KiroQcRule> rules) {
        ruleIndex.clear();
        for (KiroQcRule rule : rules) {
            String fieldCode = rule.getFieldCode();
            if (fieldCode != null && !fieldCode.isEmpty()) {
                String normalizedCode = fieldCode.toUpperCase();
                ruleIndex.computeIfAbsent(normalizedCode, k -> new ArrayList<>()).add(rule);
            }
        }
        log.info("规则索引已建立: {} 个字段, {} 条规则", ruleIndex.size(), rules.size());
    }

    /**
     * 规范化字段键为大写,避免重复查找
     */
    private Map<String, Object> normalizeFieldKeys(Map<String, Object> record) {
        Map<String, Object> normalized = new HashMap<>(record.size());
        for (Map.Entry<String, Object> entry : record.entrySet()) {
            String key = entry.getKey().toUpperCase();
            normalized.put(key, entry.getValue());
        }
        return normalized;
    }
    
    private RuleViolation applyRule(Map<String, Object> record, KiroQcRule rule) {
        String ruleType = rule.getRuleType();
        String fieldCode = rule.getFieldCode();
        String description = rule.getDescription();
        
        if ("value_check".equals(ruleType)) {
            return checkValueRule(record, rule);
        } else if ("cross_check_null".equals(ruleType)) {
            return checkCrossNullRule(record, rule);
        } else if ("range_check".equals(ruleType)) {
            return checkRangeRule(record, rule);
        } else if ("cross".equals(ruleType)) {
            // cross类型规则由专门的checkCrossRules方法处理
            return null;
        }
        
        return null;
    }
    
    private RuleViolation checkValueRule(Map<String, Object> record, KiroQcRule rule) {
        String desc = rule.getDescription();
        String fieldCode = rule.getFieldCode();
        String canonicalExpr = rule.getCanonicalExpr();
        String dictTypes = rule.getDictTypes();
        Object value = getFieldValue(record, fieldCode);
        
        // 检查规则是否明确要求字段不能为空
        boolean requiresNonNull = isRequiredField(desc);
        
        // 核心业务逻辑：
        // 1. 如果规则明确说明字段不能为空，且字段为空，则报告违规
        // 2. 如果规则没有明确说明不能为空，且字段为空，则跳过该规则检查
        if (isNullOrEmpty(value)) {
            if (requiresNonNull) {
                // 字段必填但为空，报告违规
                RuleViolation v = new RuleViolation();
                v.fieldCode = fieldCode;
                v.fieldName = rule.getFieldName();
                v.actualValue = "空";
                v.expectedValue = "不能为空";
                v.ruleDescription = desc;
                v.deductScore = rule.getDeductScore();
                v.ruleId = rule.getId();
                v.ruleCode = rule.getRuleCode();
                return v;
            } else {
                // 字段非必填且为空，跳过检查
                return null;
            }
        }
        
        // 字段有值，继续进行值域检查
        String valueStr = value.toString().trim();
        
        // 特殊规则：产妇诊断编码必须填写
        if (desc.contains("产妇诊断编码") && desc.contains("必须填写")) {
            List<String> requiredCodes = extractDiagnosisCodes(desc);
            if (hasDiagnosisCode(record, requiredCodes)) {
                // 这个逻辑已经在上面的requiresNonNull中处理了
                return null;
            }
        }
        
        // 字典值域检查：字段值必须在指定字典范围内
        if (dictTypes != null && !dictTypes.isEmpty()) {
            return checkDictValidation(rule, valueStr);
        }
        
        return null;
    }
    
    /**
     * 检查字典值域验证
     */
    private RuleViolation checkDictValidation(KiroQcRule rule, String value) {
        String dictTypes = rule.getDictTypes();
        String fieldCode = rule.getFieldCode();
        
        // 跳过空值和特殊空值标识符（如"-"），这些由专门的空值约束规则处理
        if (value == null || value.trim().isEmpty() || "-".equals(value.trim())) {
            return null;
        }
        
        try {
            // 使用内存缓存进行快速字典验证
            boolean isValid = dictMemoryCache.validateFieldValue(dictTypes, value);

            if (!isValid) {
                // 获取字典数据用于构建期望值列表
                List<Map<String, Object>> dictItems = dictMemoryCache.getDictsByType(dictTypes);
                
                // 构建期望值列表（显示前几个有效值）
                StringBuilder expectedValues = new StringBuilder();
                int count = 0;
                for (Map<String, Object> item : dictItems) {
                    if (count >= 5) {
                        expectedValues.append("等");
                        break;
                    }
                    if (count > 0) expectedValues.append(", ");
                    expectedValues.append(item.get("dict_code"));
                    count++;
                }
                
                RuleViolation v = new RuleViolation();
                v.fieldCode = fieldCode;
                v.fieldName = rule.getFieldName();
                v.actualValue = value;
                v.expectedValue = "字典" + dictTypes + "中的有效值: " + expectedValues.toString();
                v.ruleDescription = rule.getDescription();
                v.deductScore = rule.getDeductScore();
                v.ruleId = rule.getId();
                v.ruleCode = rule.getRuleCode();
                return v;
            }
            
        } catch (Exception e) {
            log.error("字典验证失败: 字段={}, 字典={}, 值={}, 错误={}", fieldCode, dictTypes, value, e.getMessage());
        }
        
        return null;
    }
    
    /**
     * 判断规则是否明确要求字段不能为空
     */
    private boolean isRequiredField(String description) {
        if (description == null) return false;
        
        // 检查描述中是否包含"必填"、"不能为空"、"必须填写"等关键词
        return description.contains("必填") 
            || description.contains("不能为空")
            || description.contains("必须填写")
            || description.contains("不得为空")
            || description.contains("必须有值")
            || description.contains("取值不为空");
    }
    
    private RuleViolation checkCrossNullRule(Map<String, Object> record, KiroQcRule rule) {
        return checkValueRule(record, rule);
    }
    
    private RuleViolation checkRangeRule(Map<String, Object> record, KiroQcRule rule) {
        String desc = rule.getDescription();
        String fieldCode = rule.getFieldCode();
        Object value = getFieldValue(record, fieldCode);
        
        // 检查规则是否明确要求字段不能为空
        boolean requiresNonNull = isRequiredField(desc);
        
        // 如果字段为空
        if (isNullOrEmpty(value)) {
            if (requiresNonNull) {
                // 字段必填但为空，报告违规
                RuleViolation v = new RuleViolation();
                v.fieldCode = fieldCode;
                v.fieldName = rule.getFieldName();
                v.actualValue = "空";
                v.expectedValue = "不能为空";
                v.ruleDescription = desc;
                v.deductScore = rule.getDeductScore();
                v.ruleId = rule.getId();
                v.ruleCode = rule.getRuleCode();
                return v;
            } else {
                // 字段非必填且为空，跳过检查
                return null;
            }
        }
        
        // 字段有值，进行范围检查
        try {
            String valueStr = value.toString().trim();
            if (valueStr.isEmpty()) return null;
            
            double numValue = Double.parseDouble(valueStr);
            
            Pattern pattern = Pattern.compile("(\\d+).*-(\\d+)");
            Matcher matcher = pattern.matcher(desc);
            if (matcher.find()) {
                double min = Double.parseDouble(matcher.group(1));
                double max = Double.parseDouble(matcher.group(2));
                
                if (numValue < min || numValue > max) {
                    RuleViolation v = new RuleViolation();
                    v.fieldCode = fieldCode;
                    v.fieldName = rule.getFieldName();
                    v.actualValue = valueStr;
                    v.expectedValue = min + "-" + max;
                    v.ruleDescription = desc;
                    v.deductScore = rule.getDeductScore();
                    v.ruleId = rule.getId();
                    v.ruleCode = rule.getRuleCode();
                    return v;
                }
            }
            
            if (desc.contains("精确到10g") && numValue % 10 != 0) {
                RuleViolation v = new RuleViolation();
                v.fieldCode = fieldCode;
                v.fieldName = rule.getFieldName();
                v.actualValue = valueStr;
                v.expectedValue = "必须是10的倍数";
                v.ruleDescription = desc;
                v.deductScore = rule.getDeductScore();
                v.ruleId = rule.getId();
                v.ruleCode = rule.getRuleCode();
                return v;
            }
        } catch (NumberFormatException e) {
            log.debug("字段{}值{}不是数字", fieldCode, value);
        }
        
        return null;
    }
    
    private List<String> extractDiagnosisCodes(String desc) {
        List<String> codes = new ArrayList<>();
        Pattern pattern = Pattern.compile("Z\\d+\\.\\d+");
        Matcher matcher = pattern.matcher(desc);
        while (matcher.find()) {
            codes.add(matcher.group());
        }
        return codes;
    }
    
    private boolean hasDiagnosisCode(Map<String, Object> record, List<String> codes) {
        for (int i = 1; i <= 40; i++) {
            String key = String.format("C06x%02dC", i);
            Object value = getFieldValue(record, key);
            if (value != null) {
                String diagCode = value.toString();
                for (String code : codes) {
                    if (diagCode.contains(code)) {
                        return true;
                    }
                }
            }
        }
        return false;
    }
    
    /**
     * 优化的字段值获取 - 直接从规范化的记录中获取
     */
    private Object getFieldValue(Map<String, Object> record, String fieldCode) {
        // record已经规范化为大写,直接获取
        return record.get(fieldCode.toUpperCase());
    }
    
    private boolean isNullOrEmpty(Object value) {
        if (value == null) return true;
        String str = value.toString().trim();
        return str.isEmpty() || "null".equalsIgnoreCase(str);
    }

    
    /**
     * 使用缓存验证字典值
     */
    private boolean validateDictValueWithCache(String dictType, String value) {
        if (dictType == null || value == null) {
            return false;
        }

        try {
            return dictMemoryCache.validateFieldValue(dictType, value);
        } catch (Exception e) {
            log.error("缓存字典验证异常 {}:{} - {}", dictType, value, e.getMessage());
            return false;
        }
    }

    /**
     * 批量字典验证（使用缓存）
     */
    private Map<String, Boolean> batchValidateDictWithCache(String dictType, List<String> values) {
        if (dictType == null || values == null || values.isEmpty()) {
            return new HashMap<>();
        }

        try {
            Map<String, Boolean> results = new HashMap<>();
            for (String value : values) {
                results.put(value, dictMemoryCache.validateFieldValue(dictType, value));
            }
            return results;
        } catch (Exception e) {
            log.error("批量缓存字典验证异常: {}", e.getMessage());
            Map<String, Boolean> results = new HashMap<>();
            for (String value : values) {
                results.put(value, false);
            }
            return results;
        }
    }

    /**
     * 检查跨字段规则
     */
    private List<RuleViolation> checkCrossRules(Map<String, Object> record) {
        List<RuleViolation> violations = new ArrayList<>();
        
        try {
            // 获取活跃的跨字段规则
            List<KiroQcRuleCross> crossRules = getActiveCrossRules();
            
            log.debug("开始检查 {} 条跨字段规则", crossRules.size());
            
            for (KiroQcRuleCross crossRule : crossRules) {
                try {
                    RuleViolation violation = applyCrossRule(record, crossRule);
                    if (violation != null) {
                        violations.add(violation);
                        log.debug("发现跨字段违规: {}", crossRule.getRuleCode());
                    }
                } catch (Exception e) {
                    log.error("跨字段规则执行失败: {} - {}", crossRule.getRuleCode(), e.getMessage());
                    // 继续处理其他规则，不要因为一个规则失败而中断整个流程
                }
            }
            
            log.debug("跨字段规则检查完成，发现 {} 个违规", violations.size());
            
        } catch (Exception e) {
            log.error("跨字段规则检查异常: {}", e.getMessage());
        }
        
        return violations;
    }
    
    /**
     * 获取活跃的跨字段规则（带缓存）
     */
    private List<KiroQcRuleCross> getActiveCrossRules() {
        long now = System.currentTimeMillis();
        if (crossRules.isEmpty() || (now - crossRulesLastLoaded) > CROSS_RULES_CACHE_TTL) {
            try {
                crossRules = crossRuleMapper.findActiveRules();
                crossRulesLastLoaded = now;
                log.debug("加载了 {} 条跨字段规则", crossRules.size());
            } catch (Exception e) {
                log.error("加载跨字段规则失败: {}", e.getMessage());
                return new ArrayList<>();
            }
        }
        return crossRules;
    }
    
    /**
     * 应用单个跨字段规则
     */
    private RuleViolation applyCrossRule(Map<String, Object> record, KiroQcRuleCross crossRule) {
        String crossType = crossRule.getCrossType();
        
        try {
            log.debug("处理跨字段规则: {} (类型: {})", crossRule.getRuleCode(), crossType);
            
            switch (crossType) {
                case "field_pair":
                    return checkFieldPairRule(record, crossRule);
                case "age_gender":
                    return checkAgeGenderRule(record, crossRule);
                case "conditional_required":
                    return checkConditionalRequiredRule(record, crossRule);
                case "age_diagnosis":
                    return checkAgeDiagnosisRule(record, crossRule);
                case "transfusion_logic":
                    return checkTransfusionLogicRule(record, crossRule);
                case "date_consistency":
                    return checkDateConsistencyRule(record, crossRule);
                case "logic_check":
                    return checkLogicRule(record, crossRule);
                default:
                    log.warn("未知的跨字段规则类型: {} (规则: {})", crossType, crossRule.getRuleCode());
                    return null;
            }
        } catch (Exception e) {
            log.error("跨字段规则处理异常: {} - {}", crossRule.getRuleCode(), e.getMessage());
            return null;
        }
    }
    
    /**
     * 检查字段配对规则（如编码与名称必须同时有值或同时为空）
     */
    private RuleViolation checkFieldPairRule(Map<String, Object> record, KiroQcRuleCross crossRule) {
        try {
            String primaryField = crossRule.getPrimaryField();
            Object primaryValue = getFieldValue(record, primaryField);
            
            // 安全解析关联字段JSON
            String relatedFieldsJson = crossRule.getRelatedFields();
            if (relatedFieldsJson == null || relatedFieldsJson.trim().isEmpty()) {
                log.warn("字段配对规则 {} 缺少关联字段配置", crossRule.getRuleCode());
                return null;
            }
            
            List<Map<String, Object>> relatedFields;
            try {
                relatedFields = objectMapper.readValue(
                    relatedFieldsJson, 
                    new TypeReference<List<Map<String, Object>>>() {}
                );
            } catch (Exception e) {
                log.error("解析关联字段JSON失败: {} - {}", crossRule.getRuleCode(), e.getMessage());
                return null;
            }
            
            // 安全解析约束条件JSON
            String constraintsJson = crossRule.getConstraintConditions();
            if (constraintsJson == null || constraintsJson.trim().isEmpty()) {
                log.warn("字段配对规则 {} 缺少约束条件配置", crossRule.getRuleCode());
                return null;
            }
            
            Map<String, Object> constraints;
            try {
                constraints = objectMapper.readValue(
                    constraintsJson,
                    new TypeReference<Map<String, Object>>() {}
                );
            } catch (Exception e) {
                log.error("解析约束条件JSON失败: {} - {}", crossRule.getRuleCode(), e.getMessage());
                return null;
            }
            
            String constraintType = (String) constraints.get("type");
            
            if ("both_or_neither".equals(constraintType)) {
                // 检查主字段和关联字段是否都有值或都为空
                boolean primaryHasValue = !isNullOrEmpty(primaryValue);
                
                for (Map<String, Object> relatedField : relatedFields) {
                    String fieldCode = (String) relatedField.get("field");
                    if (fieldCode == null) continue;
                    
                    Object fieldValue = getFieldValue(record, fieldCode);
                    boolean relatedHasValue = !isNullOrEmpty(fieldValue);
                    
                    // 如果一个有值另一个没值，则违规
                    if (primaryHasValue != relatedHasValue) {
                        RuleViolation violation = new RuleViolation();
                        violation.ruleCode = crossRule.getRuleCode();
                        violation.fieldCode = primaryField;
                        violation.fieldName = crossRule.getPrimaryFieldName();
                        violation.actualValue = primaryHasValue ? String.valueOf(primaryValue) : "空";
                        violation.expectedValue = crossRule.getExpectedValue();
                        violation.ruleDescription = crossRule.getDescription();
                        violation.deductScore = crossRule.getDeductScore();
                        violation.ruleId = crossRule.getId();
                        return violation;
                    }
                }
            }
            
        } catch (Exception e) {
            log.error("字段配对规则检查失败: {} - {}", crossRule.getRuleCode(), e.getMessage());
        }
        
        return null;
    }
    
    /**
     * 检查年龄性别逻辑规则
     */
    private RuleViolation checkAgeGenderRule(Map<String, Object> record, KiroQcRuleCross crossRule) {
        try {
            String primaryField = crossRule.getPrimaryField();
            Object primaryValue = getFieldValue(record, primaryField);
            
            if (isNullOrEmpty(primaryValue)) {
                return null; // 主字段为空，跳过检查
            }
            
            String primaryValueStr = primaryValue.toString();
            
            // 解析约束条件
            Map<String, Object> constraints = objectMapper.readValue(
                crossRule.getConstraintConditions(),
                new TypeReference<Map<String, Object>>() {}
            );
            
            String constraintType = (String) constraints.get("type");
            
            if ("gender_diagnosis".equals(constraintType)) {
                // 性别诊断逻辑检查
                String requiredGender = (String) constraints.get("gender");
                List<String> forbiddenCodes = (List<String>) constraints.get("forbidden_codes");
                
                // 获取性别字段值
                Object genderValue = getFieldValue(record, "A12C");
                if (isNullOrEmpty(genderValue)) {
                    return null; // 性别为空，跳过检查
                }
                
                String genderStr = genderValue.toString();
                
                // 如果性别匹配且诊断编码在禁用列表中
                if (requiredGender.equals(genderStr)) {
                    for (String forbiddenCode : forbiddenCodes) {
                        if (primaryValueStr.startsWith(forbiddenCode) || 
                            (forbiddenCode.contains("-") && isInRange(primaryValueStr, forbiddenCode))) {
                            
                            RuleViolation violation = new RuleViolation();
                            violation.ruleCode = crossRule.getRuleCode();
                            violation.fieldCode = primaryField;
                            violation.fieldName = crossRule.getPrimaryFieldName();
                            violation.actualValue = primaryValueStr;
                            violation.expectedValue = crossRule.getExpectedValue();
                            violation.ruleDescription = crossRule.getDescription();
                            violation.deductScore = crossRule.getDeductScore();
                            violation.ruleId = crossRule.getId();
                            return violation;
                        }
                    }
                }
            }
            
        } catch (Exception e) {
            log.error("年龄性别规则检查失败: {} - {}", crossRule.getRuleCode(), e.getMessage());
        }
        
        return null;
    }
    
    /**
     * 检查条件必填规则
     */
    private RuleViolation checkConditionalRequiredRule(Map<String, Object> record, KiroQcRuleCross crossRule) {
        try {
            String primaryField = crossRule.getPrimaryField();
            Object primaryValue = getFieldValue(record, primaryField);
            
            // 解析约束条件
            Map<String, Object> constraints = objectMapper.readValue(
                crossRule.getConstraintConditions(),
                new TypeReference<Map<String, Object>>() {}
            );
            
            String conditionField = (String) constraints.get("condition_field");
            List<String> conditionValues = (List<String>) constraints.get("condition_values");
            String requiredWhen = (String) constraints.get("required_when");
            
            // 获取条件字段的值
            Object conditionValue = getFieldValue(record, conditionField);
            
            if (isNullOrEmpty(conditionValue)) {
                return null; // 条件字段为空，跳过检查
            }
            
            String conditionValueStr = conditionValue.toString();
            
            // 检查是否满足条件
            boolean conditionMatched = false;
            for (String expectedValue : conditionValues) {
                if (conditionValueStr.contains(expectedValue) || 
                    dictMemoryCache.validateFieldValue("SURGERY_TYPE", conditionValueStr)) {
                    conditionMatched = true;
                    break;
                }
            }
            
            // 如果条件匹配且要求必填，检查主字段是否为空
            if ("condition_matched".equals(requiredWhen) && conditionMatched) {
                if (isNullOrEmpty(primaryValue)) {
                    RuleViolation violation = new RuleViolation();
                    violation.ruleCode = crossRule.getRuleCode();
                    violation.fieldCode = primaryField;
                    violation.fieldName = crossRule.getPrimaryFieldName();
                    violation.actualValue = "空";
                    violation.expectedValue = crossRule.getExpectedValue();
                    violation.ruleDescription = crossRule.getDescription();
                    violation.deductScore = crossRule.getDeductScore();
                    violation.ruleId = crossRule.getId();
                    return violation;
                }
            }
            
        } catch (Exception e) {
            log.error("条件必填规则检查失败: {} - {}", crossRule.getRuleCode(), e.getMessage());
        }
        
        return null;
    }
    
    /**
     * 检查年龄诊断逻辑规则
     */
    private RuleViolation checkAgeDiagnosisRule(Map<String, Object> record, KiroQcRuleCross crossRule) {
        try {
            String primaryField = crossRule.getPrimaryField();
            Object primaryValue = getFieldValue(record, primaryField);
            
            if (isNullOrEmpty(primaryValue)) {
                return null; // 主字段为空，跳过检查
            }
            
            String primaryValueStr = primaryValue.toString();
            
            // 解析约束条件
            Map<String, Object> constraints = objectMapper.readValue(
                crossRule.getConstraintConditions(),
                new TypeReference<Map<String, Object>>() {}
            );
            
            Integer ageLimit = (Integer) constraints.get("age_limit");
            String comparison = (String) constraints.get("comparison");
            List<String> forbiddenCodes = (List<String>) constraints.get("forbidden_codes");
            
            // 获取年龄字段值
            Object ageValue = getFieldValue(record, "A13");
            if (isNullOrEmpty(ageValue)) {
                return null; // 年龄为空，跳过检查
            }
            
            try {
                int age = Integer.parseInt(ageValue.toString());
                boolean ageConditionMet = false;
                
                // 检查年龄条件
                if ("<".equals(comparison)) {
                    ageConditionMet = age < ageLimit;
                } else if (">=".equals(comparison)) {
                    ageConditionMet = age >= ageLimit;
                } else if ("<=".equals(comparison)) {
                    ageConditionMet = age <= ageLimit;
                } else if (">".equals(comparison)) {
                    ageConditionMet = age > ageLimit;
                }
                
                // 如果年龄条件满足，检查是否使用了禁用的诊断编码
                if (ageConditionMet) {
                    for (String forbiddenCode : forbiddenCodes) {
                        if (primaryValueStr.startsWith(forbiddenCode) || 
                            (forbiddenCode.contains("-") && isInRange(primaryValueStr, forbiddenCode))) {
                            
                            RuleViolation violation = new RuleViolation();
                            violation.ruleCode = crossRule.getRuleCode();
                            violation.fieldCode = primaryField;
                            violation.fieldName = crossRule.getPrimaryFieldName();
                            violation.actualValue = primaryValueStr + " (年龄:" + age + ")";
                            violation.expectedValue = crossRule.getExpectedValue();
                            violation.ruleDescription = crossRule.getDescription();
                            violation.deductScore = crossRule.getDeductScore();
                            violation.ruleId = crossRule.getId();
                            return violation;
                        }
                    }
                }
                
            } catch (NumberFormatException e) {
                log.debug("年龄字段值不是数字: {}", ageValue);
            }
            
        } catch (Exception e) {
            log.error("年龄诊断规则检查失败: {} - {}", crossRule.getRuleCode(), e.getMessage());
        }
        
        return null;
    }
    
    /**
     * 检查输血逻辑规则
     */
    private RuleViolation checkTransfusionLogicRule(Map<String, Object> record, KiroQcRuleCross crossRule) {
        try {
            String primaryField = crossRule.getPrimaryField();
            Object primaryValue = getFieldValue(record, primaryField);
            
            // 解析约束条件
            Map<String, Object> constraints = objectMapper.readValue(
                crossRule.getConstraintConditions(),
                new TypeReference<Map<String, Object>>() {}
            );
            
            String logicType = (String) constraints.get("logic");
            
            // 解析相关字段
            List<Map<String, Object>> relatedFields = objectMapper.readValue(
                crossRule.getRelatedFields(), 
                new TypeReference<List<Map<String, Object>>>() {}
            );
            
            if ("no_transfusion_but_reaction".equals(logicType)) {
                // 检查：无输血记录但存在输血反应
                boolean hasTransfusion = false;
                
                // 检查所有输血相关字段
                for (Map<String, Object> field : relatedFields) {
                    String fieldCode = (String) field.get("field");
                    Object fieldValue = getFieldValue(record, fieldCode);
                    
                    if (!isNullOrEmpty(fieldValue)) {
                        try {
                            double value = Double.parseDouble(fieldValue.toString());
                            if (value > 0) {
                                hasTransfusion = true;
                                break;
                            }
                        } catch (NumberFormatException e) {
                            // 非数字值，检查是否为"是"等表示有输血的值
                            String valueStr = fieldValue.toString();
                            if (!"0".equals(valueStr) && !"否".equals(valueStr) && !valueStr.isEmpty()) {
                                hasTransfusion = true;
                                break;
                            }
                        }
                    }
                }
                
                // 检查是否存在输血反应
                boolean hasReaction = !isNullOrEmpty(primaryValue) && 
                    !"0".equals(primaryValue.toString()) && 
                    !"否".equals(primaryValue.toString());
                
                // 如果无输血但有反应，报告违规
                if (!hasTransfusion && hasReaction) {
                    RuleViolation violation = new RuleViolation();
                    violation.ruleCode = crossRule.getRuleCode();
                    violation.fieldCode = primaryField;
                    violation.fieldName = crossRule.getPrimaryFieldName();
                    violation.actualValue = "有输血反应但无输血记录";
                    violation.expectedValue = crossRule.getExpectedValue();
                    violation.ruleDescription = crossRule.getDescription();
                    violation.deductScore = crossRule.getDeductScore();
                    violation.ruleId = crossRule.getId();
                    return violation;
                }
                
            } else if ("has_transfusion_no_fee".equals(logicType)) {
                // 检查：存在输血记录但未产生血费
                boolean hasTransfusion = false;
                
                // 检查所有输血相关字段
                for (Map<String, Object> field : relatedFields) {
                    String fieldCode = (String) field.get("field");
                    Object fieldValue = getFieldValue(record, fieldCode);
                    
                    if (!isNullOrEmpty(fieldValue)) {
                        try {
                            double value = Double.parseDouble(fieldValue.toString());
                            if (value > 0) {
                                hasTransfusion = true;
                                break;
                            }
                        } catch (NumberFormatException e) {
                            String valueStr = fieldValue.toString();
                            if (!"0".equals(valueStr) && !"否".equals(valueStr) && !valueStr.isEmpty()) {
                                hasTransfusion = true;
                                break;
                            }
                        }
                    }
                }
                
                // 检查血费
                boolean hasFee = false;
                if (!isNullOrEmpty(primaryValue)) {
                    try {
                        double fee = Double.parseDouble(primaryValue.toString());
                        hasFee = fee > 0;
                    } catch (NumberFormatException e) {
                        // 非数字值处理
                    }
                }
                
                // 如果有输血但无血费，报告违规
                if (hasTransfusion && !hasFee) {
                    RuleViolation violation = new RuleViolation();
                    violation.ruleCode = crossRule.getRuleCode();
                    violation.fieldCode = primaryField;
                    violation.fieldName = crossRule.getPrimaryFieldName();
                    violation.actualValue = "有输血记录但无血费";
                    violation.expectedValue = crossRule.getExpectedValue();
                    violation.ruleDescription = crossRule.getDescription();
                    violation.deductScore = crossRule.getDeductScore();
                    violation.ruleId = crossRule.getId();
                    return violation;
                }
                
            } else if ("has_fee_no_transfusion".equals(logicType)) {
                // 检查：产生血费但无输血记录
                boolean hasTransfusion = false;
                
                // 检查所有输血相关字段
                for (Map<String, Object> field : relatedFields) {
                    String fieldCode = (String) field.get("field");
                    Object fieldValue = getFieldValue(record, fieldCode);
                    
                    if (!isNullOrEmpty(fieldValue)) {
                        try {
                            double value = Double.parseDouble(fieldValue.toString());
                            if (value > 0) {
                                hasTransfusion = true;
                                break;
                            }
                        } catch (NumberFormatException e) {
                            String valueStr = fieldValue.toString();
                            if (!"0".equals(valueStr) && !"否".equals(valueStr) && !valueStr.isEmpty()) {
                                hasTransfusion = true;
                                break;
                            }
                        }
                    }
                }
                
                // 检查血费
                boolean hasFee = false;
                if (!isNullOrEmpty(primaryValue)) {
                    try {
                        double fee = Double.parseDouble(primaryValue.toString());
                        hasFee = fee > 0;
                    } catch (NumberFormatException e) {
                        // 非数字值处理
                    }
                }
                
                // 如果有血费但无输血，报告违规
                if (hasFee && !hasTransfusion) {
                    RuleViolation violation = new RuleViolation();
                    violation.ruleCode = crossRule.getRuleCode();
                    violation.fieldCode = primaryField;
                    violation.fieldName = crossRule.getPrimaryFieldName();
                    violation.actualValue = "有血费但无输血记录";
                    violation.expectedValue = crossRule.getExpectedValue();
                    violation.ruleDescription = crossRule.getDescription();
                    violation.deductScore = crossRule.getDeductScore();
                    violation.ruleId = crossRule.getId();
                    return violation;
                }
            }
            
        } catch (Exception e) {
            log.error("输血逻辑规则检查失败: {} - {}", crossRule.getRuleCode(), e.getMessage());
        }
        
        return null;
    }
    
    /**
     * 检查日期一致性规则
     */
    private RuleViolation checkDateConsistencyRule(Map<String, Object> record, KiroQcRuleCross crossRule) {
        // TODO: 实现日期一致性检查逻辑
        return null;
    }
    
    /**
     * 检查逻辑规则
     */
    private RuleViolation checkLogicRule(Map<String, Object> record, KiroQcRuleCross crossRule) {
        // TODO: 实现复杂逻辑检查
        return null;
    }
    
    /**
     * 检查编码是否在范围内（如C51-C58）
     */
    private boolean isInRange(String code, String range) {
        if (!range.contains("-")) {
            return false;
        }
        
        try {
            String[] parts = range.split("-");
            if (parts.length != 2) {
                return false;
            }
            
            String start = parts[0].trim();
            String end = parts[1].trim();
            
            // 简单的字符串比较（适用于ICD编码）
            return code.compareTo(start) >= 0 && code.compareTo(end) <= 0;
            
        } catch (Exception e) {
            log.debug("范围检查失败: {} in {}", code, range);
            return false;
        }
    }

}
