import pymysql
import requests
import json

db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

print("=" * 80)
print("调试字段值不匹配问题")
print("=" * 80)

# 1. 直接查询数据库中的原始数据
print("\n1. 查询数据库原始数据:")
try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    # 查询病案445583_1的所有字段
    cursor.execute("""
        SELECT A01, A19C, A48, A49, B15
        FROM d_mr 
        WHERE A48 = '445583' AND A49 = '1'
    """)
    result = cursor.fetchone()
    
    if result:
        a01, a19c, a48, a49, b15 = result
        print(f"  病案 {a48}_{a49}:")
        print(f"    A01 (组织机构代码): '{a01}'")
        print(f"    A19C (民族): '{a19c}'")
        print(f"    B15 (时间): '{b15}'")
    else:
        print("  ❌ 未找到病案数据")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"  ❌ 数据库查询失败: {e}")

# 2. 测试MedicalRecordMapper的查询结果
print("\n2. 模拟MedicalRecordMapper查询:")
try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    # 模拟MedicalRecordMapper.findByKey的查询
    query = """
        SELECT m.*, o1.* 
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
        
        all_columns = d_mr_columns + d_mr_other_1_20_columns
        
        # 创建字段映射
        field_map = {}
        for i, col_name in enumerate(all_columns):
            if i < len(result):
                field_map[col_name] = result[i]
        
        print(f"  MedicalRecordMapper查询结果:")
        print(f"    A01: '{field_map.get('A01', 'NULL')}'")
        print(f"    A19C: '{field_map.get('A19C', 'NULL')}'")
        
        # 检查是否有字段名冲突
        if 'A01' in field_map and 'A19C' in field_map:
            if field_map['A01'] == field_map['A19C']:
                print(f"  ⚠️  A01和A19C值相同，可能存在字段混淆")
            else:
                print(f"  ✅ A01和A19C值不同，字段映射正确")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"  ❌ MedicalRecordMapper查询失败: {e}")

# 3. 检查是否存在字段名重复或混淆
print("\n3. 检查字段名重复问题:")
try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    # 检查d_mr表的A01和A19C字段
    cursor.execute("SELECT A01, A19C FROM d_mr WHERE A48 = '445583' AND A49 = '1'")
    d_mr_result = cursor.fetchone()
    
    # 检查d_mr_other_1_20表是否也有这些字段
    cursor.execute("DESCRIBE d_mr_other_1_20")
    other_columns = [col[0] for col in cursor.fetchall()]
    
    print(f"  d_mr表中:")
    if d_mr_result:
        print(f"    A01: '{d_mr_result[0]}'")
        print(f"    A19C: '{d_mr_result[1]}'")
    
    print(f"  d_mr_other_1_20表中的字段:")
    if 'A01' in other_columns:
        cursor.execute("SELECT A01 FROM d_mr_other_1_20 WHERE A48 = '445583' AND A49 = '1'")
        other_a01 = cursor.fetchone()
        print(f"    A01: '{other_a01[0] if other_a01 else 'NULL'}'")
    else:
        print(f"    A01: 不存在")
        
    if 'A19C' in other_columns:
        cursor.execute("SELECT A19C FROM d_mr_other_1_20 WHERE A48 = '445583' AND A49 = '1'")
        other_a19c = cursor.fetchone()
        print(f"    A19C: '{other_a19c[0] if other_a19c else 'NULL'}'")
    else:
        print(f"    A19C: 不存在")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"  ❌ 字段重复检查失败: {e}")

# 4. 直接调用API查看返回的数据
print("\n4. 调用API查看返回数据:")
try:
    # 先运行一个小批次
    response = requests.post(
        "http://localhost:4101/api/qc/batch",
        json={"year": 2023, "limit": 1, "a48": "445583", "a49": "1"},
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if response.status_code == 200:
        print("  ✅ 质控批次运行成功")
        
        # 获取病案的缺陷详情
        import time
        time.sleep(3)  # 等待处理完成
        
        defect_response = requests.get(
            "http://localhost:4101/api/qc/case-defects/445583_1",
            timeout=10
        )
        
        if defect_response.status_code == 200:
            defects = defect_response.json()
            print(f"  API返回的缺陷数据:")
            
            for defect in defects:
                rule_code = defect.get('ruleCode', '')
                field_code = defect.get('fieldCode', '')
                field_name = defect.get('fieldName', '')
                actual_value = defect.get('actualValue', '')
                
                if 'RC035' in rule_code or 'A19C' in field_code or 'A01' in field_code:
                    print(f"    规则: {rule_code}")
                    print(f"    字段: {field_code} ({field_name})")
                    print(f"    API返回值: '{actual_value}'")
                    print()
        else:
            print(f"  ❌ 获取缺陷详情失败: {defect_response.status_code}")
    else:
        print(f"  ❌ 质控批次失败: {response.status_code}")
        print(f"  响应: {response.text}")
        
except Exception as e:
    print(f"  ❌ API调用失败: {e}")

print("\n" + "=" * 80)
print("调试完成")
print("=" * 80)

print("\n🔍 分析要点:")
print("1. 数据库中A19C的实际值")
print("2. MedicalRecordMapper查询返回的值")
print("3. API最终返回给前端的值")
print("4. 是否存在字段名冲突或JOIN问题")
print("5. RuleEngineService中字段值获取逻辑")