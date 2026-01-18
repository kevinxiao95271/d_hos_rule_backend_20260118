import pymysql
from datetime import datetime

# 数据库连接配置
db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

try:
    # 连接数据库
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("数据库连接成功！")
    print("=" * 80)
    
    # 查看所有表
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("\n所有表列表:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # 查看d_mr表结构
    print("\n" + "=" * 80)
    print("d_mr 表结构:")
    print("=" * 80)
    cursor.execute("DESCRIBE d_mr")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]:<20} {col[1]:<20} {col[2]}")
    
    # 查看d_mr数据量和B15字段样例
    cursor.execute("SELECT COUNT(*) FROM d_mr")
    count = cursor.fetchone()[0]
    print(f"\nd_mr 总记录数: {count}")
    
    # 查看B15字段的数据格式
    print("\n" + "=" * 80)
    print("B15字段(时间字段)样例数据:")
    print("=" * 80)
    cursor.execute("SELECT A48, A49, B15 FROM d_mr LIMIT 10")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  A48: {row[0]}, A49: {row[1]}, B15: {row[2]} (类型: {type(row[2])})")
    
    # 查看B15字段的年份分布
    print("\n" + "=" * 80)
    print("B15字段年份分布:")
    print("=" * 80)
    cursor.execute("""
        SELECT YEAR(B15) as year, COUNT(*) as count 
        FROM d_mr 
        WHERE B15 IS NOT NULL 
        GROUP BY YEAR(B15) 
        ORDER BY year
    """)
    year_dist = cursor.fetchall()
    for row in year_dist:
        print(f"  {row[0]}年: {row[1]} 条记录")
    
    # 查看d_mr_other表
    print("\n" + "=" * 80)
    print("d_mr_other_1_20 表结构:")
    print("=" * 80)
    cursor.execute("DESCRIBE d_mr_other_1_20")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]:<20} {col[1]:<20}")
    
    # 查看字典表样例
    print("\n" + "=" * 80)
    print("sys_dict 表样例 (RC001性别):")
    print("=" * 80)
    cursor.execute("""
        SELECT dict_type_code, dict_code, dict_value 
        FROM sys_dict 
        WHERE dict_type_code = 'RC001' 
        LIMIT 5
    """)
    dicts = cursor.fetchall()
    for d in dicts:
        print(f"  {d[0]} - {d[1]}: {d[2]}")
    
    # 查看A18x01, A18x02, A18x03字段（新生儿出生体重）
    print("\n" + "=" * 80)
    print("新生儿出生体重字段样例:")
    print("=" * 80)
    cursor.execute("""
        SELECT A48, A49, A18x01, A18x02, A18x03 
        FROM d_mr 
        WHERE A18x01 IS NOT NULL OR A18x02 IS NOT NULL OR A18x03 IS NOT NULL 
        LIMIT 5
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(f"  A48_A49: {row[0]}_{row[1]}, 体重1: {row[2]}, 体重2: {row[3]}, 体重3: {row[4]}")
    
    cursor.close()
    conn.close()
    print("\n" + "=" * 80)
    print("数据库连接测试完成！")
    print("=" * 80)
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
