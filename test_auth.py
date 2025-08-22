#!/usr/bin/env python3
"""
Test authentication endpoints to debug the issue
"""
import requests
import json
import os

# Backend URL - adjust as needed
BACKEND_URL = "http://localhost:5001"  # Local testing
# BACKEND_URL = "https://web-production-02077.up.railway.app"  # Production

def test_authentication():
    """Test authentication endpoints"""
    print("🧪 Testing Authentication Endpoints")
    print("=" * 50)
    
    # Test data
    test_user = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    # Test 1: Health check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Registration
    print("\n2️⃣ Testing Registration...")
    try:
        response = requests.post(f"{BACKEND_URL}/register", 
                                json=test_user,
                                headers={"Content-Type": "application/json"})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
        else:
            print(f"⚠️ Registration issue: {response.json()}")
    except Exception as e:
        print(f"❌ Registration failed: {e}")
    
    # Test 3: Login
    print("\n3️⃣ Testing Login...")
    try:
        response = requests.post(f"{BACKEND_URL}/login", 
                                json=test_user,
                                headers={"Content-Type": "application/json"})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return response.json().get("access_token")
        else:
            print(f"⚠️ Login issue: {response.json()}")
    except Exception as e:
        print(f"❌ Login failed: {e}")
    
    return None

def test_malformed_requests():
    """Test various malformed requests to understand the issue"""
    print("\n🔍 Testing Malformed Requests")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Empty JSON",
            "data": {}
        },
        {
            "name": "Missing password",
            "data": {"email": "test@example.com"}
        },
        {
            "name": "Missing email",
            "data": {"password": "testpass123"}
        },
        {
            "name": "Empty strings",
            "data": {"email": "", "password": ""}
        },
        {
            "name": "Whitespace only",
            "data": {"email": "   ", "password": "   "}
        },
        {
            "name": "None values",
            "data": {"email": None, "password": None}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        try:
            response = requests.post(f"{BACKEND_URL}/login", 
                                    json=test_case['data'],
                                    headers={"Content-Type": "application/json"})
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"❌ Request failed: {e}")

def test_content_types():
    """Test different content types"""
    print("\n📋 Testing Content Types")
    print("=" * 50)
    
    test_user = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    # Test with form data
    print("\n🧪 Testing with form data...")
    try:
        response = requests.post(f"{BACKEND_URL}/login", 
                                data=test_user)  # This sends as form data
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Form data test failed: {e}")
    
    # Test with JSON but wrong content type
    print("\n🧪 Testing JSON with wrong content type...")
    try:
        response = requests.post(f"{BACKEND_URL}/login", 
                                json=test_user)  # No explicit content-type
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ JSON test failed: {e}")

if __name__ == "__main__":
    # Start by testing auth
    token = test_authentication()
    
    # Test malformed requests
    test_malformed_requests()
    
    # Test content types
    test_content_types()
    
    print("\n" + "=" * 50)
    print("🏁 Testing Complete!")
