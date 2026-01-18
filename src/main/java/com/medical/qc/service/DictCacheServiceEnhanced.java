package com.medical.qc.service;

import com.medical.qc.mapper.DictMapper;
import com.medical.qc.entity.KiroQcDict;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import javax.annotation.PostConstruct;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;

@Slf4j
@Service
public class DictCacheServiceEnhanced {
    
    @Autowired
    private DictMapper dictMapper;
    
    @Autowired(required = false)
    private RedisTemplate<String, String> redisTemplate;
    
    // 内存缓存作为Redis的备选方案
    private final Map<String, Set<String>> memoryDictCache = new ConcurrentHashMap<>();
    private final Map<String, Map<String, String>> memoryDictNameCache = new ConcurrentHashMap<>();
    private volatile boolean cacheLoaded = false;
    private volatile long lastLoadTime = 0;
    
    // 缓存刷新间隔（30分钟）
    private static final long CACHE_REFRESH_INTERVAL = 30 * 60 * 1000;
    
    @PostConstruct
    public void init() {
        log.info("初始化字典缓存服务...");
        loadAllDictToMemory();
    }
    
    /**
     * 加载所有字典到内存缓存
     */
    public synchronized void loadAllDictToMemory() {
        log.info("开始加载字典数据到内存缓存...");
        
        try {
            // 清空现有缓存
            memoryDictCache.clear();
            memoryDictNameCache.clear();
            
            // 获取所有字典数据
            List<KiroQcDict> allDicts = dictMapper.findAllActiveDict();
            
            // 按字典类型分组
            Map<String, List<KiroQcDict>> dictsByType = new HashMap<>();
            for (KiroQcDict dict : allDicts) {
                dictsByType.computeIfAbsent(dict.getDictTypeCode(), k -> new ArrayList<>()).add(dict);
            }
            
            // 构建缓存
            int totalCached = 0;
            for (Map.Entry<String, List<KiroQcDict>> entry : dictsByType.entrySet()) {
                String dictType = entry.getKey();
                List<KiroQcDict> dicts = entry.getValue();
                
                // 构建代码集合（用于快速验证）
                Set<String> codes = new HashSet<>();
                Map<String, String> nameMap = new HashMap<>();
                
                for (KiroQcDict dict : dicts) {
                    codes.add(dict.getDictCode());
                    nameMap.put(dict.getDictCode(), dict.getDictName());
                }
                
                memoryDictCache.put(dictType, codes);
                memoryDictNameCache.put(dictType, nameMap);
                totalCached += dicts.size();
            }
            
            cacheLoaded = true;
            lastLoadTime = System.currentTimeMillis();
            
            log.info("字典缓存加载完成: {} 个类型, {} 条记录", dictsByType.size(), totalCached);
            
        } catch (Exception e) {
            log.error("加载字典缓存失败: {}", e.getMessage(), e);
            cacheLoaded = false;
        }
    }
    
    /**
     * 验证字典值是否有效
     */
    public boolean validateDictValue(String dictType, String value) {
        if (dictType == null || value == null) {
            return false;
        }
        
        // 检查是否需要刷新缓存
        checkAndRefreshCache();
        
        try {
            // 优先使用Redis缓存
            if (redisTemplate != null) {
                try {
                    String cacheKey = "dict:codes:" + dictType;
                    Boolean isMember = redisTemplate.opsForSet().isMember(cacheKey, value);
                    if (isMember != null) {
                        log.debug("Redis字典验证 {}:{} = {}", dictType, value, isMember);
                        return isMember;
                    }
                } catch (Exception e) {
                    log.warn("Redis字典验证失败，使用内存缓存: {}", e.getMessage());
                }
            }
            
            // 使用内存缓存
            Set<String> codes = memoryDictCache.get(dictType);
            if (codes != null) {
                boolean isValid = codes.contains(value);
                log.debug("内存字典验证 {}:{} = {}", dictType, value, isValid);
                return isValid;
            } else {
                log.warn("字典类型 {} 缓存未找到", dictType);
                return false;
            }
            
        } catch (Exception e) {
            log.error("字典验证异常 {}:{} - {}", dictType, value, e.getMessage());
            return false;
        }
    }
    
    /**
     * 批量验证字典值
     */
    public Map<String, Boolean> batchValidateDictValues(String dictType, List<String> values) {
        Map<String, Boolean> results = new HashMap<>();
        
        if (dictType == null || values == null || values.isEmpty()) {
            return results;
        }
        
        // 检查是否需要刷新缓存
        checkAndRefreshCache();
        
        try {
            // 使用内存缓存进行批量验证（更快）
            Set<String> codes = memoryDictCache.get(dictType);
            if (codes != null) {
                for (String value : values) {
                    results.put(value, codes.contains(value));
                }
                log.debug("批量字典验证 {} - {} 个值", dictType, values.size());
            } else {
                log.warn("字典类型 {} 缓存未找到", dictType);
                for (String value : values) {
                    results.put(value, false);
                }
            }
            
        } catch (Exception e) {
            log.error("批量字典验证异常 {} - {}", dictType, e.getMessage());
            for (String value : values) {
                results.put(value, false);
            }
        }
        
        return results;
    }
    
    /**
     * 获取字典名称
     */
    public String getDictName(String dictType, String dictCode) {
        if (dictType == null || dictCode == null) {
            return null;
        }
        
        // 检查是否需要刷新缓存
        checkAndRefreshCache();
        
        try {
            Map<String, String> nameMap = memoryDictNameCache.get(dictType);
            if (nameMap != null) {
                return nameMap.get(dictCode);
            } else {
                log.warn("字典类型 {} 名称缓存未找到", dictType);
                return null;
            }
            
        } catch (Exception e) {
            log.error("获取字典名称异常 {}:{} - {}", dictType, dictCode, e.getMessage());
            return null;
        }
    }
    
    /**
     * 检查并刷新缓存
     */
    private void checkAndRefreshCache() {
        long currentTime = System.currentTimeMillis();
        if (!cacheLoaded || (currentTime - lastLoadTime) > CACHE_REFRESH_INTERVAL) {
            log.info("缓存需要刷新，重新加载字典数据");
            loadAllDictToMemory();
        }
    }
    
    /**
     * 预热所有字典缓存
     */
    public void warmupAllDictCache() {
        log.info("开始预热字典缓存...");
        loadAllDictToMemory();
        
        // 如果Redis可用，也预热Redis缓存
        if (redisTemplate != null) {
            try {
                warmupRedisCache();
            } catch (Exception e) {
                log.warn("Redis缓存预热失败: {}", e.getMessage());
            }
        }
        
        log.info("字典缓存预热完成");
    }
    
    /**
     * 预热Redis缓存
     */
    private void warmupRedisCache() {
        if (redisTemplate == null) {
            return;
        }
        
        log.info("开始预热Redis缓存...");
        
        try {
            for (Map.Entry<String, Set<String>> entry : memoryDictCache.entrySet()) {
                String dictType = entry.getKey();
                Set<String> codes = entry.getValue();
                
                String cacheKey = "dict:codes:" + dictType;
                
                // 清除旧缓存
                redisTemplate.delete(cacheKey);
                
                // 添加新缓存
                if (!codes.isEmpty()) {
                    redisTemplate.opsForSet().add(cacheKey, codes.toArray(new String[0]));
                    redisTemplate.expire(cacheKey, 24, TimeUnit.HOURS);
                }
            }
            
            log.info("Redis缓存预热完成");
            
        } catch (Exception e) {
            log.error("Redis缓存预热异常: {}", e.getMessage());
        }
    }
    
    /**
     * 获取缓存统计信息
     */
    public Map<String, Object> getCacheStats() {
        Map<String, Object> stats = new HashMap<>();
        
        stats.put("cache_loaded", cacheLoaded);
        stats.put("last_load_time", new Date(lastLoadTime));
        stats.put("dict_types_count", memoryDictCache.size());
        
        int totalItems = memoryDictCache.values().stream()
            .mapToInt(Set::size)
            .sum();
        stats.put("total_dict_items", totalItems);
        
        stats.put("redis_available", redisTemplate != null);
        
        return stats;
    }
    
    /**
     * 清理所有字典缓存
     */
    public void clearAllDictCache() {
        log.info("开始清理字典缓存...");
        
        // 清理内存缓存
        memoryDictCache.clear();
        memoryDictNameCache.clear();
        cacheLoaded = false;
        
        // 清理Redis缓存
        if (redisTemplate != null) {
            try {
                Set<String> keys = redisTemplate.keys("dict:*");
                if (keys != null && !keys.isEmpty()) {
                    redisTemplate.delete(keys);
                    log.info("已清理 {} 个Redis缓存键", keys.size());
                }
            } catch (Exception e) {
                log.error("清理Redis缓存异常: {}", e.getMessage());
            }
        }
        
        log.info("字典缓存清理完成");
    }
}
