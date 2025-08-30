#!/usr/bin/env python3
"""
Agent SDK Testing for Coastal Oak Capital Platform
Tests the new Agent SDK integration including registry, data feeds, execution, and security endpoints
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional

class AgentSDKTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        self.base_url = self._get_backend_url()
        self.session = requests.Session()
        self.test_results = []
        
    def _get_backend_url(self) -> str:
        """Get backend URL from frontend .env file"""
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        url = line.split('=', 1)[1].strip()
                        return f"{url}/api"
        except Exception as e:
            print(f"Warning: Could not read frontend .env file: {e}")
        
        # Fallback to default
        return "http://localhost:8001/api"
    
    def log_test(self, test_name: str, success: bool, details: str, response_data: Optional[Dict] = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    def test_agent_registry_endpoint(self) -> bool:
        """Test GET /api/agents/registry - Verify all 14 agents are registered"""
        try:
            response = self.session.get(f"{self.base_url}/agents/registry", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'agents', 'capabilities', 'total_agents']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Agent Registry Endpoint", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                if not data.get('success'):
                    self.log_test("Agent Registry Endpoint", False, 
                                f"API returned success=false", data)
                    return False
                
                # Check for all 14 expected agents
                agents = data.get('agents', [])
                total_agents = data.get('total_agents', 0)
                
                expected_agents = [
                    "Charts and Visualization Engineer",
                    "UI, Aesthetics, and Information Architecture", 
                    "Real-Time Data and Citations Steward",
                    "Quantitative Analysis and Models",
                    "Debt Underwriting — Data Centers",
                    "Debt Underwriting — EV Supercharging",
                    "Development Feasibility — Data Centers", 
                    "Development Feasibility — EV Supercharging",
                    "Tax Attorney Consultant",
                    "Land Use Attorney — Los Angeles",
                    "Risk Management and Controls",
                    "ESG, Incentives, and Grants",
                    "LP-GP Red Team Reviewer",
                    "Security and Distribution"
                ]
                
                if total_agents != 14:
                    self.log_test("Agent Registry Endpoint", False, 
                                f"Expected 14 agents, found {total_agents}", data)
                    return False
                
                # Check agent names (flexible matching for minor variations)
                agent_names = [agent.get('name', '') for agent in agents]
                
                # Check for core agent types with flexible name matching
                core_agent_checks = [
                    ("Charts", any("Charts" in name for name in agent_names)),
                    ("UI", any("UI" in name for name in agent_names)),
                    ("Data Steward", any("Data" in name and "Steward" in name for name in agent_names)),
                    ("Quant", any("Quantitative" in name for name in agent_names)),
                    ("Debt DC", any("Debt" in name and "Data Center" in name for name in agent_names)),
                    ("Debt EV", any("Debt" in name and "EV" in name for name in agent_names)),
                    ("Dev DC", any("Development" in name and "Data Center" in name for name in agent_names)),
                    ("Dev EV", any("Development" in name and "EV" in name for name in agent_names)),
                    ("Tax", any("Tax" in name for name in agent_names)),
                    ("Land Use", any("Land Use" in name for name in agent_names)),
                    ("Risk", any("Risk" in name for name in agent_names)),
                    ("ESG", any("ESG" in name for name in agent_names)),
                    ("Red Team", any("Red Team" in name for name in agent_names)),
                    ("Security", any("Security" in name for name in agent_names))
                ]
                
                missing_agent_types = [agent_type for agent_type, found in core_agent_checks if not found]
                
                if missing_agent_types:
                    self.log_test("Agent Registry Endpoint", False, 
                                f"Missing agent types: {missing_agent_types}", data)
                    return False
                
                # Check capabilities structure
                capabilities = data.get('capabilities', {})
                expected_capabilities = ['charts', 'ui', 'data', 'quant', 'debt-dc', 'debt-ev', 
                                       'dev-dc', 'dev-ev', 'tax', 'land-use', 'risk', 'esg', 
                                       'red-team', 'security']
                
                missing_capabilities = [cap for cap in expected_capabilities if cap not in capabilities]
                
                if missing_capabilities:
                    self.log_test("Agent Registry Endpoint", False, 
                                f"Missing capabilities: {missing_capabilities}", data)
                    return False
                
                self.log_test("Agent Registry Endpoint", True, 
                            f"All 14 agents properly registered with complete capabilities", 
                            {'total_agents': total_agents, 'sample_agents': agent_names[:3]})
                return True
                
            else:
                self.log_test("Agent Registry Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Agent Registry Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_rates_endpoint(self) -> bool:
        """Test GET /api/rates - Treasury and Fed rates data feed"""
        try:
            response = self.session.get(f"{self.base_url}/rates", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'data']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Rates Data Feed", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                if not data.get('success'):
                    self.log_test("Rates Data Feed", False, 
                                f"API returned success=false", data)
                    return False
                
                # Check rates data structure
                rates_data = data.get('data', {})
                required_sections = ['treasury_rates', 'fed_funds_rate', 'timestamp']
                missing_sections = [section for section in required_sections if section not in rates_data]
                
                if missing_sections:
                    self.log_test("Rates Data Feed", False, 
                                f"Missing data sections: {missing_sections}", data)
                    return False
                
                # Check Treasury rates
                treasury_rates = rates_data.get('treasury_rates', {})
                expected_tenors = ['5Y', '10Y', '30Y']
                missing_tenors = [tenor for tenor in expected_tenors if tenor not in treasury_rates]
                
                if missing_tenors:
                    self.log_test("Rates Data Feed", False, 
                                f"Missing Treasury tenors: {missing_tenors}", data)
                    return False
                
                # Validate rate values
                for tenor, rate_data in treasury_rates.items():
                    if not isinstance(rate_data.get('value'), (int, float)):
                        self.log_test("Rates Data Feed", False, 
                                    f"Invalid rate value for {tenor}: {rate_data.get('value')}", data)
                        return False
                
                # Check Fed funds rate
                fed_funds = rates_data.get('fed_funds_rate', {})
                if not isinstance(fed_funds.get('current'), (int, float)):
                    self.log_test("Rates Data Feed", False, 
                                f"Invalid Fed funds rate: {fed_funds.get('current')}", data)
                    return False
                
                self.log_test("Rates Data Feed", True, 
                            f"Successfully fetched Treasury and Fed rates data", 
                            {'treasury_tenors': list(treasury_rates.keys()), 'fed_rate': fed_funds.get('current')})
                return True
                
            else:
                self.log_test("Rates Data Feed", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Rates Data Feed", False, f"Request failed: {str(e)}")
            return False
    
    def test_maturities_endpoint(self) -> bool:
        """Test GET /api/maturities - CRE maturity ladder data"""
        try:
            response = self.session.get(f"{self.base_url}/maturities", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'data', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("CRE Maturities Data Feed", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                if not data.get('success'):
                    self.log_test("CRE Maturities Data Feed", False, 
                                f"API returned success=false", data)
                    return False
                
                # Check maturities data structure
                maturities_data = data.get('data', {})
                if 'rows' not in maturities_data:
                    self.log_test("CRE Maturities Data Feed", False, 
                                f"Missing 'rows' in maturities data", data)
                    return False
                
                rows = maturities_data.get('rows', [])
                if len(rows) == 0:
                    self.log_test("CRE Maturities Data Feed", False, 
                                f"No maturity data returned", data)
                    return False
                
                # Validate row structure
                sample_row = rows[0]
                expected_fields = ['property_type', 'maturity_year', 'outstanding_balance', 
                                 'maturing_loans', 'avg_ltv', 'avg_dscr', 'distress_probability']
                missing_row_fields = [field for field in expected_fields if field not in sample_row]
                
                if missing_row_fields:
                    self.log_test("CRE Maturities Data Feed", False, 
                                f"Sample row missing fields: {missing_row_fields}", data)
                    return False
                
                self.log_test("CRE Maturities Data Feed", True, 
                            f"Successfully fetched CRE maturity data with {len(rows)} property types", 
                            {'rows_count': len(rows), 'property_types': [row.get('property_type') for row in rows]})
                return True
                
            else:
                self.log_test("CRE Maturities Data Feed", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("CRE Maturities Data Feed", False, f"Request failed: {str(e)}")
            return False
    
    def test_banks_endpoint(self) -> bool:
        """Test GET /api/banks - FDIC call reports data"""
        try:
            response = self.session.get(f"{self.base_url}/banks", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'data', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("FDIC Banks Data Feed", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                if not data.get('success'):
                    self.log_test("FDIC Banks Data Feed", False, 
                                f"API returned success=false", data)
                    return False
                
                # Check FDIC data structure
                fdic_data = data.get('data', {})
                if 'rows' not in fdic_data:
                    self.log_test("FDIC Banks Data Feed", False, 
                                f"Missing 'rows' in FDIC data", data)
                    return False
                
                rows = fdic_data.get('rows', [])
                if len(rows) == 0:
                    self.log_test("FDIC Banks Data Feed", False, 
                                f"No FDIC data returned", data)
                    return False
                
                # Validate row structure
                sample_row = rows[0]
                expected_fields = ['cert', 'name', 'city', 'state', 'total_assets', 
                                 'total_deposits', 'roa', 'roe', 'as_of_date']
                missing_row_fields = [field for field in expected_fields if field not in sample_row]
                
                if missing_row_fields:
                    self.log_test("FDIC Banks Data Feed", False, 
                                f"Sample row missing fields: {missing_row_fields}", data)
                    return False
                
                self.log_test("FDIC Banks Data Feed", True, 
                            f"Successfully fetched FDIC data with {len(rows)} banks", 
                            {'banks_count': len(rows), 'sample_banks': [row.get('name') for row in rows]})
                return True
                
            else:
                self.log_test("FDIC Banks Data Feed", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("FDIC Banks Data Feed", False, f"Request failed: {str(e)}")
            return False
    
    def test_agent_execution_endpoint(self) -> bool:
        """Test POST /api/agents/execute - Agent orchestration system"""
        try:
            # Test with realistic investment analysis scenario
            payload = {
                "objective": "Analyze data center development opportunity in Los Angeles with focus on power infrastructure and financing options",
                "audience": "LP",
                "inputs": {
                    "property_type": "data_center",
                    "location": "Los Angeles",
                    "investment_size": 50000000,
                    "development_timeline": "18_months"
                },
                "tags": ["dev-dc", "debt-dc", "data", "quant", "risk"],
                "required_charts": ["yield_curve", "cre_distress"],
                "required_models": ["dcf", "sensitivity"],
                "security_tier": "restricted"
            }
            
            response = self.session.post(f"{self.base_url}/agents/execute", 
                                       json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'result', 'agents_executed', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Agent Execution", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                if not data.get('success'):
                    self.log_test("Agent Execution", False, 
                                f"API returned success=false", data)
                    return False
                
                # Check execution result
                result = data.get('result', {})
                required_result_fields = ['summary', 'packets', 'footnote_register']
                missing_result_fields = [field for field in required_result_fields if field not in result]
                
                if missing_result_fields:
                    self.log_test("Agent Execution", False, 
                                f"Missing result fields: {missing_result_fields}", data)
                    return False
                
                # Check packets (agent responses)
                packets = result.get('packets', [])
                agents_executed = data.get('agents_executed', 0)
                
                if len(packets) != agents_executed:
                    self.log_test("Agent Execution", False, 
                                f"Packet count mismatch: {len(packets)} vs {agents_executed}", data)
                    return False
                
                if agents_executed == 0:
                    self.log_test("Agent Execution", False, 
                                f"No agents were executed", data)
                    return False
                
                # Validate packet structure
                if packets:
                    sample_packet = packets[0]
                    required_packet_fields = ['executive_takeaway', 'analysis', 'findings', 
                                            'recommendations', 'footnotes', 'version', 'checks']
                    missing_packet_fields = [field for field in required_packet_fields if field not in sample_packet]
                    
                    if missing_packet_fields:
                        self.log_test("Agent Execution", False, 
                                    f"Sample packet missing fields: {missing_packet_fields}", data)
                        return False
                
                # Check footnote register
                footnote_register = result.get('footnote_register', {})
                if len(footnote_register) == 0:
                    self.log_test("Agent Execution", False, 
                                f"No footnotes generated", data)
                    return False
                
                self.log_test("Agent Execution", True, 
                            f"Successfully executed {agents_executed} agents with {len(footnote_register)} footnotes", 
                            {'agents_executed': agents_executed, 'footnotes_count': len(footnote_register)})
                return True
                
            else:
                self.log_test("Agent Execution", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Agent Execution", False, f"Request failed: {str(e)}")
            return False
    
    def test_security_endpoint(self) -> bool:
        """Test POST /api/deck/request - Single-use token generation"""
        try:
            payload = {
                "user_id": "institutional_investor_001",
                "audience": "LP"
            }
            
            response = self.session.post(f"{self.base_url}/deck/request", 
                                       json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'access_token', 'expires_at', 'audience', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Security Token Endpoint", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                if not data.get('success'):
                    self.log_test("Security Token Endpoint", False, 
                                f"API returned success=false", data)
                    return False
                
                # Validate token
                access_token = data.get('access_token')
                if not access_token or len(access_token) < 10:
                    self.log_test("Security Token Endpoint", False, 
                                f"Invalid access token: {access_token}", data)
                    return False
                
                # Check token format (should start with 'sut_')
                if not access_token.startswith('sut_'):
                    self.log_test("Security Token Endpoint", False, 
                                f"Token doesn't follow expected format: {access_token[:10]}...", data)
                    return False
                
                # Check expiration
                expires_at = data.get('expires_at')
                if not expires_at:
                    self.log_test("Security Token Endpoint", False, 
                                f"No expiration time provided", data)
                    return False
                
                # Check audience
                audience = data.get('audience')
                if audience != payload['audience']:
                    self.log_test("Security Token Endpoint", False, 
                                f"Audience mismatch: expected {payload['audience']}, got {audience}", data)
                    return False
                
                self.log_test("Security Token Endpoint", True, 
                            f"Single-use token generated successfully for {payload['user_id']}", 
                            {'token_prefix': access_token[:8] + '...', 'audience': audience})
                return True
                
            else:
                self.log_test("Security Token Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Security Token Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_footnotes_endpoint(self) -> bool:
        """Test GET /api/footnotes - Source citations"""
        try:
            response = self.session.get(f"{self.base_url}/footnotes", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'data']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Footnotes Endpoint", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                if not data.get('success'):
                    self.log_test("Footnotes Endpoint", False, 
                                f"API returned success=false", data)
                    return False
                
                # Check footnotes data structure
                footnotes_data = data.get('data', {})
                required_sections = ['footnotes', 'total_count', 'last_updated']
                missing_sections = [section for section in required_sections if section not in footnotes_data]
                
                if missing_sections:
                    self.log_test("Footnotes Endpoint", False, 
                                f"Missing data sections: {missing_sections}", data)
                    return False
                
                # Check footnotes array
                footnotes = footnotes_data.get('footnotes', [])
                total_count = footnotes_data.get('total_count', 0)
                
                if len(footnotes) != total_count:
                    self.log_test("Footnotes Endpoint", False, 
                                f"Footnotes count mismatch: {len(footnotes)} vs {total_count}", data)
                    return False
                
                if len(footnotes) == 0:
                    self.log_test("Footnotes Endpoint", False, 
                                f"No footnotes returned", data)
                    return False
                
                # Validate footnote structure
                sample_footnote = footnotes[0]
                required_footnote_fields = ['id', 'label', 'source', 'retrieved_at', 'refresh', 'transform']
                missing_footnote_fields = [field for field in required_footnote_fields if field not in sample_footnote]
                
                if missing_footnote_fields:
                    self.log_test("Footnotes Endpoint", False, 
                                f"Sample footnote missing fields: {missing_footnote_fields}", data)
                    return False
                
                self.log_test("Footnotes Endpoint", True, 
                            f"Successfully fetched {total_count} footnotes with proper citations", 
                            {'footnotes_count': total_count, 'sample_sources': [f.get('source') for f in footnotes]})
                return True
                
            else:
                self.log_test("Footnotes Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Footnotes Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_ev_charging_scenario(self) -> bool:
        """Test Agent SDK with EV charging infrastructure scenario"""
        try:
            payload = {
                "objective": "Evaluate EV supercharging station development in Los Angeles with grant stacking and utilization modeling",
                "audience": "GP",
                "inputs": {
                    "property_type": "ev_charging",
                    "location": "Los Angeles",
                    "investment_size": 25000000,
                    "charging_capacity": "350kW_superchargers",
                    "site_count": 12
                },
                "tags": ["dev-ev", "debt-ev", "esg", "land-use", "quant"],
                "required_charts": ["utilization_forecast", "grant_stacking"],
                "required_models": ["project_finance", "throughput_analysis"],
                "security_tier": "public"
            }
            
            response = self.session.post(f"{self.base_url}/agents/execute", 
                                       json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('success'):
                    self.log_test("EV Charging Scenario", False, 
                                f"API returned success=false", data)
                    return False
                
                result = data.get('result', {})
                packets = result.get('packets', [])
                agents_executed = data.get('agents_executed', 0)
                
                # Should execute multiple agents for this complex scenario
                if agents_executed < 3:
                    self.log_test("EV Charging Scenario", False, 
                                f"Too few agents executed: {agents_executed} (expected >= 3)", data)
                    return False
                
                # Check for EV-specific analysis
                ev_analysis_found = False
                for packet in packets:
                    analysis = packet.get('analysis', '').lower()
                    if any(term in analysis for term in ['ev', 'charging', 'electric vehicle', 'supercharging']):
                        ev_analysis_found = True
                        break
                
                if not ev_analysis_found:
                    self.log_test("EV Charging Scenario", False, 
                                f"No EV-specific analysis found in agent responses", data)
                    return False
                
                self.log_test("EV Charging Scenario", True, 
                            f"EV charging scenario executed successfully with {agents_executed} agents", 
                            {'agents_executed': agents_executed, 'ev_analysis': True})
                return True
                
            else:
                self.log_test("EV Charging Scenario", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("EV Charging Scenario", False, f"Request failed: {str(e)}")
            return False
    
    def run_agent_sdk_tests(self) -> Dict[str, Any]:
        """Run all Agent SDK tests"""
        print(f"\n🤖 Starting Agent SDK Integration Tests")
        print(f"Backend URL: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Test sequence for Agent SDK
        tests = [
            ("Agent Registry", self.test_agent_registry_endpoint),
            ("Rates Data Feed", self.test_rates_endpoint),
            ("CRE Maturities Data Feed", self.test_maturities_endpoint),
            ("FDIC Banks Data Feed", self.test_banks_endpoint),
            ("Agent Execution - Data Center", self.test_agent_execution_endpoint),
            ("Agent Execution - EV Charging", self.test_ev_charging_scenario),
            ("Security Token Generation", self.test_security_endpoint),
            ("Footnotes Citations", self.test_footnotes_endpoint)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            try:
                success = test_func()
                if success:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL {test_name}: Unexpected error - {str(e)}")
                self.log_test(test_name, False, f"Unexpected error: {str(e)}")
                failed += 1
            
            # Small delay between tests
            time.sleep(0.5)
        
        # Summary
        print("\n" + "=" * 80)
        print(f"🏁 AGENT SDK TEST SUMMARY")
        print(f"Total Tests: {passed + failed}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%" if (passed + failed) > 0 else "0%")
        
        return {
            'total_tests': passed + failed,
            'passed': passed,
            'failed': failed,
            'success_rate': (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0,
            'test_results': self.test_results,
            'backend_url': self.base_url
        }


def main():
    """Main test execution"""
    tester = AgentSDKTester()
    results = tester.run_agent_sdk_tests()
    
    # Save detailed results to file
    with open('/app/agent_sdk_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📊 Detailed results saved to: /app/agent_sdk_test_results.json")
    
    # Return exit code based on results
    return 0 if results['failed'] == 0 else 1


if __name__ == "__main__":
    exit(main())