package com.medical.qc.mapper;

import com.medical.qc.entity.KiroQcRule;
import org.apache.ibatis.annotations.*;
import java.util.List;

@Mapper
public interface QcRuleMapper {
    
    @Select("SELECT * FROM kiro_qc_rule WHERE status = 'active' ORDER BY id")
    List<KiroQcRule> findActiveRules();
    
    @Select("SELECT * FROM kiro_qc_rule ORDER BY id")
    List<KiroQcRule> findAllRules();
    
    @Select("<script>" +
            "SELECT * FROM kiro_qc_rule WHERE 1=1 " +
            "<if test='status != null'> AND status = #{status} </if>" +
            "ORDER BY id" +
            "</script>")
    List<KiroQcRule> findByStatus(@Param("status") String status);
    
    @Select("SELECT * FROM kiro_qc_rule WHERE id = #{id}")
    KiroQcRule findById(Long id);
    
    @Select("<script>" +
            "SELECT * FROM kiro_qc_rule WHERE 1=1 " +
            "<if test='status != null'> AND status = #{status} </if>" +
            "<if test='fieldCode != null'> AND field_code = #{fieldCode} </if>" +
            "<if test='keyword != null'> AND (description LIKE CONCAT('%',#{keyword},'%') OR field_name LIKE CONCAT('%',#{keyword},'%')) </if>" +
            "ORDER BY id" +
            "</script>")
    List<KiroQcRule> searchRules(@Param("status") String status, @Param("fieldCode") String fieldCode, @Param("keyword") String keyword);
    
    @Insert("INSERT INTO kiro_qc_rule(rule_code, field_name, field_code, table_name, rule_type, deduct_score, description, urule_content, canonical_expr, status, source_tables, dict_types, involved_tables, involved_fields) " +
            "VALUES(#{ruleCode}, #{fieldName}, #{fieldCode}, #{tableName}, #{ruleType}, #{deductScore}, #{description}, #{uruleContent}, #{canonicalExpr}, #{status}, #{sourceTables}, #{dictTypes}, #{involvedTables}, #{involvedFields})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(KiroQcRule rule);
    
    @Update("UPDATE kiro_qc_rule SET field_name=#{fieldName}, field_code=#{fieldCode}, table_name=#{tableName}, rule_type=#{ruleType}, " +
            "deduct_score=#{deductScore}, description=#{description}, urule_content=#{uruleContent}, canonical_expr=#{canonicalExpr}, " +
            "status=#{status}, source_tables=#{sourceTables}, dict_types=#{dictTypes}, involved_tables=#{involvedTables}, involved_fields=#{involvedFields} WHERE id=#{id}")
    int update(KiroQcRule rule);
    
    @Update("UPDATE kiro_qc_rule SET status = #{status} WHERE id = #{id}")
    int updateStatus(@Param("id") Long id, @Param("status") String status);
    
    @Select("SELECT * FROM kiro_qc_rule WHERE canonical_expr = #{canonicalExpr} AND id != #{excludeId}")
    KiroQcRule findByCanonicalExpr(@Param("canonicalExpr") String canonicalExpr, @Param("excludeId") Long excludeId);
}
