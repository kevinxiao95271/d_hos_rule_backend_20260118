package com.medical.qc.entity;

import lombok.Data;
import java.math.BigDecimal;
import java.util.Date;

@Data
public class QcRule {
    private Long id;
    private String ruleCode;
    private String ruleName;
    private String sourceText;
    private String fieldCode;
    private String fieldName;
    private String ruleType;
    private BigDecimal priority;
    private String description;
    private String uruleContent;
    private String canonicalExpr;
    private String status;
    private String involvedTables;
    private String involvedFields;
    private Date lastRunStart;
    private Date lastRunEnd;
    private Date createdAt;
    private Date updatedAt;
}
