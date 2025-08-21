#!/usr/bin/env python3
"""
Railway Deployment Helper
Simplified deployment for Railway (Backend + Database) + Vercel (Frontend)
"""
import os
import json
import subprocess
import sys
from pathlib import Path

def check_railway_requirements():
    """Check if everything is ready for Railway deployment"""
    print("🚂 Checking Railway deployment requirements...")
    
    issues = []
    
    # Check required files for Railway
    required_files = [
        'Spam-backend/requirements.txt',
        'Spam-backend/Procfile',
        'Spam-backend/app_postgresql.py',
        'Spam-backend/database.py',
        'frontend-react/package.json',
        'frontend-react/vercel.json'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            issues.append(f"Missing: {file_path}")
    
    # Check if git is initialized
    if not os.path.exists('.git'):
        issues.append("Git repository not initialized")
    
    return issues

def create_railway_env_template():
    """Create environment variables template for Railway"""
    env_template = """
# Railway Environment Variables Template
# Copy these to your Railway project dashboard

JWT_SECRET_KEY=your-256-bit-secret-key-here-change-me
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-16-character-app-password
EMAIL_FROM=your-email@gmail.com
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
DEBUG=false

# DATABASE_URL is automatically provided by Railway PostgreSQL service
# No need to set this manually - Railway handles it automatically!
"""
    
    with open('RAILWAY_ENV_VARS.txt', 'w', encoding='utf-8') as f:
        f.write(env_template.strip())
    
    print("✅ Created RAILWAY_ENV_VARS.txt")

def create_deployment_checklist():
    """Create simplified Railway deployment checklist"""
    checklist = """
# 🚂 Railway + Vercel Deployment Checklist

## ✅ Pre-Deployment Setup

### 1. Accounts Setup
- [ ] Create Railway account at [railway.app](https://railway.app)
- [ ] Create Vercel account at [vercel.com](https://vercel.com)
- [ ] Connect both accounts to your GitHub

### 2. Email Setup (Gmail)
- [ ] Enable 2-factor authentication on Gmail
- [ ] Generate app password for email
- [ ] Test email sending locally

### 3. Repository Setup
- [ ] Push all code to GitHub repository
- [ ] Ensure main branch has latest changes

## 🚂 Backend + Database (Railway)

### Step 1: Create Railway Project
- [ ] Go to [railway.app](https://railway.app)
- [ ] Click "New Project" → "Deploy from GitHub repo"
- [ ] Select your Spam Detector repository
- [ ] Railway auto-detects Python Flask app

### Step 2: Add PostgreSQL Database
- [ ] In Railway project dashboard
- [ ] Click "New Service" → "Database" → "Add PostgreSQL"
- [ ] Railway automatically connects database to your app

### Step 3: Configure Environment Variables
Copy from RAILWAY_ENV_VARS.txt to Railway dashboard:
- [ ] JWT_SECRET_KEY
- [ ] EMAIL_HOST
- [ ] EMAIL_PORT  
- [ ] EMAIL_USER
- [ ] EMAIL_PASSWORD
- [ ] EMAIL_FROM
- [ ] CORS_ORIGINS (update with your Vercel URL)
- [ ] DEBUG=false

### Step 4: Deploy Backend
- [ ] Railway automatically deploys on git push
- [ ] Note your Railway app URL: https://your-app.railway.app
- [ ] Test health endpoint: https://your-app.railway.app/health

## 🌐 Frontend (Vercel)

### Step 1: Deploy Frontend
- [ ] Go to [vercel.com](https://vercel.com)
- [ ] Click "New Project" → Import from GitHub
- [ ] Select your repository
- [ ] Set root directory to `frontend-react`
- [ ] Framework preset: "Create React App"

### Step 2: Environment Variables
- [ ] Add REACT_APP_API_BASE_URL = https://your-app.railway.app

### Step 3: Deploy
- [ ] Click Deploy
- [ ] Note your Vercel URL: https://your-app.vercel.app

## 🔧 Final Configuration

### Update CORS Origins
- [ ] Go back to Railway dashboard
- [ ] Update CORS_ORIGINS with your actual Vercel URL
- [ ] CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000

## 🧪 Testing

### Backend Tests
- [ ] https://your-app.railway.app/health → Should return {"status": "healthy"}
- [ ] Test user registration via frontend
- [ ] Test email functionality

### Frontend Tests  
- [ ] https://your-app.vercel.app → Should load homepage
- [ ] Register new account
- [ ] Login functionality
- [ ] Spam analysis works
- [ ] History page loads
- [ ] Password reset emails work

## 🎉 Success!

Your app is now live:
- **Frontend**: https://your-app.vercel.app
- **Backend**: https://your-app.railway.app  
- **Database**: Managed by Railway (PostgreSQL)

## 💰 Cost Estimate

### Free Tier (Good for testing/demos)
- Railway: $0/month (with usage limits)
- Vercel: $0/month (hobby use)
- **Total**: $0/month

### Production Tier
- Railway: ~$5-20/month (backend + database)
- Vercel: $0/month (still free for most apps)
- **Total**: ~$5-20/month

## 🆘 Troubleshooting

### Common Issues
1. **Build fails on Railway**:
   - Check requirements.txt has all dependencies
   - Verify Python version in runtime.txt

2. **Database connection errors**:
   - Railway automatically provides DATABASE_URL
   - Don't manually set database connection

3. **CORS errors**:
   - Ensure CORS_ORIGINS includes your Vercel URL
   - Update after frontend deployment

4. **Email not working**:
   - Verify Gmail app password
   - Check email environment variables

### Get Help
- Railway docs: [docs.railway.app](https://docs.railway.app)
- Vercel docs: [vercel.com/docs](https://vercel.com/docs)
- Check Railway project logs for errors
"""
    
    with open('RAILWAY_DEPLOYMENT_CHECKLIST.md', 'w', encoding='utf-8') as f:
        f.write(checklist.strip())
    
    print("✅ Created RAILWAY_DEPLOYMENT_CHECKLIST.md")

def main():
    """Main Railway deployment helper"""
    print("🚂 Railway + Vercel Deployment Helper")
    print("=" * 50)
    
    # Check requirements
    issues = check_railway_requirements()
    
    if issues:
        print("❌ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nPlease fix these issues first.")
        return
    
    print("✅ All required files found!")
    
    # Create helpful files
    create_railway_env_template()
    create_deployment_checklist()
    
    print("\n" + "=" * 50)
    print("🎉 Railway deployment preparation complete!")
    print("\n📋 Next steps:")
    print("1. Check RAILWAY_DEPLOYMENT_CHECKLIST.md")
    print("2. Copy environment variables from RAILWAY_ENV_VARS.txt")
    print("3. Deploy to Railway (backend + database)")
    print("4. Deploy to Vercel (frontend)")
    
    print("\n🌟 Benefits of Railway + Vercel:")
    print("✅ Only 2 platforms to manage")
    print("✅ Railway provides backend + database together")  
    print("✅ Automatic deployments from GitHub")
    print("✅ Free tier available for both platforms")
    print("✅ Simpler environment variable management")
    
    print(f"\n📁 Your deployment architecture:")
    print(f"🌐 Frontend (Vercel) → 🚂 Backend + Database (Railway)")

if __name__ == "__main__":
    main()
