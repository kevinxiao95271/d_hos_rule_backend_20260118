package com.medical.qc.dto;

import lombok.Data;
import java.util.List;

@Data
public class DictQueryRequest {
    private List<String> dictTypeCodes;  // 字典类型代码列表
    private String keyword;               // 关键词搜索
    private Integer limit;                // 返回数量限制
}
