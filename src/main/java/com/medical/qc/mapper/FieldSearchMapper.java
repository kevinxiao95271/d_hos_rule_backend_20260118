package com.medical.qc.mapper;

import org.apache.ibatis.annotations.*;
import java.util.List;
import java.util.Map;

@Mapper
public interface FieldSearchMapper {
    
    @Select("SELECT COLUMN_NAME as columnName, DATA_TYPE as dataType, IS_NULLABLE as isNullable " +
            "FROM INFORMATION_SCHEMA.COLUMNS " +
            "WHERE TABLE_SCHEMA = 'd_hosq_traegj_20260115' " +
            "AND TABLE_NAME = 'd_mr' " +
            "AND COLUMN_NAME LIKE CONCAT('%',#{fieldName},'%') " +
            "ORDER BY ORDINAL_POSITION")
    List<Map<String, Object>> searchInDMr(@Param("fieldName") String fieldName);
    
    @Select("SELECT COLUMN_NAME as columnName, DATA_TYPE as dataType, IS_NULLABLE as isNullable " +
            "FROM INFORMATION_SCHEMA.COLUMNS " +
            "WHERE TABLE_SCHEMA = 'd_hosq_traegj_20260115' " +
            "AND TABLE_NAME = 'd_mr_other_1_20' " +
            "AND COLUMN_NAME LIKE CONCAT('%',#{fieldName},'%') " +
            "ORDER BY ORDINAL_POSITION")
    List<Map<String, Object>> searchInDMrOther120(@Param("fieldName") String fieldName);
    
    @Select("SELECT COLUMN_NAME as columnName, DATA_TYPE as dataType, IS_NULLABLE as isNullable " +
            "FROM INFORMATION_SCHEMA.COLUMNS " +
            "WHERE TABLE_SCHEMA = 'd_hosq_traegj_20260115' " +
            "AND TABLE_NAME = 'd_mr_other_21_40' " +
            "AND COLUMN_NAME LIKE CONCAT('%',#{fieldName},'%') " +
            "ORDER BY ORDINAL_POSITION")
    List<Map<String, Object>> searchInDMrOther2140(@Param("fieldName") String fieldName);
    
    @Select("SELECT COLUMN_NAME as columnName, DATA_TYPE as dataType, IS_NULLABLE as isNullable " +
            "FROM INFORMATION_SCHEMA.COLUMNS " +
            "WHERE TABLE_SCHEMA = 'd_hosq_traegj_20260115' " +
            "AND TABLE_NAME = 'd_mr_other_f' " +
            "AND COLUMN_NAME LIKE CONCAT('%',#{fieldName},'%') " +
            "ORDER BY ORDINAL_POSITION")
    List<Map<String, Object>> searchInDMrOtherF(@Param("fieldName") String fieldName);
}
