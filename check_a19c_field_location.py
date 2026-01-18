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

print("=" * 80)
print("检查A19C字段位置")
print("=" * 80)

# 检查A19C字段在哪些表中存在
tables = ['d_mr', 'd_mr_other_1_20', 'd_mr_other_21_40', 'd_mr_other_f']

for table in tables:
    print(f"\n检查表 {table}:")
    try:
        # 检查表结构中是否有A19C字段
        cursor.execute(f"DESCRIBE {table}")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        if 'A19C' in column_names:
            print(f"  ✅ 表 {table} 包含A19C字段")
            
            # 检查A19C字段的数据
            cursor.execute(f"SELECT A19C, COUNT(*) as cnt FROM {table} WHERE A19C IS NOT NULL AND A19C != '' AND A19C != '-' GROUP BY A19C ORDER BY cnt DESC LIMIT 5")
            data = cursor.fetchall()
            if data:
                print(f"  A19C字段数据:")
                for row in data:
                    print(f"    '{row[0]}': {row[1]}次")
            else:
                print(f"  A19C字段无数据")
        else:
            print(f"  ❌ 表 {table} 不包含A19C字段")
            
    except Exception as e:
        print(f"  ❌ 检查表 {table} 失败: {e}")

# 检查病案445583_1在各表中的A19C值
print(f"\n检查病案445583_1的A19C字段值:")
for table in tables:
    try:
        cursor.execute(f"SELECT A19C FROM {table} WHERE A48 = '445583' AND A49 = '1'")
        result = cursor.fetchone()
        if result:
            print(f"  表 {table}: A19C = '{result[0]}'")
        else:
            print(f"  表 {table}: 无记录或A19C字段不存在")
    except Exception as e:
        print(f"  表 {table}: 查询失败 - {e}")

# 检查当前MedicalRecordMapper的查询是否能获取到A19C字段
print(f"\n检查当前查询能否获取A19C字段:")
try:
    # 模拟MedicalRecordMapper的查询
    query = """
    SELECT CONCAT(m.A48, '_', m.A49) as mrKey, m.*, o1.* 
    FROM d_mr m 
    LEFT JOIN d_mr_other_1_20 o1 ON m.A48 = o1.A48 AND m.A49 = o1.A49 
    WHERE m.A48 = '445583' AND m.A49 = '1'
    """
    cursor.execute(query)
    result = cursor.fetchone()
    
    if result:
        # 获取列名
        cursor.execute("DESCRIBE d_mr")
        d_mr_columns = [col[0] for col in cursor.fetchall()]
        
        cursor.execute("DESCRIBE d_mr_other_1_20")
        d_mr_other_1_20_columns = [col[0] for col in cursor.fetchall()]
        
        all_columns = ['mrKey'] + d_mr_columns + d_mr_other_1_20_columns
        
        print(f"  当前查询返回的列数: {len(result)}")
        print(f"  预期列数: {len(all_columns)}")
        
        if 'A19C' in d_mr_columns:
            print(f"  ✅ A19C在d_mr表中，当前查询可以获取")
        elif 'A19C' in d_mr_other_1_20_columns:
            print(f"  ✅ A19C在d_mr_other_1_20表中，当前查询可以获取")
        else:
            print(f"  ❌ A19C不在当前查询的表中")
            print(f"  需要修改MedicalRecordMapper以包含包含A19C的表")
    else:
        print(f"  ❌ 查询无结果")
        
except Exception as e:
    print(f"  ❌ 查询失败: {e}")

cursor.close()
conn.close()

print(f"\n" + "=" * 80)
print("检查完成")
print("=" * 80)