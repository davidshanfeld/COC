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
        self.access_token = None
        
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
    
    def test_daily_refresh_endpoint(self) -> bool:
        """Test POST /api/system/refresh-all - Daily refresh endpoint for living document functionality"""
        try:
            response = self.session.post(f"{self.base_url}/system/refresh-all", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'refreshed_count', 'total_documents', 'timestamp', 'message']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Daily Refresh Endpoint", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                if not data.get('success'):
                    self.log_test("Daily Refresh Endpoint", False, 
                                f"API returned success=false: {data.get('message', 'No message')}", data)
                    return False
                
                # Check refresh results
                refreshed_count = data.get('refreshed_count', 0)
                total_documents = data.get('total_documents', 0)
                
                if total_documents == 0:
                    self.log_test("Daily Refresh Endpoint", False, 
                                f"No documents found to refresh", data)
                    return False
                
                if refreshed_count == 0:
                    self.log_test("Daily Refresh Endpoint", False, 
                                f"No documents were refreshed despite {total_documents} total documents", data)
                    return False
                
                # Validate message content
                message = data.get('message', '')
                if 'refresh completed' not in message.lower():
                    self.log_test("Daily Refresh Endpoint", False, 
                                f"Unexpected message format: {message}", data)
                    return False
                
                self.log_test("Daily Refresh Endpoint", True, 
                            f"Daily refresh completed successfully - {refreshed_count}/{total_documents} documents updated", 
                            {'refreshed': refreshed_count, 'total': total_documents})
                return True
                
            else:
                self.log_test("Daily Refresh Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Daily Refresh Endpoint", False, f"Request failed: {str(e)}")
            return False

    # ======= V1.3.0 ENDPOINTS TESTING =======
    
    def test_healthz_deps_endpoint(self) -> bool:
        """Test GET /api/healthz/deps - Dependency health check"""
        try:
            response = self.session.get(f"{self.base_url}/healthz/deps", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'status', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Healthz Deps Endpoint", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                if not data.get('success'):
                    self.log_test("Healthz Deps Endpoint", False, 
                                f"API returned success=false", data)
                    return False
                
                # Check status structure
                status = data.get('status', {})
                required_status_fields = ['mongo', 'fred_api_key', 'weasyprint', 'agents_registered']
                missing_status_fields = [field for field in required_status_fields if field not in status]
                
                if missing_status_fields:
                    self.log_test("Healthz Deps Endpoint", False, 
                                f"Missing status fields: {missing_status_fields}", data)
                    return False
                
                # Validate specific requirements
                mongo_status = status.get('mongo')
                fred_api_key = status.get('fred_api_key')
                weasyprint = status.get('weasyprint')
                agents_registered = status.get('agents_registered', 0)
                
                if mongo_status != "connected":
                    self.log_test("Healthz Deps Endpoint", False, 
                                f"MongoDB not connected: {mongo_status}", data)
                    return False
                
                if not isinstance(fred_api_key, bool):
                    self.log_test("Healthz Deps Endpoint", False, 
                                f"FRED API key should be boolean: {fred_api_key}", data)
                    return False
                
                if not isinstance(weasyprint, bool):
                    self.log_test("Healthz Deps Endpoint", False, 
                                f"WeasyPrint should be boolean: {weasyprint}", data)
                    return False
                
                if agents_registered < 1:
                    self.log_test("Healthz Deps Endpoint", False, 
                                f"Expected >= 1 agents registered, got: {agents_registered}", data)
                    return False
                
                self.log_test("Healthz Deps Endpoint", True, 
                            f"All dependencies healthy - Mongo: {mongo_status}, FRED: {fred_api_key}, WeasyPrint: {weasyprint}, Agents: {agents_registered}", 
                            status)
                return True
                
            else:
                self.log_test("Healthz Deps Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Healthz Deps Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_rates_history_endpoint(self) -> bool:
        """Test GET /api/rates/history?days=180 - Historical rates data"""
        try:
            response = self.session.get(f"{self.base_url}/rates/history?days=180", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'data', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Rates History Endpoint", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                if not data.get('success'):
                    self.log_test("Rates History Endpoint", False, 
                                f"API returned success=false", data)
                    return False
                
                # Check data structure
                rates_data = data.get('data', {})
                required_keys = ['5Y', '10Y', '30Y', 'DFF']
                missing_keys = [key for key in required_keys if key not in rates_data]
                
                if missing_keys:
                    self.log_test("Rates History Endpoint", False, 
                                f"Missing data keys: {missing_keys}", data)
                    return False
                
                # Validate each rate series has data
                for key in required_keys:
                    series_data = rates_data.get(key, [])
                    if not isinstance(series_data, list):
                        self.log_test("Rates History Endpoint", False, 
                                    f"Key {key} should be array, got: {type(series_data)}", data)
                        return False
                    
                    if len(series_data) == 0:
                        self.log_test("Rates History Endpoint", False, 
                                    f"Key {key} has no data", data)
                        return False
                    
                    # Check first item structure (should have date/value)
                    if series_data:
                        first_item = series_data[0]
                        if not isinstance(first_item, dict) or 'date' not in first_item or 'value' not in first_item:
                            self.log_test("Rates History Endpoint", False, 
                                        f"Key {key} items should have date/value structure", data)
                            return False
                
                self.log_test("Rates History Endpoint", True, 
                            f"Historical rates data retrieved successfully - 5Y: {len(rates_data['5Y'])} points, 10Y: {len(rates_data['10Y'])} points, 30Y: {len(rates_data['30Y'])} points, DFF: {len(rates_data['DFF'])} points", 
                            {key: len(rates_data[key]) for key in required_keys})
                return True
                
            else:
                self.log_test("Rates History Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Rates History Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_execsum_pdf_endpoint(self) -> bool:
        """Test GET /api/execsum.pdf - Executive summary PDF or HTML fallback"""
        try:
            response = self.session.get(f"{self.base_url}/execsum.pdf", timeout=15)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                
                # Should return either PDF or HTML with fallback header
                if content_type == 'application/pdf':
                    # PDF response
                    if len(response.content) < 100:  # PDF should be substantial
                        self.log_test("Execsum PDF Endpoint", False, 
                                    f"PDF content too small: {len(response.content)} bytes")
                        return False
                    
                    self.log_test("Execsum PDF Endpoint", True, 
                                f"PDF generated successfully - {len(response.content)} bytes", 
                                {'content_type': content_type, 'size_bytes': len(response.content)})
                    return True
                    
                elif 'text/html' in content_type:
                    # HTML fallback
                    fallback_header = response.headers.get('X-PDF-Mode')
                    if fallback_header != 'fallback-html':
                        self.log_test("Execsum PDF Endpoint", False, 
                                    f"HTML fallback missing proper header: {fallback_header}")
                        return False
                    
                    html_content = response.text
                    if len(html_content) < 100:
                        self.log_test("Execsum PDF Endpoint", False, 
                                    f"HTML content too small: {len(html_content)} characters")
                        return False
                    
                    # Check for basic HTML structure
                    if '<html>' not in html_content or '<body>' not in html_content:
                        self.log_test("Execsum PDF Endpoint", False, 
                                    f"Invalid HTML structure")
                        return False
                    
                    self.log_test("Execsum PDF Endpoint", True, 
                                f"HTML fallback working correctly - {len(html_content)} characters", 
                                {'content_type': content_type, 'fallback_header': fallback_header, 'size_chars': len(html_content)})
                    return True
                    
                else:
                    self.log_test("Execsum PDF Endpoint", False, 
                                f"Unexpected content type: {content_type}")
                    return False
                
            else:
                self.log_test("Execsum PDF Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Execsum PDF Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_deck_request_endpoint(self) -> bool:
        """Test POST /api/deck/request - Request secure access token"""
        try:
            payload = {"email": "test@example.com"}
            response = self.session.post(f"{self.base_url}/deck/request", json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure - updated for actual API response
                required_fields = ['token', 'expiresAt']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Deck Request Endpoint", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                # Validate token
                access_token = data.get('token')
                if not access_token or len(access_token) < 10:
                    self.log_test("Deck Request Endpoint", False, 
                                f"Invalid access token: {access_token}", data)
                    return False
                
                # Validate expires_at format
                expires_at = data.get('expiresAt')
                if not expires_at:
                    self.log_test("Deck Request Endpoint", False, 
                                f"Missing expiresAt", data)
                    return False
                
                # Store token for download test
                self.access_token = access_token
                
                self.log_test("Deck Request Endpoint", True, 
                            f"Access token issued successfully - Token: {access_token[:8]}..., Expires: {expires_at}", 
                            {'token_length': len(access_token), 'expires_at': expires_at})
                return True
                
            else:
                self.log_test("Deck Request Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Deck Request Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_deck_download_endpoint(self) -> bool:
        """Test GET /api/deck/download?token=... - Single-use token download with comprehensive enforcement testing"""
        if not hasattr(self, 'access_token') or not self.access_token:
            self.log_test("Deck Download Endpoint", False, "No access token available (deck request test must run first)")
            return False
        
        try:
            # First download - should succeed
            response1 = self.session.get(f"{self.base_url}/deck/download?token={self.access_token}", timeout=15)
            
            if response1.status_code == 200:
                content_type = response1.headers.get('content-type', '').lower()
                
                # Should return either PDF or HTML
                if content_type == 'application/pdf':
                    if len(response1.content) < 100:
                        self.log_test("Deck Download Endpoint", False, 
                                    f"PDF content too small: {len(response1.content)} bytes")
                        return False
                elif 'text/html' in content_type:
                    if len(response1.text) < 100:
                        self.log_test("Deck Download Endpoint", False, 
                                    f"HTML content too small: {len(response1.text)} characters")
                        return False
                else:
                    self.log_test("Deck Download Endpoint", False, 
                                f"Unexpected content type: {content_type}")
                    return False
                
                # Second download - should fail with 403 (token already used)
                response2 = self.session.get(f"{self.base_url}/deck/download?token={self.access_token}", timeout=10)
                
                if response2.status_code != 403:
                    self.log_test("Deck Download Endpoint", False, 
                                f"Second download should return 403, got: {response2.status_code}. Single-use enforcement FAILED!")
                    return False
                
                # Check error message for "token already used"
                try:
                    error_data = response2.json()
                    error_detail = error_data.get('detail', '').lower()
                    if 'token already used' not in error_detail:
                        self.log_test("Deck Download Endpoint", False, 
                                    f"Expected 'token already used' error message, got: {error_detail}")
                        return False
                except:
                    # If not JSON, check text response
                    if 'token already used' not in response2.text.lower():
                        self.log_test("Deck Download Endpoint", False, 
                                    f"Expected 'token already used' error message in response")
                        return False
                
                # Third download attempt - should also fail with 403
                response3 = self.session.get(f"{self.base_url}/deck/download?token={self.access_token}", timeout=10)
                
                if response3.status_code != 403:
                    self.log_test("Deck Download Endpoint", False, 
                                f"Third download should also return 403, got: {response3.status_code}")
                    return False
                
                self.log_test("Deck Download Endpoint", True, 
                            f"✅ SINGLE-USE TOKEN ENFORCEMENT WORKING CORRECTLY - First download: {response1.status_code} ({content_type}), Second download: {response2.status_code} (blocked), Third download: {response3.status_code} (blocked)", 
                            {'first_response': response1.status_code, 'second_response': response2.status_code, 'third_response': response3.status_code, 'content_type': content_type})
                return True
                
            elif response1.status_code == 403:
                self.log_test("Deck Download Endpoint", False, 
                            f"First download failed with 403 - token may be invalid or expired")
                return False
            elif response1.status_code == 404:
                self.log_test("Deck Download Endpoint", False, 
                            f"First download failed with 404 - invalid token")
                return False
            else:
                self.log_test("Deck Download Endpoint", False, 
                            f"HTTP {response1.status_code}: {response1.text}")
                return False
                
        except Exception as e:
            self.log_test("Deck Download Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_invalid_token_scenario(self) -> bool:
        """Test GET /api/deck/download with invalid token - should return 404"""
        try:
            invalid_token = "tok_invalid123456789"
            response = self.session.get(f"{self.base_url}/deck/download?token={invalid_token}", timeout=10)
            
            if response.status_code == 404:
                # Check error message
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', '').lower()
                    if 'invalid token' in error_detail:
                        self.log_test("Invalid Token Scenario", True, 
                                    f"Invalid token correctly rejected with 404 and proper error message: {error_detail}")
                        return True
                    else:
                        self.log_test("Invalid Token Scenario", False, 
                                    f"Expected 'invalid token' error message, got: {error_detail}")
                        return False
                except:
                    # If not JSON, still pass if 404
                    self.log_test("Invalid Token Scenario", True, 
                                f"Invalid token correctly rejected with 404")
                    return True
            else:
                self.log_test("Invalid Token Scenario", False, 
                            f"Expected 404 for invalid token, got: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Token Scenario", False, f"Request failed: {str(e)}")
            return False
    
    def test_concurrent_token_usage(self) -> bool:
        """Test concurrent access with same token to verify race condition protection"""
        try:
            # Get a fresh token for this test
            payload = {"email": "concurrent@example.com"}
            token_response = self.session.post(f"{self.base_url}/deck/request", json=payload, timeout=15)
            
            if token_response.status_code != 200:
                self.log_test("Concurrent Token Usage", False, 
                            f"Failed to get token for concurrent test: {token_response.status_code}")
                return False
            
            token_data = token_response.json()
            concurrent_token = token_data.get('token')
            
            if not concurrent_token:
                self.log_test("Concurrent Token Usage", False, 
                            f"No token received for concurrent test")
                return False
            
            import threading
            import time
            
            results = []
            
            def download_attempt(token, attempt_id):
                try:
                    response = self.session.get(f"{self.base_url}/deck/download?token={token}", timeout=10)
                    results.append({
                        'attempt_id': attempt_id,
                        'status_code': response.status_code,
                        'success': response.status_code == 200
                    })
                except Exception as e:
                    results.append({
                        'attempt_id': attempt_id,
                        'status_code': 'error',
                        'success': False,
                        'error': str(e)
                    })
            
            # Launch 3 concurrent download attempts
            threads = []
            for i in range(3):
                thread = threading.Thread(target=download_attempt, args=(concurrent_token, i+1))
                threads.append(thread)
            
            # Start all threads nearly simultaneously
            for thread in threads:
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Analyze results
            successful_downloads = [r for r in results if r['success']]
            failed_downloads = [r for r in results if not r['success']]
            
            if len(successful_downloads) == 1 and len(failed_downloads) == 2:
                self.log_test("Concurrent Token Usage", True, 
                            f"✅ RACE CONDITION PROTECTION WORKING - Only 1 of 3 concurrent attempts succeeded, 2 were blocked", 
                            {'successful': len(successful_downloads), 'failed': len(failed_downloads), 'results': results})
                return True
            elif len(successful_downloads) > 1:
                self.log_test("Concurrent Token Usage", False, 
                            f"❌ RACE CONDITION DETECTED - {len(successful_downloads)} concurrent downloads succeeded (should be only 1)", 
                            {'successful': len(successful_downloads), 'failed': len(failed_downloads), 'results': results})
                return False
            else:
                self.log_test("Concurrent Token Usage", False, 
                            f"Unexpected result - {len(successful_downloads)} successful, {len(failed_downloads)} failed", 
                            {'results': results})
                return False
                
        except Exception as e:
            self.log_test("Concurrent Token Usage", False, f"Request failed: {str(e)}")
            return False
    
    def test_audit_endpoint(self) -> bool:
        """Test GET /api/audit - Audit log entries"""
        try:
            response = self.session.get(f"{self.base_url}/audit", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'data', 'count']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Audit Endpoint", False, 
                                f"Missing required fields: {missing_fields}", data)
                    return False
                
                if not data.get('success'):
                    self.log_test("Audit Endpoint", False, 
                                f"API returned success=false", data)
                    return False
                
                # Check audit entries
                audit_entries = data.get('data', [])
                count = data.get('count', 0)
                
                if count != len(audit_entries):
                    self.log_test("Audit Endpoint", False, 
                                f"Count mismatch: count={count}, actual={len(audit_entries)}", data)
                    return False
                
                # Check for expected events (token_issued, deck_download_pdf or deck_download_html_fallback)
                expected_events = ['token_issued']
                found_events = []
                
                for entry in audit_entries:
                    action = entry.get('action', '')
                    if action in expected_events or action.startswith('deck_download'):
                        found_events.append(action)
                
                if not found_events:
                    self.log_test("Audit Endpoint", False, 
                                f"No expected audit events found. Expected: {expected_events} or deck_download_*", data)
                    return False
                
                # Validate audit entry structure
                if audit_entries:
                    sample_entry = audit_entries[0]
                    # Handle mixed audit log formats
                    if 'action' in sample_entry and 'details' in sample_entry:
                        # New format
                        required_entry_fields = ['action', 'details', 'timestamp']
                    elif 'event' in sample_entry and 'meta' in sample_entry:
                        # Agent system format
                        required_entry_fields = ['event', 'meta', 'timestamp']
                    else:
                        self.log_test("Audit Endpoint", False, 
                                    f"Unknown audit entry format: {sample_entry.keys()}", data)
                        return False
                    
                    missing_entry_fields = [field for field in required_entry_fields if field not in sample_entry]
                    
                    if missing_entry_fields:
                        self.log_test("Audit Endpoint", False, 
                                    f"Audit entry missing fields: {missing_entry_fields}", data)
                        return False
                
                self.log_test("Audit Endpoint", True, 
                            f"Audit log retrieved successfully - {count} entries, found events: {found_events}", 
                            {'count': count, 'found_events': found_events})
                return True
                
            else:
                self.log_test("Audit Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Audit Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_footnotes_endpoint(self) -> bool:
        """Test GET /api/footnotes - Footnotes and citations (updated for v1.3.x)"""
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
                
                # Check footnotes data
                footnotes_data = data.get('data', {})
                footnotes = footnotes_data.get('footnotes', [])
                
                # Check for required footnote IDs (updated for v1.3.x with new regulatory/FDIC footnotes)
                required_ids = ['F1', 'T1', 'M1', 'B1', 'H1', 'R1', 'S1', 'C1', 
                               'NEVI', 'ITC30C', 'AB1236', 'AB970', 'CEQA32', 
                               'LAZ1', 'LACode', 'LAGP', 'LADBS']
                found_ids = [footnote.get('id') for footnote in footnotes]
                missing_ids = [id for id in required_ids if id not in found_ids]
                
                if missing_ids:
                    self.log_test("Footnotes Endpoint", False, 
                                f"Missing required footnote IDs: {missing_ids}", data)
                    return False
                
                # Check total count should be 16 now
                total_count = footnotes_data.get('total_count', len(footnotes))
                if total_count < 16:
                    self.log_test("Footnotes Endpoint", False, 
                                f"Expected at least 16 footnotes, got: {total_count}", data)
                    return False
                
                # Validate footnote structure
                for footnote in footnotes[:3]:  # Check first 3
                    required_footnote_fields = ['id', 'label', 'source', 'retrieved_at']
                    missing_footnote_fields = [field for field in required_footnote_fields if field not in footnote]
                    
                    if missing_footnote_fields:
                        self.log_test("Footnotes Endpoint", False, 
                                    f"Footnote {footnote.get('id')} missing fields: {missing_footnote_fields}", data)
                        return False
                
                self.log_test("Footnotes Endpoint", True, 
                            f"Footnotes retrieved successfully - {len(footnotes)} entries including all required IDs (16 total expected)", 
                            {'total_footnotes': len(footnotes), 'required_ids_found': len(required_ids), 'new_regulatory_ids': ['NEVI', 'ITC30C', 'AB1236', 'AB970', 'CEQA32', 'LAZ1', 'LACode', 'LAGP', 'LADBS']})
                return True
                
            else:
                self.log_test("Footnotes Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Footnotes Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    # ======= REGRESSION TESTING =======
    
    def test_rates_endpoint(self) -> bool:
        """Test GET /api/rates - Current rates (regression test)"""
        try:
            response = self.session.get(f"{self.base_url}/rates", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('success'):
                    self.log_test("Rates Endpoint (Regression)", False, 
                                f"API returned success=false", data)
                    return False
                
                # Check basic structure
                rates_data = data.get('data', {})
                if 'treasury_rates' not in rates_data or 'fed_funds_rate' not in rates_data:
                    self.log_test("Rates Endpoint (Regression)", False, 
                                f"Missing treasury_rates or fed_funds_rate", data)
                    return False
                
                self.log_test("Rates Endpoint (Regression)", True, 
                            f"Current rates endpoint working", 
                            {'has_treasury': 'treasury_rates' in rates_data, 'has_fed_funds': 'fed_funds_rate' in rates_data})
                return True
                
            else:
                self.log_test("Rates Endpoint (Regression)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Rates Endpoint (Regression)", False, f"Request failed: {str(e)}")
            return False
    
    def test_maturities_endpoint(self) -> bool:
        """Test GET /api/maturities - CRE maturities (regression test)"""
        try:
            response = self.session.get(f"{self.base_url}/maturities", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('success'):
                    self.log_test("Maturities Endpoint (Regression)", False, 
                                f"API returned success=false", data)
                    return False
                
                # Check basic structure
                if 'data' not in data:
                    self.log_test("Maturities Endpoint (Regression)", False, 
                                f"Missing data field", data)
                    return False
                
                self.log_test("Maturities Endpoint (Regression)", True, 
                            f"CRE maturities endpoint working")
                return True
                
            else:
                self.log_test("Maturities Endpoint (Regression)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Maturities Endpoint (Regression)", False, f"Request failed: {str(e)}")
            return False
    
    def test_banks_endpoint(self) -> bool:
        """Test GET /api/banks - FDIC data (regression test)"""
        try:
            response = self.session.get(f"{self.base_url}/banks", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('success'):
                    self.log_test("Banks Endpoint (Regression)", False, 
                                f"API returned success=false", data)
                    return False
                
                # Check basic structure
                if 'data' not in data:
                    self.log_test("Banks Endpoint (Regression)", False, 
                                f"Missing data field", data)
                    return False
                
                self.log_test("Banks Endpoint (Regression)", True, 
                            f"FDIC banks endpoint working")
                return True
                
            else:
                self.log_test("Banks Endpoint (Regression)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Banks Endpoint (Regression)", False, f"Request failed: {str(e)}")
            return False
    
    def test_agents_execute_endpoint(self) -> bool:
        """Test POST /api/agents/execute - Agent execution (regression test)"""
        try:
            payload = {
                "objective": "Test agent execution for regression testing",
                "audience": "LP",
                "inputs": {"test": "regression"},
                "security_tier": "public",
                "tags": ["charts", "ui"]  # Add required tags field
            }
            response = self.session.post(f"{self.base_url}/agents/execute", json=payload, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('success'):
                    self.log_test("Agents Execute Endpoint (Regression)", False, 
                                f"API returned success=false", data)
                    return False
                
                # Check basic structure
                if 'result' not in data or 'agents_executed' not in data:
                    self.log_test("Agents Execute Endpoint (Regression)", False, 
                                f"Missing result or agents_executed field", data)
                    return False
                
                agents_executed = data.get('agents_executed', 0)
                if agents_executed < 1:
                    self.log_test("Agents Execute Endpoint (Regression)", False, 
                                f"No agents executed: {agents_executed}", data)
                    return False
                
                self.log_test("Agents Execute Endpoint (Regression)", True, 
                            f"Agent execution working - {agents_executed} agents executed")
                return True
                
            else:
                self.log_test("Agents Execute Endpoint (Regression)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Agents Execute Endpoint (Regression)", False, f"Request failed: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all backend API tests in sequence"""
        print(f"\n🚀 Starting Coastal Oak Capital Backend API Tests")
        print(f"Backend URL: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Test sequence - order matters for document tests and token-based tests
        tests = [
            ("System Status", self.test_status_endpoint),
            ("Live Data Integration", self.test_live_data_endpoint),
            ("Document Creation", self.test_document_create_endpoint),
            ("Document Retrieval", self.test_document_get_endpoint),
            ("Document Update", self.test_document_update_endpoint),
            ("Markdown Export", self.test_document_export_markdown_endpoint),
            ("Documents List", self.test_documents_list_endpoint),
            ("Daily Refresh System", self.test_daily_refresh_endpoint),
            
            # V1.3.0 New Endpoints
            ("V1.3.0 - Healthz Dependencies", self.test_healthz_deps_endpoint),
            ("V1.3.0 - Rates History", self.test_rates_history_endpoint),
            ("V1.3.0 - Executive Summary PDF", self.test_execsum_pdf_endpoint),
            ("V1.3.0 - Deck Request Token", self.test_deck_request_endpoint),
            ("V1.3.0 - Deck Download Single-Use", self.test_deck_download_endpoint),
            ("V1.3.0 - Invalid Token Scenario", self.test_invalid_token_scenario),
            ("V1.3.0 - Concurrent Token Usage (Race Condition Test)", self.test_concurrent_token_usage),
            ("V1.3.0 - Audit Logs", self.test_audit_endpoint),
            ("V1.3.0 - Footnotes", self.test_footnotes_endpoint),
            
            # Regression Tests
            ("Regression - Current Rates", self.test_rates_endpoint),
            ("Regression - CRE Maturities", self.test_maturities_endpoint),
            ("Regression - FDIC Banks", self.test_banks_endpoint),
            ("Regression - Agent Execution", self.test_agents_execute_endpoint)
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