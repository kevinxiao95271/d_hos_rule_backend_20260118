package com.medical.qc.entity;

import lombok.Data;
import java.math.BigDecimal;
import java.util.Date;

@Data
public class KiroQcDefectDetail {
    private Long id;
    private String mrKey;
    private String a48;
    private String a49;
    private Long ruleId;
    private String ruleCode;
    private String fieldCode;
    private String fieldName;
    private String actualValue;
    private String expectedValue;
    private String ruleDescription;
    private BigDecimal deductScore;
    private Date checkTime;
}
