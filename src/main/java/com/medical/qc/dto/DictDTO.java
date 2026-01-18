package com.medical.qc.dto;

import lombok.Data;

@Data
public class DictDTO {
    private Long dictId;
    private String dictCode;
    private String dictName;
    private String dictTypeCode;
    private String dictTypeName;
}
