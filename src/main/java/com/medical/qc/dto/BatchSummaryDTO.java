package com.medical.qc.dto;

import lombok.Data;
import java.math.BigDecimal;
import java.util.Date;

@Data
public class BatchSummaryDTO {
    private String batchKey;
    private String periodType;
    private Integer year;
    private Integer quarter;
    private Integer month;
    private Integer caseCount;
    private Integer totalDefectCount;
    private BigDecimal avgDefect;
    private BigDecimal avgScore;
    private String status;
    private Integer progress;
    private Date startTime;
    private Date endTime;
    private Long elapsedSeconds;  // 已执行时间（秒）
}
