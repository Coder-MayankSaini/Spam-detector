#!/usr/bin/env python3
"""
Authentication Debugging Tool for Spam Detector App
This tool helps identify and fix authentication issues between frontend and backend.
"""

import requests
import json
import sys
from datetime import datetime

class AuthDebugger:
    def __init__(self):
        # Your actual backend URLs
        self.urls_to_test = [
            "http://localhost:5001",  # Local development
            "https://web-production-02077.up.railway.app",  # Your Railway backend
            "http://localhost:5000",  # Alternative local port
        ]
        
        self.test_user = {
            "email": "debug@test.com",
            "password": "debugpass123"
        }
    
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🔧 {title}")
        print(f"{'='*60}")
    
    def print_subheader(self, title):
        print(f"\n--- {title} ---")
    
    def test_url_accessibility(self, base_url):
        """Test if the backend URL is accessible"""
        print(f"🌐 Testing: {base_url}")
        
        try:
            # Test health endpoint
            response = requests.get(f"{base_url}/health", timeout=10)
            print(f"   ✅ Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   📊 Response: {response.json()}")
                return True
            else:
                print(f"   ⚠️  Response: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection refused - server not running or unreachable")
            return False
        except requests.exceptions.Timeout:
            print(f"   ⏰ Request timed out")
            return False
        except Exception as e:
            print(f"   🚨 Error: {e}")
            return False
    
    def test_authentication_endpoint(self, base_url, endpoint):
        """Test authentication endpoints with various scenarios"""
        print(f"\n🔐 Testing {endpoint} at {base_url}")
        
        test_cases = [
            {
                "name": "✅ Valid credentials",
                "data": self.test_user,
                "expected_success": True
            },
            {
                "name": "❌ Empty JSON",
                "data": {},
                "expected_success": False
            },
            {
                "name": "❌ Missing password", 
                "data": {"email": self.test_user["email"]},
                "expected_success": False
            },
            {
                "name": "❌ Missing email",
                "data": {"password": self.test_user["password"]},
                "expected_success": False
            },
            {
                "name": "❌ Empty strings",
                "data": {"email": "", "password": ""},
                "expected_success": False
            },
            {
                "name": "❌ Whitespace only",
                "data": {"email": "   ", "password": "   "},
                "expected_success": False
            }
        ]
        
        for test_case in test_cases:
            print(f"\n  🧪 {test_case['name']}")
            try:
                response = requests.post(
                    f"{base_url}/{endpoint}",
                    json=test_case['data'],
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    timeout=10
                )
                
                print(f"     Status: {response.status_code}")
                
                try:
                    response_json = response.json()
                    if response.status_code in [200, 201]:
                        print(f"     ✅ Success: {response_json.get('message', 'OK')}")
                        if 'access_token' in response_json:
                            print(f"     🎫 Token received: {response_json['access_token'][:50]}...")
                    else:
                        print(f"     ⚠️  Error: {response_json.get('error', 'Unknown error')}")
                        if 'received_data' in response_json:
                            print(f"     📨 Server received: {response_json['received_data']}")
                except:
                    print(f"     📄 Raw response: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"     🚨 Request failed: {e}")
    
    def test_cors_preflight(self, base_url):
        """Test CORS preflight requests"""
        print(f"\n🌐 Testing CORS for {base_url}")
        
        try:
            response = requests.options(
                f"{base_url}/login",
                headers={
                    "Origin": "https://spamwall.vercel.app",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                }
            )
            
            print(f"   Status: {response.status_code}")
            cors_headers = {
                k: v for k, v in response.headers.items() 
                if k.lower().startswith('access-control')
            }
            
            if cors_headers:
                print("   ✅ CORS Headers found:")
                for header, value in cors_headers.items():
                    print(f"      {header}: {value}")
            else:
                print("   ❌ No CORS headers found")
                
        except Exception as e:
            print(f"   🚨 CORS test failed: {e}")
    
    def test_frontend_request_format(self, base_url):
        """Test the exact format your frontend sends"""
        print(f"\n📱 Testing Frontend Request Format for {base_url}")
        
        # Simulate exactly what your React frontend sends
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Origin': 'https://spamwall.vercel.app',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        payload = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        
        print(f"   📨 Sending request with headers: {headers}")
        print(f"   📦 Payload: {payload}")
        
        try:
            response = requests.post(
                f"{base_url}/login",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            print(f"   📊 Response Status: {response.status_code}")
            print(f"   📋 Response Headers: {dict(response.headers)}")
            
            try:
                result = response.json()
                print(f"   📄 Response Body: {json.dumps(result, indent=2)}")
            except:
                print(f"   📄 Raw Response: {response.text}")
                
        except Exception as e:
            print(f"   🚨 Frontend format test failed: {e}")
    
    def generate_fix_recommendations(self, working_urls):
        """Generate specific fix recommendations"""
        print(f"\n🛠️  RECOMMENDED FIXES")
        print("="*60)
        
        if not working_urls:
            print("❌ NO WORKING BACKEND FOUND!")
            print("\n🔧 IMMEDIATE FIXES NEEDED:")
            print("1. Check if your Railway backend is deployed and running")
            print("2. Verify your Railway backend URL is correct")
            print("3. Check Railway service logs for errors")
            print("4. Ensure all environment variables are set on Railway")
            
        else:
            print(f"✅ Working backend(s) found: {working_urls}")
            print("\n🔧 FRONTEND FIXES:")
            
            # Check if Railway URL is working
            railway_url = "https://web-production-02077.up.railway.app"
            if railway_url not in working_urls:
                print(f"1. ⚠️  Railway backend ({railway_url}) is not responding")
                print("   - Check Railway deployment status")
                print("   - Verify environment variables are set")
                print("   - Check Railway service logs")
                
            print("\n2. 📝 Update your frontend authService.ts:")
            print(f"   Replace the baseUrl with: '{working_urls[0]}'")
            
            print("\n3. 🌐 Verify CORS configuration in your backend")
            print("   Ensure your frontend domain is allowed")
    
    def run_full_diagnosis(self):
        """Run complete authentication diagnosis"""
        self.print_header("AUTHENTICATION DEBUGGING TOOL")
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        working_urls = []
        
        # Test URL accessibility
        self.print_subheader("1. Testing Backend Accessibility")
        for url in self.urls_to_test:
            if self.test_url_accessibility(url):
                working_urls.append(url)
        
        if not working_urls:
            print("\n❌ No working backends found! Cannot proceed with auth tests.")
            self.generate_fix_recommendations(working_urls)
            return
        
        # Test authentication endpoints
        for url in working_urls:
            self.print_subheader(f"2. Testing Authentication - {url}")
            self.test_authentication_endpoint(url, "register")
            self.test_authentication_endpoint(url, "login")
            
            self.test_cors_preflight(url)
            self.test_frontend_request_format(url)
        
        # Generate recommendations
        self.generate_fix_recommendations(working_urls)
        
        self.print_header("DEBUGGING COMPLETE")

if __name__ == "__main__":
    debugger = AuthDebugger()
    debugger.run_full_diagnosis()
