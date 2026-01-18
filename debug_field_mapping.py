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
print("调试字段映射问题")
print("=" * 80)

# 1. 查看d_mr表的所有字段，寻找可能的医疗付费方式字段
print("\n1. 查看d_mr表的字段结构（寻找医疗付费方式相关字段）:")
cursor.execute("DESCRIBE d_mr")
columns = cursor.fetchall()
payment_related_fields = []
for col in columns:
    field_name = col[0]
    # 寻找可能与付费方式相关的字段
    if any(keyword in field_name.lower() for keyword in ['pay', 'fee', 'cost', 'charge', 'money', 'fund']):
        payment_related_fields.append(field_name)
        print(f"  可能的付费字段: {field_name} - {col[1]}")

# 2. 检查A32字段的实际含义 - 从数据内容推断
print(f"\n2. A32字段数据分析（当前存储的是姓名，不是付费方式）:")
cursor.execute("SELECT A32, COUNT(*) as cnt FROM d_mr WHERE A32 IS NOT NULL AND A32 != '' AND A32 != '-' GROUP BY A32 ORDER BY cnt DESC LIMIT 5")
rows = cursor.fetchall()
for row in rows:
    print(f"  A32值: '{row[0]}', 出现次数: {row[1]}")

# 3. 寻找真正的医疗付费方式字段 - 检查数据内容是否匹配RC032字典
print(f"\n3. 寻找真正的医疗付费方式字段:")
# 获取RC032字典的有效值
cursor.execute("SELECT dict_code FROM sys_dict WHERE dict_type_code = 'RC032'")
valid_codes = [row[0] for row in cursor.fetchall()]
print(f"  RC032有效代码: {valid_codes}")

# 检查d_mr表中可能包含这些代码的字段
test_fields = ['A31', 'A33', 'A34', 'A35', 'B01', 'B02', 'B03', 'B04', 'B05']
for field in test_fields:
    try:
        cursor.execute(f"SELECT {field}, COUNT(*) as cnt FROM d_mr WHERE {field} IN ({','.join(['%s'] * len(valid_codes))}) GROUP BY {field} ORDER BY cnt DESC LIMIT 3", valid_codes)
        matches = cursor.fetchall()
        if matches:
            print(f"  字段 {field} 包含RC032代码:")
            for match in matches:
                print(f"    代码: {match[0]}, 出现次数: {match[1]}")
    except Exception as e:
        print(f"  字段 {field} 检查失败: {e}")

# 4. 检查其他表中是否有医疗付费方式字段
print(f"\n4. 检查其他表中的付费方式字段:")
other_tables = ['d_mr_other_1_20', 'd_mr_other_21_40', 'd_mr_other_f']
for table in other_tables:
    try:
        cursor.execute(f"DESCRIBE {table}")
        cols = cursor.fetchall()
        for col in cols:
            field_name = col[0]
            if any(keyword in field_name.lower() for keyword in ['pay', 'fee', 'cost', 'charge', 'money', 'fund']) or field_name in ['A32']:
                print(f"  表 {table} 字段: {field_name} - {col[1]}")
                # 检查该字段是否包含RC032代码
                cursor.execute(f"SELECT {field_name}, COUNT(*) as cnt FROM {table} WHERE {field_name} IN ({','.join(['%s'] * len(valid_codes))}) GROUP BY {field_name} ORDER BY cnt DESC LIMIT 2", valid_codes)
                matches = cursor.fetchall()
                if matches:
                    print(f"    包含RC032代码:")
                    for match in matches:
                        print(f"      代码: {match[0]}, 出现次数: {match[1]}")
    except Exception as e:
        print(f"  表 {table} 检查失败: {e}")

# 5. 检查A32在不同表中的数据类型和内容
print(f"\n5. 检查A32字段在各表中的实际内容:")
tables_to_check = ['d_mr', 'd_mr_other_1_20', 'd_mr_other_21_40', 'd_mr_other_f']
for table in tables_to_check:
    try:
        cursor.execute(f"SELECT A32, COUNT(*) as cnt FROM {table} WHERE A32 IS NOT NULL AND A32 != '' GROUP BY A32 ORDER BY cnt DESC LIMIT 3")
        rows = cursor.fetchall()
        if rows:
            print(f"  表 {table} 的A32字段内容:")
            for row in rows:
                print(f"    值: '{row[0]}', 出现次数: {row[1]}")
    except Exception as e:
        print(f"  表 {table} 的A32字段检查失败: {e}")

cursor.close()
conn.close()