package com.medical.qc.service;

import com.medical.qc.dto.QcRequest;
import com.medical.qc.entity.*;
import com.medical.qc.mapper.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Service
public class BatchQcService {
    
    @Autowired
    private QcRuleMapper ruleMapper;
    
    @Autowired
    private MedicalRecordMapper recordMapper;
    
    @Autowired
    private QcResultMapper resultMapper;
    
    @Autowired
    private RuleEngineService ruleEngine;
    
    // 规则缓存，任务完成后清理
    private final Map<String, List<KiroQcRule>> ruleCache = new ConcurrentHashMap<>();
    
    @Async("qcTaskExecutor")
    public void executeBatchCheckAsync(QcRequest request, String batchKey) {
        log.info("开始异步批量质控任务: {}", batchKey);
        
        try {
            // 初始化任务状态
            KiroQcBatchSummary summary = initBatchSummary(request, batchKey);
            
            // 获取病案数据
            Map<String, Map<String, Object>> records = recordMapper.findRecords(
                request.getYear(), request.getQuarter(), request.getMonth(), null, null, null);
            
            int total = records.size();
            log.info("批次 {} 共 {} 条病案", batchKey, total);
            
            if (total == 0) {
                summary.setStatus("completed");
                summary.setProgress(100);
                summary.setEndTime(new Date());
                resultMapper.saveBatchSummary(summary);
                return;
            }
            
            // 获取并缓存活跃规则
            List<KiroQcRule> rules = getCachedRules(batchKey);
            log.info("批次 {} 使用 {} 条活跃规则", batchKey, rules.size());
            
            // 批量处理病案
            processBatchRecords(records, rules, request, summary, batchKey);
            
            // 完成任务
            summary.setStatus("completed");
            summary.setProgress(100);
            summary.setEndTime(new Date());
            resultMapper.saveBatchSummary(summary);
            
            log.info("批量质控任务完成: {}, 共处理 {} 条病案", batchKey, total);
            
        } catch (Exception e) {
            log.error("批量质控任务失败: {} - {}", batchKey, e.getMessage(), e);
            updateBatchStatus(batchKey, "failed", 0);
        } finally {
            // 清理缓存
            clearRuleCache(batchKey);
        }
    }
    
    private KiroQcBatchSummary initBatchSummary(QcRequest request, String batchKey) {
        KiroQcBatchSummary summary = new KiroQcBatchSummary();
        summary.setBatchKey(batchKey);
        summary.setPeriodType(request.getPeriodType());
        summary.setCheckYear(request.getYear());
        summary.setCheckQuarter(request.getQuarter());
        summary.setCheckMonth(request.getMonth());
        summary.setStatus("processing");
        summary.setProgress(0);
        summary.setCaseCount(0);
        summary.setTotalDefectCount(0);
        summary.setAvgDefect(BigDecimal.ZERO);
        summary.setAvgScore(new BigDecimal("100"));
        summary.setStartTime(new Date());
        resultMapper.saveBatchSummary(summary);
        return summary;
    }
    
    private List<KiroQcRule> getCachedRules(String batchKey) {
        return ruleCache.computeIfAbsent(batchKey, k -> ruleMapper.findActiveRules());
    }
    
    private void clearRuleCache(String batchKey) {
        ruleCache.remove(batchKey);
        log.info("清理批次 {} 的规则缓存", batchKey);
    }
    
    private void processBatchRecords(Map<String, Map<String, Object>> records, 
                                     List<KiroQcRule> rules,
                                     QcRequest request,
                                     KiroQcBatchSummary summary,
                                     String batchKey) {
        int total = records.size();
        int processed = 0;
        int totalDefects = 0;
        BigDecimal totalScoreSum = BigDecimal.ZERO;
        
        // 批量数据缓冲区
        List<KiroQcCaseResult> caseResultBatch = new ArrayList<>(100);
        List<KiroQcDefectDetail> defectDetailBatch = new ArrayList<>(500);
        
        for (Map.Entry<String, Map<String, Object>> entry : records.entrySet()) {
            Map<String, Object> record = entry.getValue();
            String a48 = record.get("A48").toString();
            String a49 = record.get("A49").toString();
            String mrKey = a48 + "_" + a49;
            
            try {
                // 执行规则检查
                List<RuleEngineService.RuleViolation> violations = ruleEngine.checkRecord(record, rules);
                
                // 计算得分
                BigDecimal totalDeduct = BigDecimal.ZERO;
                for (RuleEngineService.RuleViolation v : violations) {
                    totalDeduct = totalDeduct.add(v.deductScore.abs());
                }
                
                BigDecimal finalScore = new BigDecimal("100").subtract(totalDeduct);
                if (finalScore.compareTo(BigDecimal.ZERO) < 0) {
                    finalScore = BigDecimal.ZERO;
                }
                
                // 准备病案结果
                String b15 = record.get("B15") != null ? record.get("B15").toString() : null;
                KiroQcCaseResult caseResult = new KiroQcCaseResult();
                caseResult.setMrKey(mrKey);
                caseResult.setA48(a48);
                caseResult.setA49(a49);
                caseResult.setB15(b15);
                caseResult.setCheckYear(request.getYear());
                caseResult.setCheckQuarter(request.getQuarter());
                caseResult.setCheckMonth(request.getMonth());
                caseResult.setDefectCount(violations.size());
                caseResult.setTotalDeduct(totalDeduct);
                caseResult.setFinalScore(finalScore);
                caseResultBatch.add(caseResult);
                
                // 准备缺陷明细
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
                    defectDetailBatch.add(detail);
                }
                
                totalDefects += violations.size();
                totalScoreSum = totalScoreSum.add(finalScore);
                
            } catch (Exception e) {
                log.error("检查病案失败: {} - {}", mrKey, e.getMessage());
            }
            
            processed++;
            
            // 每100条或最后一批，批量保存到数据库
            if (processed % 100 == 0 || processed == total) {
                saveBatchResults(caseResultBatch, defectDetailBatch);
                caseResultBatch.clear();
                defectDetailBatch.clear();
                
                // 更新进度（每100条更新一次）
                updateProgress(summary, processed, total, totalDefects, totalScoreSum);
            }
        }
    }
    
    @Transactional
    private void saveBatchResults(List<KiroQcCaseResult> caseResults, 
                                  List<KiroQcDefectDetail> defectDetails) {
        if (caseResults.isEmpty()) {
            return;
        }
        
        // 批量删除旧的缺陷记录
        for (KiroQcCaseResult result : caseResults) {
            resultMapper.deleteDefectsByMrKey(result.getMrKey());
        }
        
        // 批量插入病案结果
        for (KiroQcCaseResult result : caseResults) {
            resultMapper.saveCaseResult(result);
        }
        
        // 批量插入缺陷明细
        for (KiroQcDefectDetail detail : defectDetails) {
            resultMapper.saveDefectDetail(detail);
        }
    }
    
    private void updateProgress(KiroQcBatchSummary summary, int processed, int total, 
                               int totalDefects, BigDecimal totalScoreSum) {
        int progress = (int) ((processed * 100.0) / total);
        summary.setProgress(progress);
        summary.setCaseCount(processed);
        summary.setTotalDefectCount(totalDefects);
        summary.setAvgDefect(processed > 0 ? 
            new BigDecimal(totalDefects).divide(new BigDecimal(processed), 4, RoundingMode.HALF_UP) : BigDecimal.ZERO);
        summary.setAvgScore(processed > 0 ? 
            totalScoreSum.divide(new BigDecimal(processed), 2, RoundingMode.HALF_UP) : new BigDecimal("100"));
        resultMapper.saveBatchSummary(summary);
    }
    
    private void updateBatchStatus(String batchKey, String status, int progress) {
        try {
            KiroQcBatchSummary summary = resultMapper.findBatchSummary(batchKey);
            if (summary != null) {
                summary.setStatus(status);
                summary.setProgress(progress);
                if ("failed".equals(status) || "completed".equals(status)) {
                    summary.setEndTime(new Date());
                }
                resultMapper.saveBatchSummary(summary);
            }
        } catch (Exception e) {
            log.error("更新批次状态失败: {} - {}", batchKey, e.getMessage());
        }
    }
}
