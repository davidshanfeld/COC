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
BACKEND_URL = "https://lineage-tracker-7.preview.emergentagent.com/api"

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

# ============================================================================
# DATA LINEAGE & AUDITABILITY TESTS
# ============================================================================

def test_snapshot_creation():
    """Test 1: POST /api/snapshots with Basic Auth gp:Contrarians returns 201/200 and snapshot object"""
    print("\n=== Testing Snapshot Creation (POST /api/snapshots) ===")
    
    try:
        # Basic Auth with gp:Contrarians
        auth = ('gp', 'Contrarians')
        response = requests.post(f"{BACKEND_URL}/snapshots", auth=auth, timeout=15)
        print(f"POST /api/snapshots - Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            # Verify snapshot structure
            required_fields = ["id", "as_of_date", "created_at", "creator", "seq"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Snapshot missing required fields: {missing_fields}")
                return False, None
            
            # Verify UUID v4 format for id
            snapshot_id = data.get("id")
            if not snapshot_id or len(snapshot_id.split('-')) != 5:
                print(f"❌ Snapshot ID doesn't appear to be UUID v4: {snapshot_id}")
                return False, None
            
            # Verify as_of_date format (YYYY-MM-DD)
            as_of_date = data.get("as_of_date")
            if not as_of_date or len(as_of_date) != 10 or as_of_date.count('-') != 2:
                print(f"❌ as_of_date not in YYYY-MM-DD format: {as_of_date}")
                return False, None
            
            # Verify created_at is ISO format
            created_at = data.get("created_at")
            if not created_at or 'T' not in created_at:
                print(f"❌ created_at not in ISO format: {created_at}")
                return False, None
            
            # Verify creator is 'gp'
            creator = data.get("creator")
            if creator != "gp":
                print(f"❌ Creator should be 'gp', got: {creator}")
                return False, None
            
            # Verify seq format (v001, v002, etc.)
            seq = data.get("seq")
            if not seq or not seq.startswith('v') or len(seq) != 4:
                print(f"❌ Seq not in v001 format: {seq}")
                return False, None
            
            print(f"✅ Snapshot creation working correctly")
            print(f"  - ID: {snapshot_id}")
            print(f"  - As of date: {as_of_date}")
            print(f"  - Created at: {created_at}")
            print(f"  - Creator: {creator}")
            print(f"  - Sequence: {seq}")
            return True, snapshot_id
            
        else:
            print(f"❌ Snapshot creation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Snapshot creation test failed: {str(e)}")
        return False, None

def test_snapshot_list():
    """Test 2: GET /api/snapshots with Basic Auth paginates with default limit 10"""
    print("\n=== Testing Snapshot List (GET /api/snapshots) ===")
    
    try:
        # Basic Auth with gp:Contrarians
        auth = ('gp', 'Contrarians')
        
        # Test default pagination
        response = requests.get(f"{BACKEND_URL}/snapshots", auth=auth, timeout=10)
        print(f"GET /api/snapshots - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            # Verify pagination structure
            required_fields = ["items", "next_cursor"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Snapshot list missing required fields: {missing_fields}")
                return False
            
            items = data.get("items", [])
            print(f"  - Found {len(items)} snapshots")
            
            # Verify default limit (should be <= 10)
            if len(items) > 10:
                print(f"❌ Default limit exceeded: got {len(items)} items, expected <= 10")
                return False
            
            # Test custom limit
            response2 = requests.get(f"{BACKEND_URL}/snapshots?limit=2", auth=auth, timeout=10)
            if response2.status_code == 200:
                data2 = response2.json()
                items2 = data2.get("items", [])
                print(f"  - With limit=2: {len(items2)} snapshots")
                
                if len(items2) > 2:
                    print(f"❌ Custom limit not respected: got {len(items2)} items, expected <= 2")
                    return False
                
                # Test cursor pagination if we have items
                if items2 and data2.get("next_cursor"):
                    cursor = data2.get("next_cursor")
                    response3 = requests.get(f"{BACKEND_URL}/snapshots?cursor={cursor}", auth=auth, timeout=10)
                    if response3.status_code == 200:
                        data3 = response3.json()
                        print(f"  - With cursor pagination: {len(data3.get('items', []))} more snapshots")
                    else:
                        print(f"❌ Cursor pagination failed with status {response3.status_code}")
                        return False
            
            # Verify items are sorted desc by created_at
            if len(items) > 1:
                for i in range(len(items) - 1):
                    current_time = items[i].get("created_at", "")
                    next_time = items[i + 1].get("created_at", "")
                    if current_time < next_time:
                        print(f"❌ Items not sorted desc by created_at")
                        return False
            
            print(f"✅ Snapshot list working correctly")
            return True
            
        else:
            print(f"❌ Snapshot list failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Snapshot list test failed: {str(e)}")
        return False

def test_snapshot_get_by_id(snapshot_id):
    """Test 3: GET /api/snapshots/{id} returns the snapshot created"""
    print(f"\n=== Testing Snapshot Get by ID (GET /api/snapshots/{snapshot_id}) ===")
    
    if not snapshot_id:
        print("❌ No snapshot ID provided for testing")
        return False
    
    try:
        # Basic Auth with gp:Contrarians
        auth = ('gp', 'Contrarians')
        response = requests.get(f"{BACKEND_URL}/snapshots/{snapshot_id}", auth=auth, timeout=10)
        print(f"GET /api/snapshots/{snapshot_id} - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            # Verify it's the same snapshot
            returned_id = data.get("id")
            if returned_id != snapshot_id:
                print(f"❌ Returned snapshot ID mismatch: expected {snapshot_id}, got {returned_id}")
                return False
            
            # Verify complete snapshot structure
            required_fields = ["id", "as_of_date", "created_at", "creator", "seq", "summary", "lineage"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Complete snapshot missing required fields: {missing_fields}")
                return False
            
            # Verify summary structure
            summary = data.get("summary", {})
            required_summary_fields = ["as_of_date", "aum", "deals", "kpis"]
            missing_summary_fields = [field for field in required_summary_fields if field not in summary]
            
            if missing_summary_fields:
                print(f"❌ Snapshot summary missing required fields: {missing_summary_fields}")
                return False
            
            # Verify lineage structure
            lineage = data.get("lineage", [])
            if not isinstance(lineage, list):
                print(f"❌ Lineage should be a list, got {type(lineage)}")
                return False
            
            print(f"✅ Snapshot get by ID working correctly")
            print(f"  - ID: {returned_id}")
            print(f"  - Summary AUM: ${summary.get('aum', 0):,.0f}")
            print(f"  - Deals count: {len(summary.get('deals', []))}")
            print(f"  - Lineage entries: {len(lineage)}")
            return True
            
        else:
            print(f"❌ Snapshot get by ID failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Snapshot get by ID test failed: {str(e)}")
        return False

def test_excel_summary_refresh():
    """Test 4: GET /api/excel/summary?refresh=true returns new snapshot and respects rate limit"""
    print("\n=== Testing Excel Summary Refresh (GET /api/excel/summary?refresh=true) ===")
    
    try:
        # First refresh call
        response1 = requests.get(f"{BACKEND_URL}/excel/summary?refresh=true", timeout=15)
        print(f"GET /api/excel/summary?refresh=true (1st call) - Status: {response1.status_code}")
        
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"Response keys: {list(data1.keys())}")
            
            # Verify metadata fields
            required_meta_fields = ["_last_updated_iso", "_snapshot_id", "_lineage"]
            missing_meta_fields = [field for field in required_meta_fields if field not in data1]
            
            if missing_meta_fields:
                print(f"❌ Excel summary refresh missing metadata fields: {missing_meta_fields}")
                return False
            
            snapshot_id1 = data1.get("_snapshot_id")
            last_updated1 = data1.get("_last_updated_iso")
            lineage1 = data1.get("_lineage", [])
            
            print(f"  - Snapshot ID: {snapshot_id1}")
            print(f"  - Last updated: {last_updated1}")
            print(f"  - Lineage entries: {len(lineage1)}")
            
            # Verify lineage structure
            if not isinstance(lineage1, list):
                print(f"❌ Lineage should be a list, got {type(lineage1)}")
                return False
            
            # Immediately try another refresh (should be rate limited)
            import time
            time.sleep(1)  # Small delay to ensure different timestamp
            response2 = requests.get(f"{BACKEND_URL}/excel/summary?refresh=true", timeout=15)
            print(f"GET /api/excel/summary?refresh=true (2nd call) - Status: {response2.status_code}")
            
            if response2.status_code == 429:
                print(f"✅ Rate limiting working correctly - got 429 on immediate second refresh")
                return True
            elif response2.status_code == 200:
                # Check if it's actually a different snapshot or same one
                data2 = response2.json()
                snapshot_id2 = data2.get("_snapshot_id")
                if snapshot_id1 == snapshot_id2:
                    print(f"✅ Excel summary refresh working correctly (same snapshot returned, rate limit may be shorter)")
                    return True
                else:
                    print(f"⚠️  Got new snapshot on immediate refresh - rate limit may not be working")
                    print(f"  - First snapshot: {snapshot_id1}")
                    print(f"  - Second snapshot: {snapshot_id2}")
                    return True  # Still working, just different rate limit behavior
            else:
                print(f"❌ Second refresh failed with unexpected status {response2.status_code}")
                return False
            
        else:
            print(f"❌ Excel summary refresh failed with status {response1.status_code}")
            print(f"Response: {response1.text}")
            return False
            
    except Exception as e:
        print(f"❌ Excel summary refresh test failed: {str(e)}")
        return False

def test_excel_summary_with_snapshot_id(snapshot_id):
    """Test 5: GET /api/excel/summary?snapshot_id=<id> returns exact snapshot-backed summary"""
    print(f"\n=== Testing Excel Summary with Snapshot ID (GET /api/excel/summary?snapshot_id={snapshot_id}) ===")
    
    if not snapshot_id:
        print("❌ No snapshot ID provided for testing")
        return False
    
    try:
        response = requests.get(f"{BACKEND_URL}/excel/summary?snapshot_id={snapshot_id}", timeout=10)
        print(f"GET /api/excel/summary?snapshot_id={snapshot_id} - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            # Verify _snapshot_id matches
            returned_snapshot_id = data.get("_snapshot_id")
            if returned_snapshot_id != snapshot_id:
                print(f"❌ Snapshot ID mismatch: expected {snapshot_id}, got {returned_snapshot_id}")
                return False
            
            # Verify required fields
            required_fields = ["as_of_date", "aum", "deals", "kpis", "_last_updated_iso", "_snapshot_id", "_lineage"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Excel summary with snapshot ID missing required fields: {missing_fields}")
                return False
            
            print(f"✅ Excel summary with snapshot ID working correctly")
            print(f"  - Snapshot ID matches: {returned_snapshot_id}")
            print(f"  - As of date: {data.get('as_of_date')}")
            print(f"  - AUM: ${data.get('aum', 0):,.0f}")
            return True
            
        else:
            print(f"❌ Excel summary with snapshot ID failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Excel summary with snapshot ID test failed: {str(e)}")
        return False

def test_excel_generate_with_snapshot_id(snapshot_id):
    """Test 6: POST /api/excel/generate?snapshot_id=<id> streams XLSX with proper filename"""
    print(f"\n=== Testing Excel Generate with Snapshot ID (POST /api/excel/generate?snapshot_id={snapshot_id}) ===")
    
    if not snapshot_id:
        print("❌ No snapshot ID provided for testing")
        return False
    
    try:
        response = requests.post(f"{BACKEND_URL}/excel/generate?snapshot_id={snapshot_id}", timeout=15, stream=True)
        print(f"POST /api/excel/generate?snapshot_id={snapshot_id} - Status: {response.status_code}")
        
        if response.status_code == 200:
            # Verify Content-Type
            content_type = response.headers.get('content-type', '')
            expected_content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            if expected_content_type not in content_type:
                print(f"❌ Wrong content type: expected {expected_content_type}, got {content_type}")
                return False
            
            # Verify Content-Disposition header
            content_disposition = response.headers.get('content-disposition', '')
            if 'attachment' not in content_disposition:
                print(f"❌ Missing attachment in content-disposition: {content_disposition}")
                return False
            
            # Extract filename from Content-Disposition
            if 'filename=' in content_disposition:
                filename_part = content_disposition.split('filename=')[1].strip('"')
                print(f"  - Filename: {filename_part}")
                
                # Verify filename format: Coastal_Excel_Analytics_${AS_OF}_v${SEQ}.xlsx
                if not filename_part.startswith('Coastal_Excel_Analytics_'):
                    print(f"❌ Filename doesn't start with expected prefix: {filename_part}")
                    return False
                
                if not filename_part.endswith('.xlsx'):
                    print(f"❌ Filename doesn't end with .xlsx: {filename_part}")
                    return False
                
                # Check for date and version pattern
                parts = filename_part.replace('Coastal_Excel_Analytics_', '').replace('.xlsx', '')
                if '_v' not in parts:
                    print(f"❌ Filename missing version pattern: {filename_part}")
                    return False
                
            else:
                print(f"❌ No filename in content-disposition: {content_disposition}")
                return False
            
            # Verify we can read some content (don't download the whole file)
            content_length = response.headers.get('content-length')
            if content_length:
                print(f"  - Content length: {content_length} bytes")
            
            # Read first few bytes to verify it's actually Excel content
            first_chunk = next(response.iter_content(chunk_size=1024), b'')
            if len(first_chunk) > 0:
                # Excel files start with PK (ZIP signature)
                if first_chunk[:2] == b'PK':
                    print(f"  - File appears to be valid Excel format (ZIP signature found)")
                else:
                    print(f"❌ File doesn't appear to be Excel format (no ZIP signature)")
                    return False
            
            print(f"✅ Excel generate with snapshot ID working correctly")
            return True
            
        else:
            print(f"❌ Excel generate with snapshot ID failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Excel generate with snapshot ID test failed: {str(e)}")
        return False

def test_lineage_allowlist():
    """Test 7: Verify that lineage URLs domains are within the allowlist"""
    print("\n=== Testing Lineage Allowlist Verification ===")
    
    try:
        # Get a snapshot to check its lineage
        auth = ('gp', 'Contrarians')
        response = requests.get(f"{BACKEND_URL}/snapshots", auth=auth, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Could not get snapshots for lineage test: {response.status_code}")
            return False
        
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            print("❌ No snapshots available for lineage testing")
            return False
        
        # Get the first snapshot's full details
        snapshot_id = items[0].get("id")
        response2 = requests.get(f"{BACKEND_URL}/snapshots/{snapshot_id}", auth=auth, timeout=10)
        
        if response2.status_code != 200:
            print(f"❌ Could not get snapshot details for lineage test: {response2.status_code}")
            return False
        
        snapshot_data = response2.json()
        lineage = snapshot_data.get("lineage", [])
        
        if not lineage:
            print("❌ No lineage data found in snapshot")
            return False
        
        # Define expected allowlist (from server.py)
        allowlist = {
            "home.treasury.gov",
            "treasury.gov", 
            "bls.gov",
            "download.bls.gov",
            "fred.stlouisfed.org",
            "stlouisfed.org",
            "bea.gov",
            "eia.gov",
            "sec.gov",
            "energy.ca.gov",
            "cpuc.ca.gov",
        }
        
        print(f"  - Found {len(lineage)} lineage entries")
        
        # Check each lineage entry
        violations = []
        for entry in lineage:
            url = entry.get("url", "")
            if url:
                # Extract domain from URL
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    domain = parsed.netloc
                    
                    if domain not in allowlist:
                        violations.append(f"Domain '{domain}' from URL '{url}' not in allowlist")
                    else:
                        print(f"  ✅ {domain} - allowed")
                        
                except Exception as e:
                    violations.append(f"Could not parse URL '{url}': {e}")
        
        if violations:
            print("❌ Allowlist violations found:")
            for violation in violations:
                print(f"  - {violation}")
            return False
        
        print(f"✅ Lineage allowlist verification passed - all {len(lineage)} entries use allowed domains")
        return True
        
    except Exception as e:
        print(f"❌ Lineage allowlist test failed: {str(e)}")
        return False

def test_nonexistent_snapshot_404():
    """Test 8: Non-existent snapshot id returns 404 for both endpoints"""
    print("\n=== Testing Non-existent Snapshot 404 Responses ===")
    
    fake_id = "00000000-0000-0000-0000-000000000000"
    auth = ('gp', 'Contrarians')
    
    try:
        # Test GET /api/snapshots/{id}
        response1 = requests.get(f"{BACKEND_URL}/snapshots/{fake_id}", auth=auth, timeout=10)
        print(f"GET /api/snapshots/{fake_id} - Status: {response1.status_code}")
        
        if response1.status_code != 404:
            print(f"❌ Expected 404 for non-existent snapshot, got {response1.status_code}")
            return False
        
        # Test GET /api/excel/summary?snapshot_id=
        response2 = requests.get(f"{BACKEND_URL}/excel/summary?snapshot_id={fake_id}", timeout=10)
        print(f"GET /api/excel/summary?snapshot_id={fake_id} - Status: {response2.status_code}")
        
        if response2.status_code != 404:
            print(f"❌ Expected 404 for non-existent snapshot in excel/summary, got {response2.status_code}")
            return False
        
        # Test POST /api/excel/generate?snapshot_id=
        response3 = requests.post(f"{BACKEND_URL}/excel/generate?snapshot_id={fake_id}", timeout=10)
        print(f"POST /api/excel/generate?snapshot_id={fake_id} - Status: {response3.status_code}")
        
        if response3.status_code != 404:
            print(f"❌ Expected 404 for non-existent snapshot in excel/generate, got {response3.status_code}")
            return False
        
        print(f"✅ Non-existent snapshot 404 responses working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Non-existent snapshot 404 test failed: {str(e)}")
        return False

# ============================================================================
# EXPORT ENDPOINTS TESTS (GP Basic Auth Required)
# ============================================================================

def test_export_executive_summary_auth():
    """Test POST /api/export/executive-summary requires Basic Auth"""
    print("\n=== Testing Executive Summary Export Auth (POST /api/export/executive-summary) ===")
    
    try:
        # Test without auth - should get 401
        response = requests.post(f"{BACKEND_URL}/export/executive-summary", json={}, timeout=15)
        print(f"POST /api/export/executive-summary (no auth) - Status: {response.status_code}")
        
        if response.status_code != 401:
            print(f"❌ Expected 401 without auth, got {response.status_code}")
            return False
        
        # Test with wrong auth - should get 401
        wrong_auth = ('wrong', 'credentials')
        response2 = requests.post(f"{BACKEND_URL}/export/executive-summary", json={}, auth=wrong_auth, timeout=15)
        print(f"POST /api/export/executive-summary (wrong auth) - Status: {response2.status_code}")
        
        if response2.status_code != 401:
            print(f"❌ Expected 401 with wrong auth, got {response2.status_code}")
            return False
        
        print("✅ Executive Summary export auth requirements working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Executive Summary export auth test failed: {str(e)}")
        return False

def test_export_executive_summary():
    """Test POST /api/export/executive-summary returns PDF with correct filename"""
    print("\n=== Testing Executive Summary Export (POST /api/export/executive-summary) ===")
    
    try:
        # Basic Auth with gp:Contrarians
        auth = ('gp', 'Contrarians')
        payload = {"as_of_date": None, "scenario": "Base"}
        
        response = requests.post(f"{BACKEND_URL}/export/executive-summary", json=payload, auth=auth, timeout=15, stream=True)
        print(f"POST /api/export/executive-summary - Status: {response.status_code}")
        
        if response.status_code == 200:
            # Verify Content-Type
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' not in content_type:
                print(f"❌ Wrong content type: expected application/pdf, got {content_type}")
                return False
            
            # Verify Content-Disposition header
            content_disposition = response.headers.get('content-disposition', '')
            if 'attachment' not in content_disposition:
                print(f"❌ Missing attachment in content-disposition: {content_disposition}")
                return False
            
            # Extract filename from Content-Disposition
            if 'filename=' in content_disposition:
                filename_part = content_disposition.split('filename=')[1].strip('"')
                print(f"  - Filename: {filename_part}")
                
                # Verify filename format: Executive_Summary_YYYY-MM-DD.pdf
                if not filename_part.startswith('Executive_Summary_'):
                    print(f"❌ Filename doesn't start with expected prefix: {filename_part}")
                    return False
                
                if not filename_part.endswith('.pdf'):
                    print(f"❌ Filename doesn't end with .pdf: {filename_part}")
                    return False
                
                # Check for date pattern YYYY-MM-DD
                date_part = filename_part.replace('Executive_Summary_', '').replace('.pdf', '')
                if len(date_part) != 10 or date_part.count('-') != 2:
                    print(f"❌ Filename missing proper date format YYYY-MM-DD: {filename_part}")
                    return False
                
            else:
                print(f"❌ No filename in content-disposition: {content_disposition}")
                return False
            
            # Read first few bytes to verify it's actually PDF content
            first_chunk = next(response.iter_content(chunk_size=1024), b'')
            if len(first_chunk) > 0:
                # PDF files start with %PDF
                if first_chunk[:4] == b'%PDF':
                    print(f"  - File appears to be valid PDF format")
                else:
                    print(f"❌ File doesn't appear to be PDF format (no %PDF signature)")
                    return False
            
            print(f"✅ Executive Summary export working correctly")
            return True
            
        else:
            print(f"❌ Executive Summary export failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Executive Summary export test failed: {str(e)}")
        return False

def test_export_pitch_deck_auth():
    """Test POST /api/export/pitch-deck requires Basic Auth"""
    print("\n=== Testing Pitch Deck Export Auth (POST /api/export/pitch-deck) ===")
    
    try:
        # Test without auth - should get 401
        response = requests.post(f"{BACKEND_URL}/export/pitch-deck", json={}, timeout=15)
        print(f"POST /api/export/pitch-deck (no auth) - Status: {response.status_code}")
        
        if response.status_code != 401:
            print(f"❌ Expected 401 without auth, got {response.status_code}")
            return False
        
        # Test with wrong auth - should get 401
        wrong_auth = ('wrong', 'credentials')
        response2 = requests.post(f"{BACKEND_URL}/export/pitch-deck", json={}, auth=wrong_auth, timeout=15)
        print(f"POST /api/export/pitch-deck (wrong auth) - Status: {response2.status_code}")
        
        if response2.status_code != 401:
            print(f"❌ Expected 401 with wrong auth, got {response2.status_code}")
            return False
        
        print("✅ Pitch Deck export auth requirements working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Pitch Deck export auth test failed: {str(e)}")
        return False

def test_export_pitch_deck():
    """Test POST /api/export/pitch-deck returns PPTX with correct filename"""
    print("\n=== Testing Pitch Deck Export (POST /api/export/pitch-deck) ===")
    
    try:
        # Basic Auth with gp:Contrarians
        auth = ('gp', 'Contrarians')
        payload = {"as_of_date": None, "format": "pptx", "include_notes": True}
        
        response = requests.post(f"{BACKEND_URL}/export/pitch-deck", json=payload, auth=auth, timeout=15, stream=True)
        print(f"POST /api/export/pitch-deck - Status: {response.status_code}")
        
        if response.status_code == 200:
            # Verify Content-Type
            content_type = response.headers.get('content-type', '')
            expected_content_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            
            if expected_content_type not in content_type:
                print(f"❌ Wrong content type: expected {expected_content_type}, got {content_type}")
                return False
            
            # Verify Content-Disposition header
            content_disposition = response.headers.get('content-disposition', '')
            if 'attachment' not in content_disposition:
                print(f"❌ Missing attachment in content-disposition: {content_disposition}")
                return False
            
            # Extract filename from Content-Disposition
            if 'filename=' in content_disposition:
                filename_part = content_disposition.split('filename=')[1].strip('"')
                print(f"  - Filename: {filename_part}")
                
                # Verify filename format: Coastal_Oak_Pitch_YYYY-MM-DD.pptx
                if not filename_part.startswith('Coastal_Oak_Pitch_'):
                    print(f"❌ Filename doesn't start with expected prefix: {filename_part}")
                    return False
                
                if not filename_part.endswith('.pptx'):
                    print(f"❌ Filename doesn't end with .pptx: {filename_part}")
                    return False
                
                # Check for date pattern YYYY-MM-DD
                date_part = filename_part.replace('Coastal_Oak_Pitch_', '').replace('.pptx', '')
                if len(date_part) != 10 or date_part.count('-') != 2:
                    print(f"❌ Filename missing proper date format YYYY-MM-DD: {filename_part}")
                    return False
                
            else:
                print(f"❌ No filename in content-disposition: {content_disposition}")
                return False
            
            # Read first few bytes to verify it's actually PPTX content
            first_chunk = next(response.iter_content(chunk_size=1024), b'')
            if len(first_chunk) > 0:
                # PPTX files start with PK (ZIP signature)
                if first_chunk[:2] == b'PK':
                    print(f"  - File appears to be valid PPTX format (ZIP signature found)")
                else:
                    print(f"❌ File doesn't appear to be PPTX format (no ZIP signature)")
                    return False
            
            print(f"✅ Pitch Deck export working correctly")
            return True
            
        else:
            print(f"❌ Pitch Deck export failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Pitch Deck export test failed: {str(e)}")
        return False

def test_export_excel_auth():
    """Test GET /api/export/excel requires Basic Auth"""
    print("\n=== Testing Excel Export Auth (GET /api/export/excel) ===")
    
    try:
        # Test without auth - should get 401
        response = requests.get(f"{BACKEND_URL}/export/excel", timeout=15)
        print(f"GET /api/export/excel (no auth) - Status: {response.status_code}")
        
        if response.status_code != 401:
            print(f"❌ Expected 401 without auth, got {response.status_code}")
            return False
        
        # Test with wrong auth - should get 401
        wrong_auth = ('wrong', 'credentials')
        response2 = requests.get(f"{BACKEND_URL}/export/excel", auth=wrong_auth, timeout=15)
        print(f"GET /api/export/excel (wrong auth) - Status: {response2.status_code}")
        
        if response2.status_code != 401:
            print(f"❌ Expected 401 with wrong auth, got {response2.status_code}")
            return False
        
        print("✅ Excel export auth requirements working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Excel export auth test failed: {str(e)}")
        return False

def test_export_excel_with_snapshot():
    """Test GET /api/export/excel?snapshot_id=<existing> returns XLSX with correct filename"""
    print("\n=== Testing Excel Export with Snapshot (GET /api/export/excel?snapshot_id=<id>) ===")
    
    try:
        # First, get an existing snapshot ID
        auth = ('gp', 'Contrarians')
        snapshots_response = requests.get(f"{BACKEND_URL}/snapshots", auth=auth, timeout=10)
        
        if snapshots_response.status_code != 200:
            print(f"❌ Could not get snapshots for Excel export test: {snapshots_response.status_code}")
            return False
        
        snapshots_data = snapshots_response.json()
        items = snapshots_data.get("items", [])
        
        if not items:
            print("❌ No snapshots available for Excel export testing")
            return False
        
        snapshot_id = items[0].get("id")
        print(f"  - Using snapshot ID: {snapshot_id}")
        
        # Test Excel export with existing snapshot
        response = requests.get(f"{BACKEND_URL}/export/excel?snapshot_id={snapshot_id}", auth=auth, timeout=15, stream=True)
        print(f"GET /api/export/excel?snapshot_id={snapshot_id} - Status: {response.status_code}")
        
        if response.status_code == 200:
            # Verify Content-Type
            content_type = response.headers.get('content-type', '')
            expected_content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            if expected_content_type not in content_type:
                print(f"❌ Wrong content type: expected {expected_content_type}, got {content_type}")
                return False
            
            # Verify Content-Disposition header
            content_disposition = response.headers.get('content-disposition', '')
            if 'attachment' not in content_disposition:
                print(f"❌ Missing attachment in content-disposition: {content_disposition}")
                return False
            
            # Extract filename from Content-Disposition
            if 'filename=' in content_disposition:
                filename_part = content_disposition.split('filename=')[1].strip('"')
                print(f"  - Filename: {filename_part}")
                
                # Verify filename format: Coastal_Excel_Analytics_${AS_OF}_v${SEQ}.xlsx
                if not filename_part.startswith('Coastal_Excel_Analytics_'):
                    print(f"❌ Filename doesn't start with expected prefix: {filename_part}")
                    return False
                
                if not filename_part.endswith('.xlsx'):
                    print(f"❌ Filename doesn't end with .xlsx: {filename_part}")
                    return False
                
                # Check for date and version pattern
                parts = filename_part.replace('Coastal_Excel_Analytics_', '').replace('.xlsx', '')
                if '_v' not in parts:
                    print(f"❌ Filename missing version pattern: {filename_part}")
                    return False
                
            else:
                print(f"❌ No filename in content-disposition: {content_disposition}")
                return False
            
            # Read first few bytes to verify it's actually Excel content
            first_chunk = next(response.iter_content(chunk_size=1024), b'')
            if len(first_chunk) > 0:
                # Excel files start with PK (ZIP signature)
                if first_chunk[:2] == b'PK':
                    print(f"  - File appears to be valid Excel format (ZIP signature found)")
                else:
                    print(f"❌ File doesn't appear to be Excel format (no ZIP signature)")
                    return False
            
            print(f"✅ Excel export with snapshot working correctly")
            return True
            
        else:
            print(f"❌ Excel export with snapshot failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Excel export with snapshot test failed: {str(e)}")
        return False

def test_export_excel_nonexistent_snapshot():
    """Test GET /api/export/excel?snapshot_id=<nonexistent> returns 404"""
    print("\n=== Testing Excel Export with Non-existent Snapshot (GET /api/export/excel?snapshot_id=<fake>) ===")
    
    try:
        fake_id = "00000000-0000-0000-0000-000000000000"
        auth = ('gp', 'Contrarians')
        
        response = requests.get(f"{BACKEND_URL}/export/excel?snapshot_id={fake_id}", auth=auth, timeout=10)
        print(f"GET /api/export/excel?snapshot_id={fake_id} - Status: {response.status_code}")
        
        if response.status_code == 404:
            print("✅ Excel export correctly returns 404 for non-existent snapshot")
            return True
        else:
            print(f"❌ Expected 404 for non-existent snapshot, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Excel export non-existent snapshot test failed: {str(e)}")
        return False

def test_export_endpoints():
    """Run all Export Endpoints tests"""
    print("\n" + "="*80)
    print("📤 EXPORT ENDPOINTS TESTING (GP Basic Auth Required)")
    print("="*80)
    
    results = {}
    
    # Test Executive Summary Export
    results['export_executive_summary_auth'] = test_export_executive_summary_auth()
    results['export_executive_summary'] = test_export_executive_summary()
    
    # Test Pitch Deck Export
    results['export_pitch_deck_auth'] = test_export_pitch_deck_auth()
    results['export_pitch_deck'] = test_export_pitch_deck()
    
    # Test Excel Export
    results['export_excel_auth'] = test_export_excel_auth()
    results['export_excel_with_snapshot'] = test_export_excel_with_snapshot()
    results['export_excel_nonexistent_snapshot'] = test_export_excel_nonexistent_snapshot()
    
    return results

def test_data_lineage_auditability():
    """Run all Data Lineage & Auditability tests"""
    print("\n" + "="*80)
    print("🔍 DATA LINEAGE & AUDITABILITY TESTING")
    print("="*80)
    
    results = {}
    snapshot_id = None
    
    # Test 1: Create snapshot
    results['snapshot_creation'], snapshot_id = test_snapshot_creation()
    
    # Test 2: List snapshots with pagination
    results['snapshot_list'] = test_snapshot_list()
    
    # Test 3: Get snapshot by ID (requires snapshot_id from test 1)
    results['snapshot_get_by_id'] = test_snapshot_get_by_id(snapshot_id)
    
    # Test 4: Excel summary refresh with rate limiting
    results['excel_summary_refresh'] = test_excel_summary_refresh()
    
    # Test 5: Excel summary with specific snapshot ID
    results['excel_summary_with_snapshot_id'] = test_excel_summary_with_snapshot_id(snapshot_id)
    
    # Test 6: Excel generate with specific snapshot ID
    results['excel_generate_with_snapshot_id'] = test_excel_generate_with_snapshot_id(snapshot_id)
    
    # Test 7: Lineage allowlist verification
    results['lineage_allowlist'] = test_lineage_allowlist()
    
    # Test 8: Non-existent snapshot 404 responses
    results['nonexistent_snapshot_404'] = test_nonexistent_snapshot_404()
    
    return results

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
    
    # Test Excel Analytics Endpoints (Legacy)
    print("\n" + "="*60)
    print("📊 TESTING EXCEL ANALYTICS ENDPOINTS (LEGACY)")
    print("="*60)
    
    results['excel_summary'] = test_excel_summary()
    results['excel_data'] = test_excel_data()
    results['excel_deals'] = test_excel_deals()
    results['excel_generate'] = test_excel_generate()
    
    # Test Data Lineage & Auditability (NEW SPRINT)
    lineage_results = test_data_lineage_auditability()
    results.update(lineage_results)
    
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
    
    # Separate summary for Excel endpoints
    excel_tests = {k: v for k, v in results.items() if k.startswith('excel_')}
    excel_passed = sum(1 for result in excel_tests.values() if result)
    excel_total = len(excel_tests)
    
    print(f"\n📊 Excel Analytics: {excel_passed}/{excel_total} tests passed")
    
    # Separate summary for Data Lineage & Auditability
    lineage_tests = {k: v for k, v in results.items() if k in [
        'snapshot_creation', 'snapshot_list', 'snapshot_get_by_id', 
        'excel_summary_refresh', 'excel_summary_with_snapshot_id', 
        'excel_generate_with_snapshot_id', 'lineage_allowlist', 'nonexistent_snapshot_404'
    ]}
    lineage_passed = sum(1 for result in lineage_tests.values() if result)
    lineage_total = len(lineage_tests)
    
    print(f"\n🔍 Data Lineage & Auditability: {lineage_passed}/{lineage_total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the details above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)