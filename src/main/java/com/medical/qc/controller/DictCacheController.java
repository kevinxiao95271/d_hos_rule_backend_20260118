package com.medical.qc.controller;

import com.medical.qc.common.Result;
import com.medical.qc.service.DictCacheServiceEnhanced;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import io.swagger.annotations.ApiParam;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@Api(tags = "字典缓存管理")
@RestController
@RequestMapping("/api/dict/enhanced")
@CrossOrigin
public class DictCacheController {
    
    @Autowired
    private DictCacheServiceEnhanced dictCacheService;
    
    @ApiOperation("获取缓存状态")
    @GetMapping("/status")
    public Result<Map<String, Object>> getCacheStatus() {
        try {
            Map<String, Object> stats = dictCacheService.getCacheStats();
            return Result.success("缓存状态获取成功", stats);
        } catch (Exception e) {
            return Result.error("获取缓存状态失败: " + e.getMessage());
        }
    }
    
    @ApiOperation("预热字典缓存")
    @PostMapping("/warmup")
    public Result<String> warmupCache() {
        try {
            dictCacheService.warmupAllDictCache();
            return Result.success("字典缓存预热完成");
        } catch (Exception e) {
            return Result.error("字典缓存预热失败: " + e.getMessage());
        }
    }
    
    @ApiOperation("重新加载字典缓存")
    @PostMapping("/reload")
    public Result<String> reloadCache() {
        try {
            dictCacheService.loadAllDictToMemory();
            return Result.success("字典缓存重新加载完成");
        } catch (Exception e) {
            return Result.error("字典缓存重新加载失败: " + e.getMessage());
        }
    }
    
    @ApiOperation("清理字典缓存")
    @PostMapping("/clear")
    public Result<String> clearCache() {
        try {
            dictCacheService.clearAllDictCache();
            return Result.success("字典缓存清理完成");
        } catch (Exception e) {
            return Result.error("字典缓存清理失败: " + e.getMessage());
        }
    }
    
    @ApiOperation("验证字典值")
    @PostMapping("/validate")
    public Result<Boolean> validateDictValue(
            @ApiParam("字典类型") @RequestParam String dictType,
            @ApiParam("字典值") @RequestParam String value) {
        try {
            boolean isValid = dictCacheService.validateDictValue(dictType, value);
            return Result.success("验证完成", isValid);
        } catch (Exception e) {
            return Result.error("字典验证失败: " + e.getMessage());
        }
    }
    
    @ApiOperation("批量验证字典值")
    @PostMapping("/validate/batch")
    public Result<Map<String, Boolean>> batchValidateDictValues(
            @ApiParam("字典类型") @RequestParam String dictType,
            @ApiParam("字典值列表") @RequestBody List<String> values) {
        try {
            Map<String, Boolean> results = dictCacheService.batchValidateDictValues(dictType, values);
            return Result.success("批量验证完成", results);
        } catch (Exception e) {
            return Result.error("批量字典验证失败: " + e.getMessage());
        }
    }
    
    @ApiOperation("获取字典名称")
    @GetMapping("/name/{dictType}/{dictCode}")
    public Result<String> getDictName(
            @ApiParam("字典类型") @PathVariable String dictType,
            @ApiParam("字典代码") @PathVariable String dictCode) {
        try {
            String dictName = dictCacheService.getDictName(dictType, dictCode);
            return Result.success("字典名称获取成功", dictName);
        } catch (Exception e) {
            return Result.error("获取字典名称失败: " + e.getMessage());
        }
    }
}
