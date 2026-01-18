package com.medical.qc.entity;

import lombok.Data;
import java.math.BigDecimal;
import java.util.Date;

@Data
public class QcCaseResult {
    private Long id;
    private String mrKey;
    private String a48;
    private String a49;
    private String periodType;
    private Integer aggYear;
    private Integer quarter;
    private Integer month;
    private Integer defectCount;
    private BigDecimal totalDeduct;
    private BigDecimal score;
    private Date createdAt;
}
