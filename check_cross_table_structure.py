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

def check_table_structure():
    """检查Cross规则表结构"""
    print("🔍 检查Cross规则表结构")
    print("=" * 50)
    
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'kiro_qc_rule_cross'")
        if not cursor.fetchone():
            print("❌ kiro_qc_rule_cross表不存在")
            return
        
        # 获取表结构
        cursor.execute("DESCRIBE kiro_qc_rule_cross")
        columns = cursor.fetchall()
        
        print("📋 表结构:")
        for column in columns:
            field, type_, null, key, default, extra = column
            print(f"  {field}: {type_} {'NULL' if null == 'YES' else 'NOT NULL'}")
        
        # 检查表中现有数据
        cursor.execute("SELECT COUNT(*) FROM kiro_qc_rule_cross")
        count = cursor.fetchone()[0]
        print(f"\n📊 现有记录数: {count}")
        
        if count > 0:
            cursor.execute("SELECT rule_code, cross_type FROM kiro_qc_rule_cross LIMIT 5")
            samples = cursor.fetchall()
            print("\n🔍 示例记录:")
            for rule_code, cross_type in samples:
                print(f"  {rule_code}: {cross_type}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    check_table_structure()