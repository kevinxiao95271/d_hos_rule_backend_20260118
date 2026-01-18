package com.medical.qc.mapper;

import com.medical.qc.entity.KiroQcCaseResult;
import com.medical.qc.entity.KiroQcDefectDetail;
import com.medical.qc.entity.KiroQcRule;
import org.apache.ibatis.annotations.*;
import java.util.List;
import java.util.Map;

@Mapper
public interface OptimizedBatchMapper {
    
    /**
     * 批量插入病案结果
     */
    @Insert({
        "<script>",
        "INSERT INTO kiro_qc_case_result(mr_key, a48, a49, b15, check_year, check_quarter, check_month, defect_count, total_deduct, final_score) VALUES ",
        "<foreach collection='list' item='item' separator=','>",
        "(#{item.mrKey}, #{item.a48}, #{item.a49}, #{item.b15}, #{item.checkYear}, #{item.checkQuarter}, #{item.checkMonth}, #{item.defectCount}, #{item.totalDeduct}, #{item.finalScore})",
        "</foreach>",
        "ON DUPLICATE KEY UPDATE defect_count=VALUES(defect_count), total_deduct=VALUES(total_deduct), final_score=VALUES(final_score), check_time=NOW()",
        "</script>"
    })
    int batchInsertCaseResults(@Param("list") List<KiroQcCaseResult> caseResults);
    
    /**
     * 批量插入缺陷明细
     */
    @Insert({
        "<script>",
        "INSERT INTO kiro_qc_defect_detail(mr_key, a48, a49, rule_id, rule_code, field_code, field_name, actual_value, expected_value, rule_description, deduct_score) VALUES ",
        "<foreach collection='list' item='item' separator=','>",
        "(#{item.mrKey}, #{item.a48}, #{item.a49}, #{item.ruleId}, #{item.ruleCode}, #{item.fieldCode}, #{item.fieldName}, #{item.actualValue}, #{item.expectedValue}, #{item.ruleDescription}, #{item.deductScore})",
        "</foreach>",
        "</script>"
    })
    int batchInsertDefectDetails(@Param("list") List<KiroQcDefectDetail> defectDetails);
    
    /**
     * 一次性获取所有激活规则
     */
    @Select("SELECT * FROM kiro_qc_rule WHERE status = 'active' ORDER BY id")
    List<KiroQcRule> getActiveRules();
    
    /**
     * 批量获取病案数据（优化查询）
     */
    @Select({
        "<script>",
        "SELECT * FROM d_mr WHERE 1=1",
        "<if test='year != null'>",
        "AND B15 LIKE CONCAT(#{year}, '/%')",
        "</if>",
        "<if test='quarter != null'>",
        "AND QUARTER(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = #{quarter}",
        "</if>",
        "<if test='month != null'>",
        "AND MONTH(STR_TO_DATE(B15, '%Y/%c/%e %H:%i')) = #{month}",
        "</if>",
        "ORDER BY A48, A49",
        "</script>"
    })
    List<Map<String, Object>> getBatchRecords(@Param("year") Integer year, 
                                            @Param("quarter") Integer quarter, 
                                            @Param("month") Integer month);
}