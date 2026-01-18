package com.medical.qc.dto;

import lombok.Data;
import java.util.List;

@Data
public class FieldSearchResult {
    private String fieldName;
    private List<TableFieldInfo> foundInTables;
    
    @Data
    public static class TableFieldInfo {
        private String tableName;
        private String columnName;
        private String dataType;
        private Boolean isNullable;
    }
}
