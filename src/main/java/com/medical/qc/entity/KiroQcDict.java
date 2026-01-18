package com.medical.qc.entity;

import lombok.Data;
import java.util.Date;

@Data
public class KiroQcDict {
    private Long dictId;
    private String dictCode;
    private String dictName;
    private String dictTypeCode;
    private Integer dictSort;
    private Integer isActive;
    private Date createdAt;
    private Date updatedAt;
}
