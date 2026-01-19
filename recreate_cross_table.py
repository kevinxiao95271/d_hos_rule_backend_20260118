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
print("重新创建Cross规则表")
print("=" * 80)

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    # 1. 删除现有表
    print("1. 删除现有表...")
    cursor.execute("DROP TABLE IF EXISTS kiro_qc_cross_log")
    cursor.execute("DROP TABLE IF EXISTS kiro_qc_rule_cross")
    print("✅ 旧表已删除")
    
    # 2. 创建新的跨字段规则表
    print("\n2. 创建新的跨字段规则表...")
    create_table_sql = """
    CREATE TABLE kiro_qc_rule_cross (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        rule_code VARCHAR(64) NOT NULL UNIQUE COMMENT '规则编码',
        description TEXT NOT NULL COMMENT '规则描述',
        
        -- 规则类型
        cross_type VARCHAR(32) NOT NULL COMMENT '跨字段类型: field_pair, logic_check, age_gender, date_consistency',
        
        -- 主字段信息
        primary_field VARCHAR(64) NOT NULL COMMENT '主字段代码',
        primary_field_name VARCHAR(200) COMMENT '主字段名称',
        
        -- 关联字段信息 (JSON格式存储多个字段)
        related_fields JSON COMMENT '关联字段列表',
        
        -- 约束条件 (JSON格式存储复杂条件)
        constraint_conditions JSON COMMENT '约束条件',
        
        -- 逻辑表达式 (用于复杂逻辑判断)
        logic_expression TEXT COMMENT '逻辑表达式',
        
        -- 错误信息
        error_message TEXT COMMENT '违规时的错误信息',
        expected_value TEXT COMMENT '期望值描述',
        
        -- 规则配置
        deduct_score DECIMAL(10,2) DEFAULT 0.20 COMMENT '扣分',
        severity VARCHAR(16) DEFAULT 'warning' COMMENT '严重程度',
        
        -- 适用范围
        source_tables VARCHAR(500) COMMENT '数据来源表',
        applicable_conditions TEXT COMMENT '适用条件',
        
        -- 状态管理
        status VARCHAR(16) DEFAULT 'active' COMMENT '状态',
        priority INT DEFAULT 100 COMMENT '优先级',
        
        -- 审计字段
        created_by VARCHAR(64) COMMENT '创建人',
        updated_by VARCHAR(64) COMMENT '更新人',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        
        -- 索引
        INDEX idx_rule_code (rule_code),
        INDEX idx_primary_field (primary_field),
        INDEX idx_cross_type (cross_type),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='跨字段约束规则表'
    """
    
    cursor.execute(create_table_sql)
    print("✅ 跨字段规则表创建成功")
    
    # 3. 插入示例规则
    print("\n3. 插入示例规则...")
    insert_rules = [
        # 诊断编码与名称配对规则
        ("CROSS_C06x01C_C07x01C", "出院其他诊断编码1为空，但出院其他诊断名称1不为空，两者必须同时有值或同时为空",
         "field_pair", "C06x01C", "出院其他诊断编码1",
         '[{"field":"C07x01C","name":"出院其他诊断名称1"}]',
         '{"type":"both_or_neither","logic":"AND"}',
         "诊断编码与名称必须同时填写或同时为空", "编码和名称同时有值或同时为空", 0.20, "d_mr"),
        
        # 手术编码与名称配对规则
        ("CROSS_C14x01C_C15x01C", "主要手术操作编码为空，但主要手术操作名称不为空，两者必须同时有值或同时为空",
         "field_pair", "C14x01C", "主要手术操作编码",
         '[{"field":"C15x01C","name":"主要手术操作名称"}]',
         '{"type":"both_or_neither","logic":"AND"}',
         "手术编码与名称必须同时填写或同时为空", "编码和名称同时有值或同时为空", 0.20, "d_mr"),
        
        # 性别与诊断逻辑检查
        ("CROSS_C03C_GENDER_MALE", "出院主要诊断编码不符合逻辑判断，男性不允许编码妇科相关疾病",
         "age_gender", "C03C", "出院主要诊断编码",
         '[{"field":"A12C","name":"性别"}]',
         '{"type":"gender_diagnosis","gender":"1","forbidden_codes":["N70-N98","O00-O99"]}',
         "男性患者不应编码妇科相关疾病", "符合性别的诊断编码", 0.20, "d_mr"),
    ]
    
    for rule_data in insert_rules:
        insert_sql = """
        INSERT INTO kiro_qc_rule_cross (
            rule_code, description, cross_type, primary_field, primary_field_name,
            related_fields, constraint_conditions, error_message, expected_value, 
            deduct_score, source_tables
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, rule_data)
    
    print(f"✅ 插入了 {len(insert_rules)} 条示例规则")
    
    # 4. 创建日志表
    print("\n4. 创建日志表...")
    create_log_table_sql = """
    CREATE TABLE kiro_qc_cross_log (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        rule_id BIGINT NOT NULL COMMENT '规则ID',
        mr_key VARCHAR(128) NOT NULL COMMENT '病案键',
        execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '执行时间',
        result VARCHAR(16) NOT NULL COMMENT '结果: pass, fail, error',
        error_details TEXT COMMENT '错误详情',
        field_values JSON COMMENT '相关字段值',
        
        INDEX idx_rule_id (rule_id),
        INDEX idx_mr_key (mr_key),
        INDEX idx_execution_time (execution_time),
        FOREIGN KEY (rule_id) REFERENCES kiro_qc_rule_cross(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='跨字段规则执行日志表'
    """
    
    cursor.execute(create_log_table_sql)
    print("✅ 日志表创建成功")
    
    conn.commit()
    
    # 5. 验证结果
    print("\n5. 验证结果...")
    cursor.execute("SELECT COUNT(*) FROM kiro_qc_rule_cross")
    count = cursor.fetchone()[0]
    print(f"跨字段规则表记录数: {count}")
    
    cursor.execute("SELECT rule_code, cross_type, primary_field FROM kiro_qc_rule_cross")
    rules = cursor.fetchall()
    print("插入的规则:")
    for rule in rules:
        print(f"  {rule[0]}: {rule[1]} - {rule[2]}")
    
    cursor.close()
    conn.close()
    
    print(f"\n" + "=" * 80)
    print("Cross规则表重新创建完成")
    print("=" * 80)
    
except Exception as e:
    print(f"❌ 执行失败: {e}")
    import traceback
    traceback.print_exc()