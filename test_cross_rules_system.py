#!/usr/bin/env python3
import requests
import json
import time

# API配置
BASE_URL = "http://localhost:8080"

def test_cross_rules_system():
    """测试Cross规则系统"""
    print("🧪 测试Cross规则系统")
    print("=" * 60)
    
    # 1. 测试单个病案质控（包含Cross规则）
    print("\n1. 测试单个病案质控...")
    try:
        response = requests.post(f"{BASE_URL}/api/qc/check", json={
            "a48": "2023001",
            "a49": "001"
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 单病案质控成功")
            print(f"   病案键: {result.get('mrKey')}")
            print(f"   总违规数: {result.get('defectCount', 0)}")
            print(f"   总扣分: {result.get('totalDeduct', 0)}")
            print(f"   最终得分: {result.get('finalScore', 0)}")
            
            # 检查Cross规则违规
            cross_defects = result.get('crossDefects', [])
            print(f"   Cross规则违规数: {len(cross_defects)}")
            
            if cross_defects:
                print("   Cross规则违规详情:")
                for i, defect in enumerate(cross_defects[:3]):  # 只显示前3个
                    print(f"     {i+1}. {defect.get('ruleCode')}: {defect.get('ruleDescription')}")
            
            # 检查普通违规
            all_defects = result.get('allDefects', [])
            normal_defects = [d for d in all_defects if not d.get('ruleCode', '').startswith('RULE_CROSS_')]
            print(f"   普通规则违规数: {len(normal_defects)}")
            
        else:
            print(f"❌ 单病案质控失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 单病案质控异常: {e}")
    
    # 2. 测试Cross规则数量统计
    print("\n2. 检查Cross规则数量...")
    try:
        # 这里我们直接查询数据库来验证
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
        
        # 统计Cross规则
        cursor.execute("SELECT COUNT(*) FROM kiro_qc_rule_cross WHERE status = 'active'")
        active_cross_rules = cursor.fetchone()[0]
        
        cursor.execute("SELECT cross_type, COUNT(*) FROM kiro_qc_rule_cross WHERE status = 'active' GROUP BY cross_type")
        type_stats = cursor.fetchall()
        
        print(f"✅ 活跃Cross规则总数: {active_cross_rules}")
        print("   按类型分布:")
        for cross_type, count in type_stats:
            print(f"     {cross_type}: {count} 条")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 查询Cross规则失败: {e}")
    
    # 3. 测试批量质控性能
    print("\n3. 测试批量质控性能...")
    try:
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/api/qc/check/multiple", json={
            "year": 2023,
            "month": 1,
            "limit": 5  # 只测试5个病案
        }, timeout=60)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            case_count = result.get('caseCount', 0)
            total_defects = result.get('totalDefects', 0)
            avg_score = result.get('avgScore', 0)
            
            print(f"✅ 批量质控成功")
            print(f"   处理病案数: {case_count}")
            print(f"   总违规数: {total_defects}")
            print(f"   平均得分: {avg_score}")
            print(f"   总耗时: {elapsed:.2f}秒")
            print(f"   平均耗时: {elapsed/case_count:.2f}秒/病案")
            
            # 检查是否有Cross规则违规
            results = result.get('results', [])
            cross_violations_count = 0
            for case_result in results:
                cross_defects = case_result.get('crossDefects', [])
                cross_violations_count += len(cross_defects)
            
            print(f"   Cross规则违规总数: {cross_violations_count}")
            
        else:
            print(f"❌ 批量质控失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 批量质控异常: {e}")
    
    # 4. 性能评估
    print("\n4. 性能评估...")
    if 'elapsed' in locals() and 'case_count' in locals() and case_count > 0:
        avg_time_per_case = elapsed / case_count
        if avg_time_per_case < 2.0:
            print("✅ 性能良好 (< 2秒/病案)")
        elif avg_time_per_case < 5.0:
            print("⚠️  性能一般 (2-5秒/病案)")
        else:
            print("❌ 性能较差 (> 5秒/病案)")
            print("   建议启用性能优化措施")
    
    print("\n" + "=" * 60)
    print("🎯 Cross规则系统测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_cross_rules_system()