package com.medical.qc.entity;

import lombok.Data;
import java.math.BigDecimal;
import java.util.Date;

@Data
public class KiroQcBatchSummary {
    private Long id;
    private String batchKey;
    private String periodType;
    private Integer checkYear;
    private Integer checkQuarter;
    private Integer checkMonth;
    private Integer caseCount;
    private Integer totalDefectCount;
    private BigDecimal avgDefect;
    private BigDecimal avgScore;
    private String status;
    private Integer progress;
    private Date startTime;
    private Date endTime;
    private Date createdAt;
    
    // Cross规则统计字段
    private Integer crossDefectCount; // Cross规则违规总数
    private BigDecimal crossTotalDeduct; // Cross规则总扣分
    private BigDecimal avgCrossDefect; // 平均Cross规则违规数
}
