package com.medical.qc.entity;

import lombok.Data;
import java.util.Map;

@Data
public class MedicalRecord {
    private String a48;
    private String a49;
    private String b15;
    private Map<String, Object> allFields;
    
    public String getMrKey() {
        return a48 + "_" + a49;
    }
}
