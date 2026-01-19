package com.medical.qc.dto;

import lombok.Data;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@Data
public class QcResultDTO {
    private String mrKey;
    private String a48;
    private String a49;
    private String b15;
    private Integer defectCount;
    private BigDecimal totalDeduct;
    private BigDecimal finalScore;
    private Map<String, List<DefectDTO>> defectsByField;
    private List<DefectDTO> allDefects;
    
    // Cross规则违规单独分组，便于前端特殊展示
    private List<CrossDefectDTO> crossDefects;
    
    // Cross规则统计信息
    private Integer crossDefectCount; // Cross规则违规总数
    private BigDecimal crossTotalDeduct; // Cross规则总扣分
    
    @Data
    public static class DefectDTO {
        private String fieldCode;
        private String fieldName;
        private String ruleCode;
        private String ruleDescription;
        private String actualValue;
        private String expectedValue;
        private BigDecimal deductScore;
    }
    
    @Data
    public static class CrossDefectDTO {
        private String ruleCode;
        private String ruleDescription;
        private String crossType; // field_pair, age_gender, transfusion_logic等
        private List<String> involvedFields; // 涉及的字段列表
        private Map<String, String> fieldValues; // 字段名->值的映射
        private String logicDescription; // 逻辑描述，如"诊断编码与名称不匹配"
        private BigDecimal deductScore;
        private String severity; // 严重程度: low, medium, high
    }
}
