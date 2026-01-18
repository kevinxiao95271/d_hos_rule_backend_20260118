#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

BASE_URL = "http://localhost:4101/api"

def test_service_status():
    """Test service status"""
    print("=== Testing Service Status ===")
    response = requests.get(f"{BASE_URL}/qc/status")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    return response.status_code == 200

def test_dictionary_apis():
    """Test dictionary APIs"""
    print("\n=== Testing Dictionary APIs ===")
    
    # Test dict types
    response = requests.get(f"{BASE_URL}/dict/types")
    print(f"Dict Types: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Dict Types Count: {len(data.get('data', []))}")
    
    # Test field search
    response = requests.get(f"{BASE_URL}/dict/fields/search?keyword=A18")
    print(f"Field Search: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        found_tables = data.get('data', {}).get('foundInTables', [])
        print(f"Found A18 fields in {len(found_tables)} locations")
    
    # Test dict query
    query_data = {
        "dictTypeCode": "RC001",
        "limit": 10
    }
    response = requests.post(f"{BASE_URL}/dict/query", json=query_data)
    print(f"Dict Query: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"RC001 entries: {len(data.get('data', []))}")
    
    return True

def test_rule_management():
    """Test rule management APIs"""
    print("\n=== Testing Rule Management ===")
    
    # Get all rules
    response = requests.get(f"{BASE_URL}/qc/rules")
    print(f"Get Rules: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        rules = data.get('data', [])
        print(f"Total rules: {len(rules)}")
        if rules:
            print(f"Sample rule: {rules[0].get('ruleName', 'N/A')}")
    
    # Search rules
    response = requests.get(f"{BASE_URL}/qc/rules/search?keyword=新生儿")
    print(f"Search Rules: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found rules with '新生儿': {len(data.get('data', []))}")
    
    return True

def test_quality_control():
    """Test quality control functionality"""
    print("\n=== Testing Quality Control ===")
    
    # Test single case check
    response = requests.post(f"{BASE_URL}/qc/check/single?a48=TEST001&a49=1")
    print(f"Single Case Check: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Single case result: {data.get('message', 'N/A')}")
    
    # Test batch check
    batch_data = {
        "startDate": "2023-01-01",
        "endDate": "2023-01-31",
        "batchType": "month"
    }
    response = requests.post(f"{BASE_URL}/qc/check/batch", json=batch_data)
    print(f"Batch Check: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Batch result: {data.get('message', 'N/A')}")
    
    return True

def main():
    """Run all tests"""
    print("Medical QC System - Full System Test")
    print("=" * 50)
    
    tests = [
        ("Service Status", test_service_status),
        ("Dictionary APIs", test_dictionary_apis),
        ("Rule Management", test_rule_management),
        ("Quality Control", test_quality_control)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASS" if result else "FAIL"))
        except Exception as e:
            print(f"Error in {test_name}: {e}")
            results.append((test_name, "ERROR"))
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    for test_name, status in results:
        print(f"{test_name:20} : {status}")
    
    # Check Swagger UI
    print(f"\nSwagger UI: http://localhost:4101/swagger-ui/index.html")
    print(f"API Base URL: {BASE_URL}")

if __name__ == "__main__":
    main()