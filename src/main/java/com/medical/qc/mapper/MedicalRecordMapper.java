package com.medical.qc.mapper;

import org.apache.ibatis.annotations.*;
import java.util.List;
import java.util.Map;

@Mapper
public interface MedicalRecordMapper {
    
    @Select("<script>" +
            "SELECT CONCAT(m.A48, '_', m.A49) as mrKey, m.*, o1.* FROM d_mr m " +
            "LEFT JOIN d_mr_other_1_20 o1 ON m.A48 = o1.A48 AND m.A49 = o1.A49 " +
            "WHERE 1=1 " +
            "<if test='year != null'> AND YEAR(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = #{year} </if>" +
            "<if test='quarter != null'> AND QUARTER(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = #{quarter} </if>" +
            "<if test='month != null'> AND MONTH(STR_TO_DATE(m.B15, '%Y/%c/%e %H:%i')) = #{month} </if>" +
            "<if test='a48 != null'> AND m.A48 = #{a48} </if>" +
            "<if test='a49 != null'> AND m.A49 = #{a49} </if>" +
            "<if test='limit != null'> LIMIT #{limit} </if>" +
            "</script>")
    @MapKey("mrKey")
    Map<String, Map<String, Object>> findRecords(@Param("year") Integer year,
                                                   @Param("quarter") Integer quarter,
                                                   @Param("month") Integer month,
                                                   @Param("limit") Integer limit,
                                                   @Param("a48") String a48,
                                                   @Param("a49") String a49);
    
    @Select("SELECT m.*, o1.* FROM d_mr m " +
            "LEFT JOIN d_mr_other_1_20 o1 ON m.A48 = o1.A48 AND m.A49 = o1.A49 " +
            "WHERE m.A48 = #{a48} AND m.A49 = #{a49}")
    Map<String, Object> findByKey(@Param("a48") String a48, @Param("a49") String a49);
    
    @Select("<script>" +
            "SELECT COUNT(*) FROM d_mr WHERE 1=1 " +
            "<if test='year != null'> AND YEAR(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = #{year} </if>" +
            "<if test='quarter != null'> AND QUARTER(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = #{quarter} </if>" +
            "<if test='month != null'> AND MONTH(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = #{month} </if>" +
            "</script>")
    int countRecords(@Param("year") Integer year, @Param("quarter") Integer quarter, @Param("month") Integer month);
}
