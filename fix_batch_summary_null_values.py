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

def fix_batch_summary_null_values():
    """修复批量汇总表中的NULL值"""
    print("🔧 修复批量汇总表中的NULL值...")
    
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # 检查当前数据
        cursor.execute("SELECT batch_key, cross_defect_count, cross_total_deduct, avg_cross_defect FROM kiro_qc_batch_summary")
        rows = cursor.fetchall()
        
        print(f"   📊 当前数据状态:")
        null_count = 0
        for row in rows:
            batch_key, cross_defect_count, cross_total_deduct, avg_cross_defect = row
            if cross_defect_count is None or cross_total_deduct is None or avg_cross_defect is None:
                null_count += 1
                print(f"     - {batch_key}: cross_defect_count={cross_defect_count}, cross_total_deduct={cross_total_deduct}, avg_cross_defect={avg_cross_defect}")
        
        if null_count > 0:
            print(f"   ⚠️  发现 {null_count} 条记录有NULL值，正在修复...")
            
            # 更新NULL值为0
            cursor.execute("""
                UPDATE kiro_qc_batch_summary 
                SET cross_defect_count = COALESCE(cross_defect_count, 0),
                    cross_total_deduct = COALESCE(cross_total_deduct, 0.00),
                    avg_cross_defect = COALESCE(avg_cross_defect, 0.00)
                WHERE cross_defect_count IS NULL 
                   OR cross_total_deduct IS NULL 
                   OR avg_cross_defect IS NULL
            """)
            
            affected_rows = cursor.rowcount
            conn.commit()
            
            print(f"   ✅ 已修复 {affected_rows} 条记录")
        else:
            print(f"   ✅ 所有记录都正常，无需修复")
        
        # 验证修复结果
        cursor.execute("SELECT COUNT(*) FROM kiro_qc_batch_summary WHERE cross_defect_count IS NULL OR cross_total_deduct IS NULL OR avg_cross_defect IS NULL")
        remaining_nulls = cursor.fetchone()[0]
        
        if remaining_nulls == 0:
            print(f"   ✅ 修复完成，无剩余NULL值")
        else:
            print(f"   ⚠️  仍有 {remaining_nulls} 条记录存在NULL值")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   ❌ 修复失败: {e}")

if __name__ == "__main__":
    fix_batch_summary_null_values()