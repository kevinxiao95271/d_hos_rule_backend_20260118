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
print("寻找医疗付费方式字段")
print("=" * 80)

# 获取RC032字典的有效值
cursor.execute("SELECT dict_code FROM sys_dict WHERE dict_type_code = 'RC032'")
valid_codes = [row[0] for row in cursor.fetchall()]
print(f"RC032有效代码: {valid_codes}")

# 1. 检查d_mr表的所有字段
print(f"\n1. 检查d_mr表的所有字段，寻找包含RC032代码的字段:")
cursor.execute("DESCRIBE d_mr")
columns = cursor.fetchall()
field_names = [col[0] for col in columns]

# 检查每个字段是否包含RC032的有效代码
found_fields = []
for field in field_names:
    try:
        # 构建查询，检查该字段是否包含RC032的任何代码
        placeholders = ','.join(['%s'] * len(valid_codes))
        query = f"SELECT {field}, COUNT(*) as cnt FROM d_mr WHERE {field} IN ({placeholders}) GROUP BY {field} ORDER BY cnt DESC LIMIT 5"
        cursor.execute(query, valid_codes)
        matches = cursor.fetchall()
        if matches:
            found_fields.append(field)
            print(f"  字段 {field} 包含RC032代码:")
            for match in matches:
                print(f"    代码: {match[0]}, 出现次数: {match[1]}")
    except Exception as e:
        # 忽略数据类型不匹配的字段
        pass

if not found_fields:
    print("  在d_mr表中未找到包含RC032代码的字段")

# 2. 检查其他表
other_tables = ['d_mr_other_1_20', 'd_mr_other_21_40', 'd_mr_other_f']
for table in other_tables:
    print(f"\n2. 检查表 {table}:")
    try:
        cursor.execute(f"DESCRIBE {table}")
        cols = cursor.fetchall()
        table_fields = [col[0] for col in cols]
        
        found_in_table = []
        for field in table_fields:
            try:
                placeholders = ','.join(['%s'] * len(valid_codes))
                query = f"SELECT {field}, COUNT(*) as cnt FROM {table} WHERE {field} IN ({placeholders}) GROUP BY {field} ORDER BY cnt DESC LIMIT 5"
                cursor.execute(query, valid_codes)
                matches = cursor.fetchall()
                if matches:
                    found_in_table.append(field)
                    print(f"  字段 {field} 包含RC032代码:")
                    for match in matches:
                        print(f"    代码: {match[0]}, 出现次数: {match[1]}")
            except Exception as e:
                pass
        
        if not found_in_table:
            print(f"  在表 {table} 中未找到包含RC032代码的字段")
            
    except Exception as e:
        print(f"  表 {table} 检查失败: {e}")

# 3. 如果没找到，尝试查找可能的字段名模式
print(f"\n3. 查找可能的付费方式字段名模式:")
all_tables = ['d_mr'] + other_tables
for table in all_tables:
    try:
        cursor.execute(f"DESCRIBE {table}")
        cols = cursor.fetchall()
        print(f"\n  表 {table} 的所有字段:")
        for i, col in enumerate(cols):
            field_name = col[0]
            data_type = col[1]
            print(f"    {i+1:2d}. {field_name} ({data_type})")
            
            # 如果字段名包含可能的关键词，检查其数据
            if any(keyword in field_name.lower() for keyword in ['pay', 'fee', 'cost', 'charge', 'money', 'fund', 'type', 'method', 'way']) or field_name.startswith('B') or field_name.startswith('C'):
                try:
                    cursor.execute(f"SELECT {field_name}, COUNT(*) as cnt FROM {table} WHERE {field_name} IS NOT NULL AND {field_name} != '' AND {field_name} != '-' GROUP BY {field_name} ORDER BY cnt DESC LIMIT 3")
                    samples = cursor.fetchall()
                    if samples:
                        print(f"        样例数据: {[row[0] for row in samples]}")
                except:
                    pass
    except Exception as e:
        print(f"  表 {table} 结构检查失败: {e}")

cursor.close()
conn.close()