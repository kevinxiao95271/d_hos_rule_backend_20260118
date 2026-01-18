import pymysql

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

try:
    # 添加source_tables字段
    cursor.execute("""
        ALTER TABLE kiro_qc_rule 
        ADD COLUMN `source_tables` varchar(500) DEFAULT NULL COMMENT '源数据表，多个用逗号分隔'
    """)
    print("✓ 添加source_tables字段成功")
except Exception as e:
    if "Duplicate column name" in str(e):
        print("✓ source_tables字段已存在")
    else:
        print(f"✗ 添加source_tables字段失败: {e}")

try:
    # 添加dict_types字段
    cursor.execute("""
        ALTER TABLE kiro_qc_rule 
        ADD COLUMN `dict_types` varchar(500) DEFAULT NULL COMMENT '值域数据集，多个用逗号分隔'
    """)
    print("✓ 添加dict_types字段成功")
except Exception as e:
    if "Duplicate column name" in str(e):
        print("✓ dict_types字段已存在")
    else:
        print(f"✗ 添加dict_types字段失败: {e}")

conn.commit()

# 查看表结构
cursor.execute("DESCRIBE kiro_qc_rule")
print("\n当前表结构:")
for col in cursor.fetchall():
    print(f"  {col[0]:<30} {col[1]:<20} {col[4]}")

cursor.close()
conn.close()
print("\n表结构更新完成！")
