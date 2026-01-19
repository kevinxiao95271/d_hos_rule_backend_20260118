import pymysql

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

print("=" * 80)
print("创建Cross规则表")
print("=" * 80)

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    # 读取SQL文件内容
    with open('create_cross_rule_table.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 分割SQL语句（按分号分割）
    sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
    
    print(f"发现 {len(sql_statements)} 条SQL语句")
    
    for i, sql in enumerate(sql_statements, 1):
        try:
            print(f"\n执行语句 {i}:")
            print(f"  {sql[:100]}{'...' if len(sql) > 100 else ''}")
            
            cursor.execute(sql)
            
            if sql.strip().upper().startswith('INSERT'):
                affected_rows = cursor.rowcount
                print(f"  ✅ 插入了 {affected_rows} 条记录")
            elif sql.strip().upper().startswith('CREATE'):
                print(f"  ✅ 表创建成功")
            else:
                print(f"  ✅ 执行成功")
                
        except Exception as e:
            print(f"  ❌ 执行失败: {e}")
            if "already exists" in str(e) or "Duplicate" in str(e):
                print(f"  ⚠️  表或记录已存在，跳过")
            else:
                raise e
    
    conn.commit()
    print(f"\n✅ 所有SQL语句执行完成")
    
    # 验证表创建结果
    print(f"\n验证表结构:")
    cursor.execute("DESCRIBE kiro_qc_cross_rule")
    columns = cursor.fetchall()
    
    print(f"kiro_qc_cross_rule表结构:")
    for col in columns:
        print(f"  {col[0]}: {col[1]} {col[2] if col[2] == 'NO' else ''}")
    
    # 检查插入的数据
    cursor.execute("SELECT COUNT(*) FROM kiro_qc_cross_rule")
    count = cursor.fetchone()[0]
    print(f"\nkiro_qc_cross_rule表记录数: {count}")
    
    if count > 0:
        cursor.execute("SELECT rule_code, primary_field, secondary_field, rule_description FROM kiro_qc_cross_rule LIMIT 5")
        rules = cursor.fetchall()
        print(f"\n前5条cross规则:")
        for rule in rules:
            print(f"  {rule[0]}: {rule[1]} <-> {rule[2]} - {rule[3][:50]}...")
    
    cursor.close()
    conn.close()
    
    print(f"\n" + "=" * 80)
    print("Cross规则表创建完成")
    print("=" * 80)
    
except Exception as e:
    print(f"❌ 执行失败: {e}")
    import traceback
    traceback.print_exc()