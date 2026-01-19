import pymysql
import json

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

print("🔧 修复Cross规则字段名")
print("=" * 50)

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    # 1. 更新诊断编码与名称配对规则
    print("\n1. 更新诊断编码与名称配对规则...")
    new_related_fields = json.dumps([{"field": "C07x01N", "name": "出院其他诊断名称1"}])
    
    cursor.execute("""
        UPDATE kiro_qc_rule_cross 
        SET related_fields = %s 
        WHERE rule_code = 'CROSS_C06x01C_C07x01C'
    """, (new_related_fields,))
    
    print(f"  ✅ 更新了CROSS_C06x01C_C07x01C规则的关联字段")
    
    # 2. 更新手术编码与名称配对规则
    print("\n2. 更新手术编码与名称配对规则...")
    new_related_fields = json.dumps([{"field": "C15x01N", "name": "主要手术操作名称"}])
    
    cursor.execute("""
        UPDATE kiro_qc_rule_cross 
        SET related_fields = %s 
        WHERE rule_code = 'CROSS_C14x01C_C15x01C'
    """, (new_related_fields,))
    
    print(f"  ✅ 更新了CROSS_C14x01C_C15x01C规则的关联字段")
    
    conn.commit()
    
    # 3. 验证更新结果
    print("\n3. 验证更新结果...")
    cursor.execute("SELECT rule_code, related_fields FROM kiro_qc_rule_cross WHERE status = 'active'")
    rules = cursor.fetchall()
    
    for rule_code, related_fields in rules:
        print(f"  {rule_code}:")
        try:
            fields = json.loads(related_fields)
            for field in fields:
                print(f"    关联字段: {field['field']} ({field['name']})")
        except:
            print(f"    关联字段: {related_fields}")
        print()
    
    # 4. 测试病案数据
    print("4. 测试病案445583_1的相关字段:")
    cursor.execute("""
        SELECT A48, A49, A12C, C03C, C06x01C, C07x01N, C14x01C, C15x01N
        FROM d_mr 
        WHERE A48 = '445583' AND A49 = '1'
    """)
    
    result = cursor.fetchone()
    if result:
        print(f"  A48: {result[0]}")
        print(f"  A49: {result[1]}")
        print(f"  A12C(性别): {result[2]} ({'男' if result[2] == '1' else '女' if result[2] == '2' else '未知'})")
        print(f"  C03C(主诊断): {result[3]}")
        print(f"  C06x01C(其他诊断编码1): '{result[4]}' {'有值' if result[4] else '空'}")
        print(f"  C07x01N(其他诊断名称1): '{result[5]}' {'有值' if result[5] else '空'}")
        print(f"  C14x01C(手术编码): '{result[6]}' {'有值' if result[6] else '空'}")
        print(f"  C15x01N(手术名称): '{result[7]}' {'有值' if result[7] else '空'}")
        
        # 分析可能的违规
        c06x01c = result[4]
        c07x01n = result[5]
        c14x01c = result[6]
        c15x01n = result[7]
        
        print(f"\n  Cross规则分析:")
        
        # 诊断编码与名称配对
        if (c06x01c and not c07x01n) or (not c06x01c and c07x01n):
            print(f"    ⚠️  违反诊断配对规则: 编码='{c06x01c}', 名称='{c07x01n}'")
        else:
            print(f"    ✅ 诊断配对正常: 编码和名称都{'有值' if c06x01c else '为空'}")
            
        # 手术编码与名称配对
        if (c14x01c and not c15x01n) or (not c14x01c and c15x01n):
            print(f"    ⚠️  违反手术配对规则: 编码='{c14x01c}', 名称='{c15x01n}'")
        else:
            print(f"    ✅ 手术配对正常: 编码和名称都{'有值' if c14x01c else '为空'}")
            
        # 性别诊断逻辑
        gender = result[2]
        diagnosis = result[3]
        if gender == '1' and diagnosis:  # 男性
            if any(code in str(diagnosis) for code in ['N70', 'N80', 'N90', 'O00', 'O10']):
                print(f"    ⚠️  违反性别诊断规则: 男性患者诊断包含妇科代码")
            else:
                print(f"    ✅ 性别诊断正常: 男性患者诊断不包含妇科代码")
    
    cursor.close()
    conn.close()
    
    print(f"\n" + "=" * 50)
    print("字段名修复完成")
    print("=" * 50)
    
except Exception as e:
    print(f"❌ 修复失败: {e}")
    import traceback
    traceback.print_exc()