#!/usr/bin/env python3
"""
Railway Deployment Checker and Fix Guide
"""

import requests
import json

def check_railway_deployment():
    """Check Railway deployment status and provide fix guidance"""
    
    print("🚂 RAILWAY DEPLOYMENT DIAGNOSIS")
    print("="*50)
    
    railway_url = "https://web-production-02077.up.railway.app"
    
    print(f"\n🔍 Testing your Railway backend: {railway_url}")
    
    try:
        response = requests.get(f"{railway_url}/health", timeout=30)
        if response.status_code == 200:
            print("✅ Railway backend is WORKING!")
            print(f"📊 Response: {response.json()}")
            return True
        else:
            print(f"⚠️  Railway responding but with error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Railway backend is DOWN or UNREACHABLE!")
        print("\n🔧 POSSIBLE CAUSES & FIXES:")
        print("1. 💰 Railway service may be suspended (check billing)")
        print("2. 🚀 Deployment may have failed (check Railway dashboard)")
        print("3. 🔧 Service may be sleeping (try visiting the URL in browser)")
        print("4. 🌐 Domain/URL may have changed")
        
        return False
        
    except requests.exceptions.Timeout:
        print("⏰ Railway backend is responding slowly (may be cold start)")
        print("📝 This is common with Railway - try again in 30 seconds")
        return False
        
    except Exception as e:
        print(f"🚨 Unexpected error: {e}")
        return False

def provide_railway_fixes():
    """Provide step-by-step Railway fixes"""
    
    print(f"\n🛠️  RAILWAY DEPLOYMENT FIXES")
    print("="*50)
    
    print("1. 🌐 VISIT RAILWAY DASHBOARD:")
    print("   → Go to https://railway.app/dashboard")
    print("   → Find your 'Spam-detector' or backend project")
    print("   → Check the deployment status")
    
    print(f"\n2. 📊 CHECK DEPLOYMENT LOGS:")
    print("   → Click on your service in Railway dashboard")
    print("   → Go to 'Deployments' tab")
    print("   → Check latest deployment status")
    print("   → Look for error messages in logs")
    
    print(f"\n3. 🔧 COMMON FIXES:")
    print("   → If deployment failed: Redeploy from Railway dashboard")
    print("   → If service is sleeping: Visit your Railway URL in browser")
    print("   → If domain changed: Update frontend URL in authService.ts")
    print("   → If suspended: Check Railway billing/usage limits")
    
    print(f"\n4. 🚀 MANUAL REDEPLOY:")
    print("   → In Railway dashboard, click 'Deploy'")
    print("   → Or push a commit to your connected GitHub repo")
    
    print(f"\n5. 🔍 VERIFY ENVIRONMENT VARIABLES:")
    print("   → Check that all required env vars are set in Railway")
    print("   → DATABASE_URL, JWT_SECRET_KEY, CORS_ORIGINS, etc.")

def test_alternative_solutions():
    """Provide alternative solutions if Railway is down"""
    
    print(f"\n🔄 ALTERNATIVE SOLUTIONS")
    print("="*50)
    
    print("📍 OPTION 1: Use Local Development")
    print("   1. Run backend locally on your computer")
    print("   2. Update frontend to use http://localhost:5001")
    print("   3. Test authentication locally")
    
    print(f"\n📍 OPTION 2: Deploy to Different Platform")
    print("   → Vercel (serverless)")
    print("   → Render (similar to Railway)")
    print("   → DigitalOcean App Platform")
    print("   → AWS/Google Cloud")
    
    print(f"\n📍 OPTION 3: Use Railway Alternative URL")
    print("   → Railway sometimes provides multiple URLs")
    print("   → Check Railway dashboard for alternative domains")
    print("   → Some deployments use railway.internal URLs")

if __name__ == "__main__":
    is_working = check_railway_deployment()
    
    if not is_working:
        provide_railway_fixes()
        test_alternative_solutions()
    
    print(f"\n📞 NEED IMMEDIATE HELP?")
    print("="*50)
    print("1. Check Railway status page: https://status.railway.app/")
    print("2. Visit Railway dashboard: https://railway.app/dashboard")
    print("3. Check Railway documentation: https://docs.railway.app/")
    print("4. If urgent: Run backend locally for testing")
