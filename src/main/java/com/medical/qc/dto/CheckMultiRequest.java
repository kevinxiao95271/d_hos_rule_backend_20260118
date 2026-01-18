package com.medical.qc.dto;

import lombok.Data;

@Data
public class CheckMultiRequest {
    private Integer year;
    private Integer quarter;
    private Integer month;
    private Integer limit = 10;  // 默认10条
}
