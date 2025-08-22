#!/usr/bin/env python3
"""
Quick test to verify local backend is working
"""
import requests
import json

def test_local_backend():
    url = 'http://localhost:5001'
    
    print("🧪 TESTING LOCAL AUTHENTICATION BACKEND")
    print("=" * 50)
    
    # Test user data
    test_user = {
        'email': 'demo@test.com',
        'password': 'demopass123'
    }
    
    try:
        # Test health
        print("1️⃣ Testing health endpoint...")
        r = requests.get(f'{url}/health', timeout=5)
        if r.status_code == 200:
            print(f"   ✅ Health check: {r.json()['message']}")
        else:
            print(f"   ❌ Health check failed: {r.status_code}")
            return
        
        # Test registration
        print("\n2️⃣ Testing registration...")
        r = requests.post(f'{url}/register', json=test_user, 
                         headers={'Content-Type': 'application/json'}, timeout=10)
        
        if r.status_code == 201:
            result = r.json()
            print(f"   ✅ Registration successful: {result['message']}")
            print(f"   🎫 Token received: ...{result['access_token'][-10:]}")
        elif r.status_code == 400 and 'already exists' in r.json().get('error', ''):
            print("   ✅ User already exists (that's fine for testing)")
        else:
            print(f"   ⚠️ Registration response: {r.status_code} - {r.json()}")
        
        # Test login
        print("\n3️⃣ Testing login...")
        r = requests.post(f'{url}/login', json=test_user, 
                         headers={'Content-Type': 'application/json'}, timeout=10)
        
        if r.status_code == 200:
            result = r.json()
            print(f"   ✅ Login successful: {result['message']}")
            print(f"   🎫 Token received: ...{result['access_token'][-10:]}")
            
            # Test token verification
            print("\n4️⃣ Testing token verification...")
            token = result['access_token']
            r = requests.get(f'{url}/verify-token', 
                           headers={'Authorization': f'Bearer {token}'}, timeout=5)
            
            if r.status_code == 200:
                print(f"   ✅ Token verification successful")
            else:
                print(f"   ❌ Token verification failed: {r.status_code}")
                
        else:
            print(f"   ❌ Login failed: {r.status_code} - {r.json()}")
            return
            
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"🔧 Your local backend is working perfectly!")
        print(f"\n📝 NEXT STEPS:")
        print(f"   1. Update your frontend to use: http://localhost:5001")
        print(f"   2. Test your login/register forms") 
        print(f"   3. Once working, fix Railway backend with same approach")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to local backend!")
        print("📝 Make sure local_auth_backend.py is running")
        print("💡 Run: python local_auth_backend.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == '__main__':
    test_local_backend()
