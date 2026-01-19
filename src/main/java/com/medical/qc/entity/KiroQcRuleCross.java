package com.medical.qc.entity;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
public class KiroQcRuleCross {
    private Long id;
    private String ruleCode;
    private String description;
    private String crossType;
    private String primaryField;
    private String primaryFieldName;
    private String relatedFields; // JSON字符串
    private String constraintConditions; // JSON字符串
    private String logicExpression;
    private String errorMessage;
    private String expectedValue;
    private BigDecimal deductScore;
    private String severity;
    private String sourceTables;
    private String applicableConditions;
    private String status;
    private Integer priority;
    private String createdBy;
    private String updatedBy;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}