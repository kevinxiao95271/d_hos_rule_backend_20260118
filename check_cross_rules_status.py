import pymysql

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

print("🔍 检查Cross规则状态")
print("=" * 50)

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    # 1. 检查cross规则表
    print("\n1. 检查cross规则表:")
    cursor.execute("SELECT COUNT(*) FROM kiro_qc_rule_cross")
    total_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM kiro_qc_rule_cross WHERE status = 'active'")
    active_count = cursor.fetchone()[0]
    
    print(f"  总规则数: {total_count}")
    print(f"  活跃规则数: {active_count}")
    
    if active_count > 0:
        cursor.execute("SELECT rule_code, cross_type, primary_field, description FROM kiro_qc_rule_cross WHERE status = 'active'")
        rules = cursor.fetchall()
        
        print(f"\n  活跃的cross规则:")
        for rule in rules:
            print(f"    {rule[0]}: {rule[1]} - {rule[2]}")
            print(f"      描述: {rule[3][:60]}...")
            print()
    
    # 2. 检查测试病案的相关字段
    print("\n2. 检查测试病案445583_1的相关字段:")
    cursor.execute("""
        SELECT A48, A49, A12C, C03C, C06x01C, C07x01C, C14x01C, C15x01C
        FROM d_mr 
        WHERE A48 = '445583' AND A49 = '1'
    """)
    
    result = cursor.fetchone()
    if result:
        fields = ['A48', 'A49', 'A12C(性别)', 'C03C(主诊断)', 'C06x01C(其他诊断编码1)', 'C07x01C(其他诊断名称1)', 'C14x01C(手术编码)', 'C15x01C(手术名称)']
        print(f"  病案字段值:")
        for i, field in enumerate(fields):
            value = result[i] if result[i] is not None else "NULL"
            print(f"    {field}: '{value}'")
    else:
        print(f"  ❌ 未找到病案445583_1")
    
    # 3. 分析可能的cross规则违规
    print("\n3. 分析可能的cross规则违规:")
    if result:
        a12c = result[2]  # 性别
        c03c = result[3]  # 主诊断
        c06x01c = result[4]  # 其他诊断编码1
        c07x01c = result[5]  # 其他诊断名称1
        c14x01c = result[6]  # 手术编码
        c15x01c = result[7]  # 手术名称
        
        print(f"  字段配对分析:")
        print(f"    C06x01C(其他诊断编码1): '{c06x01c}' {'有值' if c06x01c else '空'}")
        print(f"    C07x01C(其他诊断名称1): '{c07x01c}' {'有值' if c07x01c else '空'}")
        
        if (c06x01c and not c07x01c) or (not c06x01c and c07x01c):
            print(f"    ⚠️  可能违反字段配对规则: 编码和名称不匹配")
        else:
            print(f"    ✅ 字段配对正常")
            
        print(f"    C14x01C(手术编码): '{c14x01c}' {'有值' if c14x01c else '空'}")
        print(f"    C15x01C(手术名称): '{c15x01c}' {'有值' if c15x01c else '空'}")
        
        if (c14x01c and not c15x01c) or (not c14x01c and c15x01c):
            print(f"    ⚠️  可能违反手术配对规则: 编码和名称不匹配")
        else:
            print(f"    ✅ 手术配对正常")
            
        print(f"  性别诊断分析:")
        print(f"    A12C(性别): '{a12c}' ({'男' if a12c == '1' else '女' if a12c == '2' else '未知'})")
        print(f"    C03C(主诊断): '{c03c}'")
        
        if a12c == '1' and c03c:  # 男性
            if any(code in str(c03c) for code in ['N70', 'N80', 'N90', 'O00', 'O10']):
                print(f"    ⚠️  可能违反性别诊断规则: 男性患者有妇科诊断")
            else:
                print(f"    ✅ 性别诊断匹配正常")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ 检查失败: {e}")
    import traceback
    traceback.print_exc()

print(f"\n" + "=" * 50)
print("检查完成")
print("=" * 50)