#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql

DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def restore_rules():
    print("恢复所有规则...")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE kiro_qc_rule SET status = 'active' WHERE status = 'disabled_temp'")
        restored_count = cursor.rowcount
        conn.commit()
        
        print(f"✅ 已恢复 {restored_count} 条规则")
        
        # 验证恢复结果
        cursor.execute("SELECT status, COUNT(*) as count FROM kiro_qc_rule GROUP BY status")
        results = cursor.fetchall()
        
        print("当前规则状态:")
        for status, count in results:
            print(f"  {status}: {count}条")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    restore_rules()