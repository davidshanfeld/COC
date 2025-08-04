#!/usr/bin/env python3
"""
Enhanced Backend Testing for Coastal Oak Capital - Validating New Content
Tests specifically for PICO case study and AI data center modular grid infrastructure
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class EnhancedCoastalOakTester:
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
    
    def test_enhanced_document_creation(self) -> bool:
        """Test document creation with enhanced content (7 sections)"""
        try:
            response = self.session.post(f"{self.base_url}/document/create", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('success'):
                    self.log_test("Enhanced Document Creation", False, 
                                f"API returned success=false: {data.get('message', 'No message')}", data)
                    return False
                
                # Store document ID for subsequent tests
                self.created_document_id = data.get('document_id')
                sections_count = data.get('sections_count', 0)
                
                # Validate enhanced content - should have 7 sections now
                if sections_count != 7:
                    self.log_test("Enhanced Document Creation", False, 
                                f"Expected 7 sections, got {sections_count}", data)
                    return False
                
                self.log_test("Enhanced Document Creation", True, 
                            f"Document created with {sections_count} sections (enhanced content)", 
                            {'document_id': self.created_document_id, 'sections': sections_count})
                return True
                
            else:
                self.log_test("Enhanced Document Creation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Document Creation", False, f"Request failed: {str(e)}")
            return False
    
    def test_pico_case_study_content(self) -> bool:
        """Test PICO Boulevard case study content validation"""
        if not self.created_document_id:
            self.log_test("PICO Case Study Content", False, "No document ID available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/document/{self.created_document_id}", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                document = data.get('document', {})
                sections = document.get('sections', [])
                
                # Find PICO case study section
                pico_section = None
                for section in sections:
                    if 'PICO' in section.get('title', ''):
                        pico_section = section
                        break
                
                if not pico_section:
                    self.log_test("PICO Case Study Content", False, 
                                "PICO Boulevard case study section not found", data)
                    return False
                
                # Validate PICO content requirements
                content = pico_section.get('content', '').lower()
                required_elements = [
                    'investment discipline',
                    'floor-to-ceiling glass',
                    'business model',
                    'heat-to-energy',
                    'data center cooling',
                    'when to say no'
                ]
                
                missing_elements = []
                for element in required_elements:
                    if element not in content:
                        missing_elements.append(element)
                
                if missing_elements:
                    self.log_test("PICO Case Study Content", False, 
                                f"Missing required elements: {missing_elements}", 
                                {'section_title': pico_section.get('title'), 'content_length': len(content)})
                    return False
                
                # Check section order (should be section 6)
                if pico_section.get('order') != 6:
                    self.log_test("PICO Case Study Content", False, 
                                f"PICO section has wrong order: {pico_section.get('order')} (expected 6)", data)
                    return False
                
                self.log_test("PICO Case Study Content", True, 
                            f"PICO case study validated with all required elements", 
                            {'section_order': pico_section.get('order'), 'content_length': len(pico_section.get('content', ''))})
                return True
                
            else:
                self.log_test("PICO Case Study Content", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PICO Case Study Content", False, f"Request failed: {str(e)}")
            return False
    
    def test_ai_data_center_strategy_content(self) -> bool:
        """Test AI Data Center Modular Grid Infrastructure content validation"""
        if not self.created_document_id:
            self.log_test("AI Data Center Strategy Content", False, "No document ID available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/document/{self.created_document_id}", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                document = data.get('document', {})
                sections = document.get('sections', [])
                
                # Find AI Data Center section
                ai_section = None
                for section in sections:
                    if 'AI Data Center' in section.get('title', ''):
                        ai_section = section
                        break
                
                if not ai_section:
                    self.log_test("AI Data Center Strategy Content", False, 
                                "AI Data Center strategy section not found", data)
                    return False
                
                # Validate AI Data Center content requirements
                content = ai_section.get('content', '').lower()
                required_elements = [
                    'modular grid infrastructure',
                    'heat-to-energy conversion',
                    'financial model',
                    'edge computing',
                    'power density',
                    'cooling requirements',
                    'grid integration',
                    'revenue streams'
                ]
                
                missing_elements = []
                for element in required_elements:
                    if element not in content:
                        missing_elements.append(element)
                
                if missing_elements:
                    self.log_test("AI Data Center Strategy Content", False, 
                                f"Missing required elements: {missing_elements}", 
                                {'section_title': ai_section.get('title'), 'content_length': len(content)})
                    return False
                
                # Check section order (should be section 4)
                if ai_section.get('order') != 4:
                    self.log_test("AI Data Center Strategy Content", False, 
                                f"AI Data Center section has wrong order: {ai_section.get('order')} (expected 4)", data)
                    return False
                
                # Check content length (should be substantial)
                if len(ai_section.get('content', '')) < 5000:
                    self.log_test("AI Data Center Strategy Content", False, 
                                f"AI Data Center content too short: {len(ai_section.get('content', ''))} characters", data)
                    return False
                
                self.log_test("AI Data Center Strategy Content", True, 
                            f"AI Data Center strategy validated with all required elements", 
                            {'section_order': ai_section.get('order'), 'content_length': len(ai_section.get('content', ''))})
                return True
                
            else:
                self.log_test("AI Data Center Strategy Content", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("AI Data Center Strategy Content", False, f"Request failed: {str(e)}")
            return False
    
    def test_enhanced_markdown_export(self) -> bool:
        """Test markdown export with enhanced content"""
        if not self.created_document_id:
            self.log_test("Enhanced Markdown Export", False, "No document ID available")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/document/{self.created_document_id}/export/markdown", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                content = data.get('content', '')
                
                if not data.get('success'):
                    self.log_test("Enhanced Markdown Export", False, 
                                f"API returned success=false", data)
                    return False
                
                # Check for enhanced content in markdown
                required_content = [
                    'PICO Boulevard Property',
                    'AI Data Center Modular Grid Infrastructure',
                    'investment discipline',
                    'heat-to-energy conversion',
                    'floor-to-ceiling glass',
                    'modular grid architecture'
                ]
                
                missing_content = []
                for content_item in required_content:
                    if content_item.lower() not in content.lower():
                        missing_content.append(content_item)
                
                if missing_content:
                    self.log_test("Enhanced Markdown Export", False, 
                                f"Missing content in markdown: {missing_content}", 
                                {'content_length': len(content)})
                    return False
                
                # Check section count in markdown
                section_count = content.count('## Section')
                if section_count != 7:
                    self.log_test("Enhanced Markdown Export", False, 
                                f"Expected 7 sections in markdown, found {section_count}", data)
                    return False
                
                # Check content length (should be substantial with enhanced content)
                if len(content) < 30000:
                    self.log_test("Enhanced Markdown Export", False, 
                                f"Markdown content too short: {len(content)} characters (expected >30,000)", data)
                    return False
                
                self.log_test("Enhanced Markdown Export", True, 
                            f"Enhanced markdown export validated with all content", 
                            {'content_length': len(content), 'sections': section_count})
                return True
                
            else:
                self.log_test("Enhanced Markdown Export", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Markdown Export", False, f"Request failed: {str(e)}")
            return False
    
    def test_real_time_data_integration_with_enhanced_content(self) -> bool:
        """Test that real-time data integrates properly with enhanced sections"""
        try:
            response = self.session.get(f"{self.base_url}/data/live", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('success'):
                    self.log_test("Real-Time Data Integration", False, 
                                f"API returned success=false: {data.get('message', 'No message')}", data)
                    return False
                
                # Check that we have all expected data sources
                market_data = data.get('data', {})
                expected_sources = [
                    'fed_funds_rate', '10_year_treasury', 'cpi_inflation', 
                    'construction_cost_index', 'commercial_electricity_rate',
                    'cmbs_spread', 'cap_rates_office', 'distressed_debt_discount'
                ]
                
                missing_sources = [source for source in expected_sources if source not in market_data]
                
                if missing_sources:
                    self.log_test("Real-Time Data Integration", False, 
                                f"Missing data sources: {missing_sources}", data)
                    return False
                
                # Validate that enhanced sections can use this data
                if self.created_document_id:
                    # Test document update with new data
                    update_payload = {"document_id": self.created_document_id, "force_refresh": True}
                    update_response = self.session.post(f"{self.base_url}/document/{self.created_document_id}/update", 
                                                       json=update_payload, timeout=20)
                    
                    if update_response.status_code != 200:
                        self.log_test("Real-Time Data Integration", False, 
                                    f"Failed to update document with new data: {update_response.status_code}")
                        return False
                
                self.log_test("Real-Time Data Integration", True, 
                            f"Real-time data integration working with {len(market_data)} sources", 
                            {'sources_count': len(market_data), 'sample_sources': list(market_data.keys())[:3]})
                return True
                
            else:
                self.log_test("Real-Time Data Integration", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Real-Time Data Integration", False, f"Request failed: {str(e)}")
            return False
    
    def run_enhanced_tests(self) -> Dict[str, Any]:
        """Run all enhanced backend tests focusing on new content"""
        print(f"\n🚀 Starting Enhanced Coastal Oak Capital Backend Tests")
        print(f"Backend URL: {self.base_url}")
        print(f"Focus: PICO case study and AI data center modular grid infrastructure")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Enhanced test sequence
        tests = [
            ("Enhanced Document Creation (7 Sections)", self.test_enhanced_document_creation),
            ("PICO Case Study Content Validation", self.test_pico_case_study_content),
            ("AI Data Center Strategy Content Validation", self.test_ai_data_center_strategy_content),
            ("Enhanced Markdown Export", self.test_enhanced_markdown_export),
            ("Real-Time Data Integration with Enhanced Content", self.test_real_time_data_integration_with_enhanced_content)
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
        print(f"🏁 ENHANCED TEST SUMMARY")
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
    """Main enhanced test execution"""
    tester = EnhancedCoastalOakTester()
    results = tester.run_enhanced_tests()
    
    # Save detailed results to file
    with open('/app/enhanced_backend_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📊 Detailed results saved to: /app/enhanced_backend_test_results.json")
    
    # Return exit code based on results
    return 0 if results['failed'] == 0 else 1


if __name__ == "__main__":
    exit(main())