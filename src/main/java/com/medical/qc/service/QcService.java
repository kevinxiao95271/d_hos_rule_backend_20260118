package com.medical.qc.service;

import com.medical.qc.dto.*;
import com.medical.qc.entity.*;
import com.medical.qc.mapper.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.stream.Collectors;

@Slf4j
@Service
public class QcService {
    
    @Autowired
    private QcRuleMapper ruleMapper;
    
    @Autowired
    private MedicalRecordMapper recordMapper;
    
    @Autowired
    private QcResultMapper resultMapper;
    
    @Autowired
    private RuleEngineService ruleEngine;
    
    @Autowired
    private BatchQcService batchQcService;
    
    @Autowired
    private BatchQcServiceOptimized batchQcServiceOptimized;
    
    public List<RuleDTO> getAllRules() {
        List<KiroQcRule> rules = ruleMapper.findAllRules();
        return rules.stream().map(this::toRuleDTO).collect(Collectors.toList());
    }
    
    public List<RuleDTO> getRulesByStatus(String status) {
        List<KiroQcRule> rules = ruleMapper.findByStatus(status);
        return rules.stream().map(this::toRuleDTO).collect(Collectors.toList());
    }
    
    public List<RuleDTO> searchRules(String status, String fieldCode, String keyword) {
        List<KiroQcRule> rules = ruleMapper.searchRules(status, fieldCode, keyword);
        return rules.stream().map(this::toRuleDTO).collect(Collectors.toList());
    }
    
    public RuleDTO getRuleById(Long id) {
        KiroQcRule rule = ruleMapper.findById(id);
        if (rule == null) {
            throw new RuntimeException("规则不存在: " + id);
        }
        return toRuleDTO(rule);
    }
    
    @Transactional
    public RuleDTO updateRule(RuleUpdateRequest request) {
        KiroQcRule rule = ruleMapper.findById(request.getId());
        if (rule == null) {
            throw new RuntimeException("规则不存在: " + request.getId());
        }
        
        rule.setFieldName(request.getFieldName());
        rule.setFieldCode(request.getFieldCode());
        rule.setTableName(request.getTableName());
        rule.setRuleType(request.getRuleType());
        rule.setDeductScore(request.getDeductScore());
        rule.setDescription(request.getDescription());
        rule.setStatus(request.getStatus());
        rule.setSourceTables(request.getSourceTables());
        rule.setDictTypes(request.getDictTypes());
        rule.setInvolvedTables(request.getInvolvedTables());
        rule.setInvolvedFields(request.getInvolvedFields());
        
        ruleMapper.update(rule);
        return toRuleDTO(rule);
    }
    
    @Transactional
    public void updateRuleStatus(Long id, String status) {
        KiroQcRule rule = ruleMapper.findById(id);
        if (rule == null) {
            throw new RuntimeException("规则不存在: " + id);
        }
        
        if (!"draft".equals(status) && !"active".equals(status)) {
            throw new RuntimeException("无效的状态值，只能是draft或active");
        }
        
        ruleMapper.updateStatus(id, status);
    }
    
    public RuleTestResult testRule(RuleTestRequest request) {
        KiroQcRule rule = ruleMapper.findById(request.getRuleId());
        if (rule == null) {
            throw new RuntimeException("规则不存在: " + request.getRuleId());
        }
        
        // 获取测试数据
        Map<String, Map<String, Object>> records;
        if (request.getA48() != null && request.getA49() != null) {
            // 测试单个病案
            Map<String, Object> record = recordMapper.findByKey(request.getA48(), request.getA49());
            records = new HashMap<>();
            if (record != null) {
                records.put(request.getA48() + "_" + request.getA49(), record);
            }
        } else {
            // 测试批量数据
            records = recordMapper.findRecords(request.getYear(), null, request.getMonth(), null, null, null);
        }
        
        // 应用规则
        List<KiroQcRule> testRules = new ArrayList<>();
        testRules.add(rule);
        
        RuleTestResult result = new RuleTestResult();
        result.setRuleId(rule.getId());
        result.setRuleCode(rule.getRuleCode());
        result.setDescription(rule.getDescription());
        result.setTotalRecords(records.size());
        
        List<RuleTestResult.ViolationDetail> violations = new ArrayList<>();
        int violationCount = 0;
        int limit = request.getLimit() != null ? request.getLimit() : 10;
        
        for (Map.Entry<String, Map<String, Object>> entry : records.entrySet()) {
            Map<String, Object> record = entry.getValue();
            List<RuleEngineService.RuleViolation> ruleViolations = ruleEngine.checkRecord(record, testRules);
            
            if (!ruleViolations.isEmpty()) {
                violationCount++;
                if (violations.size() < limit) {
                    for (RuleEngineService.RuleViolation v : ruleViolations) {
                        RuleTestResult.ViolationDetail detail = new RuleTestResult.ViolationDetail();
                        detail.setMrKey(record.get("A48") + "_" + record.get("A49"));
                        detail.setA48(record.get("A48").toString());
                        detail.setA49(record.get("A49").toString());
                        detail.setFieldCode(v.fieldCode);
                        detail.setActualValue(v.actualValue);
                        detail.setExpectedValue(v.expectedValue);
                        detail.setReason(v.ruleDescription);
                        violations.add(detail);
                    }
                }
            }
        }
        
        result.setViolationCount(violationCount);
        result.setViolationRate(records.size() > 0 ? (violationCount * 100.0 / records.size()) : 0.0);
        result.setViolations(violations);
        
        return result;
    }
    
    @Transactional
    public QcResultDTO checkSingleCase(String a48, String a49) {
        Map<String, Object> record = recordMapper.findByKey(a48, a49);
        if (record == null || record.isEmpty()) {
            throw new RuntimeException("病案不存在: " + a48 + "_" + a49);
        }
        
        List<KiroQcRule> rules = ruleMapper.findActiveRules();
        List<RuleEngineService.RuleViolation> violations = ruleEngine.checkRecord(record, rules);
        
        String mrKey = a48 + "_" + a49;
        resultMapper.deleteDefectsByMrKey(mrKey);
        
        BigDecimal totalDeduct = BigDecimal.ZERO;
        for (RuleEngineService.RuleViolation v : violations) {
            KiroQcDefectDetail detail = new KiroQcDefectDetail();
            detail.setMrKey(mrKey);
            detail.setA48(a48);
            detail.setA49(a49);
            detail.setRuleId(v.ruleId);
            detail.setRuleCode(v.ruleCode);
            detail.setFieldCode(v.fieldCode);
            detail.setFieldName(v.fieldName);
            detail.setActualValue(v.actualValue);
            detail.setExpectedValue(v.expectedValue);
            detail.setRuleDescription(v.ruleDescription);
            detail.setDeductScore(v.deductScore.abs());
            resultMapper.saveDefectDetail(detail);
            
            totalDeduct = totalDeduct.add(v.deductScore.abs());
        }
        
        BigDecimal finalScore = new BigDecimal("100").subtract(totalDeduct);
        if (finalScore.compareTo(BigDecimal.ZERO) < 0) {
            finalScore = BigDecimal.ZERO;
        }
        
        String b15 = record.get("B15") != null ? record.get("B15").toString() : null;
        Integer year = extractYear(b15);
        Integer quarter = extractQuarter(b15);
        Integer month = extractMonth(b15);
        
        KiroQcCaseResult caseResult = new KiroQcCaseResult();
        caseResult.setMrKey(mrKey);
        caseResult.setA48(a48);
        caseResult.setA49(a49);
        caseResult.setB15(b15);
        caseResult.setCheckYear(year);
        caseResult.setCheckQuarter(quarter);
        caseResult.setCheckMonth(month);
        caseResult.setDefectCount(violations.size());
        caseResult.setTotalDeduct(totalDeduct);
        caseResult.setFinalScore(finalScore);
        resultMapper.saveCaseResult(caseResult);

        return buildQcResultDTO(caseResult, violations);
    }

    public MultiQcResultDTO checkMultipleCases(Integer year, Integer quarter, Integer month, Integer limit) {
        long t0 = System.currentTimeMillis();

        // 获取病案数据(限制数量)
        Map<String, Map<String, Object>> records = recordMapper.findRecords(
            year, quarter, month, limit, null, null);
        long t1 = System.currentTimeMillis();
        log.info("[性能] 获取病案数据耗时: {}ms", t1 - t0);

        if (records.isEmpty()) {
            throw new RuntimeException("未找到病案数据");
        }

        log.info("开始检查 {} 个病案", records.size());

        // 获取活跃规则
        List<KiroQcRule> rules = ruleMapper.findActiveRules();
        long t2 = System.currentTimeMillis();
        log.info("[性能] 获取规则耗时: {}ms, 规则数: {}", t2 - t1, rules.size());

        // 处理每个病案
        List<QcResultDTO> results = new ArrayList<>();
        int totalDefects = 0;
        BigDecimal totalScore = BigDecimal.ZERO;

        int caseNum = 0;
        for (Map<String, Object> record : records.values()) {
            long caseStart = System.currentTimeMillis();
            try {
                String a48 = record.get("A48").toString();
                String a49 = record.get("A49").toString();
                String mrKey = a48 + "_" + a49;

                // 执行规则检查
                long checkStart = System.currentTimeMillis();
                List<RuleEngineService.RuleViolation> violations = ruleEngine.checkRecord(record, rules);
                long checkEnd = System.currentTimeMillis();

                caseNum++;
                long caseElapsed = checkEnd - caseStart;
                if (caseNum <= 3 || caseElapsed > 1000) {
                    log.info("[性能] 病案#{} {} 规则检查耗时: {}ms, 违规数: {}",
                        caseNum, mrKey, caseElapsed, violations.size());
                }

                // 计算得分
                BigDecimal totalDeduct = BigDecimal.ZERO;
                for (RuleEngineService.RuleViolation v : violations) {
                    totalDeduct = totalDeduct.add(v.deductScore.abs());
                }

                BigDecimal finalScore = new BigDecimal("100").subtract(totalDeduct);
                if (finalScore.compareTo(BigDecimal.ZERO) < 0) {
                    finalScore = BigDecimal.ZERO;
                }

                // 创建病案结果
                String b15 = record.get("B15") != null ? record.get("B15").toString() : null;

                KiroQcCaseResult caseResult = new KiroQcCaseResult();
                caseResult.setMrKey(mrKey);
                caseResult.setA48(a48);
                caseResult.setA49(a49);
                caseResult.setB15(b15);
                caseResult.setDefectCount(violations.size());
                caseResult.setTotalDeduct(totalDeduct);
                caseResult.setFinalScore(finalScore);

                results.add(buildQcResultDTO(caseResult, violations));

                totalDefects += violations.size();
                totalScore = totalScore.add(finalScore);

            } catch (Exception e) {
                log.error("处理病案失败: {} - {}", record.get("A48") + "_" + record.get("A49"), e.getMessage());
            }
        }

        long endTime = System.currentTimeMillis();
        long totalTime = endTime - t0;

        // 构建返回结果
        MultiQcResultDTO result = new MultiQcResultDTO();
        result.setYear(year);
        result.setQuarter(quarter);
        result.setMonth(month);
        result.setCaseCount(results.size());
        result.setTotalTime(totalTime);
        result.setAvgTimePerCase(totalTime / 1000.0 / results.size());
        result.setTotalDefects(totalDefects);
        result.setAvgScore(results.size() > 0 ?
            totalScore.divide(new BigDecimal(results.size()), 2, BigDecimal.ROUND_HALF_UP) :
            BigDecimal.ZERO);
        result.setResults(results);

        log.info("[性能] 多病案质控完成: {} 个病案, 总耗时 {}ms, 平均 {}ms/病案",
            results.size(), totalTime, totalTime / results.size());

        return result;
    }

    public BatchSummaryDTO batchCheck(QcRequest request) {
        String batchKey = buildBatchKey(request);
        
        // 先查询病案数量
        int caseCount = recordMapper.countRecords(
            request.getYear(), request.getQuarter(), request.getMonth());
        
        // 初始化任务状态（强制重置所有字段，包括时间）
        KiroQcBatchSummary summary = new KiroQcBatchSummary();
        summary.setBatchKey(batchKey);
        summary.setPeriodType(request.getPeriodType());
        summary.setCheckYear(request.getYear());
        summary.setCheckQuarter(request.getQuarter());
        summary.setCheckMonth(request.getMonth());
        summary.setStatus("processing");
        summary.setProgress(0);
        summary.setCaseCount(caseCount);
        summary.setTotalDefectCount(0);
        summary.setAvgDefect(BigDecimal.ZERO);
        summary.setAvgScore(new BigDecimal("100"));
        summary.setStartTime(new Date());  // 设置当前时间为开始时间
        summary.setEndTime(null);  // 清空结束时间
        
        resultMapper.saveBatchSummary(summary);
        
        // 异步执行批量质控
        batchQcService.executeBatchCheckAsync(request, batchKey);
        
        return toBatchSummaryDTO(summary);
    }
    
    public BatchSummaryDTO batchCheckOptimized(QcRequest request) {
        String batchKey = buildBatchKey(request) + "_opt";  // 添加后缀区分优化版本
        
        // 验证服务注入
        log.info("BatchQcServiceOptimized注入状态: {}", batchQcServiceOptimized != null);
        
        // 先查询病案数量
        int caseCount = recordMapper.countRecords(
            request.getYear(), request.getQuarter(), request.getMonth());
        
        log.info("启动优化批量质控: 批次键={}, 病案数={}", batchKey, caseCount);
        
        // 初始化任务状态
        KiroQcBatchSummary summary = new KiroQcBatchSummary();
        summary.setBatchKey(batchKey);
        summary.setPeriodType(request.getPeriodType());
        summary.setCheckYear(request.getYear());
        summary.setCheckQuarter(request.getQuarter());
        summary.setCheckMonth(request.getMonth());
        summary.setStatus("processing");
        summary.setProgress(0);
        summary.setCaseCount(caseCount);
        summary.setTotalDefectCount(0);
        summary.setAvgDefect(BigDecimal.ZERO);
        summary.setAvgScore(new BigDecimal("100"));
        summary.setStartTime(new Date());
        summary.setEndTime(null);
        
        resultMapper.saveBatchSummary(summary);
        
        // 异步执行优化批量质控
        try {
            batchQcServiceOptimized.executeBatchCheckAsyncOptimized(request, batchKey);
            log.info("优化批量质控任务已提交: {}", batchKey);
        } catch (Exception e) {
            log.error("提交优化批量质控任务失败: {} - {}", batchKey, e.getMessage(), e);
        }
        
        return toBatchSummaryDTO(summary);
    }
    
    public QcResultDTO getCaseResult(String a48, String a49) {
        String mrKey = a48 + "_" + a49;
        KiroQcCaseResult caseResult = resultMapper.findCaseResult(mrKey);
        if (caseResult == null) {
            throw new RuntimeException("未找到质控结果，请先执行质控");
        }
        
        List<KiroQcDefectDetail> defects = resultMapper.findDefectsByMrKey(mrKey);
        List<RuleEngineService.RuleViolation> violations = defects.stream().map(d -> {
            RuleEngineService.RuleViolation v = new RuleEngineService.RuleViolation();
            v.fieldCode = d.getFieldCode();
            v.fieldName = d.getFieldName();
            v.ruleCode = d.getRuleCode();
            v.actualValue = d.getActualValue();
            v.expectedValue = d.getExpectedValue();
            v.ruleDescription = d.getRuleDescription();
            v.deductScore = d.getDeductScore();
            return v;
        }).collect(Collectors.toList());
        
        return buildQcResultDTO(caseResult, violations);
    }
    
    public BatchSummaryDTO getBatchSummary(QcRequest request) {
        String batchKey = buildBatchKey(request);
        KiroQcBatchSummary summary = resultMapper.findBatchSummary(batchKey);
        if (summary == null) {
            throw new RuntimeException("未找到批量质控结果，请先执行质控");
        }
        return toBatchSummaryDTO(summary);
    }
    
    public List<QcResultDTO> getBatchCaseResults(QcRequest request) {
        List<KiroQcCaseResult> caseResults = resultMapper.findCaseResults(
            request.getYear(), request.getQuarter(), request.getMonth());
        
        return caseResults.stream().map(cr -> {
            List<KiroQcDefectDetail> defects = resultMapper.findDefectsByMrKey(cr.getMrKey());
            List<RuleEngineService.RuleViolation> violations = defects.stream().map(d -> {
                RuleEngineService.RuleViolation v = new RuleEngineService.RuleViolation();
                v.fieldCode = d.getFieldCode();
                v.fieldName = d.getFieldName();
                v.ruleCode = d.getRuleCode();
                v.actualValue = d.getActualValue();
                v.expectedValue = d.getExpectedValue();
                v.ruleDescription = d.getRuleDescription();
                v.deductScore = d.getDeductScore();
                return v;
            }).collect(Collectors.toList());
            return buildQcResultDTO(cr, violations);
        }).collect(Collectors.toList());
    }
    
    private QcResultDTO buildQcResultDTO(KiroQcCaseResult caseResult, List<RuleEngineService.RuleViolation> violations) {
        QcResultDTO dto = new QcResultDTO();
        dto.setMrKey(caseResult.getMrKey());
        dto.setA48(caseResult.getA48());
        dto.setA49(caseResult.getA49());
        dto.setB15(caseResult.getB15());
        dto.setDefectCount(caseResult.getDefectCount());
        dto.setTotalDeduct(caseResult.getTotalDeduct());
        dto.setFinalScore(caseResult.getFinalScore());
        
        // 分离普通违规和Cross规则违规
        List<RuleEngineService.RuleViolation> normalViolations = new ArrayList<>();
        List<RuleEngineService.RuleViolation> crossViolations = new ArrayList<>();
        
        for (RuleEngineService.RuleViolation violation : violations) {
            if (violation.ruleCode != null && violation.ruleCode.startsWith("RULE_CROSS_")) {
                crossViolations.add(violation);
            } else {
                normalViolations.add(violation);
            }
        }
        
        // 处理普通违规（保持原有逻辑）
        List<QcResultDTO.DefectDTO> defectList = normalViolations.stream().map(v -> {
            QcResultDTO.DefectDTO d = new QcResultDTO.DefectDTO();
            d.setFieldCode(v.fieldCode);
            d.setFieldName(v.fieldName);
            d.setRuleCode(v.ruleCode);
            d.setRuleDescription(v.ruleDescription);
            d.setActualValue(v.actualValue);
            d.setExpectedValue(v.expectedValue);
            d.setDeductScore(v.deductScore);
            return d;
        }).collect(Collectors.toList());
        
        // 处理Cross规则违规
        List<QcResultDTO.CrossDefectDTO> crossDefectList = crossViolations.stream().map(v -> {
            QcResultDTO.CrossDefectDTO cd = new QcResultDTO.CrossDefectDTO();
            cd.setRuleCode(v.ruleCode);
            cd.setRuleDescription(v.ruleDescription);
            cd.setDeductScore(v.deductScore);
            
            // 解析Cross规则类型和涉及字段
            parseCrossRuleInfo(cd, v);
            
            return cd;
        }).collect(Collectors.toList());
        
        // 将所有违规合并到allDefects中（保持向后兼容）
        List<QcResultDTO.DefectDTO> allDefects = new ArrayList<>(defectList);
        // 将Cross违规也转换为DefectDTO格式加入allDefects
        crossViolations.forEach(v -> {
            QcResultDTO.DefectDTO d = new QcResultDTO.DefectDTO();
            d.setFieldCode(v.fieldCode);
            d.setFieldName(v.fieldName);
            d.setRuleCode(v.ruleCode);
            d.setRuleDescription(v.ruleDescription);
            d.setActualValue(v.actualValue);
            d.setExpectedValue(v.expectedValue);
            d.setDeductScore(v.deductScore);
            allDefects.add(d);
        });
        
        dto.setAllDefects(allDefects);
        dto.setCrossDefects(crossDefectList);
        
        // 计算Cross规则统计
        dto.setCrossDefectCount(crossViolations.size());
        BigDecimal crossTotalDeduct = crossViolations.stream()
            .map(v -> v.deductScore != null ? v.deductScore.abs() : BigDecimal.ZERO)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
        dto.setCrossTotalDeduct(crossTotalDeduct);
        
        // 按字段分组（只包含普通违规）
        Map<String, List<QcResultDTO.DefectDTO>> byField = defectList.stream()
            .collect(Collectors.groupingBy(QcResultDTO.DefectDTO::getFieldCode));
        dto.setDefectsByField(byField);
        
        return dto;
    }
    
    /**
     * 解析Cross规则信息，填充CrossDefectDTO的详细信息
     */
    private void parseCrossRuleInfo(QcResultDTO.CrossDefectDTO crossDefect, RuleEngineService.RuleViolation violation) {
        String ruleCode = violation.ruleCode;
        
        // 根据规则代码解析类型和涉及字段
        if (ruleCode.contains("TRANSFUSION")) {
            crossDefect.setCrossType("transfusion_logic");
            crossDefect.setInvolvedFields(Arrays.asList("输血记录", "血液费用"));
            crossDefect.setLogicDescription("输血记录与血液费用逻辑不一致");
            crossDefect.setSeverity("medium");
            
            Map<String, String> fieldValues = new HashMap<>();
            fieldValues.put("输血记录", "存在");
            fieldValues.put("血液费用", "无");
            crossDefect.setFieldValues(fieldValues);
            
        } else if (ruleCode.contains("FIELD_PAIR")) {
            crossDefect.setCrossType("field_pair");
            crossDefect.setLogicDescription("字段配对不匹配");
            crossDefect.setSeverity("high");
            
            // 解析字段配对信息
            if (ruleCode.contains("C06x01C_C07x01C")) {
                crossDefect.setInvolvedFields(Arrays.asList("C06x01C", "C07x01C"));
                crossDefect.setLogicDescription("诊断编码与诊断名称不匹配");
            } else if (ruleCode.contains("C14x01C_C15x01C")) {
                crossDefect.setInvolvedFields(Arrays.asList("C14x01C", "C15x01C"));
                crossDefect.setLogicDescription("手术编码与手术名称不匹配");
            }
            
        } else if (ruleCode.contains("GENDER") || ruleCode.contains("AGE")) {
            crossDefect.setCrossType("age_gender");
            crossDefect.setInvolvedFields(Arrays.asList("A12C", "C03C"));
            crossDefect.setLogicDescription("年龄性别与诊断不匹配");
            crossDefect.setSeverity("high");
            
        } else {
            // 默认处理
            crossDefect.setCrossType("logic_check");
            crossDefect.setInvolvedFields(Arrays.asList(violation.fieldCode));
            crossDefect.setLogicDescription("跨字段逻辑检查");
            crossDefect.setSeverity("medium");
        }
    }
    
    public BatchSummaryDTO getBatchStatus(String batchKey) {
        KiroQcBatchSummary summary = resultMapper.findBatchSummary(batchKey);
        if (summary == null) {
            throw new RuntimeException("批量任务不存在: " + batchKey);
        }
        return toBatchSummaryDTO(summary);
    }
    
    private RuleDTO toRuleDTO(KiroQcRule rule) {
        RuleDTO dto = new RuleDTO();
        dto.setId(rule.getId());
        dto.setRuleCode(rule.getRuleCode());
        dto.setFieldName(rule.getFieldName());
        dto.setFieldCode(rule.getFieldCode());
        dto.setTableName(rule.getTableName());
        dto.setRuleType(rule.getRuleType());
        dto.setDeductScore(rule.getDeductScore());
        dto.setDescription(rule.getDescription());
        dto.setStatus(rule.getStatus());
        dto.setSourceTables(rule.getSourceTables());
        dto.setDictTypes(rule.getDictTypes());
        dto.setInvolvedTables(rule.getInvolvedTables());
        dto.setInvolvedFields(rule.getInvolvedFields());
        dto.setUruleContent(rule.getUruleContent());
        dto.setCanonicalExpr(rule.getCanonicalExpr());
        return dto;
    }
    
    private BatchSummaryDTO toBatchSummaryDTO(KiroQcBatchSummary summary) {
        BatchSummaryDTO dto = new BatchSummaryDTO();
        dto.setBatchKey(summary.getBatchKey());
        dto.setPeriodType(summary.getPeriodType());
        dto.setYear(summary.getCheckYear());
        dto.setQuarter(summary.getCheckQuarter());
        dto.setMonth(summary.getCheckMonth());
        dto.setCaseCount(summary.getCaseCount());
        dto.setTotalDefectCount(summary.getTotalDefectCount());
        dto.setAvgDefect(summary.getAvgDefect());
        dto.setAvgScore(summary.getAvgScore());
        dto.setStatus(summary.getStatus());
        dto.setProgress(summary.getProgress());
        dto.setStartTime(summary.getStartTime());
        dto.setEndTime(summary.getEndTime());
        
        // 设置Cross规则统计
        dto.setCrossDefectCount(summary.getCrossDefectCount());
        dto.setCrossTotalDeduct(summary.getCrossTotalDeduct());
        dto.setAvgCrossDefect(summary.getAvgCrossDefect());
        
        // 计算已执行时间（秒）
        if (summary.getStartTime() != null) {
            Date endTime = summary.getEndTime() != null ? summary.getEndTime() : new Date();
            long elapsedMs = endTime.getTime() - summary.getStartTime().getTime();
            dto.setElapsedSeconds(elapsedMs / 1000);
        }
        
        return dto;
    }
    
    private String buildBatchKey(QcRequest request) {
        StringBuilder key = new StringBuilder();
        key.append(request.getYear());
        if (request.getQuarter() != null) {
            key.append("_Q").append(request.getQuarter());
        }
        if (request.getMonth() != null) {
            key.append("_M").append(request.getMonth());
        }
        return key.toString();
    }
    
    private Integer extractYear(String b15) {
        if (b15 == null) return null;
        try {
            return Integer.parseInt(b15.substring(0, 4));
        } catch (Exception e) {
            return null;
        }
    }
    
    private Integer extractQuarter(String b15) {
        Integer month = extractMonth(b15);
        if (month == null) return null;
        return (month - 1) / 3 + 1;
    }
    
    private Integer extractMonth(String b15) {
        if (b15 == null) return null;
        try {
            String[] parts = b15.split("/");
            if (parts.length >= 2) {
                return Integer.parseInt(parts[1]);
            }
        } catch (Exception e) {
        }
        return null;
    }
}
