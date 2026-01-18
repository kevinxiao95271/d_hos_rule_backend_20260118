package com.medical.qc.dto;

import lombok.Data;

@Data
public class RuleTestRequest {
    private Long ruleId;
    private String a48;
    private String a49;
    private Integer year;
    private Integer month;
    private Integer limit;  // 测试记录数限制
}
