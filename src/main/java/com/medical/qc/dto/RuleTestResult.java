package com.medical.qc.dto;

import lombok.Data;
import java.util.List;

@Data
public class RuleTestResult {
    private Long ruleId;
    private String ruleCode;
    private String description;
    private Integer totalRecords;
    private Integer violationCount;
    private Double violationRate;
    private List<ViolationDetail> violations;
    
    @Data
    public static class ViolationDetail {
        private String mrKey;
        private String a48;
        private String a49;
        private String fieldCode;
        private String actualValue;
        private String expectedValue;
        private String reason;
    }
}
