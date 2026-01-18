package com.medical.qc.service;

import com.medical.qc.entity.KiroQcRule;
import com.medical.qc.mapper.DictMapper;
import lombok.extern.slf4j.Slf4j;
import com.medical.qc.service.DictCacheServiceEnhanced;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.math.BigDecimal;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Slf4j
@Service
public class RuleEngineService {

    @Autowired
    private DictMemoryCacheService dictMemoryCache;

    // 规则索引: 按字段代码分组规则
    private Map<String, List<KiroQcRule>> ruleIndex = new HashMap<>();

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

}
