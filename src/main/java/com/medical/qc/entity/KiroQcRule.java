package com.medical.qc.entity;

import lombok.Data;
import java.math.BigDecimal;
import java.util.Date;

@Data
public class KiroQcRule {
    private Long id;
    private String ruleCode;
    private String fieldName;
    private String fieldCode;
    private String tableName;
    private String ruleType;
    private BigDecimal deductScore;
    private String description;
    private String uruleContent;
    private String canonicalExpr;
    private String status;
    private String sourceTables;      // 源数据表
    private String dictTypes;         // 值域数据集
    private String involvedTables;
    private String involvedFields;
    private Date createdAt;
    private Date updatedAt;
}
