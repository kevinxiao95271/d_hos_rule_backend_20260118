package com.medical.qc.dto;

import lombok.Data;
import java.math.BigDecimal;

@Data
public class RuleUpdateRequest {
    private Long id;
    private String ruleCode;
    private String fieldName;
    private String fieldCode;
    private String tableName;
    private String ruleType;
    private BigDecimal deductScore;
    private String description;
    private String status;
    private String sourceTables;      // 源数据表
    private String dictTypes;         // 值域数据集
    private String involvedTables;
    private String involvedFields;
}
