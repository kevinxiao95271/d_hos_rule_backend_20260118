#!/usr/bin/env python3
import requests
import json
import pymysql

# API配置
BASE_URL = "http://localhost:4101"

# 数据库配置
db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def check_cross_defects_statistics():
    """检查Cross规则错误统计"""
    print("🔍 检查Cross规则错误统计")
    print("=" * 60)
    
    # 1. 检查数据库中的Cross规则状态
    print("\n1. 📊 数据库Cross规则状态...")
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # 统计活跃的Cross规则
        cursor.execute("SELECT COUNT(*) FROM kiro_qc_rule_cross WHERE status = 'active'")
        active_cross_rules = cursor.fetchone()[0]
        
        # 按类型统计
        cursor.execute("""
            SELECT cross_type, COUNT(*) 
            FROM kiro_qc_rule_cross 
            WHERE status = 'active' 
            GROUP BY cross_type 
            ORDER BY COUNT(*) DESC
        """)
        type_stats = cursor.fetchall()
        
        print(f"   ✅ 活跃Cross规则总数: {active_cross_rules}")
        print("   📋 按类型分布:")
        for cross_type, count in type_stats:
            print(f"     - {cross_type}: {count} 条")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   ❌ 数据库查询失败: {e}")
        return
    
    # 2. 测试单个病案的Cross规则检出
    print("\n2. 🧪 测试单个病案Cross规则检出...")
    test_cases = [
        {"a48": "2023001", "a49": "001"},
        {"a48": "19079841", "a49": "1"},
        {"a48": "445583", "a49": "1"}
    ]
    
    total_cross_defects = 0
    for i, test_case in enumerate(test_cases, 1):
        try:
            # 使用正确的API端点
            response = requests.post(f"{BASE_URL}/api/qc/check/single", 
                                   params=test_case, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                cross_defects = result.get('crossDefects', [])
                all_defects = result.get('allDefects', [])
                
                print(f"   病案 {test_case['a48']}_{test_case['a49']}:")
                print(f"     - Cross规则违规: {len(cross_defects)} 个")
                print(f"     - 总违规数: {len(all_defects)} 个")
                
                if cross_defects:
                    print(f"     - Cross规则详情:")
                    for j, defect in enumerate(cross_defects[:3], 1):
                        print(f"       {j}. {defect.get('ruleCode', 'N/A')}: {defect.get('ruleDescription', 'N/A')}")
                
                total_cross_defects += len(cross_defects)
                
            else:
                print(f"   ❌ 病案 {test_case['a48']}_{test_case['a49']} 检查失败: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 病案 {test_case['a48']}_{test_case['a49']} 检查异常: {e}")
    
    print(f"\n   📊 总计Cross规则违规: {total_cross_defects} 个")
    
    # 3. 测试批量质控的Cross规则统计
    print("\n3. 📈 测试批量质控Cross规则统计...")
    try:
        response = requests.post(f"{BASE_URL}/api/qc/check/batch", json={
            "periodType": "month",
            "year": 2023,
            "month": 1
        }, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 批量质控成功")
            print(f"   📋 基本统计:")
            print(f"     - 处理病案数: {result.get('caseCount', 0)}")
            print(f"     - 总违规数: {result.get('totalDefectCount', 0)}")
            print(f"     - 平均得分: {result.get('avgScore', 0)}")
            
            # 检查是否有Cross规则统计
            if 'crossDefectCount' in result:
                print(f"     - Cross规则违规总数: {result.get('crossDefectCount', 0)}")
            else:
                print(f"     ⚠️  批量结果中缺少Cross规则统计")
                
        else:
            print(f"   ❌ 批量质控失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 批量质控异常: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Cross规则错误统计检查完成")
    print("=" * 60)

if __name__ == "__main__":
    check_cross_defects_statistics()