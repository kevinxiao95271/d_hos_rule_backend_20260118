package com.medical.qc.dto;

import lombok.Data;

@Data
public class QcRequest {
    private String periodType;
    private Integer year;
    private Integer quarter;
    private Integer month;
    private String a48;
    private String a49;
}
