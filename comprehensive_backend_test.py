#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Coastal Oak Capital - Final System Validation
Tests the finalized comprehensive master deck system with all enhanced features
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class ComprehensiveCoastalOakTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        self.base_url = self._get_backend_url()
        self.session = requests.Session()
        self.test_results = []
        self.created_document_id = None
        
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
    
    def test_enhanced_document_creation_8_sections(self) -> bool:
        """Test document creation with 8 comprehensive sections as requested"""
        try:
            response = self.session.post(f"{self.base_url}/document/create", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('success'):
                    self.log_test("Enhanced Document Creation (8 Sections)", False, 
                                f"API returned success=false: {data.get('message', 'No message')}", data)
                    return False
                
                # Store document ID for subsequent tests
                self.created_document_id = data.get('document_id')
                sections_count = data.get('sections_count', 0)
                version = data.get('version', '')
                
                # Validate 8 sections as requested
                if sections_count != 8:
                    self.log_test("Enhanced Document Creation (8 Sections)", False, 
                                f"Expected 8 sections, got {sections_count}", data)
                    return False
                
                # Validate version is "2.0 - Final Comprehensive Edition"
                if "2.0" not in version or "Final Comprehensive Edition" not in version:
                    self.log_test("Enhanced Document Creation (8 Sections)", False, 
                                f"Expected version '2.0 - Final Comprehensive Edition', got '{version}'", data)
                    return False
                
                self.log_test("Enhanced Document Creation (8 Sections)", True, 
                            f"Document created with {sections_count} sections, version: {version}", 
                            {'document_id': self.created_document_id, 'sections': sections_count, 'version': version})
                return True
                
            else:
                self.log_test("Enhanced Document Creation (8 Sections)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Document Creation (8 Sections)", False, f"Request failed: {str(e)}")
            return False
    
    def test_living_master_deck_title_and_version(self) -> bool:
        """Test that document has correct title and version as 'Living Master Deck System'"""
        if not self.created_document_id:
            self.log_test("Living Master Deck Title/Version", False, "No document ID available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/document/{self.created_document_id}", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                document = data.get('document', {})
                title = document.get('title', '')
                version = document.get('version', '')
                
                # Check for "Living Master Deck System" in title
                if "Living Master Deck" not in title:
                    self.log_test("Living Master Deck Title/Version", False, 
                                f"Title should contain 'Living Master Deck', got: {title}", data)
                    return False
                
                # Check for version "2.0 - Final Comprehensive Edition"
                if "2.0" not in version or "Final Comprehensive Edition" not in version:
                    self.log_test("Living Master Deck Title/Version", False, 
                                f"Expected version '2.0 - Final Comprehensive Edition', got: {version}", data)
                    return False
                
                self.log_test("Living Master Deck Title/Version", True, 
                            f"Correct title and version validated", 
                            {'title': title, 'version': version})
                return True
                
            else:
                self.log_test("Living Master Deck Title/Version", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Living Master Deck Title/Version", False, f"Request failed: {str(e)}")
            return False
    
    def test_comprehensive_8_sections_content(self) -> bool:
        """Test that all 8 comprehensive sections are present with expected content"""
        if not self.created_document_id:
            self.log_test("8 Sections Content Validation", False, "No document ID available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/document/{self.created_document_id}", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                document = data.get('document', {})
                sections = document.get('sections', [])
                
                if len(sections) != 8:
                    self.log_test("8 Sections Content Validation", False, 
                                f"Expected 8 sections, found {len(sections)}", data)
                    return False
                
                # Expected section content validation
                expected_sections = [
                    ("Executive Summary", ["political", "crypto", "Trump administration", "GENIUS Act"]),
                    ("Market Dislocation", ["Q1 2025", "distressed", "opportunity"]),
                    ("Five-Pillar Strategy", ["blockchain integration", "stablecoin"]),
                    ("AI Data Center Infrastructure", ["heat-to-energy", "modular grid"]),
                    ("Financial Case Studies", ["stablecoin scenarios", "case study"]),
                    ("PICO Property Investment", ["investment discipline", "declined"]),
                    ("Trump Administration Policy", ["policy impact", "GENIUS Act"]),
                    ("Risk Management & ESG", ["ESG integration", "risk management"])
                ]
                
                missing_content = []
                for i, (expected_title_part, expected_content) in enumerate(expected_sections):
                    if i >= len(sections):
                        missing_content.append(f"Section {i+1}: {expected_title_part} - Missing entirely")
                        continue
                    
                    section = sections[i]
                    section_title = section.get('title', '').lower()
                    section_content = section.get('content', '').lower()
                    
                    # Check if title contains expected part
                    if expected_title_part.lower() not in section_title:
                        missing_content.append(f"Section {i+1}: Title should contain '{expected_title_part}', got '{section.get('title', '')}'")
                    
                    # Check for expected content elements
                    for content_element in expected_content:
                        if content_element.lower() not in section_content:
                            missing_content.append(f"Section {i+1}: Missing '{content_element}' in content")
                
                if missing_content:
                    self.log_test("8 Sections Content Validation", False, 
                                f"Content validation failed: {missing_content[:5]}", 
                                {'total_issues': len(missing_content)})
                    return False
                
                self.log_test("8 Sections Content Validation", True, 
                            f"All 8 sections validated with expected content", 
                            {'sections_count': len(sections)})
                return True
                
            else:
                self.log_test("8 Sections Content Validation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("8 Sections Content Validation", False, f"Request failed: {str(e)}")
            return False
    
    def test_daily_refresh_endpoint(self) -> bool:
        """Test the new daily refresh endpoint /api/system/refresh-all"""
        try:
            response = self.session.post(f"{self.base_url}/system/refresh-all", timeout=45)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('success'):
                    self.log_test("Daily Refresh Endpoint", False, 
                                f"API returned success=false: {data.get('message', 'No message')}", data)
                    return False
                
                # Check required fields for daily refresh
                required_fields = ['success', 'refreshed_count', 'total_documents', 'timestamp', 'message']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Daily Refresh Endpoint", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                refreshed_count = data.get('refreshed_count', 0)
                total_documents = data.get('total_documents', 0)
                
                # Should have refreshed at least one document if any exist
                if total_documents > 0 and refreshed_count == 0:
                    self.log_test("Daily Refresh Endpoint", False, 
                                f"No documents refreshed despite {total_documents} total documents", data)
                    return False
                
                self.log_test("Daily Refresh Endpoint", True, 
                            f"Daily refresh completed: {refreshed_count}/{total_documents} documents updated", 
                            {'refreshed': refreshed_count, 'total': total_documents})
                return True
                
            else:
                self.log_test("Daily Refresh Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Daily Refresh Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_real_time_data_integration_all_sections(self) -> bool:
        """Test that real-time data is properly integrated across all 8 sections"""
        try:
            # First get live data
            data_response = self.session.get(f"{self.base_url}/data/live", timeout=15)
            
            if data_response.status_code != 200:
                self.log_test("Real-Time Data Integration", False, 
                            f"Failed to fetch live data: {data_response.status_code}")
                return False
            
            live_data = data_response.json()
            if not live_data.get('success'):
                self.log_test("Real-Time Data Integration", False, 
                            f"Live data API failed: {live_data.get('message', 'No message')}")
                return False
            
            market_data = live_data.get('data', {})
            expected_sources = [
                'fed_funds_rate', '10_year_treasury', 'cpi_inflation', 
                'construction_cost_index', 'commercial_electricity_rate',
                'cmbs_spread', 'cap_rates_office', 'distressed_debt_discount'
            ]
            
            missing_sources = [source for source in expected_sources if source not in market_data]
            if missing_sources:
                self.log_test("Real-Time Data Integration", False, 
                            f"Missing data sources: {missing_sources}")
                return False
            
            # Test document creation with real-time data
            if not self.created_document_id:
                create_response = self.session.post(f"{self.base_url}/document/create", timeout=30)
                if create_response.status_code == 200:
                    self.created_document_id = create_response.json().get('document_id')
            
            if self.created_document_id:
                # Test document update with force refresh
                update_payload = {"document_id": self.created_document_id, "force_refresh": True}
                update_response = self.session.post(f"{self.base_url}/document/{self.created_document_id}/update", 
                                                   json=update_payload, timeout=20)
                
                if update_response.status_code != 200:
                    self.log_test("Real-Time Data Integration", False, 
                                f"Failed to update document with real-time data: {update_response.status_code}")
                    return False
            
            self.log_test("Real-Time Data Integration", True, 
                        f"Real-time data integration working with {len(market_data)} sources", 
                        {'sources_count': len(market_data), 'sample_sources': list(market_data.keys())[:3]})
            return True
            
        except Exception as e:
            self.log_test("Real-Time Data Integration", False, f"Request failed: {str(e)}")
            return False
    
    def test_comprehensive_markdown_export(self) -> bool:
        """Test markdown export produces comprehensive master deck content"""
        if not self.created_document_id:
            self.log_test("Comprehensive Markdown Export", False, "No document ID available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/document/{self.created_document_id}/export/markdown", timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                content = data.get('content', '')
                
                if not data.get('success'):
                    self.log_test("Comprehensive Markdown Export", False, 
                                f"API returned success=false", data)
                    return False
                
                # Check for comprehensive content elements
                required_content = [
                    'Living Master Deck',
                    'PICO Boulevard Property',
                    'AI Data Center Modular Grid Infrastructure',
                    'Trump Administration Policy',
                    'ESG Integration',
                    'investment discipline',
                    'heat-to-energy conversion',
                    'GENIUS Act',
                    'stablecoin',
                    'blockchain integration'
                ]
                
                missing_content = []
                for content_item in required_content:
                    if content_item.lower() not in content.lower():
                        missing_content.append(content_item)
                
                if missing_content:
                    self.log_test("Comprehensive Markdown Export", False, 
                                f"Missing content in markdown: {missing_content}", 
                                {'content_length': len(content)})
                    return False
                
                # Check section count in markdown (should be 8)
                section_count = content.count('## Section')
                if section_count != 8:
                    self.log_test("Comprehensive Markdown Export", False, 
                                f"Expected 8 sections in markdown, found {section_count}", data)
                    return False
                
                # Check content length (should be substantial with all comprehensive content)
                if len(content) < 50000:  # Increased expectation for comprehensive content
                    self.log_test("Comprehensive Markdown Export", False, 
                                f"Markdown content too short: {len(content)} characters (expected >50,000)", data)
                    return False
                
                self.log_test("Comprehensive Markdown Export", True, 
                            f"Comprehensive markdown export validated with all content", 
                            {'content_length': len(content), 'sections': section_count})
                return True
                
            else:
                self.log_test("Comprehensive Markdown Export", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Comprehensive Markdown Export", False, f"Request failed: {str(e)}")
            return False
    
    def test_api_endpoints_success_rate(self) -> bool:
        """Test all API endpoints for 100% success rate as requested"""
        try:
            endpoints_to_test = [
                ("GET", "/status", None),
                ("GET", "/data/live", None),
                ("POST", "/document/create", None),
                ("GET", "/documents/list", None)
            ]
            
            if self.created_document_id:
                endpoints_to_test.extend([
                    ("GET", f"/document/{self.created_document_id}", None),
                    ("POST", f"/document/{self.created_document_id}/update", {"document_id": self.created_document_id, "force_refresh": True}),
                    ("GET", f"/document/{self.created_document_id}/export/markdown", None)
                ])
            
            successful_endpoints = 0
            total_endpoints = len(endpoints_to_test)
            
            for method, endpoint, payload in endpoints_to_test:
                try:
                    if method == "GET":
                        response = self.session.get(f"{self.base_url}{endpoint}", timeout=15)
                    elif method == "POST":
                        response = self.session.post(f"{self.base_url}{endpoint}", json=payload, timeout=20)
                    
                    if response.status_code == 200:
                        successful_endpoints += 1
                    else:
                        print(f"   Failed endpoint: {method} {endpoint} - Status: {response.status_code}")
                        
                except Exception as e:
                    print(f"   Error testing endpoint {method} {endpoint}: {str(e)}")
            
            success_rate = (successful_endpoints / total_endpoints) * 100
            
            if success_rate == 100.0:
                self.log_test("API Endpoints Success Rate", True, 
                            f"100% success rate achieved: {successful_endpoints}/{total_endpoints} endpoints", 
                            {'success_rate': success_rate})
                return True
            else:
                self.log_test("API Endpoints Success Rate", False, 
                            f"Success rate {success_rate:.1f}%: {successful_endpoints}/{total_endpoints} endpoints", 
                            {'success_rate': success_rate})
                return False
                
        except Exception as e:
            self.log_test("API Endpoints Success Rate", False, f"Request failed: {str(e)}")
            return False
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all comprehensive backend tests for final system validation"""
        print(f"\n🚀 Starting Comprehensive Coastal Oak Capital Final System Tests")
        print(f"Backend URL: {self.base_url}")
        print(f"Focus: Final comprehensive system with 8 sections, living document features")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Comprehensive test sequence
        tests = [
            ("Enhanced Document Creation (8 Sections)", self.test_enhanced_document_creation_8_sections),
            ("Living Master Deck Title/Version Validation", self.test_living_master_deck_title_and_version),
            ("8 Comprehensive Sections Content Validation", self.test_comprehensive_8_sections_content),
            ("Daily Refresh Endpoint (/api/system/refresh-all)", self.test_daily_refresh_endpoint),
            ("Real-Time Data Integration Across All Sections", self.test_real_time_data_integration_all_sections),
            ("Comprehensive Markdown Export", self.test_comprehensive_markdown_export),
            ("100% API Endpoints Success Rate", self.test_api_endpoints_success_rate)
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
        print(f"🏁 COMPREHENSIVE FINAL SYSTEM TEST SUMMARY")
        print(f"Total Tests: {passed + failed}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%" if (passed + failed) > 0 else "0%")
        
        if self.created_document_id:
            print(f"📄 Created Document ID: {self.created_document_id}")
        
        return {
            'total_tests': passed + failed,
            'passed': passed,
            'failed': failed,
            'success_rate': (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0,
            'created_document_id': self.created_document_id,
            'test_results': self.test_results,
            'backend_url': self.base_url
        }


def main():
    """Main comprehensive test execution"""
    tester = ComprehensiveCoastalOakTester()
    results = tester.run_comprehensive_tests()
    
    # Save detailed results to file
    with open('/app/comprehensive_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📊 Detailed results saved to: /app/comprehensive_test_results.json")
    
    # Return exit code based on results
    return 0 if results['failed'] == 0 else 1


if __name__ == "__main__":
    exit(main())