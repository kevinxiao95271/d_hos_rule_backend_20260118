#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import time

DB_CONFIG = {'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com', 'port': 63606, 'user': 'root', 'password': 'Yiguo9527_', 'database': 'd_hosq_traegj_20260115', 'charset': 'utf8mb4'}

def execute_performance_fix():
    print("执行性能修复...")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 执行索引创建
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_d_mr_a48_a49 ON d_mr(A48, A49)",
            "CREATE INDEX IF NOT EXISTS idx_d_mr_b15 ON d_mr(B15)",
            "CREATE INDEX IF NOT EXISTS idx_qc_dict_type ON kiro_qc_dict(dict_type_code)"
        ]
        
        for sql in indexes:
            try:
                cursor.execute(sql)
                print(f"✅ 执行成功: {sql.split()[-1]}")
            except Exception as e:
                print(f"⚠️  跳过: {e}")
        
        conn.commit()
        print("✅ 数据库优化完成")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    execute_performance_fix()
