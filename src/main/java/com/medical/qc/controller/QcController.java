package com.medical.qc.controller;

import com.medical.qc.common.Result;
import com.medical.qc.dto.*;
import com.medical.qc.service.QcService;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import io.swagger.annotations.ApiParam;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@Api(tags = "质控管理")
@RestController
@RequestMapping("/api/qc")
@CrossOrigin
public class QcController {
    
    @Autowired
    private QcService qcService;
    
    @ApiOperation("服务状态检查")
    @GetMapping("/status")
    public Result<String> getStatus() {
        return Result.success("服务运行正常", "OK");
    }
    
    @ApiOperation("获取所有规则列表")
    @GetMapping("/rules")
    public Result<List<RuleDTO>> getAllRules() {
        return Result.success(qcService.getAllRules());
    }
    
    @ApiOperation("按状态获取规则列表")
    @GetMapping("/rules/status/{status}")
    public Result<List<RuleDTO>> getRulesByStatus(
            @ApiParam("状态: draft-未完善, active-已完善") @PathVariable String status) {
        return Result.success(qcService.getRulesByStatus(status));
    }
    
    @ApiOperation("获取单个规则详情")
    @GetMapping("/rules/{id}")
    public Result<RuleDTO> getRuleById(@PathVariable Long id) {
        try {
            return Result.success(qcService.getRuleById(id));
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
    
    @ApiOperation("搜索规则")
    @GetMapping("/rules/search")
    public Result<List<RuleDTO>> searchRules(
            @ApiParam("状态: draft/active") @RequestParam(required = false) String status,
            @ApiParam("字段编码") @RequestParam(required = false) String fieldCode,
            @ApiParam("关键词") @RequestParam(required = false) String keyword) {
        return Result.success(qcService.searchRules(status, fieldCode, keyword));
    }
    
    @ApiOperation("更新规则")
    @PutMapping("/rules")
    public Result<RuleDTO> updateRule(@RequestBody RuleUpdateRequest request) {
        try {
            RuleDTO result = qcService.updateRule(request);
            return Result.success("规则更新成功", result);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
    
    @ApiOperation("更新规则状态")
    @PutMapping("/rules/{id}/status")
    public Result<String> updateRuleStatus(
            @ApiParam("规则ID") @PathVariable Long id,
            @ApiParam("状态: draft/active") @RequestParam String status) {
        try {
            qcService.updateRuleStatus(id, status);
            return Result.success("状态更新成功");
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
    
    @ApiOperation("规则试运行")
    @PostMapping("/rules/test")
    public Result<RuleTestResult> testRule(@RequestBody RuleTestRequest request) {
        try {
            RuleTestResult result = qcService.testRule(request);
            return Result.success("试运行完成", result);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
    
    @ApiOperation("单个病案质控")
    @PostMapping("/check/single")
    public Result<QcResultDTO> checkSingleCase(
            @ApiParam("病案号A48") @RequestParam String a48,
            @ApiParam("住院次数A49") @RequestParam String a49) {
        try {
            QcResultDTO result = qcService.checkSingleCase(a48, a49);
            return Result.success("质控完成", result);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
    
    @ApiOperation("批量质控")
    @PostMapping("/check/batch")
    public Result<BatchSummaryDTO> batchCheck(@RequestBody QcRequest request) {
        try {
            BatchSummaryDTO result = qcService.batchCheck(request);
            return Result.success("批量质控完成", result);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
    
    @ApiOperation("优化批量质控（高性能版本）")
    @PostMapping("/check/batch/optimized")
    public Result<BatchSummaryDTO> batchCheckOptimized(@RequestBody QcRequest request) {
        try {
            BatchSummaryDTO result = qcService.batchCheckOptimized(request);
            return Result.success("优化批量质控已启动", result);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }

    @ApiOperation("检查多个病案 - 用于逐步测试")
    @PostMapping("/check/multi")
    public Result<MultiQcResultDTO> checkMultipleCases(@RequestBody CheckMultiRequest request) {
        try {
            MultiQcResultDTO result = qcService.checkMultipleCases(
                request.getYear(),
                request.getQuarter(),
                request.getMonth(),
                request.getLimit()
            );
            return Result.success("多病案质控完成", result);
        } catch (Exception e) {
            return Result.error("多病案质控失败: " + e.getMessage());
        }
    }
    
    @ApiOperation("查询批量任务状态")
    @GetMapping("/batch/status/{batchKey}")
    public Result<BatchSummaryDTO> getBatchStatus(
            @ApiParam("批次键，如: 2023_M1, 2020_Q1, 2023") @PathVariable String batchKey) {
        try {
            BatchSummaryDTO result = qcService.getBatchStatus(batchKey);
            return Result.success(result);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
    
    @ApiOperation("获取单个病案质控结果")
    @GetMapping("/result/case")
    public Result<QcResultDTO> getCaseResult(
            @ApiParam("病案号A48") @RequestParam String a48,
            @ApiParam("住院次数A49") @RequestParam String a49) {
        try {
            QcResultDTO result = qcService.getCaseResult(a48, a49);
            return Result.success(result);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
    
    @ApiOperation("获取批量质控汇总")
    @PostMapping("/result/batch/summary")
    public Result<BatchSummaryDTO> getBatchSummary(@RequestBody QcRequest request) {
        try {
            BatchSummaryDTO result = qcService.getBatchSummary(request);
            return Result.success(result);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
    
    @ApiOperation("获取批量质控明细列表")
    @PostMapping("/result/batch/cases")
    public Result<List<QcResultDTO>> getBatchCaseResults(@RequestBody QcRequest request) {
        try {
            List<QcResultDTO> results = qcService.getBatchCaseResults(request);
            return Result.success(results);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
}
