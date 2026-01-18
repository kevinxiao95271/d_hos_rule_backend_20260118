#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dictionary and Field Search API Test Script
Tests the new dictionary query and field search endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:4101"

def print_section(title):
    """Print a section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_dict_query():
    """Test dictionary query endpoint"""
    print_section("TEST 1: Query Dictionary - Gender Codes (RC001)")
    
    url = f"{BASE_URL}/api/dict/query"
    payload = {
        "dictTypeCode": "RC001",
        "keyword": ""
    }
    
    print(f"Request: POST {url}")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print(f"\n✓ Found {len(data)} gender codes")
        else:
            print(f"✗ Error: {response.text}")
    except Exception as e:
        print(f"✗ Exception: {str(e)}")

def test_dict_query_with_keyword():
    """Test dictionary query with keyword"""
    print_section("TEST 2: Query Dictionary with Keyword - Disease Codes")
    
    url = f"{BASE_URL}/api/dict/query"
    payload = {
        "dictTypeCode": "RCJBBM",
        "keyword": "肺炎"
    }
    
    print(f"Request: POST {url}")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response (first 5 results): {json.dumps(data[:5] if len(data) > 5 else data, ensure_ascii=False, indent=2)}")
            print(f"\n✓ Found {len(data)} disease codes containing '肺炎'")
        else:
            print(f"✗ Error: {response.text}")
    except Exception as e:
        print(f"✗ Exception: {str(e)}")

def test_dict_types():
    """Test get all dictionary types"""
    print_section("TEST 3: Get All Dictionary Types")
    
    url = f"{BASE_URL}/api/dict/types"
    
    print(f"Request: GET {url}")
    
    try:
        response = requests.get(url)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response (first 10 types): {json.dumps(data[:10] if len(data) > 10 else data, ensure_ascii=False, indent=2)}")
            print(f"\n✓ Found {len(data)} dictionary types")
        else:
            print(f"✗ Error: {response.text}")
    except Exception as e:
        print(f"✗ Exception: {str(e)}")

def test_field_search():
    """Test field search across tables"""
    print_section("TEST 4: Search Field - A18x01 (新生儿出生体重)")
    
    url = f"{BASE_URL}/api/dict/field/search"
    params = {"fieldCode": "A18x01"}
    
    print(f"Request: GET {url}?fieldCode=A18x01")
    
    try:
        response = requests.get(url, params=params)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, ensure_ascii=False, indent=2)}")
            if data:
                print(f"\n✓ Field A18x01 found in table: {data.get('tableName')}")
            else:
                print(f"\n✗ Field A18x01 not found in any table")
        else:
            print(f"✗ Error: {response.text}")
    except Exception as e:
        print(f"✗ Exception: {str(e)}")

def test_field_search_a48():
    """Test field search for A48"""
    print_section("TEST 5: Search Field - A48 (病案号)")
    
    url = f"{BASE_URL}/api/dict/field/search"
    params = {"fieldCode": "A48"}
    
    print(f"Request: GET {url}?fieldCode=A48")
    
    try:
        response = requests.get(url, params=params)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, ensure_ascii=False, indent=2)}")
            if data:
                print(f"\n✓ Field A48 found in table: {data.get('tableName')}")
            else:
                print(f"\n✗ Field A48 not found in any table")
        else:
            print(f"✗ Error: {response.text}")
    except Exception as e:
        print(f"✗ Exception: {str(e)}")

def test_validate_field_value():
    """Test field value validation"""
    print_section("TEST 6: Validate Field Value - Gender")
    
    url = f"{BASE_URL}/api/dict/validate"
    payload = {
        "dictTypeCode": "RC001",
        "value": "1"
    }
    
    print(f"Request: POST {url}")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print(f"\n✓ Validation result: {data}")
        else:
            print(f"✗ Error: {response.text}")
    except Exception as e:
        print(f"✗ Exception: {str(e)}")

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  Dictionary and Field Search API Test Suite")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Test dictionary queries
    test_dict_query()
    test_dict_query_with_keyword()
    test_dict_types()
    
    # Test field search
    test_field_search()
    test_field_search_a48()
    
    # Test field value validation
    test_validate_field_value()
    
    print("\n" + "="*80)
    print("  All Tests Completed")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
