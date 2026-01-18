package com.medical.qc.entity;

import lombok.Data;
import java.math.BigDecimal;
import java.util.Date;

@Data
public class KiroQcCaseResult {
    private Long id;
    private String mrKey;
    private String a48;
    private String a49;
    private String b15;
    private Integer checkYear;
    private Integer checkQuarter;
    private Integer checkMonth;
    private Integer defectCount;
    private BigDecimal totalDeduct;
    private BigDecimal finalScore;
    private Date checkTime;
}
