#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Coastal Oak Capital Live Document System
Tests all endpoints with real-time data integration and error handling scenarios
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional

class CoastalOakAPITester:
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
    
    def test_status_endpoint(self) -> bool:
        """Test GET /api/status - System health and database connection"""
        try:
            response = self.session.get(f"{self.base_url}/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ['status', 'database', 'system', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Status Endpoint", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                # Check database connection
                if data.get('database') == 'connected' and data.get('status') == 'healthy':
                    self.log_test("Status Endpoint", True, 
                                "System healthy, database connected", data)
                    return True
                else:
                    self.log_test("Status Endpoint", False, 
                                f"System unhealthy: status={data.get('status')}, db={data.get('database')}", data)
                    return False
            else:
                self.log_test("Status Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Status Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_live_data_endpoint(self) -> bool:
        """Test GET /api/data/live - Real-time market data fetching"""
        try:
            response = self.session.get(f"{self.base_url}/data/live", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'data', 'timestamp', 'sources_count', 'message']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Live Data Endpoint", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                if not data.get('success'):
                    self.log_test("Live Data Endpoint", False, 
                                f"API returned success=false: {data.get('message', 'No message')}", data)
                    return False
                
                # Check data sources
                market_data = data.get('data', {})
                expected_sources = [
                    'fed_funds_rate', '10_year_treasury', 'cpi_inflation', 
                    'construction_cost_index', 'commercial_electricity_rate',
                    'cmbs_spread', 'cap_rates_office', 'distressed_debt_discount'
                ]
                
                missing_sources = [source for source in expected_sources if source not in market_data]
                
                if missing_sources:
                    self.log_test("Live Data Endpoint", False, 
                                f"Missing data sources: {missing_sources}", data)
                    return False
                
                # Validate data structure for key sources
                for source_name, source_data in market_data.items():
                    required_source_fields = ['value', 'unit', 'source', 'description', 'timestamp']
                    missing_source_fields = [field for field in required_source_fields if field not in source_data]
                    
                    if missing_source_fields:
                        self.log_test("Live Data Endpoint", False, 
                                    f"Source {source_name} missing fields: {missing_source_fields}", data)
                        return False
                
                self.log_test("Live Data Endpoint", True, 
                            f"Successfully fetched {len(market_data)} data sources with complete structure", 
                            {'sources_count': len(market_data), 'sample_sources': list(market_data.keys())[:3]})
                return True
                
            else:
                self.log_test("Live Data Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Live Data Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_document_create_endpoint(self) -> bool:
        """Test POST /api/document/create - Create comprehensive master deck"""
        try:
            response = self.session.post(f"{self.base_url}/document/create", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'document_id', 'title', 'sections_count', 'data_sources_count', 'last_updated', 'message']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Document Create Endpoint", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                if not data.get('success'):
                    self.log_test("Document Create Endpoint", False, 
                                f"API returned success=false: {data.get('message', 'No message')}", data)
                    return False
                
                # Store document ID for subsequent tests
                self.created_document_id = data.get('document_id')
                
                # Validate document structure
                if not self.created_document_id:
                    self.log_test("Document Create Endpoint", False, 
                                "No document_id returned", data)
                    return False
                
                sections_count = data.get('sections_count', 0)
                data_sources_count = data.get('data_sources_count', 0)
                
                if sections_count < 5:  # Expecting at least 5 major sections
                    self.log_test("Document Create Endpoint", False, 
                                f"Insufficient sections created: {sections_count} (expected >= 5)", data)
                    return False
                
                if data_sources_count < 8:  # Expecting at least 8 data sources
                    self.log_test("Document Create Endpoint", False, 
                                f"Insufficient data sources: {data_sources_count} (expected >= 8)", data)
                    return False
                
                self.log_test("Document Create Endpoint", True, 
                            f"Document created successfully with {sections_count} sections and {data_sources_count} data sources", 
                            {'document_id': self.created_document_id, 'sections': sections_count, 'data_sources': data_sources_count})
                return True
                
            else:
                self.log_test("Document Create Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Document Create Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_document_get_endpoint(self) -> bool:
        """Test GET /api/document/{document_id} - Retrieve created document"""
        if not self.created_document_id:
            self.log_test("Document Get Endpoint", False, "No document ID available (create test must run first)")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/document/{self.created_document_id}", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'document', 'export_formats', 'real_time_data_age']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Document Get Endpoint", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                if not data.get('success'):
                    self.log_test("Document Get Endpoint", False, 
                                f"API returned success=false", data)
                    return False
                
                # Validate document structure
                document = data.get('document', {})
                required_doc_fields = ['id', 'title', 'description', 'sections', 'data_sources', 'created_at', 'last_updated', 'version']
                missing_doc_fields = [field for field in required_doc_fields if field not in document]
                
                if missing_doc_fields:
                    self.log_test("Document Get Endpoint", False, 
                                f"Document missing required fields: {missing_doc_fields}", data)
                    return False
                
                # Check sections structure
                sections = document.get('sections', [])
                if len(sections) < 5:
                    self.log_test("Document Get Endpoint", False, 
                                f"Insufficient sections in document: {len(sections)}", data)
                    return False
                
                # Validate section structure
                for i, section in enumerate(sections[:2]):  # Check first 2 sections
                    required_section_fields = ['id', 'title', 'order', 'content', 'data_dependencies', 'last_updated']
                    missing_section_fields = [field for field in required_section_fields if field not in section]
                    
                    if missing_section_fields:
                        self.log_test("Document Get Endpoint", False, 
                                    f"Section {i} missing fields: {missing_section_fields}", data)
                        return False
                
                # Check data sources
                data_sources = document.get('data_sources', {})
                if len(data_sources) < 8:
                    self.log_test("Document Get Endpoint", False, 
                                f"Insufficient data sources: {len(data_sources)}", data)
                    return False
                
                self.log_test("Document Get Endpoint", True, 
                            f"Document retrieved successfully with {len(sections)} sections and {len(data_sources)} data sources", 
                            {'sections_count': len(sections), 'data_sources_count': len(data_sources)})
                return True
                
            elif response.status_code == 404:
                self.log_test("Document Get Endpoint", False, 
                            f"Document not found: {self.created_document_id}")
                return False
            else:
                self.log_test("Document Get Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Document Get Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_document_update_endpoint(self) -> bool:
        """Test POST /api/document/{document_id}/update - Update with latest data"""
        if not self.created_document_id:
            self.log_test("Document Update Endpoint", False, "No document ID available (create test must run first)")
            return False
        
        try:
            # Test with force_refresh=true
            payload = {"document_id": self.created_document_id, "force_refresh": True}
            response = self.session.post(f"{self.base_url}/document/{self.created_document_id}/update", 
                                       json=payload, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'data', 'sources_updated', 'timestamp', 'message']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Document Update Endpoint", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                if not data.get('success'):
                    self.log_test("Document Update Endpoint", False, 
                                f"API returned success=false: {data.get('message', 'No message')}", data)
                    return False
                
                # Check sources updated
                sources_updated = data.get('sources_updated', [])
                if len(sources_updated) < 5:  # Should update multiple sources
                    self.log_test("Document Update Endpoint", False, 
                                f"Too few sources updated: {len(sources_updated)}", data)
                    return False
                
                # Validate updated document structure
                updated_document = data.get('data', {})
                if not updated_document.get('id') == self.created_document_id:
                    self.log_test("Document Update Endpoint", False, 
                                f"Document ID mismatch after update", data)
                    return False
                
                self.log_test("Document Update Endpoint", True, 
                            f"Document updated successfully, {len(sources_updated)} sources refreshed", 
                            {'sources_updated': sources_updated[:3], 'total_updated': len(sources_updated)})
                return True
                
            elif response.status_code == 404:
                self.log_test("Document Update Endpoint", False, 
                            f"Document not found: {self.created_document_id}")
                return False
            else:
                self.log_test("Document Update Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Document Update Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_document_export_markdown_endpoint(self) -> bool:
        """Test GET /api/document/{document_id}/export/markdown - Export as markdown"""
        if not self.created_document_id:
            self.log_test("Document Export Markdown Endpoint", False, "No document ID available (create test must run first)")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/document/{self.created_document_id}/export/markdown", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'format', 'content', 'title', 'last_updated']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Document Export Markdown Endpoint", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                if not data.get('success'):
                    self.log_test("Document Export Markdown Endpoint", False, 
                                f"API returned success=false", data)
                    return False
                
                # Validate markdown content
                content = data.get('content', '')
                if len(content) < 1000:  # Should be substantial content
                    self.log_test("Document Export Markdown Endpoint", False, 
                                f"Markdown content too short: {len(content)} characters", data)
                    return False
                
                # Check for markdown formatting
                markdown_indicators = ['#', '**', '*', '---', '•']
                found_indicators = [indicator for indicator in markdown_indicators if indicator in content]
                
                if len(found_indicators) < 3:
                    self.log_test("Document Export Markdown Endpoint", False, 
                                f"Content doesn't appear to be properly formatted markdown", data)
                    return False
                
                # Check format field
                if data.get('format') != 'markdown':
                    self.log_test("Document Export Markdown Endpoint", False, 
                                f"Incorrect format field: {data.get('format')}", data)
                    return False
                
                self.log_test("Document Export Markdown Endpoint", True, 
                            f"Markdown export successful, {len(content)} characters generated", 
                            {'content_length': len(content), 'format': data.get('format')})
                return True
                
            elif response.status_code == 404:
                self.log_test("Document Export Markdown Endpoint", False, 
                            f"Document not found: {self.created_document_id}")
                return False
            else:
                self.log_test("Document Export Markdown Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Document Export Markdown Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_documents_list_endpoint(self) -> bool:
        """Test GET /api/documents/list - List all available documents"""
        try:
            response = self.session.get(f"{self.base_url}/documents/list", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'documents', 'count', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Documents List Endpoint", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                if not data.get('success'):
                    self.log_test("Documents List Endpoint", False, 
                                f"API returned success=false", data)
                    return False
                
                # Check documents list
                documents = data.get('documents', [])
                count = data.get('count', 0)
                
                if count != len(documents):
                    self.log_test("Documents List Endpoint", False, 
                                f"Count mismatch: count={count}, actual={len(documents)}", data)
                    return False
                
                # If we created a document, it should be in the list
                if self.created_document_id and count > 0:
                    found_created_doc = any(doc.get('_id') == self.created_document_id for doc in documents)
                    if not found_created_doc:
                        self.log_test("Documents List Endpoint", False, 
                                    f"Created document {self.created_document_id} not found in list", data)
                        return False
                
                # Validate document list structure
                if documents:
                    sample_doc = documents[0]
                    required_doc_fields = ['_id', 'title', 'description', 'last_updated', 'version']
                    missing_doc_fields = [field for field in required_doc_fields if field not in sample_doc]
                    
                    if missing_doc_fields:
                        self.log_test("Documents List Endpoint", False, 
                                    f"Document in list missing fields: {missing_doc_fields}", data)
                        return False
                
                self.log_test("Documents List Endpoint", True, 
                            f"Successfully listed {count} documents", 
                            {'count': count, 'has_created_doc': self.created_document_id in [doc.get('_id') for doc in documents] if self.created_document_id else False})
                return True
                
            else:
                self.log_test("Documents List Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Documents List Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all backend API tests in sequence"""
        print(f"\n🚀 Starting Coastal Oak Capital Backend API Tests")
        print(f"Backend URL: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Test sequence - order matters for document tests
        tests = [
            ("System Status", self.test_status_endpoint),
            ("Live Data Integration", self.test_live_data_endpoint),
            ("Document Creation", self.test_document_create_endpoint),
            ("Document Retrieval", self.test_document_get_endpoint),
            ("Document Update", self.test_document_update_endpoint),
            ("Markdown Export", self.test_document_export_markdown_endpoint),
            ("Documents List", self.test_documents_list_endpoint)
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
        print(f"🏁 TEST SUMMARY")
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
    """Main test execution"""
    tester = CoastalOakAPITester()
    results = tester.run_all_tests()
    
    # Save detailed results to file
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📊 Detailed results saved to: /app/backend_test_results.json")
    
    # Return exit code based on results
    return 0 if results['failed'] == 0 else 1


if __name__ == "__main__":
    exit(main())