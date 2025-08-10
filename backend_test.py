#!/usr/bin/env python3
"""
Backend API Testing for Coastal Oak Capital Application
Tests authentication endpoints and market data API
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://eb048c06-c22d-40a1-a540-40b6eb2c0ec7.preview.emergentagent.com/api"

# Test credentials
LP_PASSWORD = "DigitalDepression"
GP_PASSWORD = "NicoleWest0904!!"
INVALID_PASSWORD = "wrongpassword"

def test_basic_connectivity():
    """Test basic API connectivity"""
    print("\n=== Testing Basic Connectivity ===")
    
    try:
        # Test root endpoint
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        print(f"GET /api/ - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            if data.get("message") == "Hello World":
                print("✅ Root endpoint working correctly")
                return True
            else:
                print("❌ Root endpoint returned unexpected message")
                return False
        else:
            print(f"❌ Root endpoint failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Basic connectivity test failed: {str(e)}")
        return False

def test_status_endpoint():
    """Test status endpoint"""
    print("\n=== Testing Status Endpoint ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/status", timeout=10)
        print(f"GET /api/status - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            print("✅ Status endpoint working correctly")
            return True
        else:
            print(f"❌ Status endpoint failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Status endpoint test failed: {str(e)}")
        return False

def test_lp_authentication():
    """Test LP password authentication"""
    print("\n=== Testing LP Authentication ===")
    
    try:
        payload = {"password": LP_PASSWORD}
        response = requests.post(f"{BACKEND_URL}/auth", json=payload, timeout=10)
        print(f"POST /api/auth (LP) - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify response structure
            if (data.get("success") == True and 
                data.get("user_type") == "lp" and 
                data.get("token") is not None):
                print("✅ LP authentication working correctly")
                return True, data.get("token")
            else:
                print("❌ LP authentication response structure incorrect")
                return False, None
        else:
            print(f"❌ LP authentication failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ LP authentication test failed: {str(e)}")
        return False, None

def test_gp_authentication():
    """Test GP password authentication"""
    print("\n=== Testing GP Authentication ===")
    
    try:
        payload = {"password": GP_PASSWORD}
        response = requests.post(f"{BACKEND_URL}/auth", json=payload, timeout=10)
        print(f"POST /api/auth (GP) - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify response structure
            if (data.get("success") == True and 
                data.get("user_type") == "gp" and 
                data.get("token") is not None):
                print("✅ GP authentication working correctly")
                return True, data.get("token")
            else:
                print("❌ GP authentication response structure incorrect")
                return False, None
        else:
            print(f"❌ GP authentication failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ GP authentication test failed: {str(e)}")
        return False, None

def test_invalid_authentication():
    """Test authentication with invalid password"""
    print("\n=== Testing Invalid Authentication ===")
    
    try:
        payload = {"password": INVALID_PASSWORD}
        response = requests.post(f"{BACKEND_URL}/auth", json=payload, timeout=10)
        print(f"POST /api/auth (Invalid) - Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Invalid authentication correctly rejected with 401")
            return True
        else:
            print(f"❌ Invalid authentication should return 401, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid authentication test failed: {str(e)}")
        return False

def test_market_data():
    """Test market data endpoint"""
    print("\n=== Testing Market Data Endpoint ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/market-data", timeout=10)
        print(f"GET /api/market-data - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify required fields are present
            required_fields = ["fund_value", "nav", "irr", "multiple", "occupancy", "leverage", "last_update"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                # Verify data types
                numeric_fields = ["fund_value", "nav", "irr", "multiple", "occupancy", "leverage"]
                type_errors = []
                
                for field in numeric_fields:
                    if not isinstance(data[field], (int, float)):
                        type_errors.append(f"{field} should be numeric, got {type(data[field])}")
                
                if not type_errors:
                    print("✅ Market data endpoint working correctly")
                    return True
                else:
                    print("❌ Market data type errors:")
                    for error in type_errors:
                        print(f"  - {error}")
                    return False
            else:
                print(f"❌ Market data missing required fields: {missing_fields}")
                return False
        else:
            print(f"❌ Market data endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Market data test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all backend tests"""
    print("🚀 Starting Coastal Oak Capital Backend API Tests")
    print(f"Testing against: {BACKEND_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    results = {}
    
    # Test basic connectivity
    results['basic_connectivity'] = test_basic_connectivity()
    
    # Test status endpoint
    results['status_endpoint'] = test_status_endpoint()
    
    # Test authentication endpoints
    results['lp_auth'], lp_token = test_lp_authentication()
    results['gp_auth'], gp_token = test_gp_authentication()
    results['invalid_auth'] = test_invalid_authentication()
    
    # Test market data
    results['market_data'] = test_market_data()
    
    # Summary
    print("\n" + "="*50)
    print("🏁 TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the details above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)