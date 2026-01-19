#!/usr/bin/env python3
import pymysql

# 数据库配置
db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def update_batch_summary_table():
    """更新批量汇总表，添加Cross规则统计字段"""
    print("🔧 更新批量汇总表结构...")
    
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'd_hosq_traegj_20260115' 
            AND TABLE_NAME = 'kiro_qc_batch_summary' 
            AND COLUMN_NAME IN ('cross_defect_count', 'cross_total_deduct', 'avg_cross_defect')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        if len(existing_columns) == 3:
            print("   ✅ Cross规则统计字段已存在，无需添加")
        else:
            print(f"   📋 现有Cross字段: {existing_columns}")
            
            # 添加缺失的字段
            if 'cross_defect_count' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE kiro_qc_batch_summary 
                    ADD COLUMN cross_defect_count INT DEFAULT 0 COMMENT 'Cross规则违规总数'
                """)
                print("   ✅ 添加字段: cross_defect_count")
            
            if 'cross_total_deduct' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE kiro_qc_batch_summary 
                    ADD COLUMN cross_total_deduct DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Cross规则总扣分'
                """)
                print("   ✅ 添加字段: cross_total_deduct")
            
            if 'avg_cross_defect' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE kiro_qc_batch_summary 
                    ADD COLUMN avg_cross_defect DECIMAL(10,2) DEFAULT 0.00 COMMENT '平均Cross规则违规数'
                """)
                print("   ✅ 添加字段: avg_cross_defect")
            
            conn.commit()
        
        # 验证表结构
        cursor.execute("DESCRIBE kiro_qc_batch_summary")
        columns = cursor.fetchall()
        
        print("\\n   📊 当前表结构:")
        for column in columns:
            field_name = column[0]
            field_type = column[1]
            is_null = column[2]
            default_value = column[4]
            comment = column[8] if len(column) > 8 else ''
            
            if 'cross' in field_name.lower():
                print(f"     🎯 {field_name}: {field_type} (默认: {default_value}) - {comment}")
            elif field_name in ['batch_key', 'case_count', 'total_defect_count', 'avg_defect', 'avg_score']:
                print(f"     📋 {field_name}: {field_type}")
        
        cursor.close()
        conn.close()
        
        print("\\n   ✅ 批量汇总表结构更新完成")
        
    except Exception as e:
        print(f"   ❌ 更新失败: {e}")

if __name__ == "__main__":
    update_batch_summary_table()