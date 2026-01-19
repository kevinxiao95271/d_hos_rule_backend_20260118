package com.medical.qc.mapper;

import com.medical.qc.entity.KiroQcRuleCross;
import org.apache.ibatis.annotations.*;
import java.util.List;

@Mapper
public interface CrossRuleMapper {
    
    @Select("SELECT * FROM kiro_qc_rule_cross WHERE status = 'active' ORDER BY priority DESC, id")
    List<KiroQcRuleCross> findActiveRules();
    
    @Select("SELECT * FROM kiro_qc_rule_cross WHERE cross_type = #{crossType} AND status = 'active'")
    List<KiroQcRuleCross> findByType(@Param("crossType") String crossType);
    
    @Select("SELECT * FROM kiro_qc_rule_cross WHERE primary_field = #{primaryField} AND status = 'active'")
    List<KiroQcRuleCross> findByPrimaryField(@Param("primaryField") String primaryField);
    
    @Select("SELECT * FROM kiro_qc_rule_cross WHERE id = #{id}")
    KiroQcRuleCross findById(@Param("id") Long id);
    
    @Insert("INSERT INTO kiro_qc_rule_cross (rule_code, description, cross_type, primary_field, " +
            "primary_field_name, related_fields, constraint_conditions, error_message, " +
            "expected_value, deduct_score, source_tables, status) " +
            "VALUES (#{ruleCode}, #{description}, #{crossType}, #{primaryField}, " +
            "#{primaryFieldName}, #{relatedFields}, #{constraintConditions}, #{errorMessage}, " +
            "#{expectedValue}, #{deductScore}, #{sourceTables}, #{status})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(KiroQcRuleCross rule);
    
    @Update("UPDATE kiro_qc_rule_cross SET status = #{status}, updated_at = CURRENT_TIMESTAMP " +
            "WHERE id = #{id}")
    int updateStatus(@Param("id") Long id, @Param("status") String status);
}