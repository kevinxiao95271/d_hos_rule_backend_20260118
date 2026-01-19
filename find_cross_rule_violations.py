import pymysql

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

print("🔍 查找可能违反Cross规则的病案")
print("=" * 60)

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    # 1. 查找诊断编码与名称不匹配的病案
    print("\n1. 查找诊断编码与名称不匹配的病案:")
    cursor.execute("""
        SELECT A48, A49, C06x01C, C07x01N
        FROM d_mr 
        WHERE (C06x01C IS NOT NULL AND C06x01C != '' AND (C07x01N IS NULL OR C07x01N = ''))
           OR (C07x01N IS NOT NULL AND C07x01N != '' AND (C06x01C IS NULL OR C06x01C = ''))
        LIMIT 5
    """)
    
    diagnosis_mismatches = cursor.fetchall()
    if diagnosis_mismatches:
        print(f"  找到 {len(diagnosis_mismatches)} 个诊断编码与名称不匹配的病案:")
        for record in diagnosis_mismatches:
            a48, a49, code, name = record
            print(f"    病案 {a48}_{a49}:")
            print(f"      诊断编码: '{code}' {'有值' if code else '空'}")
            print(f"      诊断名称: '{name}' {'有值' if name else '空'}")
            print()
    else:
        print("  ✅ 未找到诊断编码与名称不匹配的病案")
    
    # 2. 查找手术编码与名称不匹配的病案
    print("\n2. 查找手术编码与名称不匹配的病案:")
    cursor.execute("""
        SELECT A48, A49, C14x01C, C15x01N
        FROM d_mr 
        WHERE (C14x01C IS NOT NULL AND C14x01C != '' AND (C15x01N IS NULL OR C15x01N = ''))
           OR (C15x01N IS NOT NULL AND C15x01N != '' AND (C14x01C IS NULL OR C14x01C = ''))
        LIMIT 5
    """)
    
    surgery_mismatches = cursor.fetchall()
    if surgery_mismatches:
        print(f"  找到 {len(surgery_mismatches)} 个手术编码与名称不匹配的病案:")
        for record in surgery_mismatches:
            a48, a49, code, name = record
            print(f"    病案 {a48}_{a49}:")
            print(f"      手术编码: '{code}' {'有值' if code else '空'}")
            print(f"      手术名称: '{name}' {'有值' if name else '空'}")
            print()
    else:
        print("  ✅ 未找到手术编码与名称不匹配的病案")
    
    # 3. 查找男性患者可能有妇科诊断的病案
    print("\n3. 查找男性患者可能有妇科诊断的病案:")
    cursor.execute("""
        SELECT A48, A49, A12C, C03C
        FROM d_mr 
        WHERE A12C = '1' 
          AND (C03C LIKE 'N7%' OR C03C LIKE 'N8%' OR C03C LIKE 'N9%' OR C03C LIKE 'O%')
        LIMIT 5
    """)
    
    gender_mismatches = cursor.fetchall()
    if gender_mismatches:
        print(f"  找到 {len(gender_mismatches)} 个男性患者可能有妇科诊断的病案:")
        for record in gender_mismatches:
            a48, a49, gender, diagnosis = record
            print(f"    病案 {a48}_{a49}:")
            print(f"      性别: {gender} (男)")
            print(f"      主诊断: {diagnosis}")
            print()
    else:
        print("  ✅ 未找到男性患者有妇科诊断的病案")
    
    # 4. 如果没有找到违规病案，创建一个测试病案
    if not diagnosis_mismatches and not surgery_mismatches and not gender_mismatches:
        print("\n4. 创建测试病案数据:")
        
        # 查找一个现有病案来修改
        cursor.execute("SELECT A48, A49 FROM d_mr LIMIT 1")
        test_case = cursor.fetchone()
        
        if test_case:
            test_a48, test_a49 = test_case
            print(f"  使用病案 {test_a48}_{test_a49} 进行测试")
            
            # 临时修改数据来创建违规（仅用于测试）
            cursor.execute("""
                UPDATE d_mr 
                SET C06x01C = 'TEST_CODE', C07x01N = NULL
                WHERE A48 = %s AND A49 = %s
            """, (test_a48, test_a49))
            
            print(f"  ✅ 临时创建了诊断编码与名称不匹配的测试数据")
            print(f"  测试病案: {test_a48}_{test_a49}")
            
            conn.commit()
    
    # 5. 推荐测试病案
    print("\n5. 推荐用于测试的病案:")
    if diagnosis_mismatches:
        test_case = diagnosis_mismatches[0]
        print(f"  推荐测试病案: {test_case[0]}_{test_case[1]} (诊断编码与名称不匹配)")
    elif surgery_mismatches:
        test_case = surgery_mismatches[0]
        print(f"  推荐测试病案: {test_case[0]}_{test_case[1]} (手术编码与名称不匹配)")
    elif gender_mismatches:
        test_case = gender_mismatches[0]
        print(f"  推荐测试病案: {test_case[0]}_{test_case[1]} (性别诊断不匹配)")
    else:
        print(f"  推荐测试病案: {test_a48}_{test_a49} (临时创建的测试数据)")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ 查找失败: {e}")
    import traceback
    traceback.print_exc()

print(f"\n" + "=" * 60)
print("查找完成")
print("=" * 60)