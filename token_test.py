#!/usr/bin/env python3
"""
Focused Single-Use Token Enforcement Test
Tests the critical fix for /api/deck/download endpoint
"""

import requests
import json
import time
import threading
from datetime import datetime

class TokenEnforcementTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        self.base_url = self._get_backend_url()
        self.session = requests.Session()
        
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
    
    def test_single_use_enforcement(self):
        """Test the core single-use token enforcement"""
        print("🔐 Testing Single-Use Token Enforcement")
        print("=" * 50)
        
        # Step 1: Request a token
        print("1. Requesting access token...")
        payload = {"email": "test@example.com"}
        token_response = self.session.post(f"{self.base_url}/deck/request", json=payload, timeout=15)
        
        if token_response.status_code != 200:
            print(f"❌ FAIL: Token request failed with {token_response.status_code}")
            return False
        
        token_data = token_response.json()
        token = token_data.get('token')
        
        if not token:
            print(f"❌ FAIL: No token received")
            return False
        
        print(f"✅ Token received: {token[:8]}...")
        
        # Step 2: First download - should succeed
        print("2. First download attempt...")
        response1 = self.session.get(f"{self.base_url}/deck/download?token={token}", timeout=15)
        
        if response1.status_code != 200:
            print(f"❌ FAIL: First download failed with {response1.status_code}: {response1.text}")
            return False
        
        print(f"✅ First download succeeded ({response1.headers.get('content-type', 'unknown')})")
        
        # Step 3: Second download - should fail with 403
        print("3. Second download attempt (should fail)...")
        response2 = self.session.get(f"{self.base_url}/deck/download?token={token}", timeout=10)
        
        if response2.status_code != 403:
            print(f"❌ FAIL: Second download should return 403, got {response2.status_code}")
            print(f"Response: {response2.text}")
            return False
        
        # Check error message
        try:
            error_data = response2.json()
            error_detail = error_data.get('detail', '').lower()
            if 'token already used' not in error_detail:
                print(f"❌ FAIL: Expected 'token already used' error, got: {error_detail}")
                return False
        except:
            if 'token already used' not in response2.text.lower():
                print(f"❌ FAIL: Expected 'token already used' error in response")
                return False
        
        print(f"✅ Second download correctly blocked with 403")
        
        # Step 4: Third download - should also fail
        print("4. Third download attempt (should also fail)...")
        response3 = self.session.get(f"{self.base_url}/deck/download?token={token}", timeout=10)
        
        if response3.status_code != 403:
            print(f"❌ FAIL: Third download should return 403, got {response3.status_code}")
            return False
        
        print(f"✅ Third download correctly blocked with 403")
        
        print("\n🎉 SINGLE-USE TOKEN ENFORCEMENT: WORKING CORRECTLY!")
        return True
    
    def test_invalid_token(self):
        """Test invalid token scenario"""
        print("\n🚫 Testing Invalid Token Scenario")
        print("=" * 50)
        
        invalid_token = "tok_invalid123456789"
        response = self.session.get(f"{self.base_url}/deck/download?token={invalid_token}", timeout=10)
        
        if response.status_code != 404:
            print(f"❌ FAIL: Expected 404 for invalid token, got {response.status_code}")
            return False
        
        print(f"✅ Invalid token correctly rejected with 404")
        return True
    
    def test_race_condition_protection(self):
        """Test concurrent access to verify atomic update protection"""
        print("\n⚡ Testing Race Condition Protection")
        print("=" * 50)
        
        # Get a fresh token
        payload = {"email": "concurrent@example.com"}
        token_response = self.session.post(f"{self.base_url}/deck/request", json=payload, timeout=15)
        
        if token_response.status_code != 200:
            print(f"❌ FAIL: Token request failed")
            return False
        
        token_data = token_response.json()
        token = token_data.get('token')
        
        print(f"Token for concurrent test: {token[:8]}...")
        
        results = []
        
        def download_attempt(token, attempt_id):
            try:
                response = self.session.get(f"{self.base_url}/deck/download?token={token}", timeout=10)
                results.append({
                    'attempt_id': attempt_id,
                    'status_code': response.status_code,
                    'success': response.status_code == 200,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                results.append({
                    'attempt_id': attempt_id,
                    'status_code': 'error',
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # Launch 5 concurrent download attempts
        threads = []
        for i in range(5):
            thread = threading.Thread(target=download_attempt, args=(token, i+1))
            threads.append(thread)
        
        print("Launching 5 concurrent download attempts...")
        
        # Start all threads nearly simultaneously
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Analyze results
        successful_downloads = [r for r in results if r['success']]
        failed_downloads = [r for r in results if not r['success']]
        
        print(f"Results: {len(successful_downloads)} successful, {len(failed_downloads)} failed")
        
        for result in results:
            status = "✅ SUCCESS" if result['success'] else "❌ BLOCKED"
            print(f"  Attempt {result['attempt_id']}: {status} ({result['status_code']})")
        
        if len(successful_downloads) == 1 and len(failed_downloads) == 4:
            print(f"\n🎉 RACE CONDITION PROTECTION: WORKING CORRECTLY!")
            print(f"   Only 1 of 5 concurrent attempts succeeded, 4 were blocked")
            return True
        elif len(successful_downloads) > 1:
            print(f"\n❌ RACE CONDITION DETECTED!")
            print(f"   {len(successful_downloads)} concurrent downloads succeeded (should be only 1)")
            return False
        else:
            print(f"\n⚠️  UNEXPECTED RESULT:")
            print(f"   {len(successful_downloads)} successful, {len(failed_downloads)} failed")
            return False
    
    def run_all_tests(self):
        """Run all token enforcement tests"""
        print(f"🚀 Single-Use Token Enforcement Testing")
        print(f"Backend URL: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        tests = [
            ("Single-Use Token Enforcement", self.test_single_use_enforcement),
            ("Invalid Token Scenario", self.test_invalid_token),
            ("Race Condition Protection", self.test_race_condition_protection)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                success = test_func()
                if success:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL {test_name}: Unexpected error - {str(e)}")
                failed += 1
            
            time.sleep(1)  # Small delay between tests
        
        # Summary
        print("\n" + "=" * 80)
        print(f"🏁 TOKEN ENFORCEMENT TEST SUMMARY")
        print(f"Total Tests: {passed + failed}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%" if (passed + failed) > 0 else "0%")
        
        if failed == 0:
            print(f"\n🎉 ALL TESTS PASSED - SINGLE-USE TOKEN ENFORCEMENT IS WORKING CORRECTLY!")
        else:
            print(f"\n⚠️  SOME TESTS FAILED - REVIEW IMPLEMENTATION")
        
        return failed == 0

if __name__ == "__main__":
    tester = TokenEnforcementTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)