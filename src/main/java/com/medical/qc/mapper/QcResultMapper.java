package com.medical.qc.mapper;

import com.medical.qc.entity.KiroQcCaseResult;
import com.medical.qc.entity.KiroQcDefectDetail;
import com.medical.qc.entity.KiroQcBatchSummary;
import org.apache.ibatis.annotations.*;
import java.util.List;

@Mapper
public interface QcResultMapper {
    
    @Insert("INSERT INTO kiro_qc_case_result(mr_key, a48, a49, b15, check_year, check_quarter, check_month, defect_count, total_deduct, final_score) " +
            "VALUES(#{mrKey}, #{a48}, #{a49}, #{b15}, #{checkYear}, #{checkQuarter}, #{checkMonth}, #{defectCount}, #{totalDeduct}, #{finalScore}) " +
            "ON DUPLICATE KEY UPDATE defect_count=#{defectCount}, total_deduct=#{totalDeduct}, final_score=#{finalScore}, check_time=NOW()")
    int saveCaseResult(KiroQcCaseResult result);
    
    @Insert("INSERT INTO kiro_qc_defect_detail(mr_key, a48, a49, rule_id, rule_code, field_code, field_name, actual_value, expected_value, rule_description, deduct_score) " +
            "VALUES(#{mrKey}, #{a48}, #{a49}, #{ruleId}, #{ruleCode}, #{fieldCode}, #{fieldName}, #{actualValue}, #{expectedValue}, #{ruleDescription}, #{deductScore})")
    int saveDefectDetail(KiroQcDefectDetail detail);
    
    @Delete("DELETE FROM kiro_qc_defect_detail WHERE mr_key = #{mrKey}")
    int deleteDefectsByMrKey(String mrKey);
    
    @Select("SELECT * FROM kiro_qc_case_result WHERE mr_key = #{mrKey}")
    KiroQcCaseResult findCaseResult(String mrKey);
    
    @Select("SELECT * FROM kiro_qc_defect_detail WHERE mr_key = #{mrKey} ORDER BY field_code, rule_code")
    List<KiroQcDefectDetail> findDefectsByMrKey(String mrKey);
    
    @Select("<script>" +
            "SELECT * FROM kiro_qc_case_result WHERE 1=1 " +
            "<if test='year != null'> AND check_year = #{year} </if>" +
            "<if test='quarter != null'> AND check_quarter = #{quarter} </if>" +
            "<if test='month != null'> AND check_month = #{month} </if>" +
            "ORDER BY check_time DESC" +
            "</script>")
    List<KiroQcCaseResult> findCaseResults(@Param("year") Integer year, @Param("quarter") Integer quarter, @Param("month") Integer month);
    
    @Insert("INSERT INTO kiro_qc_batch_summary(batch_key, period_type, check_year, check_quarter, check_month, case_count, total_defect_count, avg_defect, avg_score, status, progress, start_time, cross_defect_count, cross_total_deduct, avg_cross_defect) " +
            "VALUES(#{batchKey}, #{periodType}, #{checkYear}, #{checkQuarter}, #{checkMonth}, #{caseCount}, #{totalDefectCount}, #{avgDefect}, #{avgScore}, #{status}, #{progress}, #{startTime}, #{crossDefectCount}, #{crossTotalDeduct}, #{avgCrossDefect}) " +
            "ON DUPLICATE KEY UPDATE case_count=#{caseCount}, total_defect_count=#{totalDefectCount}, avg_defect=#{avgDefect}, avg_score=#{avgScore}, status=#{status}, progress=#{progress}, start_time=#{startTime}, end_time=#{endTime}, cross_defect_count=#{crossDefectCount}, cross_total_deduct=#{crossTotalDeduct}, avg_cross_defect=#{avgCrossDefect}")
    int saveBatchSummary(KiroQcBatchSummary summary);
    
    @Select("SELECT * FROM kiro_qc_batch_summary WHERE batch_key = #{batchKey}")
    KiroQcBatchSummary findBatchSummary(String batchKey);
    
    @Select("<script>" +
            "SELECT * FROM kiro_qc_batch_summary WHERE 1=1 " +
            "<if test='year != null'> AND check_year = #{year} </if>" +
            "<if test='quarter != null'> AND check_quarter = #{quarter} </if>" +
            "<if test='month != null'> AND check_month = #{month} </if>" +
            "ORDER BY check_year DESC, check_quarter DESC, check_month DESC" +
            "</script>")
    List<KiroQcBatchSummary> findBatchSummaries(@Param("year") Integer year, @Param("quarter") Integer quarter, @Param("month") Integer month);
}
