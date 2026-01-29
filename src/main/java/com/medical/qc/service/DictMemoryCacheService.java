package com.medical.qc.service;

import com.medical.qc.mapper.DictMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import javax.annotation.PostConstruct;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 内存字典缓存服务 - 高性能本地缓存
 * 在应用启动时一次性加载所有字典到内存
 */
@Service
@Slf4j
public class DictMemoryCacheService {

    @Autowired
    private DictMapper dictMapper;

    // 字典数据缓存: dictType -> List<dict_item>
    private final Map<String, List<Map<String, Object>>> dictDataCache = new ConcurrentHashMap<>();

    // 字典验证缓存: dictType -> Set<dict_code>
    private final Map<String, Set<String>> dictCodeCache = new ConcurrentHashMap<>();

    /**
     * 应用启动时预加载所有字典
     */
    @PostConstruct
    public void init() {
        long startTime = System.currentTimeMillis();
        log.info("开始加载字典到内存...");

        try {
            // 获取所有字典类型
            List<String> dictTypes = dictMapper.getAllDictTypes();
            log.info("发现 {} 个字典类型", dictTypes.size());

            int totalItems = 0;
            for (String dictType : dictTypes) {
                try {
                    List<Map<String, Object>> items = dictMapper.getDictsByType(dictType);
                    if (items != null && !items.isEmpty()) {
                        // 缓存完整数据
                        dictDataCache.put(dictType, items);

                        // 提取dict_code集合用于快速验证
                        Set<String> codes = new HashSet<>();
                        for (Map<String, Object> item : items) {
                            Object code = item.get("dict_code");
                            if (code != null) {
                                codes.add(code.toString());
                            }
                        }
                        dictCodeCache.put(dictType, codes);

                        totalItems += items.size();
                    }
                } catch (Exception e) {
                    log.error("加载字典类型 {} 失败: {}", dictType, e.getMessage());
                }
            }

            long elapsed = System.currentTimeMillis() - startTime;
            log.info("字典加载完成: {} 个字典类型, {} 条数据, 耗时 {}ms",
                dictTypes.size(), totalItems, elapsed);

        } catch (Exception e) {
            log.error("字典初始化失败", e);
        }
    }

    /**
     * 获取字典数据
     */
    public List<Map<String, Object>> getDictsByType(String dictType) {
        List<Map<String, Object>> cached = dictDataCache.get(dictType);
        if (cached != null) {
            return cached;
        }

        // 缓存未命中,从数据库加载
        log.warn("字典 {} 缓存未命中,从数据库加载", dictType);
        List<Map<String, Object>> items = dictMapper.getDictsByType(dictType);
        if (items != null && !items.isEmpty()) {
            dictDataCache.put(dictType, items);

            Set<String> codes = new HashSet<>();
            for (Map<String, Object> item : items) {
                Object code = item.get("dict_code");
                if (code != null) {
                    codes.add(code.toString());
                }
            }
            dictCodeCache.put(dictType, codes);
        }

        return items != null ? items : new ArrayList<>();
    }

    /**
     * 快速验证字段值
     */
    public boolean validateFieldValue(String dictType, String value) {
        if (value == null || value.trim().isEmpty()) {
            return false;
        }

        Set<String> codes = dictCodeCache.get(dictType);
        if (codes != null) {
            return codes.contains(value.trim());
        }

        // 缓存未命中,尝试加载
        log.warn("字典验证缓存未命中: {}", dictType);
        getDictsByType(dictType);

        codes = dictCodeCache.get(dictType);
        return codes != null && codes.contains(value.trim());
    }

    /**
     * 验证编码与名称是否匹配
     */
    public boolean validateCodeNameMatch(String dictType, String code, String name) {
        if (code == null || name == null) {
            return false;
        }
        
        List<Map<String, Object>> items = getDictsByType(dictType);
        if (items == null || items.isEmpty()) {
            return false;
        }
        
        for (Map<String, Object> item : items) {
            Object dictCode = item.get("dict_code");
            if (dictCode != null && code.equals(dictCode.toString())) {
                Object dictName = item.get("dict_name");
                return dictName != null && name.equals(dictName.toString());
            }
        }
        
        return false;
    }

    /**
     * 清除所有缓存
     */
    public void clearAll() {
        dictDataCache.clear();
        dictCodeCache.clear();
        log.info("已清除所有字典缓存");
    }

    /**
     * 重新加载所有字典
     */
    public void reload() {
        clearAll();
        init();
    }

    /**
     * 获取缓存统计信息
     */
    public Map<String, Object> getCacheStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("dictTypes", dictDataCache.size());

        int totalItems = dictDataCache.values().stream()
            .mapToInt(List::size)
            .sum();
        stats.put("totalItems", totalItems);

        return stats;
    }
}
