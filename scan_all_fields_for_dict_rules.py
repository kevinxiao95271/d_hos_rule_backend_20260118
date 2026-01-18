#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import json

# 数据库连接配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def scan_all_fields_for_dict_rules():
    """扫描所有表字段，生成字典验证规则"""
    print("=== 扫描所有字段生成字典验证规则 ===")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 1. 获取所有RC0xx字典类型
        print("1. 获取所有RC0xx字典类型...")
        cursor.execute("""
            SELECT DISTINCT dict_type_code, COUNT(*) as dict_count
            FROM sys_dict 
            WHERE dict_type_code LIKE 'RC0%'
            GROUP BY dict_type_code
            ORDER BY dict_type_code
        """)
        rc_dicts = cursor.fetchall()
        
        print(f"找到RC0xx字典类型: {len(rc_dicts)}个")
        for dict_info in rc_dicts:
            print(f"  {dict_info['dict_type_code']}: {dict_info['dict_count']}个值")
        
        # 2. 扫描所有相关表的字段结构
        tables = ['d_mr', 'd_mr_other_1_20', 'd_mr_other_21_40', 'd_mr_other_f']
        all_fields = {}
        
        print(f"\n2. 扫描表字段结构...")
        for table in tables:
            try:
                cursor.execute(f"SHOW COLUMNS FROM {table}")
                columns = cursor.fetchall()
                all_fields[table] = columns
                print(f"  {table}: {len(columns)}个字段")
            except Exception as e:
                print(f"  {table}: 扫描失败 - {e}")
        
        # 3. 根据字段名称和医疗标准推断字典映射关系
        print(f"\n3. 分析字段与字典的映射关系...")
        
        # 已知的字段-字典映射关系
        known_mappings = {
            # 基本信息字段
            'A01': 'RC035',  # 民族
            'A02': 'RC002',  # 婚姻状况
            'A03': 'RC003',  # 职业
            'A17': 'RC019',  # 离院方式
            'A20': 'RC030',  # ABO血型
            'A21': 'RC031',  # Rh血型
            'A22': 'RC011',  # 病案质量
            'A26': 'RC026',  # 入院途径
            'A27': 'RC027',  # 入院病情
            'A32': 'RC032',  # 医疗付费方式
            'A37': 'RC037',  # 有无药物过敏
            'A38': 'RC038',  # 患者证件类别
            'A28': 'RC028',  # 出院31天内再住院计划
            'A16': 'RC016',  # 死亡患者尸检
            
            # 科别相关
            'A04': 'RC023',  # 科别
            'A05': 'RC023',  # 科别
            'A06': 'RC023',  # 科别
            
            # 手术麻醉方式 - RC013
            'C22x01C': 'RC013',  # 主要手术操作麻醉方式
            'C43x01C': 'RC013',  # 其他手术操作麻醉方式1
            'C43x02C': 'RC013',  # 其他手术操作麻醉方式2
            'C43x03C': 'RC013',  # 其他手术操作麻醉方式3
            # ... 继续到C43x40C
            
            # 手术级别 - RC029
            'C22x01D': 'RC029',  # 主要手术操作级别
            'C43x01D': 'RC029',  # 其他手术操作级别1
            # ... 继续到C43x40D
            
            # 切口愈合等级 - RC014
            'C22x01E': 'RC014',  # 主要手术切口愈合等级
            'C43x01E': 'RC014',  # 其他手术切口愈合等级1
            # ... 继续到C43x40E
        }
        
        # 4. 自动生成麻醉方式、手术级别、切口愈合等级的完整映射
        print("4. 生成完整的字段映射...")
        
        # 生成C43x01C到C43x40C的麻醉方式映射
        for i in range(1, 41):
            field_code = f"C43x{i:02d}C"
            known_mappings[field_code] = 'RC013'
        
        # 生成C43x01D到C43x40D的手术级别映射
        for i in range(1, 41):
            field_code = f"C43x{i:02d}D"
            known_mappings[field_code] = 'RC029'
        
        # 生成C43x01E到C43x40E的切口愈合等级映射
        for i in range(1, 41):
            field_code = f"C43x{i:02d}E"
            known_mappings[field_code] = 'RC014'
        
        # 5. 检查哪些字段在实际表中存在
        print(f"\n5. 检查字段在表中的存在情况...")
        
        existing_mappings = {}
        field_locations = {}
        
        for field_code, dict_type in known_mappings.items():
            for table, columns in all_fields.items():
                column_names = [col['Field'] for col in columns]
                if field_code in column_names:
                    existing_mappings[field_code] = dict_type
                    if field_code not in field_locations:
                        field_locations[field_code] = []
                    field_locations[field_code].append(table)
        
        print(f"找到存在的字段映射: {len(existing_mappings)}个")
        
        # 6. 按字典类型分组显示
        print(f"\n6. 按字典类型分组的字段映射:")
        
        dict_groups = {}
        for field_code, dict_type in existing_mappings.items():
            if dict_type not in dict_groups:
                dict_groups[dict_type] = []
            dict_groups[dict_type].append(field_code)
        
        for dict_type in sorted(dict_groups.keys()):
            fields = dict_groups[dict_type]
            print(f"\n{dict_type}: {len(fields)}个字段")
            for field in sorted(fields):
                tables = field_locations.get(field, [])
                print(f"  {field} (在表: {', '.join(tables)})")
        
        # 7. 生成规则创建SQL
        print(f"\n7. 生成规则创建SQL...")
        
        # 字典类型中文名称映射
        dict_names = {
            'RC001': '性别',
            'RC002': '婚姻状况',
            'RC003': '职业',
            'RC011': '病案质量',
            'RC013': '麻醉方式',
            'RC014': '切口愈合等级',
            'RC016': '死亡患者尸检',
            'RC019': '离院方式',
            'RC023': '科别',
            'RC026': '入院途径',
            'RC027': '入院病情',
            'RC028': '出院31天内再住院计划',
            'RC029': '手术级别',
            'RC030': 'ABO血型',
            'RC031': 'Rh血型',
            'RC032': '医疗付费方式',
            'RC033': '联系人关系',
            'RC035': '民族',
            'RC036': '省、自治区、直辖市',
            'RC037': '有无药物过敏',
            'RC038': '患者证件类别',
            'RC039': '判断代码'
        }
        
        # 生成字段中文名称
        field_names = {
            'A01': '民族',
            'A02': '婚姻状况',
            'A03': '职业',
            'A04': '科别',
            'A05': '科别',
            'A06': '科别',
            'A17': '离院方式',
            'A20': 'ABO血型',
            'A21': 'Rh血型',
            'A22': '病案质量',
            'A26': '入院途径',
            'A27': '入院病情',
            'A28': '出院31天内再住院计划',
            'A32': '医疗付费方式',
            'A37': '有无药物过敏',
            'A38': '患者证件类别',
            'A16': '死亡患者尸检',
            'C22x01C': '主要手术操作麻醉方式',
            'C22x01D': '主要手术操作级别',
            'C22x01E': '主要手术切口愈合等级'
        }
        
        # 为C43x系列字段生成名称
        for i in range(1, 41):
            field_names[f"C43x{i:02d}C"] = f"其他手术操作麻醉方式{i}"
            field_names[f"C43x{i:02d}D"] = f"其他手术操作级别{i}"
            field_names[f"C43x{i:02d}E"] = f"其他手术切口愈合等级{i}"
        
        # 生成SQL插入语句
        sql_statements = []
        
        for field_code, dict_type in sorted(existing_mappings.items()):
            field_name = field_names.get(field_code, field_code)
            dict_name = dict_names.get(dict_type, dict_type)
            rule_code = f"RULE_{field_code}_{dict_type}"
            description = f"{field_name}必须在{dict_type}字典范围内"
            tables = ','.join(field_locations.get(field_code, []))
            
            sql = f"""INSERT INTO kiro_qc_rule (
    rule_code, field_code, field_name, rule_type, description, 
    deduct_score, status, dict_types, source_tables, canonical_expr
) VALUES (
    '{rule_code}', '{field_code}', '{field_name}', 'value_check', '{description}',
    -1.0, 'active', '{dict_type}', '{tables}', '{field_code} IN (SELECT dict_code FROM sys_dict WHERE dict_type_code = \\'{dict_type}\\')'
) ON DUPLICATE KEY UPDATE
    field_name = VALUES(field_name),
    description = VALUES(description),
    dict_types = VALUES(dict_types),
    source_tables = VALUES(source_tables),
    canonical_expr = VALUES(canonical_expr);"""
            
            sql_statements.append(sql)
        
        # 8. 保存SQL到文件
        with open('generate_dict_validation_rules.sql', 'w', encoding='utf-8') as f:
            f.write("-- 自动生成的字典验证规则\n")
            f.write(f"-- 生成时间: {cursor.execute('SELECT NOW()') or cursor.fetchone()}\n")
            f.write(f"-- 总计: {len(sql_statements)}条规则\n\n")
            
            for sql in sql_statements:
                f.write(sql + "\n\n")
        
        print(f"已生成 {len(sql_statements)} 条字典验证规则")
        print(f"SQL文件已保存到: generate_dict_validation_rules.sql")
        
        # 9. 统计摘要
        print(f"\n9. 生成规则统计摘要:")
        for dict_type in sorted(dict_groups.keys()):
            dict_name = dict_names.get(dict_type, dict_type)
            field_count = len(dict_groups[dict_type])
            print(f"  {dict_type} ({dict_name}): {field_count}个字段规则")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    scan_all_fields_for_dict_rules()