package com.medical.qc.mapper;

import com.medical.qc.entity.KiroQcDict;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import java.util.List;
import java.util.Map;

@Mapper
public interface DictMapper {
    
    // 新增的方法（用于缓存系统）
    @Select("SELECT * FROM kiro_qc_dict WHERE is_active = 1 ORDER BY dict_type_code, dict_sort, dict_code")
    List<KiroQcDict> findAllActiveDict();
    
    @Select("SELECT * FROM kiro_qc_dict WHERE dict_type_code = #{dictTypeCode} AND is_active = 1 ORDER BY dict_sort, dict_code")
    List<KiroQcDict> findByDictType(String dictTypeCode);
    
    @Select("SELECT COUNT(*) FROM kiro_qc_dict WHERE is_active = 1")
    int countActiveDict();
    
    @Select("SELECT COUNT(DISTINCT dict_type_code) FROM kiro_qc_dict WHERE is_active = 1")
    int countActiveDictTypes();
    
    // 保留的旧方法（兼容现有代码）
    @Select("<script>" +
            "SELECT dict_id, dict_code, dict_name, dict_type_code, dict_sort " +
            "FROM kiro_qc_dict WHERE is_active = 1 " +
            "<if test='dictTypeCodes != null and dictTypeCodes.size() > 0'>" +
            "AND dict_type_code IN " +
            "<foreach item='item' index='index' collection='dictTypeCodes' open='(' separator=',' close=')'>" +
            "#{item}" +
            "</foreach>" +
            "</if>" +
            "<if test='keyword != null and keyword != \"\"'>" +
            "AND (dict_code LIKE CONCAT('%', #{keyword}, '%') OR dict_name LIKE CONCAT('%', #{keyword}, '%'))" +
            "</if>" +
            "<if test='limit != null and limit > 0'>" +
            "LIMIT #{limit}" +
            "</if>" +
            "</script>")
    List<Map<String, Object>> queryDicts(@Param("dictTypeCodes") List<String> dictTypeCodes, 
                                        @Param("keyword") String keyword, 
                                        @Param("limit") Integer limit);
    
    @Select("SELECT dict_id, dict_code, dict_name, dict_type_code, dict_sort " +
            "FROM kiro_qc_dict " +
            "WHERE dict_type_code = #{dictTypeCode} AND is_active = 1 " +
            "ORDER BY dict_sort, dict_code")
    List<Map<String, Object>> getDictsByType(@Param("dictTypeCode") String dictTypeCode);

    @Select("SELECT DISTINCT dict_type_code FROM kiro_qc_dict WHERE is_active = 1 ORDER BY dict_type_code")
    List<String> getAllDictTypes();
}
