#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_service_status():
    """Test if the backend service is running"""
    try:
        # Test service status
        response = requests.get('http://localhost:4101/api/qc/status')
        print(f"Service Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        
        # Test dictionary API
        print("\n=== Testing Dictionary API ===")
        dict_response = requests.get('http://localhost:4101/api/dict/fields/search?keyword=A18')
        print(f"Dict Field Search Status: {dict_response.status_code}")
        if dict_response.status_code == 200:
            print(f"Dict Response: {dict_response.json()}")
        
        # Test dict types
        dict_types_response = requests.get('http://localhost:4101/api/dict/types')
        print(f"Dict Types Status: {dict_types_response.status_code}")
        if dict_types_response.status_code == 200:
            data = dict_types_response.json()
            print(f"Dict Types Count: {len(data.get('data', []))}")
            print(f"Sample Dict Types: {data.get('data', [])[:5]}")
        
    except Exception as e:
        print(f"Error testing service: {e}")

if __name__ == "__main__":
    test_service_status()