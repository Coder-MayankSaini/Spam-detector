#!/usr/bin/env python3
"""
Quick test for the enhanced password reset email functionality
"""
import requests
import json

def test_enhanced_password_reset():
    """Test the forgot-password endpoint with the new HTML email"""
    
    # Configuration
    API_BASE = "http://127.0.0.1:5000"  # Adjust port if needed
    TEST_EMAIL = "test@example.com"  # Use a valid email you control for testing
    
    print("🧪 Testing Enhanced Password Reset Email")
    print(f"📧 Test email: {TEST_EMAIL}")
    print(f"🌐 API Base: {API_BASE}")
    print("-" * 50)
    
    # Test data
    data = {
        "email": TEST_EMAIL
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🚀 Sending password reset request...")
        response = requests.post(
            f"{API_BASE}/forgot-password", 
            json=data, 
            headers=headers, 
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📝 Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS! Password reset request sent")
            print("💌 Check your email for the beautiful HTML template!")
            print("\n🎨 New email features:")
            print("   ✨ Gradient background design")
            print("   🛡️ Professional branding with shield logo")
            print("   🔐 Prominent 'Reset My Password' button")
            print("   ℹ️ Security information box")
            print("   🔗 Alternative text link if button doesn't work")
            print("   📱 Mobile-responsive design")
            print("   🏢 Professional footer with branding")
            
        elif response.status_code == 400:
            print("⚠️  Bad Request - Check email format")
        elif response.status_code == 500:
            print("❌ Server Error - Check if server is running and configured")
        else:
            print(f"🤔 Unexpected response: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error!")
        print("💡 Make sure the Flask server is running:")
        print("   cd Spam-backend")
        print("   python app.py")
        print("   OR")
        print("   python run_server.py")
        
    except requests.exceptions.Timeout:
        print("⏰ Request timed out!")
        
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
    
    print("\n" + "=" * 50)
    print("📝 Note: The email now includes:")
    print("   • Professional HTML design with gradients")
    print("   • Brand colors and shield emoji logo")
    print("   • Clear call-to-action button")
    print("   • Security tips and information")
    print("   • Both HTML and plain text versions")
    print("   • Mobile-friendly responsive design")

if __name__ == "__main__":
    test_enhanced_password_reset()
