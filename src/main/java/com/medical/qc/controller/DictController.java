package com.medical.qc.controller;

import com.medical.qc.common.Result;
import com.medical.qc.dto.DictDTO;
import com.medical.qc.dto.DictQueryRequest;
import com.medical.qc.dto.FieldSearchResult;
import com.medical.qc.service.DictService;
import com.medical.qc.service.DictCacheService;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import io.swagger.annotations.ApiParam;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.Collections;
import java.util.List;
import java.util.Map;

@Api(tags = "字典管理")
@RestController
@RequestMapping("/api/dict")
@CrossOrigin
@Slf4j
public class DictController {
    
    @Autowired
    private DictService dictService;
    
    @Autowired
    private DictCacheService dictCacheService;
    
    @ApiOperation("查询字典数据")
    @PostMapping("/query")
    public Result<List<DictDTO>> queryDicts(@RequestBody Map<String, Object> requestMap) {
        try {
            DictQueryRequest request = new DictQueryRequest();
            
            // Handle both single dictTypeCode and list of dictTypeCodes
            if (requestMap.containsKey("dictTypeCode")) {
                String singleCode = (String) requestMap.get("dictTypeCode");
                request.setDictTypeCodes(Collections.singletonList(singleCode));
            } else if (requestMap.containsKey("dictTypeCodes")) {
                request.setDictTypeCodes((List<String>) requestMap.get("dictTypeCodes"));
            }
            
            if (requestMap.containsKey("keyword")) {
                request.setKeyword((String) requestMap.get("keyword"));
            }
            
            if (requestMap.containsKey("limit")) {
                request.setLimit((Integer) requestMap.get("limit"));
            }
            
            List<DictDTO> results = dictService.queryDicts(request);
            return Result.success(results);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
    
    @ApiOperation("获取所有字典类型")
    @GetMapping("/types")
    public Result<List<String>> getAllDictTypes() {
        return Result.success(dictService.getAllDictTypes());
    }
    
    @ApiOperation("获取字典类型名称映射")
    @GetMapping("/type-names")
    public Result<Map<String, String>> getDictTypeNames() {
        return Result.success(dictService.getDictTypeNames());
    }
    
    @ApiOperation("按类型获取字典")
    @GetMapping("/type/{dictTypeCode}")
    public Result<List<DictDTO>> getDictsByType(
            @ApiParam("字典类型代码") @PathVariable String dictTypeCode) {
        try {
            List<DictDTO> results = dictService.getDictsByType(dictTypeCode);
            return Result.success(results);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
    
    @ApiOperation("搜索字段所在表")
    @GetMapping("/field/search")
    public Result<FieldSearchResult> searchField(
            @ApiParam("字段名称") @RequestParam(required = false) String fieldName,
            @ApiParam("字段代码") @RequestParam(required = false) String fieldCode) {
        try {
            String searchTerm = fieldName != null ? fieldName : fieldCode;
            if (searchTerm == null || searchTerm.trim().isEmpty()) {
                return Result.error("fieldName or fieldCode is required");
            }
            FieldSearchResult result = dictService.searchFieldInTables(searchTerm);
            return Result.success(result);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
    
    @ApiOperation("搜索字段所在表 (别名)")
    @GetMapping("/fields/search")
    public Result<FieldSearchResult> searchFields(
            @ApiParam("关键词") @RequestParam String keyword) {
        try {
            FieldSearchResult result = dictService.searchFieldInTables(keyword);
            return Result.success(result);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
    
    @ApiOperation("验证字段值是否在字典中")
    @PostMapping("/validate")
    public Result<Boolean> validateFieldValue(@RequestBody Map<String, String> request) {
        try {
            String dictTypeCode = request.get("dictTypeCode");
            String value = request.get("value");
            
            if (dictTypeCode == null || value == null) {
                return Result.error("dictTypeCode and value are required");
            }
            
            boolean isValid = dictService.validateFieldValue(dictTypeCode, value);
            return Result.success(isValid);
        } catch (Exception e) {
            return Result.error(e.getMessage());
        }
    }
    
    @ApiOperation("获取缓存统计信息")
    @GetMapping("/cache/stats")
    public Result<Map<String, Object>> getCacheStats() {
        try {
            Map<String, Object> stats = dictCacheService.getCacheStats();
            return Result.success(stats);
        } catch (Exception e) {
            log.error("获取缓存统计失败", e);
            return Result.error("获取缓存统计失败: " + e.getMessage());
        }
    }
    
    @ApiOperation("重新加载字典缓存")
    @PostMapping("/cache/reload")
    public Result<String> reloadCache() {
        try {
            dictCacheService.reloadAllDictCache();
            return Result.success("字典缓存重新加载成功");
        } catch (Exception e) {
            log.error("重新加载缓存失败", e);
            return Result.error("重新加载缓存失败: " + e.getMessage());
        }
    }
    
    @ApiOperation("清除字典缓存")
    @DeleteMapping("/cache")
    public Result<String> clearCache() {
        try {
            dictCacheService.clearAllDictCache();
            return Result.success("字典缓存清除成功");
        } catch (Exception e) {
            log.error("清除缓存失败", e);
            return Result.error("清除缓存失败: " + e.getMessage());
        }
    }
    
    @ApiOperation("清除指定字典类型缓存")
    @DeleteMapping("/cache/{dictTypeCode}")
    public Result<String> clearDictCache(@PathVariable String dictTypeCode) {
        try {
            dictCacheService.clearDictCache(dictTypeCode);
            return Result.success("字典缓存清除成功: " + dictTypeCode);
        } catch (Exception e) {
            log.error("清除字典缓存失败: {}", dictTypeCode, e);
            return Result.error("清除字典缓存失败: " + e.getMessage());
        }
    }
}