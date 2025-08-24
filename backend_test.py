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
BACKEND_URL = "https://realestate-fund.preview.emergentagent.com/api"

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

def test_excel_summary():
    """Test Excel summary endpoint with comprehensive KPIs and external data integration"""
    print("\n=== Testing Excel Summary Endpoint ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/excel/summary", timeout=15)
        print(f"GET /api/excel/summary - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            # Verify top-level structure
            required_top_level = ["as_of_date", "aum", "deals", "kpis"]
            missing_fields = [field for field in required_top_level if field not in data]
            
            if missing_fields:
                print(f"❌ Excel summary missing required top-level fields: {missing_fields}")
                return False
            
            # Verify KPIs structure
            kpis = data.get("kpis", {})
            required_kpi_sections = ["fund", "risk", "pipeline"]
            missing_kpi_sections = [section for section in required_kpi_sections if section not in kpis]
            
            if missing_kpi_sections:
                print(f"❌ Excel summary missing KPI sections: {missing_kpi_sections}")
                return False
            
            # Verify fund KPIs
            fund_kpis = kpis.get("fund", {})
            required_fund_fields = ["nav", "gross_irr", "net_irr", "gross_moic", "net_moic", "tvpi", "dpi", "rvpi", "aum"]
            missing_fund_fields = [field for field in required_fund_fields if field not in fund_kpis]
            
            if missing_fund_fields:
                print(f"❌ Excel summary missing fund KPI fields: {missing_fund_fields}")
                return False
            
            # Verify risk KPIs
            risk_kpis = kpis.get("risk", {})
            required_risk_fields = ["wa_ltv", "wa_dscr", "interest_coverage"]
            missing_risk_fields = [field for field in required_risk_fields if field not in risk_kpis]
            
            if missing_risk_fields:
                print(f"❌ Excel summary missing risk KPI fields: {missing_risk_fields}")
                return False
            
            # Verify pipeline KPIs
            pipeline_kpis = kpis.get("pipeline", {})
            required_pipeline_fields = ["active_deals_count", "pipeline_deals_count", "exited_deals_count"]
            missing_pipeline_fields = [field for field in required_pipeline_fields if field not in pipeline_kpis]
            
            if missing_pipeline_fields:
                print(f"❌ Excel summary missing pipeline KPI fields: {missing_pipeline_fields}")
                return False
            
            # Verify deals data
            deals = data.get("deals", [])
            if not deals:
                print("❌ Excel summary has no deals data")
                return False
            
            # Check deal structure
            first_deal = deals[0]
            required_deal_fields = ["id", "name", "status", "market", "strategy"]
            missing_deal_fields = [field for field in required_deal_fields if field not in first_deal]
            
            if missing_deal_fields:
                print(f"❌ Excel summary deals missing required fields: {missing_deal_fields}")
                return False
            
            # Verify data freshness
            as_of_date = data.get("as_of_date")
            if not as_of_date:
                print("❌ Excel summary missing as_of_date")
                return False
            
            print(f"✅ Excel summary endpoint working correctly")
            print(f"  - Found {len(deals)} deals")
            print(f"  - Active deals: {pipeline_kpis.get('active_deals_count', 0)}")
            print(f"  - Pipeline deals: {pipeline_kpis.get('pipeline_deals_count', 0)}")
            print(f"  - Fund AUM: ${data.get('aum', 0):,.0f}")
            print(f"  - Net IRR: {fund_kpis.get('net_irr', 0):.2f}%")
            print(f"  - Data as of: {as_of_date}")
            return True
            
        else:
            print(f"❌ Excel summary endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Excel summary test failed: {str(e)}")
        return False

def test_excel_data():
    """Test Excel data endpoint for frontend grid display"""
    print("\n=== Testing Excel Data Endpoint ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/excel/data", timeout=10)
        print(f"GET /api/excel/data - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            # Verify structure
            required_fields = ["rows", "as_of_date", "last_updated"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Excel data missing required fields: {missing_fields}")
                return False
            
            # Verify rows data
            rows = data.get("rows", [])
            if not rows:
                print("❌ Excel data has no rows")
                return False
            
            # Check row structure
            first_row = rows[0]
            required_row_fields = ["name", "status", "market", "strategy"]
            missing_row_fields = [field for field in required_row_fields if field not in first_row]
            
            if missing_row_fields:
                print(f"❌ Excel data rows missing required fields: {missing_row_fields}")
                return False
            
            print(f"✅ Excel data endpoint working correctly")
            print(f"  - Found {len(rows)} data rows")
            print(f"  - Last updated: {data.get('last_updated')}")
            return True
            
        else:
            print(f"❌ Excel data endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Excel data test failed: {str(e)}")
        return False

def test_excel_deals():
    """Test Excel deals endpoint for deals-specific analytics"""
    print("\n=== Testing Excel Deals Endpoint ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/excel/deals", timeout=10)
        print(f"GET /api/excel/deals - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            # Verify structure
            required_fields = ["deals", "total_deals", "active_count", "pipeline_count", "exited_count", "as_of_date"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Excel deals missing required fields: {missing_fields}")
                return False
            
            # Verify deals data
            deals = data.get("deals", [])
            if not deals:
                print("❌ Excel deals has no deals data")
                return False
            
            # Verify counts make sense
            total_deals = data.get("total_deals", 0)
            active_count = data.get("active_count", 0)
            pipeline_count = data.get("pipeline_count", 0)
            exited_count = data.get("exited_count", 0)
            
            if len(deals) != total_deals:
                print(f"❌ Excel deals count mismatch: {len(deals)} deals vs {total_deals} total")
                return False
            
            print(f"✅ Excel deals endpoint working correctly")
            print(f"  - Total deals: {total_deals}")
            print(f"  - Active: {active_count}, Pipeline: {pipeline_count}, Exited: {exited_count}")
            print(f"  - Data as of: {data.get('as_of_date')}")
            return True
            
        else:
            print(f"❌ Excel deals endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Excel deals test failed: {str(e)}")
        return False

def test_excel_generate():
    """Test Excel generate endpoint for GP export functionality"""
    print("\n=== Testing Excel Generate Endpoint ===")
    
    try:
        response = requests.post(f"{BACKEND_URL}/excel/generate", timeout=15)
        print(f"POST /api/excel/generate - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            # Verify structure
            required_fields = ["export_ready", "filename", "data", "size_mb"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Excel generate missing required fields: {missing_fields}")
                return False
            
            # Verify export data structure
            export_data = data.get("data", {})
            required_export_fields = ["summary", "external_data", "generated_at", "data_sources"]
            missing_export_fields = [field for field in required_export_fields if field not in export_data]
            
            if missing_export_fields:
                print(f"❌ Excel generate export data missing fields: {missing_export_fields}")
                return False
            
            # Verify external data integration
            external_data = export_data.get("external_data", {})
            if "treasury" not in external_data or "cpi" not in external_data:
                print("❌ Excel generate missing external data integration (treasury/cpi)")
                return False
            
            # Verify data sources
            data_sources = export_data.get("data_sources", [])
            expected_sources = ["Federal Reserve Economic Data (FRED)", "Bureau of Labor Statistics (BLS)"]
            has_expected_sources = any(source in str(data_sources) for source in expected_sources)
            
            if not has_expected_sources:
                print("❌ Excel generate missing expected external data sources")
                return False
            
            print(f"✅ Excel generate endpoint working correctly")
            print(f"  - Export ready: {data.get('export_ready')}")
            print(f"  - Filename: {data.get('filename')}")
            print(f"  - Size: {data.get('size_mb'):.2f} MB")
            print(f"  - External data sources: {len(data_sources)}")
            print(f"  - Generated at: {export_data.get('generated_at')}")
            return True
            
        else:
            print(f"❌ Excel generate endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Excel generate test failed: {str(e)}")
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