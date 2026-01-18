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
}
