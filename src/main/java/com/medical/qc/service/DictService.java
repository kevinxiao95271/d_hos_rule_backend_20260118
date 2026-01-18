package com.medical.qc.service;

import com.medical.qc.dto.DictDTO;
import com.medical.qc.dto.DictQueryRequest;
import com.medical.qc.dto.FieldSearchResult;
import com.medical.qc.mapper.DictMapper;
import com.medical.qc.mapper.FieldSearchMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.*;
import java.util.stream.Collectors;

@Slf4j
@Service
public class DictService {
    
    @Autowired
    private DictMapper dictMapper;
    
    @Autowired
    private FieldSearchMapper fieldSearchMapper;
    
    @Autowired
    private DictCacheService dictCacheService;
    
    // 字典类型名称映射
    private static final Map<String, String> DICT_TYPE_NAMES = new HashMap<>();
    static {
        DICT_TYPE_NAMES.put("level4_operation_code_v2", "四级手术编码");
        DICT_TYPE_NAMES.put("operation_dict_v3", "手术编码");
        DICT_TYPE_NAMES.put("RCJBBM", "疾病编码");
        DICT_TYPE_NAMES.put("microfracture_oper_code_v2", "微创手术");
        DICT_TYPE_NAMES.put("day_operation_code_2022", "日间手术");
        DICT_TYPE_NAMES.put("operation_code_with_type", "手术类型");
        DICT_TYPE_NAMES.put("RC001", "性别值域代码表");
        DICT_TYPE_NAMES.put("RC002", "婚姻状况代码表");
        DICT_TYPE_NAMES.put("RC003", "职业代码表");
        DICT_TYPE_NAMES.put("RC011", "病案质量代码表");
        DICT_TYPE_NAMES.put("RC013", "麻醉方式代码表");
        DICT_TYPE_NAMES.put("RC014", "切口愈合等级代码表");
        DICT_TYPE_NAMES.put("RC016", "死亡患者尸检代码表");
        DICT_TYPE_NAMES.put("RC019", "离院方式代码表");
        DICT_TYPE_NAMES.put("RC023", "科别代码表");
        DICT_TYPE_NAMES.put("RC026", "入院途径代码表");
        DICT_TYPE_NAMES.put("RC027", "入院病情代码表");
        DICT_TYPE_NAMES.put("RC028", "出院31天内再住院计划代码表");
        DICT_TYPE_NAMES.put("RC029", "手术级别代码表");
        DICT_TYPE_NAMES.put("RC030", "ABO血型代码表");
        DICT_TYPE_NAMES.put("RC031", "Rh血型代码表");
        DICT_TYPE_NAMES.put("RC032", "医疗付费方式代码表");
        DICT_TYPE_NAMES.put("RC033", "联系人关系代码表");
        DICT_TYPE_NAMES.put("RC035", "民族表");
        DICT_TYPE_NAMES.put("RC036", "省、自治区、直辖市表");
        DICT_TYPE_NAMES.put("RC037", "有无药物过敏表");
        DICT_TYPE_NAMES.put("RC038", "患者证件类别代码表");
        DICT_TYPE_NAMES.put("RC039", "判断代码表");
    }
    
    public List<DictDTO> queryDicts(DictQueryRequest request) {
        List<Map<String, Object>> results = dictMapper.queryDicts(
            request.getDictTypeCodes(),
            request.getKeyword(),
            request.getLimit()
        );
        
        return results.stream().map(this::toDictDTO).collect(Collectors.toList());
    }
    
    public List<String> getAllDictTypes() {
        List<String> types = new ArrayList<>(DICT_TYPE_NAMES.keySet());
        types.sort(String::compareTo);
        return types;
    }
    
    public Map<String, String> getDictTypeNames() {
        return new HashMap<>(DICT_TYPE_NAMES);
    }
    
    public List<DictDTO> getDictsByType(String dictTypeCode) {
        // 使用缓存服务获取字典数据
        List<Map<String, Object>> results = dictCacheService.getDictsByType(dictTypeCode);
        return results.stream().map(this::toDictDTO).collect(Collectors.toList());
    }
    
    public FieldSearchResult searchFieldInTables(String fieldName) {
        FieldSearchResult result = new FieldSearchResult();
        result.setFieldName(fieldName);
        result.setFoundInTables(new ArrayList<>());
        
        // 搜索d_mr表
        List<Map<String, Object>> dmrResults = fieldSearchMapper.searchInDMr(fieldName);
        for (Map<String, Object> row : dmrResults) {
            FieldSearchResult.TableFieldInfo info = new FieldSearchResult.TableFieldInfo();
            info.setTableName("d_mr");
            info.setColumnName(row.get("columnName").toString());
            info.setDataType(row.get("dataType").toString());
            info.setIsNullable("YES".equals(row.get("isNullable")));
            result.getFoundInTables().add(info);
        }
        
        // 搜索d_mr_other_1_20表
        List<Map<String, Object>> other120Results = fieldSearchMapper.searchInDMrOther120(fieldName);
        for (Map<String, Object> row : other120Results) {
            FieldSearchResult.TableFieldInfo info = new FieldSearchResult.TableFieldInfo();
            info.setTableName("d_mr_other_1_20");
            info.setColumnName(row.get("columnName").toString());
            info.setDataType(row.get("dataType").toString());
            info.setIsNullable("YES".equals(row.get("isNullable")));
            result.getFoundInTables().add(info);
        }
        
        // 搜索d_mr_other_21_40表
        List<Map<String, Object>> other2140Results = fieldSearchMapper.searchInDMrOther2140(fieldName);
        for (Map<String, Object> row : other2140Results) {
            FieldSearchResult.TableFieldInfo info = new FieldSearchResult.TableFieldInfo();
            info.setTableName("d_mr_other_21_40");
            info.setColumnName(row.get("columnName").toString());
            info.setDataType(row.get("dataType").toString());
            info.setIsNullable("YES".equals(row.get("isNullable")));
            result.getFoundInTables().add(info);
        }
        
        // 搜索d_mr_other_f表
        List<Map<String, Object>> otherFResults = fieldSearchMapper.searchInDMrOtherF(fieldName);
        for (Map<String, Object> row : otherFResults) {
            FieldSearchResult.TableFieldInfo info = new FieldSearchResult.TableFieldInfo();
            info.setTableName("d_mr_other_f");
            info.setColumnName(row.get("columnName").toString());
            info.setDataType(row.get("dataType").toString());
            info.setIsNullable("YES".equals(row.get("isNullable")));
            result.getFoundInTables().add(info);
        }
        
        return result;
    }
    
    public boolean validateFieldValue(String dictTypeCode, String value) {
        // 使用缓存服务进行快速验证
        return dictCacheService.validateFieldValue(dictTypeCode, value);
    }
    
    private DictDTO toDictDTO(Map<String, Object> row) {
        DictDTO dto = new DictDTO();
        dto.setDictId(row.get("dict_id") != null ? Long.parseLong(row.get("dict_id").toString()) : null);
        dto.setDictCode(row.get("dict_code") != null ? row.get("dict_code").toString() : null);
        dto.setDictName(row.get("dict_name") != null ? row.get("dict_name").toString() : null);
        dto.setDictTypeCode(row.get("dict_type_code") != null ? row.get("dict_type_code").toString() : null);
        dto.setDictTypeName(DICT_TYPE_NAMES.get(dto.getDictTypeCode()));
        return dto;
    }
}
