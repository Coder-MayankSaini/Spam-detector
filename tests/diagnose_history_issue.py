#!/usr/bin/env python3
"""
Diagnostic tool to check the "Failed to fetch history" issue
"""
import requests
import json
import time

def diagnose_history_issue():
    """Diagnose the history fetch issue step by step"""
    
    print("🔍 Diagnosing 'Failed to fetch history' Issue")
    print("=" * 50)
    
    # Test different ports
    ports_to_test = [5000, 5001]
    backend_url = None
    
    print("1. Testing Backend Connectivity")
    print("-" * 30)
    
    for port in ports_to_test:
        url = f"http://localhost:{port}"
        try:
            response = requests.get(f"{url}/health", timeout=3)
            if response.status_code == 200:
                print(f"✅ Backend found on port {port}")
                print(f"   Health check: {response.json()}")
                backend_url = url
                break
            else:
                print(f"❌ Port {port}: HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Port {port}: Connection refused")
        except requests.exceptions.Timeout:
            print(f"⏱️ Port {port}: Timeout")
        except Exception as e:
            print(f"❌ Port {port}: {e}")
    
    if not backend_url:
        print("\n❌ PROBLEM FOUND: Backend server not running!")
        print("\n🔧 SOLUTION:")
        print("   cd Spam-backend")
        print("   python run_server.py")
        print("   OR")
        print("   python app.py")
        return
    
    print(f"\n2. Testing Authentication Endpoints")
    print("-" * 30)
    
    # Test auth endpoints
    auth_endpoints = ['/register', '/login', '/forgot-password']
    for endpoint in auth_endpoints:
        try:
            # Just test if endpoint exists with a HEAD request
            response = requests.post(f"{backend_url}{endpoint}", 
                                   json={}, timeout=3)
            # We expect 400 (bad request) which means endpoint exists
            if response.status_code in [400, 422]:
                print(f"✅ {endpoint}: Endpoint exists")
            else:
                print(f"⚠️ {endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    print(f"\n3. Testing History Endpoint (No Auth)")
    print("-" * 30)
    
    try:
        response = requests.get(f"{backend_url}/history", timeout=3)
        if response.status_code == 401:
            print("✅ /history: Authentication required (expected)")
        elif response.status_code == 422:
            print("✅ /history: JWT token missing (expected)")
        else:
            print(f"⚠️ /history: Unexpected status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ /history: {e}")
    
    print(f"\n4. Testing With Mock Authentication")
    print("-" * 30)
    
    # Try to register a test user and get history
    test_email = f"test_{int(time.time())}@example.com"
    test_password = "test123456"
    
    try:
        # Register test user
        reg_response = requests.post(f"{backend_url}/register", 
                                   json={
                                       "email": test_email,
                                       "password": test_password
                                   }, timeout=5)
        
        if reg_response.status_code == 201:
            print("✅ Test user registration: Success")
            token_data = reg_response.json()
            
            if 'access_token' in token_data:
                token = token_data['access_token']
                print("✅ JWT token received")
                
                # Test history with token
                headers = {'Authorization': f'Bearer {token}'}
                hist_response = requests.get(f"{backend_url}/history", 
                                           headers=headers, timeout=5)
                
                if hist_response.status_code == 200:
                    history_data = hist_response.json()
                    print(f"✅ History fetch: Success")
                    print(f"   Records found: {len(history_data)}")
                    
                    if len(history_data) == 0:
                        print("ℹ️ No history records (expected for new user)")
                    else:
                        print(f"   Sample: {history_data[0] if history_data else 'None'}")
                        
                else:
                    print(f"❌ History fetch failed: {hist_response.status_code}")
                    print(f"   Error: {hist_response.text}")
                    
            else:
                print("❌ No access token in registration response")
                print(f"   Response: {reg_response.text}")
                
        elif reg_response.status_code == 400 and "already exists" in reg_response.text:
            print("⚠️ Test user already exists, trying login...")
            
            # Try login instead
            login_response = requests.post(f"{backend_url}/login",
                                         json={
                                             "email": test_email,
                                             "password": test_password
                                         }, timeout=5)
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                token = token_data.get('access_token')
                
                if token:
                    headers = {'Authorization': f'Bearer {token}'}
                    hist_response = requests.get(f"{backend_url}/history", 
                                               headers=headers, timeout=5)
                    
                    if hist_response.status_code == 200:
                        print("✅ History fetch with existing user: Success")
                    else:
                        print(f"❌ History fetch failed: {hist_response.status_code}")
                        print(f"   Error: {hist_response.text}")
            else:
                print(f"❌ Login failed: {login_response.status_code}")
        else:
            print(f"❌ Registration failed: {reg_response.status_code}")
            print(f"   Error: {reg_response.text}")
            
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
    
    print(f"\n5. Frontend Configuration Check")
    print("-" * 30)
    
    # Check if frontend is pointing to the right backend URL
    if backend_url == "http://localhost:5000":
        print("⚠️ Backend running on port 5000, but frontend expects 5001")
        print("🔧 SOLUTION: Update frontend apiService.ts:")
        print("   Change: const API_BASE = 'http://localhost:5001';")
        print("   To:     const API_BASE = 'http://localhost:5000';")
    elif backend_url == "http://localhost:5001":
        print("✅ Backend on port 5001 matches frontend expectation")
    
    print(f"\n6. Summary & Recommendations")
    print("-" * 30)
    
    print("🎯 Most likely causes of 'Failed to fetch history':")
    print("   1. Backend server not running")
    print("   2. Port mismatch between frontend and backend")
    print("   3. Authentication token issues")
    print("   4. CORS configuration problems")
    print("   5. Windows firewall blocking requests")
    
    print(f"\n🔧 Quick fixes to try:")
    print("   1. Restart backend: cd Spam-backend && python run_server.py")
    print("   2. Clear browser localStorage and login again")
    print("   3. Check browser Network tab for exact error")
    print("   4. Run: python diagnose_network.py")

if __name__ == "__main__":
    diagnose_history_issue()
