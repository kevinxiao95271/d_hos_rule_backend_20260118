package com.medical.qc.service;

import com.medical.qc.mapper.DictMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import javax.annotation.PostConstruct;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Slf4j
@Service
public class DictCacheService {
    
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;
    
    @Autowired
    private DictMapper dictMapper;
    
    // Redis key前缀
    private static final String DICT_CACHE_PREFIX = "kiro_dict:";
    private static final String DICT_SET_PREFIX = "kiro_dict_set:";
    
    // 缓存过期时间（24小时）
    private static final long CACHE_EXPIRE_HOURS = 24;
    
    /**
     * 应用启动时预加载所有RC0xx字典到Redis
     */
    @PostConstruct
    public void preloadDictionaries() {
        log.info("开始预加载字典数据到Redis缓存...");
        
        try {
            // 获取所有需要缓存的字典类型（包括RC和医疗编码字典）
            List<String> dictTypes = getAllDictTypes();
            
            int loadedCount = 0;
            long startTime = System.currentTimeMillis();
            
            for (String dictType : dictTypes) {
                loadDictToCache(dictType);
                loadedCount++;
            }
            
            long endTime = System.currentTimeMillis();
            log.info("字典预加载完成！加载了{}个字典类型，耗时{}ms", loadedCount, endTime - startTime);
            
        } catch (Exception e) {
            log.error("字典预加载失败", e);
        }
    }
    
    /**
     * 获取所有需要缓存的字典类型
     */
    private List<String> getAllDictTypes() {
        List<Map<String, Object>> results = dictMapper.queryDicts(null, null, null);
        return results.stream()
            .map(row -> row.get("dict_type_code").toString())
            .filter(type -> type.startsWith("RC") || 
                           type.equals("level4_operation_code_v2") ||
                           type.equals("operation_dict_v3") ||
                           type.equals("RCJBBM") ||
                           type.equals("microfracture_oper_code_v2") ||
                           type.equals("day_operation_code_2022") ||
                           type.equals("operation_code_with_type"))
            .distinct()
            .collect(Collectors.toList());
    }
    
    /**
     * 加载指定字典类型到缓存
     */
    public void loadDictToCache(String dictTypeCode) {
        try {
            // 从数据库查询字典数据
            List<Map<String, Object>> dictItems = dictMapper.getDictsByType(dictTypeCode);
            
            if (dictItems.isEmpty()) {
                log.debug("字典类型 {} 无数据", dictTypeCode);
                return;
            }
            
            // 提取dict_code列表用于快速验证
            Set<String> dictCodes = dictItems.stream()
                .map(item -> item.get("dict_code").toString())
                .collect(Collectors.toSet());
            
            // 缓存完整字典数据
            String dictKey = DICT_CACHE_PREFIX + dictTypeCode;
            redisTemplate.opsForValue().set(dictKey, dictItems, CACHE_EXPIRE_HOURS, TimeUnit.HOURS);
            
            // 缓存dict_code集合用于快速验证
            String setKey = DICT_SET_PREFIX + dictTypeCode;
            redisTemplate.delete(setKey);  // 清空旧数据
            if (!dictCodes.isEmpty()) {
                redisTemplate.opsForSet().add(setKey, dictCodes.toArray());
                redisTemplate.expire(setKey, CACHE_EXPIRE_HOURS, TimeUnit.HOURS);
            }
            
            log.debug("字典 {} 已缓存，包含{}条记录", dictTypeCode, dictItems.size());
            
        } catch (Exception e) {
            log.error("缓存字典 {} 失败", dictTypeCode, e);
        }
    }
    
    /**
     * 从缓存获取字典数据（如果缓存不存在则从数据库加载）
     */
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getDictsByType(String dictTypeCode) {
        String dictKey = DICT_CACHE_PREFIX + dictTypeCode;
        
        try {
            // 先从缓存获取
            Object cached = redisTemplate.opsForValue().get(dictKey);
            if (cached != null) {
                log.debug("从缓存获取字典 {}", dictTypeCode);
                return (List<Map<String, Object>>) cached;
            }
            
            // 缓存不存在，从数据库加载并缓存
            log.debug("缓存未命中，从数据库加载字典 {}", dictTypeCode);
            loadDictToCache(dictTypeCode);
            
            // 再次从缓存获取
            cached = redisTemplate.opsForValue().get(dictKey);
            if (cached != null) {
                return (List<Map<String, Object>>) cached;
            }
            
            // 如果还是获取不到，直接查数据库
            return dictMapper.getDictsByType(dictTypeCode);
            
        } catch (Exception e) {
            log.error("从缓存获取字典 {} 失败，回退到数据库查询", dictTypeCode, e);
            return dictMapper.getDictsByType(dictTypeCode);
        }
    }
    
    /**
     * 快速验证字段值是否在字典中（使用Redis Set）
     */
    public boolean validateFieldValue(String dictTypeCode, String value) {
        if (value == null || value.trim().isEmpty()) {
            return false;
        }
        
        String setKey = DICT_SET_PREFIX + dictTypeCode;
        
        try {
            // 检查缓存是否存在
            if (!redisTemplate.hasKey(setKey)) {
                log.debug("字典集合缓存不存在，重新加载 {}", dictTypeCode);
                loadDictToCache(dictTypeCode);
            }
            
            // 使用Redis Set的isMember操作进行快速验证
            Boolean isMember = redisTemplate.opsForSet().isMember(setKey, value.trim());
            
            if (isMember != null) {
                log.debug("使用缓存验证字典值 {}:{} = {}", dictTypeCode, value, isMember);
                return isMember;
            }
            
            // 缓存验证失败，回退到数据库
            log.debug("缓存验证失败，回退到数据库验证 {}:{}", dictTypeCode, value);
            return validateFieldValueFromDB(dictTypeCode, value);
            
        } catch (Exception e) {
            log.error("缓存验证字典值失败 {}:{}，回退到数据库", dictTypeCode, value, e);
            return validateFieldValueFromDB(dictTypeCode, value);
        }
    }
    
    /**
     * 从数据库验证字段值
     */
    private boolean validateFieldValueFromDB(String dictTypeCode, String value) {
        List<Map<String, Object>> dicts = dictMapper.getDictsByType(dictTypeCode);
        return dicts.stream()
            .anyMatch(dict -> value.equals(dict.get("dict_code")) || value.equals(dict.get("dict_name")));
    }
    
    /**
     * 清除指定字典类型的缓存
     */
    public void clearDictCache(String dictTypeCode) {
        String dictKey = DICT_CACHE_PREFIX + dictTypeCode;
        String setKey = DICT_SET_PREFIX + dictTypeCode;
        
        redisTemplate.delete(dictKey);
        redisTemplate.delete(setKey);
        
        log.info("已清除字典缓存: {}", dictTypeCode);
    }
    
    /**
     * 清除所有字典缓存
     */
    public void clearAllDictCache() {
        Set<String> dictKeys = redisTemplate.keys(DICT_CACHE_PREFIX + "*");
        Set<String> setKeys = redisTemplate.keys(DICT_SET_PREFIX + "*");
        
        if (dictKeys != null && !dictKeys.isEmpty()) {
            redisTemplate.delete(dictKeys);
        }
        
        if (setKeys != null && !setKeys.isEmpty()) {
            redisTemplate.delete(setKeys);
        }
        
        log.info("已清除所有kiro字典缓存");
    }
    
    /**
     * 重新加载所有字典缓存
     */
    public void reloadAllDictCache() {
        clearAllDictCache();
        preloadDictionaries();
    }
    
    /**
     * 获取缓存统计信息
     */
    public Map<String, Object> getCacheStats() {
        Map<String, Object> stats = new HashMap<>();
        
        Set<String> dictKeys = redisTemplate.keys(DICT_CACHE_PREFIX + "*");
        Set<String> setKeys = redisTemplate.keys(DICT_SET_PREFIX + "*");
        
        stats.put("dictCacheCount", dictKeys != null ? dictKeys.size() : 0);
        stats.put("setCacheCount", setKeys != null ? setKeys.size() : 0);
        stats.put("cacheExpireHours", CACHE_EXPIRE_HOURS);
        
        return stats;
    }
}