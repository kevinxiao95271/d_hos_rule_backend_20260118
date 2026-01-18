package com.medical.qc.dto;

import lombok.Data;
import java.math.BigDecimal;
import java.util.List;

@Data
public class MultiQcResultDTO {
    private Integer year;
    private Integer quarter;
    private Integer month;
    private Integer caseCount;          // 处理的病案数
    private Long totalTime;              // 总耗时(毫秒)
    private Double avgTimePerCase;       // 平均每病案耗时(秒)
    private Integer totalDefects;        // 总缺陷数
    private BigDecimal avgScore;         // 平均得分
    private List<QcResultDTO> results;   // 每个病案的详细结果
}
