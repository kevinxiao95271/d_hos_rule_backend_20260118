package com.medical.qc;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.medical.qc.mapper")
public class QcApplication {
    public static void main(String[] args) {
        SpringApplication.run(QcApplication.class, args);
    }
}
