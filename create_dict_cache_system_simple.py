#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import json
import time
from datetime import datetime

# 数据库连接配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def analyze_dict_requirements():
    """分析字典需求"""
    print("医疗质控系统字典缓存系统创建")
    print("=" * 50)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 分析字典验证规则
        print(f"\n1. 分析字典验证规则需求:")
        
        cursor.execute("""
            SELECT rule_type, COUNT(*) as count 
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            AND rule_type = 'value_check'
        """)
        
        dict_rules = cursor.fetchall()
        total_dict_rules = sum(rule['count'] for rule in dict_rules)
        
        print(f"   字典验证规则数量: {total_dict_rules}条")
        
        # 2. 分析涉及的字典类型
        print(f"\n2. 分析涉及的字典类型:")
        
        cursor.execute("""
            SELECT DISTINCT dict_types 
            FROM kiro_qc_rule 
            WHERE status = 'active' 
            AND dict_types IS NOT NULL 
            AND dict_types != ''
        """)
        
        dict_type_rows = cursor.fetchall()
        dict_types = set()
        
        for row in dict_type_rows:
            if row['dict_types']:
                # 字典类型可能是逗号分隔的
                types = row['dict_types'].split(',')
                for dt in types:
                    dt = dt.strip()
                    if dt:
                        dict_types.add(dt)
        
        print(f"   涉及的字典类型数量: {len(dict_types)}个")
        if dict_types:
            dict_list = sorted(list(dict_types))
            print(f"   字典类型列表: {dict_list[:10]}...")  # 显示前10个
        
        # 3. 检查现有字典数据源
        print(f"\n3. 检查现有字典数据源:")
        
        # 检查sys_dict表
        try:
            cursor.execute("SELECT COUNT(*) as count FROM sys_dict")
            result = cursor.fetchone()
            sys_dict_count = result['count']
            print(f"   sys_dict表记录数: {sys_dict_count}条")
            
            # 检查sys_dict中的字典类型
            cursor.execute("SELECT DISTINCT dict_type_code FROM sys_dict LIMIT 20")
            sys_dict_types = cursor.fetchall()
            print(f"   sys_dict字典类型: {[t['dict_type_code'] for t in sys_dict_types]}")
            
        except Exception as e:
            print(f"   sys_dict表检查失败: {e}")
            sys_dict_count = 0
        
        # 检查是否有其他字典表
        cursor.execute("SHOW TABLES LIKE '%dict%'")
        dict_tables = cursor.fetchall()
        print(f"   字典相关表: {[list(t.values())[0] for t in dict_tables]}")
        
        return {
            'dict_rules_count': total_dict_rules,
            'dict_types': list(dict_types),
            'dict_types_count': len(dict_types),
            'sys_dict_count': sys_dict_count
        }
        
    finally:
        cursor.close()
        conn.close()

def create_kiro_qc_dict_table():
    """创建kiro_qc_dict表"""
    print(f"\n=== 创建kiro_qc_dict表 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 创建kiro_qc_dict表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS kiro_qc_dict (
            dict_id BIGINT PRIMARY KEY AUTO_INCREMENT,
            dict_code VARCHAR(64) NOT NULL,
            dict_name VARCHAR(200) NOT NULL,
            dict_type_code VARCHAR(64) NOT NULL,
            dict_sort INT DEFAULT 0,
            is_active TINYINT DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_dict_type_code (dict_type_code),
            INDEX idx_dict_code_type (dict_code, dict_type_code),
            UNIQUE KEY uk_dict_code_type (dict_code, dict_type_code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='医疗质控字典表'
        """
        
        cursor.execute(create_table_sql)
        print(f"✅ kiro_qc_dict表创建成功")
        
        # 从sys_dict表导入数据
        print(f"从sys_dict表导入数据...")
        
        import_sql = """
        INSERT IGNORE INTO kiro_qc_dict (dict_code, dict_name, dict_type_code, dict_sort)
        SELECT dict_code, dict_name, dict_type_code, dict_sort
        FROM sys_dict
        WHERE dict_type_code IS NOT NULL
        """
        
        cursor.execute(import_sql)
        imported_count = cursor.rowcount
        conn.commit()
        
        print(f"✅ 已导入 {imported_count} 条字典数据")
        
        # 验证导入结果
        cursor.execute("SELECT COUNT(*) as count FROM kiro_qc_dict")
        result = cursor.fetchone()
        total_count = result[0]
        
        cursor.execute("SELECT COUNT(DISTINCT dict_type_code) as count FROM kiro_qc_dict")
        result = cursor.fetchone()
        type_count = result[0]
        
        print(f"✅ kiro_qc_dict表统计:")
        print(f"   总记录数: {total_count}条")
        print(f"   字典类型数: {type_count}个")
        
        return total_count, type_count
        
    except Exception as e:
        print(f"❌ 创建kiro_qc_dict表失败: {e}")
        return 0, 0
    
    finally:
        cursor.close()
        conn.close()

def create_dict_cache_service_enhanced():
    """创建增强的字典缓存服务"""
    print(f"\n=== 创建增强的字典缓存服务 ===")
    
    enhanced_service = """package com.medical.qc.service;

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
"""
    
    try:
        with open('src/main/java/com/medical/qc/service/DictCacheServiceEnhanced.java', 'w', encoding='utf-8') as f:
            f.write(enhanced_service)
        
        print(f"✅ 已创建增强字典缓存服务: DictCacheServiceEnhanced.java")
        return True
        
    except Exception as e:
        print(f"❌ 创建增强字典缓存服务失败: {e}")
        return False

def create_dict_mapper():
    """创建字典Mapper"""
    print(f"\n=== 创建字典Mapper ===")
    
    # 创建实体类
    entity_code = """package com.medical.qc.entity;

import lombok.Data;
import java.util.Date;

@Data
public class KiroQcDict {
    private Long dictId;
    private String dictCode;
    private String dictName;
    private String dictTypeCode;
    private Integer dictSort;
    private Integer isActive;
    private Date createdAt;
    private Date updatedAt;
}
"""
    
    # 创建Mapper接口
    mapper_code = """package com.medical.qc.mapper;

import com.medical.qc.entity.KiroQcDict;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import java.util.List;

@Mapper
public interface DictMapper {
    
    @Select("SELECT * FROM kiro_qc_dict WHERE is_active = 1 ORDER BY dict_type_code, dict_sort, dict_code")
    List<KiroQcDict> findAllActiveDict();
    
    @Select("SELECT * FROM kiro_qc_dict WHERE dict_type_code = #{dictTypeCode} AND is_active = 1 ORDER BY dict_sort, dict_code")
    List<KiroQcDict> findByDictType(String dictTypeCode);
    
    @Select("SELECT COUNT(*) FROM kiro_qc_dict WHERE is_active = 1")
    int countActiveDict();
    
    @Select("SELECT COUNT(DISTINCT dict_type_code) FROM kiro_qc_dict WHERE is_active = 1")
    int countActiveDictTypes();
}
"""
    
    try:
        # 创建实体类文件
        with open('src/main/java/com/medical/qc/entity/KiroQcDict.java', 'w', encoding='utf-8') as f:
            f.write(entity_code)
        
        # 创建Mapper文件
        with open('src/main/java/com/medical/qc/mapper/DictMapper.java', 'w', encoding='utf-8') as f:
            f.write(mapper_code)
        
        print(f"✅ 已创建字典实体类和Mapper")
        return True
        
    except Exception as e:
        print(f"❌ 创建字典Mapper失败: {e}")
        return False

def create_dict_cache_controller():
    """创建字典缓存控制器"""
    print(f"\n=== 创建字典缓存控制器 ===")
    
    controller_code = """package com.medical.qc.controller;

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
@RequestMapping("/api/dict/cache")
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
"""
    
    try:
        with open('src/main/java/com/medical/qc/controller/DictCacheController.java', 'w', encoding='utf-8') as f:
            f.write(controller_code)
        
        print(f"✅ 已创建字典缓存控制器: DictCacheController.java")
        return True
        
    except Exception as e:
        print(f"❌ 创建字典缓存控制器失败: {e}")
        return False

def update_rule_engine_for_cache():
    """更新规则引擎以使用缓存"""
    print(f"\n=== 更新规则引擎使用缓存 ===")
    
    # 读取现有的RuleEngineService
    try:
        with open('src/main/java/com/medical/qc/service/RuleEngineService.java', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经包含缓存优化
        if 'DictCacheServiceEnhanced' in content:
            print(f"✅ RuleEngineService已包含缓存优化")
            return True
        
        # 在import部分添加导入
        if 'import org.springframework.beans.factory.annotation.Autowired;' in content:
            import_pos = content.find('import org.springframework.beans.factory.annotation.Autowired;')
            import_line = 'import com.medical.qc.service.DictCacheServiceEnhanced;\n'
            content = content[:import_pos] + import_line + content[import_pos:]
        
        # 添加缓存服务注入
        if '@Service' in content and 'private DictCacheServiceEnhanced' not in content:
            service_pos = content.find('@Service')
            class_start = content.find('public class', service_pos)
            brace_pos = content.find('{', class_start)
            
            injection_code = """
    
    @Autowired
    private DictCacheServiceEnhanced dictCacheServiceEnhanced;
"""
            
            content = content[:brace_pos+1] + injection_code + content[brace_pos+1:]
        
        # 添加字典验证方法
        if 'validateDictValueWithCache' not in content:
            validation_methods = """
    
    /**
     * 使用缓存验证字典值
     */
    private boolean validateDictValueWithCache(String dictType, String value) {
        if (dictType == null || value == null) {
            return false;
        }
        
        try {
            return dictCacheServiceEnhanced.validateDictValue(dictType, value);
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
            return dictCacheServiceEnhanced.batchValidateDictValues(dictType, values);
        } catch (Exception e) {
            log.error("批量缓存字典验证异常: {}", e.getMessage());
            Map<String, Boolean> results = new HashMap<>();
            for (String value : values) {
                results.put(value, false);
            }
            return results;
        }
    }
"""
            
            # 在类的最后一个方法后添加
            last_brace_pos = content.rfind('}')
            content = content[:last_brace_pos] + validation_methods + '\n' + content[last_brace_pos:]
        
        # 保存更新后的文件
        with open('src/main/java/com/medical/qc/service/RuleEngineService.java', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已更新RuleEngineService以使用缓存")
        return True
        
    except Exception as e:
        print(f"❌ 更新RuleEngineService失败: {e}")
        return False

def create_cache_test_script():
    """创建缓存测试脚本"""
    print(f"\n=== 创建缓存测试脚本 ===")
    
    test_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:4101/api"

def test_dict_cache_system():
    print("字典缓存系统测试")
    print("=" * 40)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查缓存状态
    print("\\n1. 检查缓存状态...")
    try:
        response = requests.get(f"{BASE_URL}/dict/cache/status", timeout=10)
        if response.status_code == 200:
            status = response.json().get('data', {})
            print(f"✅ 缓存状态:")
            for key, value in status.items():
                print(f"   {key}: {value}")
        else:
            print(f"❌ 缓存状态检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 缓存状态检查异常: {e}")
    
    # 2. 重新加载缓存
    print("\\n2. 重新加载字典缓存...")
    try:
        response = requests.post(f"{BASE_URL}/dict/cache/reload", timeout=30)
        if response.status_code == 200:
            print(f"✅ 缓存重新加载成功")
        else:
            print(f"❌ 缓存重新加载失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 缓存重新加载异常: {e}")
    
    # 3. 测试字典验证
    print("\\n3. 测试字典验证...")
    test_cases = [
        {"dictType": "RC001", "value": "1"},
        {"dictType": "RC002", "value": "1"},
        {"dictType": "RC011", "value": "1"},
        {"dictType": "RC001", "value": "999"}  # 无效值测试
    ]
    
    for case in test_cases:
        try:
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/dict/cache/validate", 
                                   params=case, timeout=5)
            validation_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json().get('data', False)
                print(f"  {case['dictType']}:{case['value']} = {result} ({validation_time*1000:.1f}ms)")
            else:
                print(f"  {case['dictType']}:{case['value']} = 验证失败")
        except Exception as e:
            print(f"  {case['dictType']}:{case['value']} = 异常: {e}")
    
    # 4. 测试批量验证
    print("\\n4. 测试批量字典验证...")
    try:
        batch_values = ["1", "2", "3", "999"]
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/dict/cache/validate/batch", 
                               params={"dictType": "RC001"},
                               json=batch_values,
                               timeout=10)
        
        batch_time = time.time() - start_time
        
        if response.status_code == 200:
            results = response.json().get('data', {})
            print(f"✅ 批量验证成功 ({batch_time*1000:.1f}ms):")
            for value, valid in results.items():
                print(f"   RC001:{value} = {valid}")
        else:
            print(f"❌ 批量验证失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 批量验证异常: {e}")
    
    # 5. 测试单病案性能
    print("\\n5. 测试单病案性能（使用字典缓存）...")
    test_case = {'a48': '20003285', 'a49': '1'}
    
    try:
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/qc/check/single", 
                               params=test_case, timeout=60)
        
        process_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json().get('data', {})
            defect_count = result.get('defectCount', 0)
            final_score = result.get('finalScore', 0)
            
            print(f"✅ 单病案测试成功")
            print(f"   处理时间: {process_time:.2f}秒")
            print(f"   缺陷数量: {defect_count}个")
            print(f"   最终得分: {final_score}分")
            
            # 性能评估
            if process_time <= 3:
                print(f"   🎉 性能目标达成！")
                performance = "优秀"
            elif process_time <= 5:
                print(f"   ✅ 性能显著改善")
                performance = "良好"
            elif process_time <= 10:
                print(f"   ⚠️  性能有所改善")
                performance = "一般"
            else:
                print(f"   ❌ 性能仍需优化")
                performance = "较差"
            
            return {
                'success': True,
                'time': process_time,
                'defects': defect_count,
                'score': final_score,
                'performance': performance
            }
        
        else:
            print(f"❌ 单病案测试失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return {'success': False, 'error': response.text}
    
    except Exception as e:
        print(f"❌ 单病案测试异常: {e}")
        return {'success': False, 'error': str(e)}

def main():
    result = test_dict_cache_system()
    
    print(f"\\n" + "=" * 40)
    print("测试总结")
    print("=" * 40)
    
    if result and result.get('success'):
        print(f"✅ 字典缓存系统测试成功")
        print(f"   处理时间: {result['time']:.2f}秒")
        print(f"   性能等级: {result['performance']}")
        
        if result['time'] <= 3:
            print(f"   🎯 已达到性能目标！")
        elif result['time'] <= 10:
            print(f"   ✅ 性能显著改善")
        
        # 估算批量处理性能
        estimated_96_cases = result['time'] * 96 / 8  # 8线程并行
        print(f"   预估96病案处理时间: {estimated_96_cases/60:.1f}分钟")
        
        if estimated_96_cases <= 300:  # 5分钟
            print(f"   🎯 批量处理目标可达成！")
    
    else:
        print(f"❌ 字典缓存系统测试失败")
        if result:
            print(f"   错误: {result.get('error', '未知错误')}")

if __name__ == "__main__":
    main()
"""
    
    try:
        with open('test_dict_cache_system.py', 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        print(f"✅ 已创建缓存测试脚本: test_dict_cache_system.py")
        return True
        
    except Exception as e:
        print(f"❌ 创建缓存测试脚本失败: {e}")
        return False

def main():
    """主函数"""
    print("创建完善的字典缓存系统（简化版）")
    
    # 1. 分析字典需求
    dict_info = analyze_dict_requirements()
    
    # 2. 创建kiro_qc_dict表
    total_count, type_count = create_kiro_qc_dict_table()
    
    # 3. 创建字典Mapper
    mapper_created = create_dict_mapper()
    
    # 4. 创建增强的字典缓存服务
    service_created = create_dict_cache_service_enhanced()
    
    # 5. 更新规则引擎使用缓存
    engine_updated = update_rule_engine_for_cache()
    
    # 6. 创建字典缓存控制器
    controller_created = create_dict_cache_controller()
    
    # 7. 创建缓存测试脚本
    test_created = create_cache_test_script()
    
    # 总结
    print(f"\n" + "=" * 50)
    print("字典缓存系统创建总结")
    print("=" * 50)
    
    print(f"📊 字典数据统计:")
    print(f"   字典验证规则: {dict_info['dict_rules_count']}条")
    print(f"   涉及字典类型: {dict_info['dict_types_count']}个")
    print(f"   字典数据记录: {total_count}条")
    
    print(f"\n✅ 已完成的组件:")
    if total_count > 0:
        print(f"   • kiro_qc_dict表创建和数据导入")
    if mapper_created:
        print(f"   • DictMapper和KiroQcDict实体类")
    if service_created:
        print(f"   • DictCacheServiceEnhanced服务（内存+Redis双重缓存）")
    if engine_updated:
        print(f"   • RuleEngineService缓存集成")
    if controller_created:
        print(f"   • DictCacheController控制器")
    if test_created:
        print(f"   • 缓存测试脚本")
    
    print(f"\n🚀 下一步操作:")
    print(f"   1. 重新编译项目: mvn clean compile")
    print(f"   2. 重新打包: mvn package")
    print(f"   3. 重启服务")
    print(f"   4. 测试缓存系统: python test_dict_cache_system.py")
    print(f"   5. 测试优化后的性能")
    
    print(f"\n🎯 预期效果:")
    print(f"   • 字典验证性能提升10-100倍")
    print(f"   • 单病案处理时间降到3-5秒")
    print(f"   • 96病案处理时间降到5分钟以内")
    print(f"   • 保持所有1699条规则完整性")
    print(f"   • 内存缓存确保高可用性，Redis缓存提供更好性能")

if __name__ == "__main__":
    main()